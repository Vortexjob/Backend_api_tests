import uuid
import time
from conftest import make_grpc_request, create_metadata, confirm_operation, assert_success
from data import (
    CODE_MAKE_QR_PAYMENT,
    ACCOUNT_ID_DEBIT, QR_ACCOUNT_CREDIT_PROP_VALUE, ACCOUNT_CREDIT_PROP_TYPE,
    QR_PAYMENT_PURPOSE, AMOUNT_100, QR_PAYMENT, QR_ACCOUNT_CHANGEABLE,
    QR_SERVICE_NAME, QR_SERVICE_ID, QR_CLIENT_TYPE, QR_VERSION, QR_TYPE,
    QR_MERCHANT_PROVIDER_ID, QR_ACCOUNT, QR_MCC, QR_CCY,
    QR_TRANSACTION_ID, QR_CONTROL_SUM
)


def test_qr_payment_flow():
    """Тест-кейс: Создание и подтверждение QR платежа"""
    
    # === ШАГ 1: СОЗДАНИЕ QR ПЛАТЕЖА ===
    print("\n=== ШАГ 1: Создание QR платежа ===")
    
    operation_id = str(uuid.uuid1())
    
    transfer_data = {
        "operationId": operation_id,
        "accountIdDebit": ACCOUNT_ID_DEBIT,
        "accountCreditPropValue": QR_ACCOUNT_CREDIT_PROP_VALUE,
        "accountCreditPropType": ACCOUNT_CREDIT_PROP_TYPE,
        "paymentPurpose": QR_PAYMENT_PURPOSE,
        "amount": AMOUNT_100,
        "qrPayment": QR_PAYMENT,
        "qrAccountChangeable": QR_ACCOUNT_CHANGEABLE,
        "qrServiceName": QR_SERVICE_NAME,
        "qrServiceId": QR_SERVICE_ID,
        "clientType": QR_CLIENT_TYPE,
        "qrVersion": QR_VERSION,
        "qrType": QR_TYPE,
        "qrMerchantProviderId": QR_MERCHANT_PROVIDER_ID,
        "qrAccount": QR_ACCOUNT,
        "qrMcc": QR_MCC,
        "qrCcy": QR_CCY,
        "qrTransactionId": QR_TRANSACTION_ID,
        "qrControlSum": QR_CONTROL_SUM,
        "valueDate": None,
        "knp": None,
        "theirRefNo": None,
        "valueTime": None,
        "txnId": None,
        "qrComment": None,
        "qrMerchantId": None
    }
    
    print(f"Operation ID: {operation_id}")
    print(f"Сумма: {AMOUNT_100}")
    print(f"Счет получателя: {QR_ACCOUNT_CREDIT_PROP_VALUE}")
    print(f"Тип QR: {QR_TYPE}")
    print(f"Сервис: {QR_SERVICE_NAME}")
    print(f"MCC: {QR_MCC}")
    print(f"Валюта: {QR_CCY} (KGS)")
    print(f"Данные: {transfer_data}")
    
    create_response = make_grpc_request(CODE_MAKE_QR_PAYMENT, transfer_data, create_metadata())
    print(f"Ответ: {create_response}")
    
    assert_success(create_response, "Создание QR платежа")
    print("✅ Создание QR платежа успешно!")
    
    print("\nОжидание 5 секунд...")
    time.sleep(5)
    
    
    # === ШАГ 2: ПОДТВЕРЖДЕНИЕ QR ПЛАТЕЖА ===
    print("\n=== ШАГ 2: Подтверждение QR платежа ===")
    
    print(f"Operation ID: {operation_id}")
    
    confirm_response = confirm_operation(operation_id)
    print(f"Ответ: {confirm_response}")
    
    assert_success(confirm_response, "Подтверждение QR платежа")
    print("✅ Подтверждение QR платежа успешно!")
    
    print("\n=== ✅ Тест пройден успешно ===")
