# import uuid
# import time
# from conftest import make_grpc_request, create_metadata, confirm_operation, assert_success
# from data import (
#     CODE_MAKE_GENERIC_PAYMENT_V2,
#     ACCOUNT_ID_DEBIT, AIYL_BANK_PROP_VALUE, AIYL_BANK_AMOUNT_CREDIT,
#     AIYL_BANK_SERVICE_ID, AIYL_BANK_SERVICE_PROVIDER_ID
# )


# def test_aiyl_bank_payment_flow():
#     """Тест-кейс: Создание и подтверждение платежа Айыл Банк"""
    
#     # === ШАГ 1: СОЗДАНИЕ ПЛАТЕЖА АЙЫЛ БАНК ===
#     print("\n=== ШАГ 1: Создание платежа Айыл Банк ===")
    
#     operation_id = str(uuid.uuid1())
    
#     payment_data = {
#         "operationId": operation_id,
#         "propValue": AIYL_BANK_PROP_VALUE,
#         "accountIdDebit": ACCOUNT_ID_DEBIT,
#         "amountCredit": AIYL_BANK_AMOUNT_CREDIT,
#         "serviceId": AIYL_BANK_SERVICE_ID,
#         "serviceProviderId": AIYL_BANK_SERVICE_PROVIDER_ID
#     }
    
#     print(f"Operation ID: {operation_id}")
#     print(f"Номер телефона: {AIYL_BANK_PROP_VALUE}")
#     print(f"Сумма: {AIYL_BANK_AMOUNT_CREDIT}")
#     print(f"Сервис: {AIYL_BANK_SERVICE_ID}")
#     print(f"Провайдер ID: {AIYL_BANK_SERVICE_PROVIDER_ID}")
#     print(f"Данные: {payment_data}")
    
#     create_response = make_grpc_request(CODE_MAKE_GENERIC_PAYMENT_V2, payment_data, create_metadata())
#     print(f"Ответ: {create_response}")
    
#     assert_success(create_response, "Создание платежа Айыл Банк")
#     print("✅ Создание платежа Айыл Банк успешно!")
    
#     print("\nОжидание 3 секунд...")
#     time.sleep(3)
    
    
#     # === ШАГ 2: ПОДТВЕРЖДЕНИЕ ПЛАТЕЖА АЙЫЛ БАНК ===
#     print("\n=== ШАГ 2: Подтверждение платежа Айыл Банк ===")
    
#     print(f"Operation ID: {operation_id}")
    
#     confirm_response = confirm_operation(operation_id)
#     print(f"Ответ: {confirm_response}")
    
#     assert_success(confirm_response, "Подтверждение платежа Айыл Банк")
#     print("✅ Подтверждение платежа Айыл Банк успешно!")
    
#     print("\n=== ✅ Тест пройден успешно ===")

