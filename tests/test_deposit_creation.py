# import uuid
# import time
# from conftest import make_grpc_request, create_metadata, confirm_operation, assert_success
# from data import (
#     CODE_MAKE_DEPOSIT,
#     ACCOUNT_ID_DEBIT, DEPOSIT_TYPE, DEPOSIT_ID, DEPOSIT_MAIN_INT_TYPE,
#     DEPOSIT_AMOUNT, DEPOSIT_CCY, DEPOSIT_RATE, DEPOSIT_TERM,
#     PRODUCT_TYPE_DEPOSIT
# )


# def test_deposit_creation_flow():
#     """Тест-кейс: Создание и подтверждение депозита"""
    
#     # === ШАГ 1: СОЗДАНИЕ ДЕПОЗИТА ===
#     print("\n=== ШАГ 1: Создание депозита ===")
    
#     operation_id = str(uuid.uuid4())
    
#     deposit_data = {
#         "depositType": DEPOSIT_TYPE,
#         "depositId": DEPOSIT_ID,
#         "mainIntType": DEPOSIT_MAIN_INT_TYPE,
#         "amount": DEPOSIT_AMOUNT,
#         "ccy": DEPOSIT_CCY,
#         "rate": DEPOSIT_RATE,
#         "accountDebitId": ACCOUNT_ID_DEBIT,
#         "termOfDeposit": DEPOSIT_TERM,
#         "childName": "",
#         "childBirthdate": "",
#         "files": [],
#         "productType": PRODUCT_TYPE_DEPOSIT,
#         "requestId": f"IB{int(time.time() * 1000)}",
#         "accountIdDebit": ACCOUNT_ID_DEBIT,
#         "amountDebit": DEPOSIT_AMOUNT,
#         "operationId": operation_id,
#         "txnId": None
#     }
    
#     print(f"Operation ID: {operation_id}")
#     print(f"Request ID: IB{int(time.time() * 1000)}")
#     print(f"Тип депозита: {DEPOSIT_TYPE}")
#     print(f"Сумма: {DEPOSIT_AMOUNT} {DEPOSIT_CCY}")
#     print(f"Ставка: {DEPOSIT_RATE}%")
#     print(f"Срок: {DEPOSIT_TERM} месяцев")
#     print(f"Данные: {deposit_data}")
    
#     create_response = make_grpc_request(CODE_MAKE_DEPOSIT, deposit_data, create_metadata())
#     print(f"Ответ: {create_response}")
    
#     assert_success(create_response, "Создание депозита")
#     print("✅ Создание депозита успешно!")
    
#     print("\nОжидание 3 секунд...")
#     time.sleep(3)
    
    
#     # === ШАГ 2: ПОДТВЕРЖДЕНИЕ ДЕПОЗИТА ===
#     print("\n=== ШАГ 2: Подтверждение депозита ===")
    
#     print(f"Operation ID: {operation_id}")
    
#     confirm_response = confirm_operation(operation_id)
#     print(f"Ответ: {confirm_response}")
    
#     assert_success(confirm_response, "Подтверждение депозита")
#     print("✅ Подтверждение депозита успешно!")
    
#     print("\n=== ✅ Тест пройден успешно ===")

