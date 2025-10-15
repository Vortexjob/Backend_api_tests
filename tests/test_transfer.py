"""
Упрощенный пример теста перевода с использованием helper функций из conftest
"""
import uuid
import time
from conftest import make_grpc_request, create_metadata, confirm_operation, assert_success
from data import (
    CODE_CREATE_TRANSFER,
    ACCOUNT_ID_DEBIT, ACCOUNT_CREDIT, ACCOUNT_CREDIT_PROP_TYPE,
    TRANSFER_AMOUNT, PAYMENT_PURPOSE
)


def test_transfer_flow_simplified():
    """Тест-кейс: Создание и подтверждение банковского перевода (упрощенная версия)"""
    
    # === ШАГ 1: СОЗДАНИЕ ПЕРЕВОДА ===
    print("\n=== ШАГ 1: Создание перевода (упрощенный) ===")
    
    operation_id = str(uuid.uuid1())
    
    transfer_data = {
        "operationId": operation_id,
        "accountIdDebit": ACCOUNT_ID_DEBIT,
        "accountCreditPropValue": ACCOUNT_CREDIT,
        "accountCreditPropType": ACCOUNT_CREDIT_PROP_TYPE, 
        "paymentPurpose": PAYMENT_PURPOSE,
        "amountDebit": TRANSFER_AMOUNT,
    }
    
    print(f"Operation ID: {operation_id}")
    print(f"Данные: {transfer_data}")
    
    # Используем helper функции вместо дублирования кода
    create_response = make_grpc_request(CODE_CREATE_TRANSFER, transfer_data, create_metadata())
    print(f"Ответ: {create_response}")
    
    # Используем общую проверку успешности
    assert_success(create_response, "Создание перевода")
    print("✅ Создание перевода успешно!")
    
    
    # === ШАГ 2: ПОДТВЕРЖДЕНИЕ ПЕРЕВОДА ===
    print("\n=== ШАГ 2: Подтверждение перевода (упрощенный) ===")
    
    # Используем общую функцию подтверждения
    confirm_response = confirm_operation(operation_id)
    print(f"Ответ: {confirm_response}")
    
    # Проверка успешности
    assert_success(confirm_response, "Подтверждение перевода")
    print("✅ Подтверждение перевода успешно!")
    
    print("\n=== ✅ Тест пройден успешно ===")

