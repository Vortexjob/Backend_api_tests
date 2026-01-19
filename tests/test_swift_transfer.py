import uuid
import time
import pytest
from conftest import make_grpc_request, create_metadata, confirm_operation, assert_success
from data import CODE_MAKE_SWIFT_TRANSFER, ACCOUNT_ID_DEBIT, OTP_CODE
from database_collector import DatabaseConfig, DataCollector


# === МАССИВ ТЕСТОВЫХ ДАННЫХ ДЛЯ SWIFT ПЕРЕВОДОВ ===
SWIFT_TEST_DATA = [
    # === USD - OUR ===
    {
        "test_name": "USD OUR - стандартный",
        "account_id_debit": 17425,
        "amount_debit": "10.00",
        "value_date": "2025-11-14",
        "transfer_ccy": "USD",
        "recipient_address": "123 Main Street, New York, NY 10001",
        "recipient_name": "John Smith",
        "recipient_bank_swift": "KICBKG22",
        "recipient_acc_no": "1234567890",
        "transfer_purpose_text": "Payment for services",
        "commission_type": "OUR",
        "commission_account_id": None,  # Будет использован account_id_debit
        "branch_code": None,
        "correspondent_bank": None,
        "user_id": 134,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "USD OUR - с филиалом",
        "account_id_debit": 17425,
        "amount_debit": "10.00",
        "value_date": "2025-11-14",
        "transfer_ccy": "USD",
        "recipient_address": "123 Main Street, New York, NY 10001",
        "recipient_name": "John Smith",
        "recipient_bank_swift": "KICBKG22",
        "recipient_acc_no": "1234567890",
        "transfer_purpose_text": "Payment for services",
        "commission_type": "OUR",
        "commission_account_id": None,  # Будет использован account_id_debit
        "branch_code": "001",
        "correspondent_bank": None,
        "user_id": 134,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "USD OUR - с длинным назначением",
        "account_id_debit": 17425,
        "amount_debit": "10.00",
        "value_date": "2025-11-14",
        "transfer_ccy": "USD",
        "recipient_address": "123 Main Street, New York, NY 10001",
        "recipient_name": "John Smith",
        "recipient_bank_swift": "KICBKG22",
        "recipient_acc_no": "1234567890",
        "transfer_purpose_text": "This is a very long payment purpose text that exceeds the standard length to test how the system handles extended purpose descriptions in SWIFT transfers.",
        "commission_type": "OUR",
        "commission_account_id": None,  # Будет использован account_id_debit
        "branch_code": None,
        "correspondent_bank": None,
        "user_id": 134,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "USD OUR - с длинным наименованием",
        "account_id_debit": 17425,
        "amount_debit": "10.00",
        "value_date": "2025-11-14",
        "transfer_ccy": "USD",
        "recipient_address": "123 Main Street, New York, NY 10001",
        "recipient_name": "International Trading Company Limited Partnership with Extended",
        "recipient_bank_swift": "KICBKG22",
        "recipient_acc_no": "1234567890",
        "transfer_purpose_text": "Payment for services",
        "commission_type": "OUR",
        "commission_account_id": None,  # Будет использован account_id_debit
        "branch_code": None,
        "correspondent_bank": None,
        "user_id": 134,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "USD OUR - с корр банком",
        "account_id_debit": 17425,
        "amount_debit": "10.00",
        "value_date": "2025-11-14",
        "transfer_ccy": "USD",
        "recipient_address": "123 Main Street, New York, NY 10001",
        "recipient_name": "John Smith",
        "recipient_bank_swift": "KICBKG22",
        "recipient_acc_no": "1234567890",
        "transfer_purpose_text": "Payment for services",
        "commission_type": "OUR",
        "commission_account_id": None,  # Будет использован account_id_debit
        "branch_code": None,
        "correspondent_bank": "CITIUS33",
        "user_id": 134,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    # === USD - BEN ===
    {
        "test_name": "USD BEN - стандартный",
        "account_id_debit": 17425,
        "amount_debit": "100.00",
        "value_date": "2025-11-14",
        "transfer_ccy": "USD",
        "recipient_address": "adrr",
        "recipient_name": "naim",
        "recipient_bank_swift": "KICBKG22",
        "recipient_acc_no": "IBANIBANIBANIBANIBAN",
        "transfer_purpose_text": "nazn",
        "commission_type": "BEN",
        "commission_account_id": "17425",
        "branch_code": None,
        "correspondent_bank": None,
        "user_id": 134,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "USD BEN - с филиалом",
        "account_id_debit": 17425,
        "amount_debit": "100.00",
        "value_date": "2025-11-14",
        "transfer_ccy": "USD",
        "recipient_address": "adrr",
        "recipient_name": "naim",
        "recipient_bank_swift": "KICBKG22",
        "recipient_acc_no": "IBANIBANIBANIBANIBAN",
        "transfer_purpose_text": "nazn",
        "commission_type": "BEN",
        "commission_account_id": "17425",
        "branch_code": "001",
        "correspondent_bank": None,
        "user_id": 134,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "USD BEN - с длинным назначением",
        "account_id_debit": 17425,
        "amount_debit": "100.00",
        "value_date": "2025-11-14",
        "transfer_ccy": "USD",
        "recipient_address": "qwertyuiopasdfghjklqwertyuoipqwetryuiopqwertyuiopqwertyiiopqwertyuiopa",
        "recipient_name": "dfghjnf",
        "recipient_bank_swift": "KICBKG22",
        "recipient_acc_no": "12345678901234567890123456789012345",
        "transfer_purpose_text": "wthfhrzurzitiztjxjtjtxxyxkgxjfzkgkgjfkjxgk",
        "commission_type": "BEN",
        "commission_account_id": "17425",
        "branch_code": None,
        "correspondent_bank": None,
        "user_id": 134,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "USD BEN - с длинным наименованием",
        "account_id_debit": 17425,
        "amount_debit": "100.00",
        "value_date": "2025-11-14",
        "transfer_ccy": "USD",
        "recipient_address": "adrr",
        "recipient_name": "naim",
        "recipient_bank_swift": "KICBKG22",
        "recipient_acc_no": "IBANIBANIBANIBANIBAN",
        "transfer_purpose_text": "nazn",
        "commission_type": "BEN",
        "commission_account_id": "17425",
        "branch_code": None,
        "correspondent_bank": None,
        "user_id": 134,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "USD BEN - с корр банком",
        "account_id_debit": 17425,
        "amount_debit": "100.00",
        "value_date": "2025-11-14",
        "transfer_ccy": "USD",
        "recipient_address": "adrr",
        "recipient_name": "naim",
        "recipient_bank_swift": "KICBKG22",
        "recipient_acc_no": "IBANIBANIBANIBANIBAN",
        "transfer_purpose_text": "nazn",
        "commission_type": "BEN",
        "commission_account_id": "17425",
        "branch_code": None,
        "correspondent_bank": "CITIUS33",
        "user_id": 134,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    # === USD - OUR-OUR ===
    {
        "test_name": "USD OUR-OUR - стандартный",
        "account_id_debit": 17425,
        "amount_debit": "10.00",
        "value_date": "2025-11-14",
        "transfer_ccy": "USD",
        "recipient_address": "123 Main Street, New York, NY 10001",
        "recipient_name": "John Smith",
        "recipient_bank_swift": "KICBKG22",
        "recipient_acc_no": "1234567890",
        "transfer_purpose_text": "Payment for services",
        "commission_type": "OUR-OUR",
        "commission_account_id": None,  # Будет использован account_id_debit
        "branch_code": None,
        "correspondent_bank": None,
        "user_id": 134,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "USD OUR-OUR - с филиалом",
        "account_id_debit": 17425,
        "amount_debit": "10.00",
        "value_date": "2025-11-14",
        "transfer_ccy": "USD",
        "recipient_address": "123 Main Street, New York, NY 10001",
        "recipient_name": "John Smith",
        "recipient_bank_swift": "KICBKG22",
        "recipient_acc_no": "1234567890",
        "transfer_purpose_text": "Payment for services",
        "commission_type": "OUR-OUR",
        "commission_account_id": None,  # Будет использован account_id_debit
        "branch_code": "001",
        "correspondent_bank": None,
        "user_id": 134,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "USD OUR-OUR - с длинным назначением",
        "account_id_debit": 17425,
        "amount_debit": "10.00",
        "value_date": "2025-11-14",
        "transfer_ccy": "USD",
        "recipient_address": "123 Main Street, New York, NY 10001",
        "recipient_name": "John Smith",
        "recipient_bank_swift": "KICBKG22",
        "recipient_acc_no": "1234567890",
        "transfer_purpose_text": "This is a very long payment purpose text that exceeds the standard length to test how the system handles extended purpose descriptions in SWIFT transfers.",
        "commission_type": "OUR-OUR",
        "commission_account_id": None,  # Будет использован account_id_debit
        "branch_code": None,
        "correspondent_bank": None,
        "user_id": 134,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "USD OUR-OUR - с длинным наименованием получателя",
        "account_id_debit": 17425,
        "amount_debit": "10.00",
        "value_date": "2025-11-14",
        "transfer_ccy": "USD",
        "recipient_address": "123 Main Street, New York, NY 10001",
        "recipient_name": "International Trading Company Limited Partnership with Extended",
        "recipient_bank_swift": "KICBKG22",
        "recipient_acc_no": "1234567890",
        "transfer_purpose_text": "Payment for services",
        "commission_type": "OUR-OUR",
        "commission_account_id": None,  # Будет использован account_id_debit
        "branch_code": None,
        "correspondent_bank": None,
        "user_id": 134,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "USD OUR-OUR - с корр банком",
        "account_id_debit": 17425,
        "amount_debit": "10.00",
        "value_date": "2025-11-14",
        "transfer_ccy": "USD",
        "recipient_address": "123 Main Street, New York, NY 10001",
        "recipient_name": "John Smith",
        "recipient_bank_swift": "KICBKG22",
        "recipient_acc_no": "1234567890",
        "transfer_purpose_text": "Payment for services",
        "commission_type": "OUR-OUR",
        "commission_account_id": None,  # Будет использован account_id_debit
        "branch_code": None,
        "correspondent_bank": "CITIUS33",
        "user_id": 134,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "USD OUR - с филиалом и корр банком",
        "account_id_debit": 17425,
        "amount_debit": "10.00",
        "value_date": "2025-11-14",
        "transfer_ccy": "USD",
        "recipient_address": "123 Main Street, New York, NY 10001",
        "recipient_name": "John Smith",
        "recipient_bank_swift": "KICBKG22",
        "recipient_acc_no": "1234567890",
        "transfer_purpose_text": "Payment for services",
        "commission_type": "OUR",
        "commission_account_id": None,  # Будет использован account_id_debit
        "branch_code": "001",
        "correspondent_bank": "CITIUS33",
        "user_id": 134,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "USD BEN - с филиалом и корр банком",
        "account_id_debit": 17425,
        "amount_debit": "100.00",
        "value_date": "2025-11-14",
        "transfer_ccy": "USD",
        "recipient_address": "adrr",
        "recipient_name": "naim",
        "recipient_bank_swift": "KICBKG22",
        "recipient_acc_no": "IBANIBANIBANIBANIBAN",
        "transfer_purpose_text": "nazn",
        "commission_type": "BEN",
        "commission_account_id": "17425",
        "branch_code": "001",
        "correspondent_bank": "CITIUS33",
        "user_id": 134,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "USD OUR - с другим account для комиссии",
        "account_id_debit": 17425,
        "amount_debit": "10.00",
        "value_date": "2025-11-14",
        "transfer_ccy": "USD",
        "recipient_address": "123 Main Street, New York, NY 10001",
        "recipient_name": "John Smith",
        "recipient_bank_swift": "KICBKG22",
        "recipient_acc_no": "1234567890",
        "transfer_purpose_text": "Payment for services",
        "commission_type": "OUR",
        "commission_account_id": "17435",  # Другой account для комиссии
        "branch_code": None,
        "correspondent_bank": None,
        "user_id": 134,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    # === RUB ===
    {
        "test_name": "RUB - обычный",
        "account_id_debit": 17429,
        "amount_debit": "100.00",
        "value_date": "2025-11-14",
        "transfer_ccy": "RUB",
        "recipient_address": "ул. Тверская, д. 1, Москва, 101000",
        "recipient_name": "Иван Петров",
        "recipient_bank_swift": "KICBKG22",
        "recipient_acc_no": "40817810099910004312",
        "transfer_purpose_text": "Оплата за услуги",
        "commission_type": "OUR",
        "commission_account_id": None,  # Будет использован account_id_debit
        "branch_code": None,
        "correspondent_bank": None,
        "vo_code": "10100",
        "inn": "77045259380000",
        "kpp": "503001001",
        "correspondent_acc_no": "30101810300000000105",
        "user_id": 134,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "RUB - с длинным назначением",
        "account_id_debit": 17429,
        "amount_debit": "100.00",
        "value_date": "2025-11-14",
        "transfer_ccy": "RUB",
        "recipient_address": "ул. Тверская, д. 1, Москва, 101000",
        "recipient_name": "Иван Петров",
        "recipient_bank_swift": "KICBKG22",
        "recipient_acc_no": "40817810099910004312",
        "transfer_purpose_text": "This is a very long payment purpose text that exceeds the standard length to test how the system handles extended purpose descriptions in SWIFT transfers.",
        "commission_type": "OUR",
        "commission_account_id": None,  # Будет использован account_id_debit
        "branch_code": None,
        "correspondent_bank": None,
        "vo_code": "10100",
        "inn": "77045259380000",
        "kpp": "503001001",
        "correspondent_acc_no": "30101810300000000105",
        "user_id": 134,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "RUB - с длинным наименованием получателя",
        "account_id_debit": 17429,
        "amount_debit": "100.00",
        "value_date": "2025-11-14",
        "transfer_ccy": "RUB",
        "recipient_address": "ул. Тверская, д. 1, Москва, 101000",
        "recipient_name": "Общество с ограниченной ответственностью Международная Торговая",
        "recipient_bank_swift": "KICBKG22",
        "recipient_acc_no": "40817810099910004312",
        "transfer_purpose_text": "Оплата за услуги",
        "commission_type": "OUR",
        "commission_account_id": None,  # Будет использован account_id_debit
        "branch_code": None,
        "correspondent_bank": None,
        "vo_code": "10100",
        "inn": "77045259380000",
        "kpp": "503001001",
        "correspondent_acc_no": "30101810300000000105",
        "user_id": 134,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "RUB - с филиалом",
        "account_id_debit": 17429,
        "amount_debit": "100.00",
        "value_date": "2025-11-14",
        "transfer_ccy": "RUB",
        "recipient_address": "ул. Тверская, д. 1, Москва, 101000",
        "recipient_name": "Иван Петров",
        "recipient_bank_swift": "KICBKG22",
        "recipient_acc_no": "40817810099910004312",
        "transfer_purpose_text": "Оплата за услуги",
        "commission_type": "OUR",
        "commission_account_id": None,  # Будет использован account_id_debit
        "branch_code": "001",
        "correspondent_bank": None,
        "vo_code": "10100",
        "inn": "77045259380000",
        "kpp": "503001001",
        "correspondent_acc_no": "30101810300000000105",
        "user_id": 134,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    # === KZT ===
    {
        "test_name": "KZT - обычный",
        "account_id_debit": 17430,
        "amount_debit": "1000.00",
        "value_date": "2025-11-14",
        "transfer_ccy": "KZT",
        "recipient_address": "ул. Абая, д. 150, Алматы, 050000",
        "recipient_name": "Айдар Нурланов",
        "recipient_bank_swift": "KICBKG22",
        "recipient_acc_no": "KZ86125KZT1001100100",
        "transfer_purpose_text": "Назначение",
        "commission_type": "OUR",
        "commission_account_id": None,  # Будет использован account_id_debit
        "branch_code": None,
        "correspondent_bank": None,
        "bin": "1234564541451445",
        "kbe": "15555",
        "knp": "5151515",
        "user_id": 134,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "KZT - с длинным назначением",
        "account_id_debit": 17430,
        "amount_debit": "1000.00",
        "value_date": "2025-11-14",
        "transfer_ccy": "KZT",
        "recipient_address": "ул. Абая, д. 150, Алматы, 050000",
        "recipient_name": "Айдар Нурланов",
        "recipient_bank_swift": "KICBKG22",
        "recipient_acc_no": "KZ86125KZT1001100100",
        "transfer_purpose_text": "Монтажные работы по счету 26 от 21.09.23",
        "commission_type": "OUR",
        "commission_account_id": None,  # Будет использован account_id_debit
        "branch_code": None,
        "correspondent_bank": None,
        "bin": "1234564541451445",
        "kbe": "15555",
        "knp": "5151515",
        "user_id": 134,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "KZT - с длинным наименованием получателя",
        "account_id_debit": 17430,
        "amount_debit": "1000.00",
        "value_date": "2025-11-14",
        "transfer_ccy": "KZT",
        "recipient_address": "ул. Абая, д. 150, Алматы, 050000",
        "recipient_name": "International Trade Company Limited",
        "recipient_bank_swift": "KICBKG22",
        "recipient_acc_no": "KZ86125KZT1001100100",
        "transfer_purpose_text": "Назначение",
        "commission_type": "OUR",
        "commission_account_id": None,  # Будет использован account_id_debit
        "branch_code": None,
        "correspondent_bank": None,
        "bin": "1234564541451445",
        "kbe": "15555",
        "knp": "5151515",
        "user_id": 134,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "KZT - с филиалом",
        "account_id_debit": 17430,
        "amount_debit": "1000.00",
        "value_date": "2025-11-14",
        "transfer_ccy": "KZT",
        "recipient_address": "ул. Абая, д. 150, Алматы, 050000",
        "recipient_name": "Айдар Нурланов",
        "recipient_bank_swift": "KICBKG22",
        "recipient_acc_no": "KZ86125KZT1001100100",
        "transfer_purpose_text": "Назначение",
        "commission_type": "OUR",
        "commission_account_id": None,  # Будет использован account_id_debit
        "branch_code": "001",
        "correspondent_bank": None,
        "bin": "1234564541451445",
        "kbe": "15555",
        "knp": "5151515",
        "user_id": 134,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    # === AED, EUR ===
    {
        "test_name": "AED - стандартный",
        "account_id_debit": 17759,
        "amount_debit": "10.00",
        "value_date": "2025-11-14",
        "transfer_ccy": "AED",
        "recipient_address": "Sheikh Zayed Road, Dubai, UAE",
        "recipient_name": "Ahmed Al-Mansoori",
        "recipient_bank_swift": "KICBKG22",
        "recipient_acc_no": "AE070331234567890123456",
        "transfer_purpose_text": "Payment for services",
        "commission_type": "OUR",
        "commission_account_id": None,  # Будет использован account_id_debit
        "branch_code": None,
        "correspondent_bank": None,
        "user_id": 134,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "EUR - стандартный",
        "account_id_debit": 17423,
        "amount_debit": "10.00",
        "value_date": "2025-11-14",
        "transfer_ccy": "EUR",
        "recipient_address": "Netherland, Arnhem",
        "recipient_name": "ABN AMRO BANK",
        "recipient_bank_swift": "KICBKG22",
        "recipient_acc_no": "NL09ABNA0423180746",
        "transfer_purpose_text": "for haircut service",
        "commission_type": "OUR",
        "commission_account_id": None,  # Будет использован account_id_debit
        "branch_code": None,
        "correspondent_bank": None,
        "user_id": 134,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
]


def _get_session_key(user_id: int, offset: int = 0) -> str:
    """Получает сессионный ключ из БД с возможностью указать смещение"""
    config = DatabaseConfig()
    collector = DataCollector(config)
    session_key = collector.get_valid_session_key(user_id=user_id, offset=offset)
    if not session_key:
        pytest.skip(f"Нет валидного session_key для user_id={user_id} с offset={offset}")
    print(f"[_get_session_key] Получен session_key из БД для user_id={user_id}, offset={offset}: {session_key[:20]}...")
    return session_key


def _get_session_key_with_retry(user_id: int, max_retries: int = 10) -> str:
    """Получает сессионный ключ из БД с автоматическим retry при ошибке INVALID_SESSION_KEY"""
    config = DatabaseConfig()
    collector = DataCollector(config)
    
    for offset in range(max_retries):
        session_key = collector.get_valid_session_key(user_id=user_id, offset=offset)
        if not session_key:
            if offset == 0:
                pytest.skip(f"Нет валидного session_key для user_id={user_id}")
            break  # Больше нет ключей
        
        print(f"[_get_session_key_with_retry] Пробуем session_key с offset={offset}: {session_key[:20]}...")
        return session_key
    
    pytest.skip(f"Не удалось найти валидный session_key для user_id={user_id} после {max_retries} попыток")


def _build_metadata(session_key: str, device_type: str, user_agent: str):
    """Создает метаданные для запроса"""
    return (
        ("refid", str(uuid.uuid1())),
        ("sessionkey", session_key),
        ("device-type", device_type),
        ("user-agent-c", user_agent),
    )


def _confirm_operation(operation_id: str, metadata: tuple, otp: str = OTP_CODE):
    """Подтверждение операции через OTP"""
    confirm_payload = {
        "operationId": operation_id,
        "otp": otp,
    }
    response = make_grpc_request("CONFIRM_TRANSFER", confirm_payload, metadata)
    assert_success(response, "Подтверждение SWIFT перевода")
    return response


@pytest.mark.parametrize("test_data", SWIFT_TEST_DATA)
def test_swift_transfer_flow(test_data):
    """Параметризованный тест-кейс: Создание и подтверждение SWIFT перевода"""
    
    test_name = test_data["test_name"]
    user_id = test_data["user_id"]
    
    print(f"\n=== {test_name} ===")
    print(f"Получаем session_key для user_id={user_id}")
    
    # Получаем первый ключ (offset=0)
    session_key = _get_session_key(user_id=user_id, offset=0)
    print(f"[test] Используем session_key с offset=0: {session_key[:20]}...")
    
    metadata = _build_metadata(session_key, test_data["device_type"], test_data["user_agent"])
    print(f"[test] Метаданные созданы, sessionkey в metadata: {dict(metadata).get('sessionkey', 'NOT FOUND')[:20] if isinstance(metadata, (list, tuple)) else 'N/A'}...")
    
    operation_id = str(uuid.uuid1())
    
    transfer_data = {
        "operationId": operation_id,
        "accountIdDebit": test_data["account_id_debit"],
        "amountDebit": test_data["amount_debit"],
        "valueDate": test_data["value_date"],
        "transferCcy": test_data["transfer_ccy"],
        "recipientAddress": test_data["recipient_address"],
        "recipientName": test_data["recipient_name"],
        "recipientBankSwift": test_data["recipient_bank_swift"],
        "recipientAccNo": test_data["recipient_acc_no"],
        "transferPurposeText": test_data["transfer_purpose_text"],
        "commissionType": test_data["commission_type"],
        "commissionAccountId": test_data.get("commission_account_id") or str(test_data["account_id_debit"]),
        "files": []
    }
    
    # Добавляем опциональные поля
    if test_data.get("branch_code"):
        transfer_data["branchCode"] = test_data["branch_code"]
    
    if test_data.get("correspondent_bank"):
        transfer_data["correspondentBank"] = test_data["correspondent_bank"]
    
    # Добавляем поля для KZT
    if test_data.get("bin"):
        transfer_data["bin"] = test_data["bin"]
    
    if test_data.get("kbe"):
        transfer_data["kbe"] = test_data["kbe"]
    
    if test_data.get("knp"):
        transfer_data["knp"] = test_data["knp"]
    
    # Добавляем поля для RUB
    if test_data.get("vo_code"):
        transfer_data["voCode"] = test_data["vo_code"]
    
    if test_data.get("inn"):
        transfer_data["inn"] = test_data["inn"]
    
    if test_data.get("kpp"):
        transfer_data["kpp"] = test_data["kpp"]
    
    if test_data.get("correspondent_acc_no"):
        transfer_data["corAccNo"] = test_data["correspondent_acc_no"]
    
    print(f"Operation ID: {operation_id}")
    print(f"Валюта: {test_data['transfer_ccy']}")
    print(f"Сумма: {test_data['amount_debit']} {test_data['transfer_ccy']}")
    print(f"Получатель: {test_data['recipient_name']}")
    print(f"Тип комиссии: {test_data['commission_type']}")
    if test_data.get("branch_code"):
        print(f"Код филиала: {test_data['branch_code']}")
    if test_data.get("correspondent_bank"):
        print(f"Корреспондентский банк: {test_data['correspondent_bank']}")
    
    # Пробуем запрос, при ошибке INVALID_SESSION_KEY пробуем следующий ключ
    create_response = None
    max_retries = 10
    current_key_offset = 0
    
    for retry_attempt in range(max_retries):
        try:
            create_response = make_grpc_request(CODE_MAKE_SWIFT_TRANSFER, transfer_data, metadata)
            print(f"Ответ: {create_response}")
    
            # Проверяем, не ошибка ли INVALID_SESSION_KEY
            if hasattr(create_response, 'error') and create_response.error and hasattr(create_response.error, 'code'):
                if create_response.error.code == "INVALID_SESSION_KEY":
                    if retry_attempt < max_retries - 1:
                        print(f"[test] Получена ошибка INVALID_SESSION_KEY, пробуем следующий ключ (offset={current_key_offset + 1})...")
                        # Получаем следующий ключ
                        current_key_offset += 1
                        session_key = _get_session_key(user_id=user_id, offset=current_key_offset)
                        metadata = _build_metadata(session_key, test_data["device_type"], test_data["user_agent"])
                        print(f"[test] Используем новый session_key: {session_key[:20]}...")
                        continue
                    else:
                        # Последняя попытка, выбрасываем ошибку
                        assert_success(create_response, f"{test_name} - Создание SWIFT перевода")
            
            # Если не INVALID_SESSION_KEY, проверяем успешность
            assert_success(create_response, f"{test_name} - Создание SWIFT перевода")
            break  # Успешно, выходим из цикла
            
        except AssertionError as e:
            # Проверяем, не ошибка ли INVALID_SESSION_KEY в сообщении
            error_msg = str(e)
            if "INVALID_SESSION_KEY" in error_msg and retry_attempt < max_retries - 1:
                print(f"[test] Получена ошибка INVALID_SESSION_KEY в assert, пробуем следующий ключ (offset={current_key_offset + 1})...")
                # Получаем следующий ключ
                current_key_offset += 1
                session_key = _get_session_key(user_id=user_id, offset=current_key_offset)
                metadata = _build_metadata(session_key, test_data["device_type"], test_data["user_agent"])
                print(f"[test] Используем новый session_key: {session_key[:20]}...")
                continue
            else:
                raise  # Другая ошибка или последняя попытка
    
    print(f"✅ {test_name} - Создание SWIFT перевода успешно!")
    
    print("\nОжидание 5 секунд...")
    time.sleep(5)
    
    print(f"\n=== {test_name} - Подтверждение SWIFT перевода ===")
    confirm_response = _confirm_operation(operation_id, metadata)
    print(f"Ответ: {confirm_response}")
    
    assert_success(confirm_response, f"{test_name} - Подтверждение SWIFT перевода")
    print(f"✅ {test_name} - Подтверждение SWIFT перевода успешно!")
    
    print(f"\n=== ✅ {test_name} - Тест пройден успешно ===")


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])