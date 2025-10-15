import uuid
import time
from conftest import make_grpc_request, create_metadata, confirm_operation, assert_success
from data import (
    CODE_MAKE_TXN_SHOP_OPERATION,
    ACCOUNT_ID_DEBIT, DELIVERY_TYPE, BRANCH_CODE, PHONE_NUMBER,
    AMOUNT_OF_CHECKBOOKS, TRUSTED_EMPLOYEE_FULL_NAME,
    PASSPORT_ID, ISSUED_BY, DATE_OF_ISSUE, CHECKBOOK_FEE,
    PRODUCT_TYPE_CHECKBOOK
)


def test_checkbook_request_flow():
    """Тест-кейс: Создание и подтверждение запроса на чековую книжку"""
    
    # === ШАГ 1: СОЗДАНИЕ ЗАПРОСА НА ЧЕКОВУЮ КНИЖКУ ===
    print("\n=== ШАГ 1: Создание запроса на чековую книжку ===")
    
    operation_id = str(uuid.uuid4())
    
    checkbook_data = {
        "operationId": operation_id,
        "productType": PRODUCT_TYPE_CHECKBOOK,
        "data": {
            "amountOfCheckbooks": AMOUNT_OF_CHECKBOOKS,
            "trustedEmployeeFullName": TRUSTED_EMPLOYEE_FULL_NAME,
            "passportId": PASSPORT_ID,
            "issuedBy": ISSUED_BY,
            "dateOfIssue": DATE_OF_ISSUE,
            "checkbookFee": CHECKBOOK_FEE,
            "deliveryType": DELIVERY_TYPE,
            "branchCode": BRANCH_CODE,
            "phoneNumber": PHONE_NUMBER,
            "deliveryAddress": None,
            "deliveryFee": None,
            "accountDebitId": ACCOUNT_ID_DEBIT,
            "productType": PRODUCT_TYPE_CHECKBOOK,
            "requestId": f"IB{int(time.time() * 1000)}",
            "accountIdDebit": ACCOUNT_ID_DEBIT,
            "operationId": operation_id,
            "txnId": None
        },
        "txnId": None
    }
    
    print(f"Operation ID: {operation_id}")
    print(f"Request ID: IB{int(time.time() * 1000)}")
    print(f"Количество книжек: {AMOUNT_OF_CHECKBOOKS}")
    print(f"Стоимость: {CHECKBOOK_FEE}")
    print(f"Доверенное лицо: {TRUSTED_EMPLOYEE_FULL_NAME}")
    print(f"Данные: {checkbook_data}")
    
    create_response = make_grpc_request(CODE_MAKE_TXN_SHOP_OPERATION, checkbook_data, create_metadata())
    print(f"Ответ: {create_response}")
    
    assert_success(create_response, "Создание запроса на чековую книжку")
    print("✅ Создание запроса на чековую книжку успешно!")
    
    print("\nОжидание 3 секунд...")
    time.sleep(3)
    
    
    # === ШАГ 2: ПОДТВЕРЖДЕНИЕ ЗАПРОСА НА ЧЕКОВУЮ КНИЖКУ ===
    print("\n=== ШАГ 2: Подтверждение запроса на чековую книжку ===")
    
    print(f"Operation ID: {operation_id}")
    
    confirm_response = confirm_operation(operation_id)
    print(f"Ответ: {confirm_response}")
    
    assert_success(confirm_response, "Подтверждение запроса на чековую книжку")
    print("✅ Подтверждение запроса на чековую книжку успешно!")
    
    print("\n=== ✅ Тест пройден успешно ===")
