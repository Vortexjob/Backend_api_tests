import uuid
import time
from conftest import make_grpc_request, create_metadata, confirm_operation, assert_success
from data import (
    CODE_MAKE_MONEY_TRANSFER,
    ACCOUNT_ID_DEBIT, ASTROSEND_AMOUNT_CREDIT,
    MONEY_TRANSFER_TYPE, CREDIT_CCY,
    RECIPIENT_COUNTRY_CODE, RECIPIENT_FIRST_NAME, RECIPIENT_LAST_NAME,
    MARKETING_FLAG, PROP_VALUE
)


def test_astrosend_payment_flow():
    """Тест-кейс: Создание и подтверждение платежа через Astrosend"""
    
    # === ШАГ 1: СОЗДАНИЕ ПЛАТЕЖА ASTROSEND ===
    print("\n=== ШАГ 1: Создание платежа Astrosend ===")
    
    operation_id = str(uuid.uuid1())
    
    payment_data = {
        "operationId": operation_id,
        "accountIdDebit": ACCOUNT_ID_DEBIT,
        "amountCredit": ASTROSEND_AMOUNT_CREDIT,
        "moneyTransferType": MONEY_TRANSFER_TYPE,
        "creditCcy": CREDIT_CCY,
        "recipientCountryCode": RECIPIENT_COUNTRY_CODE,
        "recipientFirstName": RECIPIENT_FIRST_NAME,
        "recipientLastName": RECIPIENT_LAST_NAME,
        "marketingFlag": MARKETING_FLAG,
        "propValue": PROP_VALUE
    }
    
    print(f"Operation ID: {operation_id}")
    print(f"Сумма: {ASTROSEND_AMOUNT_CREDIT} {CREDIT_CCY}")
    print(f"Получатель: {RECIPIENT_FIRST_NAME} {RECIPIENT_LAST_NAME}")
    print(f"Страна: {RECIPIENT_COUNTRY_CODE}")
    print(f"Данные: {payment_data}")
    
    create_response = make_grpc_request(CODE_MAKE_MONEY_TRANSFER, payment_data, create_metadata())
    print(f"Ответ: {create_response}")
    
    assert_success(create_response, "Создание платежа Astrosend")
    print("✅ Создание платежа Astrosend успешно!")
    
    print("\nОжидание 2 секунд...")
    time.sleep(2)
    
    
    # === ШАГ 2: ПОДТВЕРЖДЕНИЕ ПЛАТЕЖА ASTROSEND ===
    print("\n=== ШАГ 2: Подтверждение платежа Astrosend ===")
    
    print(f"Operation ID: {operation_id}")
    
    confirm_response = confirm_operation(operation_id)
    print(f"Ответ: {confirm_response}")
    
    assert_success(confirm_response, "Подтверждение платежа Astrosend")
    print("✅ Подтверждение платежа Astrosend успешно!")
    
    print("\n=== ✅ Тест пройден успешно ===")
