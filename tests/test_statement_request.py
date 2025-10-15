import uuid
import time
from conftest import make_grpc_request, create_metadata, confirm_operation, assert_success
from data import (
    CODE_MAKE_TXN_SHOP_OPERATION,
    ACCOUNT_ID_DEBIT, STATEMENT_LANGUAGE, DELIVERY_TYPE, PHONE_NUMBER, BRANCH_CODE,
    PRODUCT_TYPE_STATEMENT
)


def test_statement_request_flow():
    """Тест-кейс: Создание и подтверждение запроса на выписку по счету"""
    
    # === ШАГ 1: СОЗДАНИЕ ЗАПРОСА НА ВЫПИСКУ ===
    print("\n=== ШАГ 1: Создание запроса на выписку ===")
    
    operation_id = str(uuid.uuid4())
    
    statement_data = {
        "operationId": operation_id,
        "productType": PRODUCT_TYPE_STATEMENT,
        "data": {
            "statementLanguage": STATEMENT_LANGUAGE,
            "statementRequestFee": None,
            "deliveryType": DELIVERY_TYPE,
            "deliveryFee": None,
            "deliveryAddress": None,
            "phoneNumber": PHONE_NUMBER,
            "branchCode": BRANCH_CODE,
            "accountDebitId": ACCOUNT_ID_DEBIT,
            "accountDebitIds": [ACCOUNT_ID_DEBIT],
            "loanStatementType": None,
            "productType": PRODUCT_TYPE_STATEMENT,
            "requestId": f"IB{int(time.time() * 1000)}",
            "accountIdDebit": ACCOUNT_ID_DEBIT,
            "operationId": operation_id,
            "txnId": None
        },
        "txnId": None
    }
    
    print(f"Operation ID: {operation_id}")
    print(f"Request ID: IB{int(time.time() * 1000)}")
    print(f"Язык выписки: {STATEMENT_LANGUAGE}")
    print(f"Тип доставки: {DELIVERY_TYPE}")
    print(f"Счета: {[ACCOUNT_ID_DEBIT]}")
    print(f"Данные: {statement_data}")
    
    create_response = make_grpc_request(CODE_MAKE_TXN_SHOP_OPERATION, statement_data, create_metadata())
    print(f"Ответ: {create_response}")
    
    assert_success(create_response, "Создание запроса на выписку")
    print("✅ Создание запроса на выписку успешно!")
    
    print("\nОжидание 2 секунд...")
    time.sleep(2)
    
    
    # === ШАГ 2: ПОДТВЕРЖДЕНИЕ ЗАПРОСА НА ВЫПИСКУ ===
    print("\n=== ШАГ 2: Подтверждение запроса на выписку ===")
    
    print(f"Operation ID: {operation_id}")
    
    confirm_response = confirm_operation(operation_id)
    print(f"Ответ: {confirm_response}")
    
    assert_success(confirm_response, "Подтверждение запроса на выписку")
    print("✅ Подтверждение запроса на выписку успешно!")
    
    print("\n=== ✅ Тест пройден успешно ===")
