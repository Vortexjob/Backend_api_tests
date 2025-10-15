import uuid
import time
from conftest import make_grpc_request, create_metadata, confirm_operation, assert_success
from data import (
    CODE_MAKE_SWIFT_TRANSFER,SWIFT_ACCOUNT_ID_DEBIT,
    ACCOUNT_ID_DEBIT, SWIFT_AMOUNT_DEBIT, SWIFT_VALUE_DATE,
    SWIFT_TRANSFER_CCY, SWIFT_RECIPIENT_ADDRESS, SWIFT_RECIPIENT_NAME,
    SWIFT_RECIPIENT_BANK_SWIFT, SWIFT_RECIPIENT_ACC_NO,
    SWIFT_TRANSFER_PURPOSE_TEXT, SWIFT_COMMISSION_TYPE, SWIFT_COMMISSION_ACCOUNT_ID
)


def test_swift_transfer_flow():
    """Тест-кейс: Создание и подтверждение SWIFT перевода"""
    
    # === ШАГ 1: СОЗДАНИЕ SWIFT ПЕРЕВОДА ===
    print("\n=== ШАГ 1: Создание SWIFT перевода ===")
    
    operation_id = str(uuid.uuid1())
    
    transfer_data = {
        "operationId": operation_id,
        "accountIdDebit": SWIFT_ACCOUNT_ID_DEBIT,
        "amountDebit": SWIFT_AMOUNT_DEBIT,
        "valueDate": SWIFT_VALUE_DATE,
        "transferCcy": SWIFT_TRANSFER_CCY,
        "recipientAddress": SWIFT_RECIPIENT_ADDRESS,
        "recipientName": SWIFT_RECIPIENT_NAME,
        "recipientBankSwift": SWIFT_RECIPIENT_BANK_SWIFT,
        "recipientAccNo": SWIFT_RECIPIENT_ACC_NO,
        "transferPurposeText": SWIFT_TRANSFER_PURPOSE_TEXT,
        "commissionType": SWIFT_COMMISSION_TYPE,
        "commissionAccountId": SWIFT_COMMISSION_ACCOUNT_ID,
        "files": []
    }
    
    print(f"Operation ID: {operation_id}")
    print(f"Сумма: {SWIFT_AMOUNT_DEBIT} {SWIFT_TRANSFER_CCY}")
    print(f"Получатель: {SWIFT_RECIPIENT_NAME}")
    print(f"Адрес получателя: {SWIFT_RECIPIENT_ADDRESS}")
    print(f"Банк получателя (SWIFT): {SWIFT_RECIPIENT_BANK_SWIFT}")
    print(f"Счет получателя: {SWIFT_RECIPIENT_ACC_NO}")
    print(f"Дата валютирования: {SWIFT_VALUE_DATE}")
    print(f"Тип комиссии: {SWIFT_COMMISSION_TYPE}")
    print(f"Данные: {transfer_data}")
    
    create_response = make_grpc_request(CODE_MAKE_SWIFT_TRANSFER, transfer_data, create_metadata())
    print(f"Ответ: {create_response}")
    
    assert_success(create_response, "Создание SWIFT перевода")
    print("✅ Создание SWIFT перевода успешно!")
    
    print("\nОжидание 5 секунд...")
    time.sleep(5)
    
    
    # === ШАГ 2: ПОДТВЕРЖДЕНИЕ SWIFT ПЕРЕВОДА ===
    print("\n=== ШАГ 2: Подтверждение SWIFT перевода ===")
    
    print(f"Operation ID: {operation_id}")
    
    confirm_response = confirm_operation(operation_id)
    print(f"Ответ: {confirm_response}")
    
    assert_success(confirm_response, "Подтверждение SWIFT перевода")
    print("✅ Подтверждение SWIFT перевода успешно!")
    
    print("\n=== ✅ Тест пройден успешно ===")

