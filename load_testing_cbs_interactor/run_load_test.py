"""
Load testing: deposit opening requests to CBS interactor (gRPC).
Config and request data are in config.json — no DB, session_key and payload are edited there.
"""
import json
import os
import sys
import time
import uuid
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Parent repo: protofiles and grpc
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROTO_PATH = os.path.join(REPO_ROOT, "protofiles")
sys.path.insert(0, PROTO_PATH)

import grpc
import protofile_pb2 as pb2
import protofile_pb2_grpc as pb2_grpc

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
DEFAULT_REQUEST_CODE = "MAKE_TXN_SHOP_OPERATION"
CODE_CONFIRM_TRANSFER = "CONFIRM_TRANSFER"


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    if not cfg.get("session_key"):
        raise ValueError(
            "В config.json заполните session_key (и при необходимости остальные поля запроса)."
        )
    return cfg


def make_metadata(cfg):
    return (
        ("refid", str(uuid.uuid1())),
        ("sessionkey", cfg["session_key"]),
        ("device-type", cfg["device_type"]),
        ("user-agent-c", cfg["user_agent"]),
    )


def make_grpc_deposit_request(cfg, request_index, thread_id):
    """One gRPC deposit request. Returns (thread_id, request_index, response_or_exception)."""
    raw = cfg["deposit_request"]
    data = {k: v for k, v in raw.items() if not (isinstance(k, str) and k.startswith("_"))}
    operation_id = str(uuid.uuid4())
    data["operationId"] = operation_id
    data["requestId"] = f"IB{int(time.time() * 1000)}_{thread_id}_{request_index}"
    data["txnId"] = None
    if "depositTypeId" not in data and "depositId" in data:
        data["depositTypeId"] = data["depositId"]

    product_type = data.get("productType", "makeDepositApplication")
    payload = {
        "operationId": operation_id,
        "productType": product_type,
        "data": data,
        "txnId": None,
    }

    metadata = make_metadata(cfg)
    request_code = cfg.get("request_code") or DEFAULT_REQUEST_CODE

    grpc_opts = cfg.get("grpc_options")
    if grpc_opts:
        options = [tuple(o) for o in grpc_opts]
    else:
        options = [("grpc.enable_http_proxy", 0), ("grpc.keepalive_timeout_ms", 10000)]
    def do_request(code, data_dict):
        req = pb2.IncomingWebTransfer(code=code, data=json.dumps(data_dict))
        with grpc.secure_channel(
            cfg["grpc_server_url"],
            grpc.ssl_channel_credentials(),
            options=options,
        ) as channel:
            stub = pb2_grpc.WebTransferApiStub(channel)
            return stub.makeWebTransfer(req, metadata=metadata)

    try:
        open_resp = do_request(request_code, payload)
        if not getattr(open_resp, "success", False):
            return (thread_id, request_index, open_resp, None)

        otp = cfg.get("otp") or "111111"
        confirm_payload = {"operationId": operation_id, "otp": otp}
        confirm_resp = do_request(CODE_CONFIRM_TRANSFER, confirm_payload)
        return (thread_id, request_index, confirm_resp, None)
    except Exception as e:
        return (thread_id, request_index, None, e)


def run_thread(cfg, thread_id, results_list, lock):
    num_requests = cfg["num_requests_per_thread"]
    wait_for_response = cfg["wait_for_response"]

    if wait_for_response:
        for i in range(num_requests):
            out = make_grpc_deposit_request(cfg, i, thread_id)
            with lock:
                results_list.append(out)
    else:
        with ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [
                executor.submit(make_grpc_deposit_request, cfg, i, thread_id)
                for i in range(num_requests)
            ]
            for fut in as_completed(futures):
                with lock:
                    results_list.append(fut.result())


def main():
    cfg = load_config()
    num_threads = cfg["num_threads"]
    num_per_thread = cfg["num_requests_per_thread"]
    wait = cfg["wait_for_response"]

    request_code = cfg.get("request_code") or DEFAULT_REQUEST_CODE
    print(f"Load test: deposit opening (code={request_code})")
    print(f"  Threads: {num_threads}, requests per thread: {num_per_thread}, wait_for_response: {wait}")
    print(f"  Total requests: {num_threads * num_per_thread}")
    print()

    results = []
    lock = threading.Lock()
    threads = []
    t0 = time.perf_counter()

    for tid in range(num_threads):
        t = threading.Thread(target=run_thread, args=(cfg, tid, results, lock))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    elapsed = time.perf_counter() - t0
    ok = sum(1 for r in results if len(r) >= 4 and r[3] is None and r[2] and getattr(r[2], "success", False))
    err_resp = sum(1 for r in results if len(r) >= 4 and r[3] is None and r[2] and not getattr(r[2], "success", True))
    exc = sum(1 for r in results if len(r) >= 4 and r[3] is not None)

    print(f"Done in {elapsed:.2f} s")
    print(f"  Success: {ok}, Error response: {err_resp}, Exception: {exc}")
    if results and (err_resp or exc):
        for r in results:
            if len(r) >= 4 and (r[3] or (r[2] and not getattr(r[2], "success", True))):
                print(f"    Thread {r[0]} req {r[1]}: {r[3] or getattr(r[2], 'error', r[2])}")


if __name__ == "__main__":
    main()
