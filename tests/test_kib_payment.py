# import uuid
# import time
# from conftest import make_grpc_request, create_metadata, confirm_operation, assert_success
# from data import (
#     CODE_MAKE_GENERIC_PAYMENT_V2,
#     ACCOUNT_ID_DEBIT, KIB_PROP_VALUE, KIB_AMOUNT_CREDIT,
#     KIB_SERVICE_ID, KIB_SERVICE_PROVIDER_ID
# )


# def test_kib_payment_flow():
#     """Тест-кейс: Создание и подтверждение платежа KIB"""
    
#     # === ШАГ 1: СОЗДАНИЕ ПЛАТЕЖА KIB ===
#     print("\n=== ШАГ 1: Создание платежа KIB ===")
    
#     operation_id = str(uuid.uuid1())
    
#     payment_data = {
#         "operationId": operation_id,
#         "propValue": KIB_PROP_VALUE,
#         "accountIdDebit": ACCOUNT_ID_DEBIT,
#         "amountCredit": KIB_AMOUNT_CREDIT,
#         "serviceId": KIB_SERVICE_ID,
#         "serviceProviderId": KIB_SERVICE_PROVIDER_ID
#     }
    
#     print(f"Operation ID: {operation_id}")
#     print(f"Получатель: {KIB_PROP_VALUE}")
#     print(f"Сумма: {KIB_AMOUNT_CREDIT}")
#     print(f"Сервис: {KIB_SERVICE_ID}")
#     print(f"Провайдер ID: {KIB_SERVICE_PROVIDER_ID}")
#     print(f"Данные: {payment_data}")
    
#     create_response = make_grpc_request(CODE_MAKE_GENERIC_PAYMENT_V2, payment_data, create_metadata())
#     print(f"Ответ: {create_response}")
    
#     assert_success(create_response, "Создание платежа KIB")
#     print("✅ Создание платежа KIB успешно!")
    
#     print("\nОжидание 2 секунд...")
#     time.sleep(2)
    
    
#     # === ШАГ 2: ПОДТВЕРЖДЕНИЕ ПЛАТЕЖА KIB ===
#     print("\n=== ШАГ 2: Подтверждение платежа KIB ===")
    
#     print(f"Operation ID: {operation_id}")
    
#     confirm_response = confirm_operation(operation_id)
#     print(f"Ответ: {confirm_response}")
    
#     assert_success(confirm_response, "Подтверждение платежа KIB")
#     print("✅ Подтверждение платежа KIB успешно!")
    
#     print("\n=== ✅ Тест пройден успешно ===")

