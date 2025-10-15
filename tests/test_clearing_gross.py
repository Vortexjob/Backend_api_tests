import uuid
import time
from conftest import make_grpc_request, create_metadata, confirm_operation, assert_success
from data import (
    CODE_MAKE_OTHER_BANK_TRANSFER,
    ACCOUNT_ID_DEBIT, TRANSFER_CLEARING_GROSS, VALUE_DATE,
    RECIPIENT_NAME, RECIPIENT_BANK_BIC, ACCOUNT_CREDIT_NUMBER,
    TRANSFER_PURPOSE_TEXT, KNP, AMOUNT_CREDIT_CLEARING
)


def test_clearing_gross_transfer_flow():
    """Тест-кейс: Создание и подтверждение клиринг/гросс перевода в другой банк"""
    
    # === ШАГ 1: СОЗДАНИЕ КЛИРИНГ/ГРОСС ПЕРЕВОДА ===
    print("\n=== ШАГ 1: Создание клиринг/гросс перевода ===")
    
    operation_id = str(uuid.uuid1())
    
    transfer_data = {
        "operationId": operation_id,
        "accountIdDebit": ACCOUNT_ID_DEBIT,
        "transferClearingGross": TRANSFER_CLEARING_GROSS,
        "valueDate": VALUE_DATE,
        "recipientName": RECIPIENT_NAME,
        "recipientBankBic": RECIPIENT_BANK_BIC,
        "accountCreditNumber": ACCOUNT_CREDIT_NUMBER,
        "transferPurposeText": TRANSFER_PURPOSE_TEXT,
        "knp": KNP,
        "amountCredit": AMOUNT_CREDIT_CLEARING
    }
    
    print(f"Operation ID: {operation_id}")
    print(f"Тип перевода: {'Клиринг' if TRANSFER_CLEARING_GROSS == 'C' else 'Гросс'}")
    print(f"Сумма: {AMOUNT_CREDIT_CLEARING}")
    print(f"Получатель: {RECIPIENT_NAME}")
    print(f"Банк получателя (BIC): {RECIPIENT_BANK_BIC}")
    print(f"Счет получателя: {ACCOUNT_CREDIT_NUMBER}")
    print(f"Дата валютирования: {VALUE_DATE}")
    print(f"КНП: {KNP}")
    print(f"Данные: {transfer_data}")
    
    create_response = make_grpc_request(CODE_MAKE_OTHER_BANK_TRANSFER, transfer_data, create_metadata())
    print(f"Ответ: {create_response}")
    
    assert_success(create_response, "Создание клиринг/гросс перевода")
    print("✅ Создание клиринг/гросс перевода успешно!")
    
    print("\nОжидание 5 секунд...")
    time.sleep(5)
    
    
    # === ШАГ 2: ПОДТВЕРЖДЕНИЕ КЛИРИНГ/ГРОСС ПЕРЕВОДА ===
    print("\n=== ШАГ 2: Подтверждение клиринг/гросс перевода ===")
    
    print(f"Operation ID: {operation_id}")
    
    confirm_response = confirm_operation(operation_id)
    print(f"Ответ: {confirm_response}")
    
    assert_success(confirm_response, "Подтверждение клиринг/гросс перевода")
    print("✅ Подтверждение клиринг/гросс перевода успешно!")
    
    print("\n=== ✅ Тест пройден успешно ===")
