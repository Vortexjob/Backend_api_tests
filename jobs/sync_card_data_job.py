"""
Job для синхронизации данных карты через IPC сервис
Голый запрос без проверок
Запускается отдельно, не участвует в общем цикле тестов
"""
import sys
import os
import grpc
import pytest
import json
import uuid

# Добавляем путь к protofiles
PROTOBUF_PATH = os.path.join(os.path.dirname(__file__), '..', 'protofiles')
sys.path.append(PROTOBUF_PATH)

# Импорт IPC protobuf файлов
import ipc_interactor_pb2
import ipc_interactor_pb2_grpc

# Импорт данных
import data as app_data


def sync_single_account(account_no: str):
    """Голый запрос без проверок"""
    request = ipc_interactor_pb2.SyncCardDataRequest(accountNo=account_no)
    
    metadata = (
        ('refid', str(uuid.uuid4())),
    )
    
    with grpc.insecure_channel(
            app_data.IPC_GRPC_SERVER_URL,
            options=app_data.IPC_GRPC_OPTIONS
    ) as channel:
        stub = ipc_interactor_pb2_grpc.InternalIpcInteractorStub(channel)
        response = stub.syncCardData(request, metadata=metadata, timeout=30.0)
        return response


def load_accounts_from_json():
    """Загрузка счетов из JSON"""
    json_path = os.path.join(os.path.dirname(__file__), 'accounts_for_sync.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


_ACCOUNTS_FOR_TEST = load_accounts_from_json() if os.path.exists(os.path.join(os.path.dirname(__file__), 'accounts_for_sync.json')) else []


@pytest.mark.parametrize("account_no", _ACCOUNTS_FOR_TEST if _ACCOUNTS_FOR_TEST else ["__no_accounts__"])
def test_sync_card_data(account_no):
    """Отправка одного запроса"""
    if account_no == "__no_accounts__":
        pytest.skip("Счета не загружены")
    
    response = sync_single_account(account_no)
    print(f"[{account_no}] Response: {response}")

