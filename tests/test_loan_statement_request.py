import uuid
import time
from conftest import make_grpc_request, create_metadata, confirm_operation, assert_success
from data import (
    CODE_MAKE_TXN_SHOP_OPERATION,
    ACCOUNT_ID_DEBIT, STATEMENT_LANGUAGE, DELIVERY_TYPE,
    PHONE_NUMBER, BRANCH_CODE, LOAN_STATEMENT_TYPE,
    PRODUCT_TYPE_LOAN_STATEMENT
)


def test_loan_statement_request_flow():
    """Тест-кейс: Создание и подтверждение запроса справки о выплатах по кредиту"""
    
    # === ШАГ 1: СОЗДАНИЕ ЗАПРОСА СПРАВКИ О ВЫПЛАТАХ ===
    print("\n=== ШАГ 1: Создание запроса справки о выплатах по кредиту ===")
    
    operation_id = str(uuid.uuid4())
    
    loan_statement_data = {
        "operationId": operation_id,
        "productType": PRODUCT_TYPE_LOAN_STATEMENT,
        "data": {
            "statementLanguage": STATEMENT_LANGUAGE,
            "statementRequestFee": None,
            "deliveryType": DELIVERY_TYPE,
            "deliveryFee": None,
            "deliveryAddress": None,
            "phoneNumber": PHONE_NUMBER,
            "branchCode": BRANCH_CODE,
            "accountDebitId": ACCOUNT_ID_DEBIT,
            "accountDebitIds": None,
            "loanStatementType": LOAN_STATEMENT_TYPE,
            "productType": PRODUCT_TYPE_LOAN_STATEMENT,
            "requestId": f"IB{int(time.time() * 1000)}",
            "accountIdDebit": ACCOUNT_ID_DEBIT,
            "operationId": operation_id,
            "txnId": None
        },
        "txnId": None
    }
    
    print(f"Operation ID: {operation_id}")
    print(f"Request ID: IB{int(time.time() * 1000)}")
    print(f"Язык справки: {STATEMENT_LANGUAGE}")
    print(f"Тип доставки: {DELIVERY_TYPE}")
    print(f"Тип справки: {LOAN_STATEMENT_TYPE['ru']}")
    print(f"Данные: {loan_statement_data}")
    
    create_response = make_grpc_request(CODE_MAKE_TXN_SHOP_OPERATION, loan_statement_data, create_metadata())
    print(f"Ответ: {create_response}")
    
    assert_success(create_response, "Создание запроса справки о выплатах")
    print("✅ Создание запроса справки о выплатах успешно!")
    
    print("\nОжидание 3 секунд...")
    time.sleep(3)
    
    
    # === ШАГ 2: ПОДТВЕРЖДЕНИЕ ЗАПРОСА СПРАВКИ О ВЫПЛАТАХ ===
    print("\n=== ШАГ 2: Подтверждение запроса справки о выплатах ===")
    
    print(f"Operation ID: {operation_id}")
    
    confirm_response = confirm_operation(operation_id)
    print(f"Ответ: {confirm_response}")
    
    assert_success(confirm_response, "Подтверждение запроса справки о выплатах")
    print("✅ Подтверждение запроса справки о выплатах успешно!")
    
    print("\n=== ✅ Тест пройден успешно ===")

