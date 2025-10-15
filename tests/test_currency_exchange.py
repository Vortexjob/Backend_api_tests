import uuid
import time
from conftest import make_grpc_request, create_metadata, confirm_operation, assert_success
from data import (
    CODE_MAKE_OWN_ACCOUNTS_TRANSFER,
    EXCHANGE_ACCOUNT_ID_DEBIT, EXCHANGE_ACCOUNT_ID_CREDIT, AMOUNT_SMALL
)


def test_currency_exchange_flow():
    """Тест-кейс: Создание и подтверждение обмена валют между своими счетами"""
    
    # === ШАГ 1: СОЗДАНИЕ ОБМЕНА ВАЛЮТ ===
    print("\n=== ШАГ 1: Создание обмена валют ===")
    
    operation_id = str(uuid.uuid1())
    
    exchange_data = {
        "operationId": operation_id,
        "accountIdDebit": EXCHANGE_ACCOUNT_ID_DEBIT,
        "accountIdCredit": EXCHANGE_ACCOUNT_ID_CREDIT,
        "amountDebit": AMOUNT_SMALL,
    }
    
    print(f"Operation ID: {operation_id}")
    print(f"Счет списания: {EXCHANGE_ACCOUNT_ID_DEBIT}")
    print(f"Счет зачисления: {EXCHANGE_ACCOUNT_ID_CREDIT}")
    print(f"Сумма обмена: {AMOUNT_SMALL}")
    print(f"Данные: {exchange_data}")
    
    create_response = make_grpc_request(CODE_MAKE_OWN_ACCOUNTS_TRANSFER, exchange_data, create_metadata())
    print(f"Ответ: {create_response}")
    
    assert_success(create_response, "Создание обмена валют")
    print("✅ Создание обмена валют успешно!")
    
    print("\nОжидание 5 секунд...")
    time.sleep(5)
    
    
    # === ШАГ 2: ПОДТВЕРЖДЕНИЕ ОБМЕНА ВАЛЮТ ===
    print("\n=== ШАГ 2: Подтверждение обмена валют ===")
    
    print(f"Operation ID: {operation_id}")
    
    confirm_response = confirm_operation(operation_id)
    print(f"Ответ: {confirm_response}")
    
    assert_success(confirm_response, "Подтверждение обмена валют")
    print("✅ Подтверждение обмена валют успешно!")
    
    print("\n=== ✅ Тест пройден успешно ===")

