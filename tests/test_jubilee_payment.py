import uuid
import time
from conftest import make_grpc_request, create_metadata, confirm_operation, assert_success
from data import (
    CODE_MAKE_GENERIC_PAYMENT_V2,
    ACCOUNT_ID_DEBIT, JUBILEE_PROP_VALUE, AMOUNT_100,
    JUBILEE_SERVICE_ID, JUBILEE_SERVICE_PROVIDER_ID
)


def test_jubilee_payment_flow():
    """Тест-кейс: Создание и подтверждение платежа Jubilee"""
    
    # === ШАГ 1: СОЗДАНИЕ ПЛАТЕЖА JUBILEE ===
    print("\n=== ШАГ 1: Создание платежа Jubilee ===")
    
    operation_id = str(uuid.uuid1())
    
    payment_data = {
        "operationId": operation_id,
        "propValue": JUBILEE_PROP_VALUE,
        "accountIdDebit": ACCOUNT_ID_DEBIT,
        "amountCredit": AMOUNT_100,
        "serviceId": JUBILEE_SERVICE_ID,
        "serviceProviderId": JUBILEE_SERVICE_PROVIDER_ID
    }
    
    print(f"Operation ID: {operation_id}")
    print(f"Номер договора: {JUBILEE_PROP_VALUE}")
    print(f"Сумма: {AMOUNT_100}")
    print(f"Сервис: {JUBILEE_SERVICE_ID}")
    print(f"Провайдер ID: {JUBILEE_SERVICE_PROVIDER_ID}")
    print(f"Данные: {payment_data}")
    
    create_response = make_grpc_request(CODE_MAKE_GENERIC_PAYMENT_V2, payment_data, create_metadata())
    print(f"Ответ: {create_response}")
    
    assert_success(create_response, "Создание платежа Jubilee")
    print("✅ Создание платежа Jubilee успешно!")
    
    print("\nОжидание 5 секунд...")
    time.sleep(5)
    
    
    # === ШАГ 2: ПОДТВЕРЖДЕНИЕ ПЛАТЕЖА JUBILEE ===
    print("\n=== ШАГ 2: Подтверждение платежа Jubilee ===")
    
    print(f"Operation ID: {operation_id}")
    
    confirm_response = confirm_operation(operation_id)
    print(f"Ответ: {confirm_response}")
    
    assert_success(confirm_response, "Подтверждение платежа Jubilee")
    print("✅ Подтверждение платежа Jubilee успешно!")
    
    print("\n=== ✅ Тест пройден успешно ===")

