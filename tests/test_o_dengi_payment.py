import uuid
import time
from conftest import make_grpc_request, create_metadata, confirm_operation, assert_success
from data import (
    CODE_MAKE_GENERIC_PAYMENT_V2,
    ACCOUNT_ID_DEBIT, O_DENGI_PROP_VALUE, AMOUNT_100,
    O_DENGI_SERVICE_ID, O_DENGI_SERVICE_PROVIDER_ID
)


def test_o_dengi_payment_flow():
    """Тест-кейс: Создание и подтверждение платежа O! Деньги"""
    
    # === ШАГ 1: СОЗДАНИЕ ПЛАТЕЖА O! ДЕНЬГИ ===
    print("\n=== ШАГ 1: Создание платежа O! Деньги ===")
    
    operation_id = str(uuid.uuid1())
    
    payment_data = {
        "operationId": operation_id,
        "propValue": O_DENGI_PROP_VALUE,
        "accountIdDebit": ACCOUNT_ID_DEBIT,
        "amountCredit": AMOUNT_100,
        "serviceId": O_DENGI_SERVICE_ID,
        "serviceProviderId": O_DENGI_SERVICE_PROVIDER_ID
    }
    
    print(f"Operation ID: {operation_id}")
    print(f"Номер телефона: {O_DENGI_PROP_VALUE}")
    print(f"Сумма: {AMOUNT_100}")
    print(f"Сервис: {O_DENGI_SERVICE_ID}")
    print(f"Провайдер ID: {O_DENGI_SERVICE_PROVIDER_ID}")
    print(f"Данные: {payment_data}")
    
    create_response = make_grpc_request(CODE_MAKE_GENERIC_PAYMENT_V2, payment_data, create_metadata())
    print(f"Ответ: {create_response}")
    
    assert_success(create_response, "Создание платежа O! Деньги")
    print("✅ Создание платежа O! Деньги успешно!")
    
    print("\nОжидание 5 секунд...")
    time.sleep(5)
    
    
    # === ШАГ 2: ПОДТВЕРЖДЕНИЕ ПЛАТЕЖА O! ДЕНЬГИ ===
    print("\n=== ШАГ 2: Подтверждение платежа O! Деньги ===")
    
    print(f"Operation ID: {operation_id}")
    
    confirm_response = confirm_operation(operation_id)
    print(f"Ответ: {confirm_response}")
    
    assert_success(confirm_response, "Подтверждение платежа O! Деньги")
    print("✅ Подтверждение платежа O! Деньги успешно!")
    
    print("\n=== ✅ Тест пройден успешно ===")

