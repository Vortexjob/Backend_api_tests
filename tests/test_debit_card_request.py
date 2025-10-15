import uuid
import time
from conftest import make_grpc_request, create_metadata, confirm_operation, assert_success
from data import (
    CODE_MAKE_TXN_SHOP_OPERATION,
    ACCOUNT_ID_DEBIT, ACCOUNT_CLASS_GROUP_ID, CARD_CCY,
    CODEWORD, CARD_HOLDER_NAME, PHONE_NUMBER, EMAIL,
    DELIVERY_TYPE, BRANCH_CODE, PRODUCT_TYPE_DEBIT_CARD
)


def test_debit_card_request_flow():
    """Тест-кейс: Создание и подтверждение запроса на открытие дебетовой карты"""
    
    # === ШАГ 1: СОЗДАНИЕ ЗАПРОСА НА ДЕБЕТОВУЮ КАРТУ ===
    print("\n=== ШАГ 1: Создание запроса на открытие дебетовой карты ===")
    
    operation_id = str(uuid.uuid4())
    
    debit_card_data = {
        "operationId": operation_id,
        "productType": PRODUCT_TYPE_DEBIT_CARD,
        "data": {
            "accountClassGroupId": ACCOUNT_CLASS_GROUP_ID,
            "cardCcy": CARD_CCY,
            "codeword": CODEWORD,
            "cardHolderName": CARD_HOLDER_NAME,
            "phoneNumber": PHONE_NUMBER,
            "email": EMAIL,
            "accountDebitId": ACCOUNT_ID_DEBIT,
            "deliveryType": DELIVERY_TYPE,
            "branch": BRANCH_CODE,
            "address": None,
            "productType": PRODUCT_TYPE_DEBIT_CARD,
            "requestId": f"IB{int(time.time() * 1000)}",
            "accountIdDebit": ACCOUNT_ID_DEBIT,
            "operationId": operation_id,
            "txnId": None
        },
        "txnId": None
    }
    
    print(f"Operation ID: {operation_id}")
    print(f"Request ID: IB{int(time.time() * 1000)}")
    print(f"Валюта карты: {CARD_CCY}")
    print(f"Держатель карты: {CARD_HOLDER_NAME}")
    print(f"Email: {EMAIL}")
    print(f"Данные: {debit_card_data}")
    
    create_response = make_grpc_request(CODE_MAKE_TXN_SHOP_OPERATION, debit_card_data, create_metadata())
    print(f"Ответ: {create_response}")
    
    assert_success(create_response, "Создание запроса на дебетовую карту")
    print("✅ Создание запроса на дебетовую карту успешно!")
    
    print("\nОжидание 3 секунд...")
    time.sleep(3)
    
    
    # === ШАГ 2: ПОДТВЕРЖДЕНИЕ ЗАПРОСА НА ДЕБЕТОВУЮ КАРТУ ===
    print("\n=== ШАГ 2: Подтверждение запроса на дебетовую карту ===")
    
    print(f"Operation ID: {operation_id}")
    
    confirm_response = confirm_operation(operation_id)
    print(f"Ответ: {confirm_response}")
    
    assert_success(confirm_response, "Подтверждение запроса на дебетовую карту")
    print("✅ Подтверждение запроса на дебетовую карту успешно!")
    
    print("\n=== ✅ Тест пройден успешно ===")

