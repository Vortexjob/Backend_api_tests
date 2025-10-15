# import uuid
# import time
# from conftest import make_grpc_request, create_metadata, confirm_operation, assert_success
# from data import (
#     CODE_MAKE_MOI_DOM_PAYMENT,
#     MOI_DOM_PROP_VALUE, MOI_DOM_ADDRESS, MOI_DOM_FULLNAME,
#     MOI_DOM_SERVICES, MOI_DOM_AMOUNT_CREDIT,
#     MOI_DOM_SERVICE_PROVIDER_ID, MOI_DOM_ACCOUNT_ID_DEBIT,
#     MOI_DOM_PAYMENT_CODE
# )


# def test_moi_dom_payment_flow():
#     """Тест-кейс: Создание и подтверждение платежа Мой Дом (коммунальные услуги)"""
    
#     # === ШАГ 1: СОЗДАНИЕ ПЛАТЕЖА МОЙ ДОМ ===
#     print("\n=== ШАГ 1: Создание платежа Мой Дом ===")
    
#     operation_id = str(uuid.uuid1())
    
#     # Формируем структуру данных для сервисов Мой Дом
#     moidom_services = {
#         "address": MOI_DOM_ADDRESS,
#         "fullname": MOI_DOM_FULLNAME,
#         "services": MOI_DOM_SERVICES
#     }
    
#     payment_data = {
#         "operationId": operation_id,
#         "propValue": MOI_DOM_PROP_VALUE,
#         "moidomServices": moidom_services,
#         "amountCredit": MOI_DOM_AMOUNT_CREDIT,
#         "serviceProviderId": MOI_DOM_SERVICE_PROVIDER_ID,
#         "accountIdDebit": MOI_DOM_ACCOUNT_ID_DEBIT,
#         "paymentCode": MOI_DOM_PAYMENT_CODE
#     }
    
#     print(f"Operation ID: {operation_id}")
#     print(f"Лицевой счет: {MOI_DOM_PROP_VALUE}")
#     print(f"Адрес: {MOI_DOM_ADDRESS}")
#     print(f"Плательщик: {MOI_DOM_FULLNAME}")
#     print(f"Общая сумма: {MOI_DOM_AMOUNT_CREDIT}")
#     print(f"Количество услуг: {len(MOI_DOM_SERVICES)}")
    
#     # Выводим детали по каждой услуге
#     print("\nКоммунальные услуги:")
#     for service in MOI_DOM_SERVICES:
#         print(f"  - {service['comserviceName']}: {service['total']}")
    
#     print(f"\nДанные: {payment_data}")
    
#     create_response = make_grpc_request(CODE_MAKE_MOI_DOM_PAYMENT, payment_data, create_metadata())
#     print(f"Ответ: {create_response}")
    
#     assert_success(create_response, "Создание платежа Мой Дом")
#     print("✅ Создание платежа Мой Дом успешно!")
    
#     print("\nОжидание 3 секунд...")
#     time.sleep(3)
    
    
#     # === ШАГ 2: ПОДТВЕРЖДЕНИЕ ПЛАТЕЖА МОЙ ДОМ ===
#     print("\n=== ШАГ 2: Подтверждение платежа Мой Дом ===")
    
#     print(f"Operation ID: {operation_id}")
    
#     confirm_response = confirm_operation(operation_id)
#     print(f"Ответ: {confirm_response}")
    
#     assert_success(confirm_response, "Подтверждение платежа Мой Дом")
#     print("✅ Подтверждение платежа Мой Дом успешно!")
    
#     print("\n=== ✅ Тест пройден успешно ===")

