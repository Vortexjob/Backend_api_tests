import uuid
import time

import pytest

from conftest import make_grpc_request, create_metadata, confirm_operation, assert_success
from data import (
    CODE_MAKE_DEPOSIT,
    DEPOSIT_CUSTOMER_NO,
    DEPOSIT_ACCOUNT_ID_DEBIT,
    DEPOSIT_ACCOUNT_NO_DEBIT,
    DEPOSIT_TYPE,
    DEPOSIT_ID,
    DEPOSIT_MAIN_INT_TYPE,
    DEPOSIT_AMOUNT,
    DEPOSIT_CCY,
    DEPOSIT_RATE,
    DEPOSIT_TERM,
    PRODUCT_TYPE_DEPOSIT,
)
from database_collector import DatabaseConfig, DataCollector


def _deposit_metadata():
    collector = DataCollector(DatabaseConfig())
    session_key = collector.get_valid_session_key_by_customer_no(DEPOSIT_CUSTOMER_NO)
    if not session_key:
        pytest.skip(f"Нет валидной сессии для клиента {DEPOSIT_CUSTOMER_NO}")
    return create_metadata(session_key=session_key)


def test_deposit_creation_flow():
    """Тест-кейс: Создание и подтверждение депозита"""
    metadata = _deposit_metadata()

    # === ШАГ 1: СОЗДАНИЕ ДЕПОЗИТА ===
    print("\n=== ШАГ 1: Создание депозита ===")
    print(f"Клиент: {DEPOSIT_CUSTOMER_NO}, счёт списания id={DEPOSIT_ACCOUNT_ID_DEBIT}, № {DEPOSIT_ACCOUNT_NO_DEBIT}")

    operation_id = str(uuid.uuid4())

    deposit_data = {
        "depositType": DEPOSIT_TYPE,
        "depositId": DEPOSIT_ID,
        "mainIntType": DEPOSIT_MAIN_INT_TYPE,
        "amount": DEPOSIT_AMOUNT,
        "ccy": DEPOSIT_CCY,
        "rate": DEPOSIT_RATE,
        "accountDebitId": DEPOSIT_ACCOUNT_ID_DEBIT,
        "termOfDeposit": DEPOSIT_TERM,
        "childName": "",
        "childBirthdate": "",
        "files": [],
        "productType": PRODUCT_TYPE_DEPOSIT,
        "requestId": f"IB{int(time.time() * 1000)}",
        "accountIdDebit": DEPOSIT_ACCOUNT_ID_DEBIT,
        "amountDebit": DEPOSIT_AMOUNT,
        "operationId": operation_id,
        "txnId": None
    }
    
    print(f"Operation ID: {operation_id}")
    print(f"Request ID: IB{int(time.time() * 1000)}")
    print(f"Тип депозита: {DEPOSIT_TYPE}")
    print(f"Сумма: {DEPOSIT_AMOUNT} {DEPOSIT_CCY}")
    print(f"Ставка: {DEPOSIT_RATE}%")
    print(f"Срок: {DEPOSIT_TERM} месяцев")
    print(f"Данные: {deposit_data}")
    
    create_response = make_grpc_request(CODE_MAKE_DEPOSIT, deposit_data, metadata)
    print(f"Ответ: {create_response}")
    
    assert_success(create_response, "Создание депозита")
    print("✅ Создание депозита успешно!")
    
    print("\nОжидание 3 секунд...")
    time.sleep(3)
    
    
    # === ШАГ 2: ПОДТВЕРЖДЕНИЕ ДЕПОЗИТА ===
    print("\n=== ШАГ 2: Подтверждение депозита ===")
    
    print(f"Operation ID: {operation_id}")
    
    confirm_response = confirm_operation(operation_id, metadata=metadata)
    print(f"Ответ: {confirm_response}")
    
    assert_success(confirm_response, "Подтверждение депозита")
    print("✅ Подтверждение депозита успешно!")
    
    print("\n=== ✅ Тест пройден успешно ===")

