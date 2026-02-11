"""
Отправка всех видов депозитов из deposit_cases.json по одному запросу (open + confirm).
Не нагрузочный тест — один проход по кейсам. Новые кейсы добавляются в deposit_cases.json.
"""
import json
import os
import sys
import time
import uuid

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROTO_PATH = os.path.join(REPO_ROOT, "protofiles")
sys.path.insert(0, PROTO_PATH)

import grpc
import protofile_pb2 as pb2
import protofile_pb2_grpc as pb2_grpc

CASES_PATH = os.path.join(os.path.dirname(__file__), "deposit_cases.json")
DEFAULT_REQUEST_CODE = "MAKE_TXN_SHOP_OPERATION"
CODE_CONFIRM_TRANSFER = "CONFIRM_TRANSFER"


def load_cases():
    with open(CASES_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    if not cfg.get("session_key"):
        raise ValueError("В deposit_cases.json заполните session_key.")
    if not cfg.get("deposit_cases"):
        raise ValueError("В deposit_cases.json добавьте хотя бы один кейс в deposit_cases.")
    return cfg


def make_metadata(cfg):
    return (
        ("refid", str(uuid.uuid1())),
        ("sessionkey", cfg["session_key"]),
        ("device-type", cfg["device_type"]),
        ("user-agent-c", cfg["user_agent"]),
    )


def run_one_case(cfg, case, index):
    """
    Один кейс: открытие депозита (MAKE_TXN_SHOP_OPERATION) + подтверждение (CONFIRM_TRANSFER).
    Возвращает (name, success, response_or_error_text).
    """
    name = case.get("name", f"Кейс {index + 1}")
    account_id = case.get("accountDebitId") or cfg.get("default_account_debit_id")
    if not account_id:
        return (name, False, "Не задан accountDebitId и default_account_debit_id")

    data = {
        "depositType": case.get("depositType", ""),
        "depositId": case["depositId"],
        "mainIntType": case.get("mainIntType", "B"),
        "amount": case.get("amount", "10000"),
        "ccy": case.get("ccy", "KGS"),
        "rate": case.get("rate", ""),
        "termOfDeposit": case.get("termOfDeposit", ""),
        "accountDebitId": account_id,
        "accountIdDebit": account_id,
        "amountDebit": case.get("amount", "10000"),
        "productType": case.get("productType", "makeDepositApplication"),
        "childName": case.get("childName", ""),
        "childBirthdate": case.get("childBirthdate", ""),
        "files": case.get("files", []),
        "valueDate": cfg.get("valueDate", "2025.07.29"),
    }
    operation_id = str(uuid.uuid4())
    data["operationId"] = operation_id
    data["requestId"] = f"IB{int(time.time() * 1000)}_{index}"
    data["txnId"] = None
    if "depositTypeId" not in data:
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
    options = [tuple(o) for o in grpc_opts] if grpc_opts else [("grpc.enable_http_proxy", 0), ("grpc.keepalive_timeout_ms", 10000)]

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
            err = getattr(open_resp, "error", open_resp)
            return (name, False, str(err))

        otp = cfg.get("otp") or "111111"
        confirm_resp = do_request(CODE_CONFIRM_TRANSFER, {"operationId": operation_id, "otp": otp})
        if not getattr(confirm_resp, "success", False):
            err = getattr(confirm_resp, "error", confirm_resp)
            return (name, False, f"Confirm: {err}")
        return (name, True, None)
    except Exception as e:
        return (name, False, str(e))


def main():
    cfg = load_cases()
    cases = cfg["deposit_cases"]
    print(f"Отправка всех видов депозитов: {len(cases)} кейсов")
    print(f"  session: {cfg['session_key'][:12]}...")
    print()

    results = []
    for i, case in enumerate(cases):
        name, ok, err = run_one_case(cfg, case, i)
        results.append((name, ok, err))
        status = "OK" if ok else "FAIL"
        print(f"  [{status}] {name}")
        if not ok and err:
            print(f"         {err}")

    ok_count = sum(1 for _, ok, _ in results if ok)
    print()
    print(f"Итого: {ok_count}/{len(results)} успешно")


if __name__ == "__main__":
    main()
