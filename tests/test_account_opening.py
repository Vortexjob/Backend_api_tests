import uuid
import time
from conftest import make_grpc_request, create_metadata, confirm_operation, assert_success
from data import (
    CODE_MAKE_TXN_SHOP_OPERATION,
    ACCOUNT_ID_DEBIT, OPEN_ACCOUNT_CCY, PRODUCT_TYPE_ACCOUNT_OPENING
)


def test_account_opening_flow():
    """Тест-кейс: Создание и подтверждение запроса на открытие счета"""
    
    # === ШАГ 1: СОЗДАНИЕ ЗАПРОСА НА ОТКРЫТИЕ СЧЕТА ===
    print("\n=== ШАГ 1: Создание запроса на открытие счета ===")
    
    operation_id = str(uuid.uuid4())
    
    account_opening_data = {
        "operationId": operation_id,
        "productType": PRODUCT_TYPE_ACCOUNT_OPENING,
        "data": {
            "accountDebitId": ACCOUNT_ID_DEBIT,
            "openAccountCcy": OPEN_ACCOUNT_CCY,
            "productType": PRODUCT_TYPE_ACCOUNT_OPENING,
            "requestId": f"IB{int(time.time() * 1000)}",
            "accountIdDebit": ACCOUNT_ID_DEBIT,
            "operationId": operation_id,
            "txnId": None
        },
        "txnId": None
    }
    
    print(f"Operation ID: {operation_id}")
    print(f"Request ID: IB{int(time.time() * 1000)}")
    print(f"Валюта счета: {OPEN_ACCOUNT_CCY}")
    print(f"Данные: {account_opening_data}")
    
    create_response = make_grpc_request(CODE_MAKE_TXN_SHOP_OPERATION, account_opening_data, create_metadata())
    print(f"Ответ: {create_response}")
    
    assert_success(create_response, "Создание запроса на открытие счета")
    print("✅ Создание запроса на открытие счета успешно!")
    
    print("\nОжидание 2 секунд...")
    time.sleep(2)
    
    
    # === ШАГ 2: ПОДТВЕРЖДЕНИЕ ЗАПРОСА НА ОТКРЫТИЕ СЧЕТА ===
    print("\n=== ШАГ 2: Подтверждение запроса на открытие счета ===")
    
    print(f"Operation ID: {operation_id}")
    
    confirm_response = confirm_operation(operation_id)
    print(f"Ответ: {confirm_response}")
    
    assert_success(confirm_response, "Подтверждение запроса на открытие счета")
    print("✅ Подтверждение запроса на открытие счета успешно!")
    
    print("\n=== ✅ Тест пройден успешно ===")
