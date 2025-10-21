import uuid
import time
import pytest
import json
from datetime import datetime
from conftest import make_grpc_request, create_metadata, confirm_operation, assert_success
from data import CODE_MAKE_MONEY_EXPRESS
from database_collector import DatabaseConfig, DataCollector


# === ГЛОБАЛЬНЫЙ СПИСОК ДЛЯ СБОРА PROCESSING_ID ===
PROCESSING_IDS_COLLECTION = []


def get_processing_id_by_operation_id(operation_id: str) -> str:
    """
    Получает processing_id из БД по operation_id
    
    Args:
        operation_id: Уникальный идентификатор операции
        
    Returns:
        str: processing_id или None если не найден
    """
    try:
        config = DatabaseConfig()
        collector = DataCollector(config)
        
        with collector.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT pay_ref_1 
                    FROM transactions 
                    WHERE operation_id = %s
                """, (operation_id,))
                result = cur.fetchone()
                
                if result:
                    processing_id = result[0]
                    print(f"✅ Найден processing_id: {processing_id} для operation_id: {operation_id}")
                    return processing_id
                else:
                    print(f"❌ Не найден processing_id для operation_id: {operation_id}")
                    return None
                    
    except Exception as e:
        print(f"❌ Ошибка получения processing_id: {e}")
        return None


def save_processing_ids_to_file():
    """Сохраняет все собранные processing_id в JSON файл"""
    if not PROCESSING_IDS_COLLECTION:
        print("⚠️ Нет processing_id для сохранения")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"money_express_processing_ids_{timestamp}.json"
    
    data = {
        "timestamp": datetime.now().isoformat(),
        "total_count": len(PROCESSING_IDS_COLLECTION),
        "processing_ids": PROCESSING_IDS_COLLECTION
    }
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ Сохранено {len(PROCESSING_IDS_COLLECTION)} processing_id в файл: {filename}")
    except Exception as e:
        print(f"❌ Ошибка сохранения файла: {e}")


# === МАССИВ ХАРДКОДНЫХ ДАННЫХ ДЛЯ MONEY EXPRESS ===
MONEY_EXPRESS_TEST_DATA = [ 
    {
        "test_name": "To test if acquirer get exchange rate provided by UPI",
        "account_id_debit": "17575",
        "recipient_name": "Feng Qixiang",
        "account_credit_prop_value": "6222040000030002",
        "account_credit_prop_type": "CARD_NO",
        "amount_debit": "100",
        "payment_purpose": "135",
        "user_id": 3360,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "To test if Credit Verify succeeds- (The payee is NOT a Hong Kong, Macao or Taiwan resident)",
        "account_id_debit": "17575",
        "recipient_name": "Feng Qixiang",
        "account_credit_prop_value": "6222040000030002",
        "account_credit_prop_type": "CARD_NO",
        "amount_debit": "200",
        "payment_purpose": "135",
        "user_id": 3360,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "Мульти запрос тест 1",
        "account_id_debit": "17424",
        "recipient_name": "Feng Qixiang",
        "account_credit_prop_value": "6222040000030002",
        "account_credit_prop_type": "CARD_NO",
        "amount_debit": "100",
        "payment_purpose": "135",
        "user_id": 134,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "Мульти запрос тест 2",
        "account_id_debit": "17424",
        "recipient_name": "Feng Qixiang",
        "account_credit_prop_value": "6222040000030002",
        "account_credit_prop_type": "CARD_NO",
        "amount_debit": "100",
        "payment_purpose": "135",
        "user_id": 134,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "Мульти запрос тест 3",
        "account_id_debit": "17424",
        "recipient_name": "Feng Qixiang",
        "account_credit_prop_value": "6222040000030002",
        "account_credit_prop_type": "CARD_NO",
        "amount_debit": "100",
        "payment_purpose": "135",
        "user_id": 134,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "Мульти запрос тест 4",
        "account_id_debit": "17424",
        "recipient_name": "Feng Qixiang",
        "account_credit_prop_value": "6222040000030002",
        "account_credit_prop_type": "CARD_NO",
        "amount_debit": "100",
        "payment_purpose": "135",
        "user_id": 134,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "Мульти запрос тест 5",
        "account_id_debit": "17424",
        "recipient_name": "Feng Qixiang",
        "account_credit_prop_value": "6222040000030002",
        "account_credit_prop_type": "CARD_NO",
        "amount_debit": "100",
        "payment_purpose": "135",
        "user_id": 134,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "Мульти запрос тест 6",
        "account_id_debit": "17424",
        "recipient_name": "Feng Qixiang",
        "account_credit_prop_value": "6222040000030002",
        "account_credit_prop_type": "CARD_NO",
        "amount_debit": "100",
        "payment_purpose": "135",
        "user_id": 134,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "To test Credit Verify fails when the beneficiary name is incorrect",
        "account_id_debit": "17575",
        "recipient_name": "An Xin",
        "account_credit_prop_value": "6222040000030002",
        "account_credit_prop_type": "CARD_NO",
        "amount_debit": "100",
        "payment_purpose": "135",
        "user_id": 3360,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "To test Credit Verify fails when transaction exceeds maximum single transaction amount limit.",
        "account_id_debit": "17575",
        "recipient_name": "Feng Qixiang",
        "account_credit_prop_value": "6222040000030002",
        "account_credit_prop_type": "CARD_NO",
        "amount_debit": "40001",
        "payment_purpose": "135",
        "user_id": 3360,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "1 To test Credit Verify fails when transaction exceeds maximum daliy transaction amount limit.",
        "account_id_debit": "17560",
        "recipient_name": "Feng Qixiang",
        "account_credit_prop_value": "6222040000030002",
        "account_credit_prop_type": "CARD_NO",
        "amount_debit": "40000",
        "payment_purpose": "135",
        "user_id": 3359,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "2 To test Credit Verify fails when transaction exceeds maximum daliy transaction amount limit.",
        "account_id_debit": "17560",
        "recipient_name": "Feng Qixiang",
        "account_credit_prop_value": "6222040000030002",
        "account_credit_prop_type": "CARD_NO",
        "amount_debit": "40001",
        "payment_purpose": "135",
        "user_id": 3359,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "Test credit verify using PAN with 81 BIN",
        "account_id_debit": "17575",
        "recipient_name": "Lily Zhang",
        "account_credit_prop_value": "8171999927660000",
        "account_credit_prop_type": "CARD_NO",
        "amount_debit": "50",
        "payment_purpose": "135",
        "user_id": 3360,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "Test primary credit using PAN with 81 BIN",
        "account_id_debit": "17575",
        "recipient_name": "Lily Zhang",
        "account_credit_prop_value": "8171999927660000",
        "account_credit_prop_type": "CARD_NO",
        "amount_debit": "50",
        "payment_purpose": "135",
        "user_id": 3360,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "Test credit verify ",
        "account_id_debit": "17575",
        "recipient_name": "MeiMei Wang",
        "account_credit_prop_value": "6250940500000006",
        "account_credit_prop_type": "CARD_NO",
        "amount_debit": "70",
        "payment_purpose": "135",
        "user_id": 3360,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    }
]


@pytest.mark.parametrize("test_data", MONEY_EXPRESS_TEST_DATA)
def test_money_express_payment_flow(test_data):
    """Параметризованный тест-кейс: Создание и подтверждение платежа через Money Express"""
    
    # === ИЗВЛЕЧЕНИЕ ДАННЫХ ИЗ ПАРАМЕТРА ===
    test_name = test_data["test_name"]
    account_id_debit = test_data["account_id_debit"]
    recipient_name = test_data["recipient_name"]
    account_credit_prop_value = test_data["account_credit_prop_value"]
    account_credit_prop_type = test_data["account_credit_prop_type"]
    amount_debit = test_data["amount_debit"]
    payment_purpose = test_data["payment_purpose"]
    user_id = test_data["user_id"]
    device_type = test_data["device_type"]
    user_agent = test_data["user_agent"]
    
    # === ПОЛУЧЕНИЕ СЕССИОННОГО КЛЮЧА ДЛЯ КОНКРЕТНОГО ПОЛЬЗОВАТЕЛЯ ===
    print(f"\n=== Получение сессионного ключа для user_id={user_id} ===")
    try:
        config = DatabaseConfig()
        collector = DataCollector(config)
        session_key = collector.get_valid_session_key(user_id=user_id)
        if not session_key:
            print(f"❌ Не найден валидный session_key для user_id={user_id}")
            pytest.skip(f"Нет валидного session_key для user_id={user_id}")
        print(f"✅ Получен session_key: {session_key[:10]}...")
    except Exception as e:
        print(f"❌ Ошибка получения session_key: {e}")
        pytest.skip(f"Ошибка получения session_key для user_id={user_id}: {e}")
    
    # === СОЗДАНИЕ МЕТАДАННЫХ С ПОЛЬЗОВАТЕЛЬСКИМ СЕССИОННЫМ КЛЮЧОМ ===
    def create_custom_metadata():
        return (
            ('refid', str(uuid.uuid1())),
            ('sessionkey', session_key),
            ('device-type', device_type),
            ('user-agent-c', user_agent),
        )
    
    # === ФУНКЦИЯ ПОДТВЕРЖДЕНИЯ С ПОЛЬЗОВАТЕЛЬСКИМИ МЕТАДАННЫМИ ===
    def confirm_operation_custom(operation_id: str, otp: str = "123456"):
        """Подтверждение операции через OTP с пользовательскими метаданными"""
        metadata = create_custom_metadata()
        
        confirm_data = {
            "operationId": operation_id,
            "otp": otp
        }
        
        return make_grpc_request("CONFIRM_TRANSFER", confirm_data, metadata)
    
    # === ШАГ 1: СОЗДАНИЕ ПЛАТЕЖА MONEY EXPRESS ===
    print(f"\n=== ШАГ 1: {test_name} - Создание платежа Money Express ===")
    
    operation_id = str(uuid.uuid1())
    
    payment_data = {
        "operationId": operation_id,
        "accountIdDebit": account_id_debit,
        "recipientName": recipient_name,
        "accountCreditPropValue": account_credit_prop_value,
        "accountCreditPropType": account_credit_prop_type,
        "amountDebit": amount_debit,
        "paymentPurpose": payment_purpose
    }
    
    print(f"Test: {test_name}")
    print(f"Operation ID: {operation_id}")
    print(f"Получатель: {recipient_name}")
    print(f"Номер карты: {account_credit_prop_value}")
    print(f"Сумма: {amount_debit} KGS")
    print(f"Данные: {payment_data}")
    
    # Используем helper функции из conftest с пользовательскими метаданными
    create_response = make_grpc_request(CODE_MAKE_MONEY_EXPRESS, payment_data, create_custom_metadata())
    print(f"Ответ: {create_response}")
    
    # Используем общую проверку успешности
    assert_success(create_response, f"{test_name} - Создание платежа Money Express")
    print(f"✅ {test_name} - Создание платежа Money Express успешно!")
    
    print("\nОжидание 2 секунд...")
    time.sleep(2)
    
    
    # === ШАГ 2: ПОДТВЕРЖДЕНИЕ ПЛАТЕЖА MONEY EXPRESS ===
    print(f"\n=== ШАГ 2: {test_name} - Подтверждение платежа Money Express ===")
    
    # Используем пользовательскую функцию подтверждения
    confirm_response = confirm_operation_custom(operation_id)
    print(f"Ответ: {confirm_response}")
    
    # Проверка успешности
    assert_success(confirm_response, f"{test_name} - Подтверждение платежа Money Express")
    print(f"✅ {test_name} - Подтверждение платежа Money Express успешно!")
    
    # === ШАГ 3: ПОЛУЧЕНИЕ PROCESSING_ID ИЗ БД ===
    print(f"\n=== ШАГ 3: {test_name} - Получение processing_id из БД ===")
    
    processing_id = get_processing_id_by_operation_id(operation_id)
    if processing_id:
        # Добавляем в глобальную коллекцию
        PROCESSING_IDS_COLLECTION.append({
            "test_name": test_name,
            "operation_id": operation_id,
            "processing_id": processing_id,
            "timestamp": datetime.now().isoformat()
        })
        print(f"✅ {test_name} - processing_id добавлен в коллекцию")
    else:
        print(f"⚠️ {test_name} - processing_id не найден")
    
    print(f"\n=== ✅ {test_name} - Тест пройден успешно ===")


def pytest_sessionfinish(session, exitstatus):
    """Вызывается после завершения всех тестов - сохраняет processing_id в файл"""
    print(f"\n=== ФИНАЛЬНЫЙ ЭТАП: Сохранение processing_id ===")
    save_processing_ids_to_file()


if __name__ == "__main__":
    # Запуск тестов
    import pytest
    pytest.main([__file__, "-v"])