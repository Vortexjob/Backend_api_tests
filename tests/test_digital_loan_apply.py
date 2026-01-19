"""
Тест для заявки на цифровой кредит с разными датами рождения
"""
import uuid
import pytest
from conftest import make_web_account_request, create_metadata, assert_success
from data import CODE_DIGITAL_LOAN_APPLY, CODE_DIGITAL_LOAN_CHECK_SERVICE, ACCOUNT_ID_DEBIT


# ===== ТЕСТОВЫЕ ДАННЫЕ =====
# Массив дат рождения для тестирования
BIRTH_DATES = [
    "1990-01-15",  # 34 года
    "1985-05-20",  # 39 лет
    "1995-12-31",  # 29 лет
    "1980-03-10",  # 44 года
    "2000-07-25",  # 24 года
    "1975-11-05",  # 49 лет
]

# Базовые данные для заявки
LOAN_AMOUNT = "10000"
LOAN_INSTALLMENTS = 3
LOAN_ACCOUNT_ID = 425  # Можно изменить на ACCOUNT_ID_DEBIT если нужно

# Базовые base64 строки для фото (заглушки)
PASSPORT_FRONT_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
PASSPORT_BACK_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
SELFIE_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
# ============================


@pytest.mark.parametrize("birth_date", BIRTH_DATES)
def test_digital_loan_apply_with_birth_date(birth_date):
    """
    Тест-кейс: Заявка на цифровой кредит с разными датами рождения
    
    Args:
        birth_date: Дата рождения в формате YYYY-MM-DD
    """
    print(f"\n=== Тест заявки на кредит с датой рождения: {birth_date} ===")
    
    # Подготовка данных заявки
    loan_data = {
        "amount": LOAN_AMOUNT,
        "numberOfInstallments": LOAN_INSTALLMENTS,
        "accountId": LOAN_ACCOUNT_ID,
        "passportFrontSide": PASSPORT_FRONT_BASE64,
        "passportBackSide": PASSPORT_BACK_BASE64,
        "selfie": SELFIE_BASE64
    }
    
    # Если API требует дату рождения, добавляем её
    # Раскомментируйте следующую строку, если поле birthDate требуется:
    # loan_data["birthDate"] = birth_date
    
    print(f"Дата рождения: {birth_date}")
    print(f"Сумма кредита: {LOAN_AMOUNT}")
    print(f"Количество платежей: {LOAN_INSTALLMENTS}")
    print(f"ID счета: {LOAN_ACCOUNT_ID}")
    print(f"Данные заявки: {loan_data}")
    
    # Выполнение запроса через WebAccountApi
    response = make_web_account_request(
        CODE_DIGITAL_LOAN_APPLY,
        loan_data,
        create_metadata()
    )
    
    print(f"\nОтвет сервера:")
    print(f"Success: {response.success}")
    
    if response.success:
        if hasattr(response, 'data') and response.data:
            import json
            try:
                response_data = json.loads(response.data)
                print(f"Request ID: {response_data.get('requestId', 'N/A')}")
                print(f"Request Status: {response_data.get('requestStatus', 'N/A')}")
            except json.JSONDecodeError:
                print(f"Data (raw): {response.data}")
    else:
        if hasattr(response, 'error') and response.error:
            print(f"Error code: {response.error.code}")
            print(f"Error data: {response.error.data}")
    
    # Проверка успешности
    assert_success(response, f"Заявка на кредит с датой рождения {birth_date}")
    
    print(f"✅ Заявка на кредит с датой рождения {birth_date} успешно создана!")


def test_digital_loan_apply_basic():
    """
    Базовый тест-кейс: Заявка на цифровой кредит без параметризации
    """
    print("\n=== Базовый тест заявки на цифровой кредит ===")
    
    loan_data = {
        "amount": LOAN_AMOUNT,
        "numberOfInstallments": LOAN_INSTALLMENTS,
        "accountId": LOAN_ACCOUNT_ID,
        "passportFrontSide": PASSPORT_FRONT_BASE64,
        "passportBackSide": PASSPORT_BACK_BASE64,
        "selfie": SELFIE_BASE64
    }
    
    print(f"Сумма кредита: {LOAN_AMOUNT}")
    print(f"Количество платежей: {LOAN_INSTALLMENTS}")
    print(f"ID счета: {LOAN_ACCOUNT_ID}")
    
    response = make_web_account_request(
        CODE_DIGITAL_LOAN_APPLY,
        loan_data,
        create_metadata()
    )
    
    print(f"\nОтвет: {response}")
    
    assert_success(response, "Заявка на цифровой кредит")
    
    if response.success and hasattr(response, 'data') and response.data:
        import json
        try:
            response_data = json.loads(response.data)
            print(f"✅ Request ID: {response_data.get('requestId', 'N/A')}")
            print(f"✅ Request Status: {response_data.get('requestStatus', 'N/A')}")
        except json.JSONDecodeError:
            pass
    
    print("\n✅ Базовый тест заявки на кредит пройден успешно!")


def test_digital_loan_health_check():
    """
    Тест-кейс: Health check сервиса digital loan
    
    Проверяет доступность сервиса и статус блокировки кредита
    """
    print("\n=== Тест health check сервиса digital loan ===")
    
    # Данные запроса - пустой объект
    health_check_data = {}
    
    print(f"Данные запроса: {health_check_data}")
    
    # Выполнение запроса через WebAccountApi
    response = make_web_account_request(
        CODE_DIGITAL_LOAN_CHECK_SERVICE,
        health_check_data,
        create_metadata()
    )
    
    print(f"\nОтвет сервера:")
    print(f"Success: {response.success}")
    
    if response.success:
        if hasattr(response, 'data') and response.data:
            import json
            try:
                response_data = json.loads(response.data)
                print(f"isDigitalLoanServiceEnable: {response_data.get('isDigitalLoanServiceEnable', 'N/A')}")
                print(f"isCreditLocked: {response_data.get('isCreditLocked', 'N/A')}")
                
                # creditLockText присутствует только если isCreditLocked = true
                if response_data.get('isCreditLocked', False):
                    credit_lock_text = response_data.get('creditLockText')
                    print(f"creditLockText: {credit_lock_text}")
                else:
                    print("creditLockText: отсутствует (isCreditLocked = false)")
                
                # Проверки
                assert 'isDigitalLoanServiceEnable' in response_data, "Отсутствует поле isDigitalLoanServiceEnable"
                assert 'isCreditLocked' in response_data, "Отсутствует поле isCreditLocked"
                
                # Если кредит заблокирован, должно быть поле creditLockText
                if response_data.get('isCreditLocked', False):
                    assert 'creditLockText' in response_data, "При isCreditLocked=true должно быть поле creditLockText"
                    assert response_data['creditLockText'], "creditLockText не должен быть пустым"
                
                print(f"\n✅ Полный ответ: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
                
            except json.JSONDecodeError:
                print(f"Data (raw): {response.data}")
    else:
        if hasattr(response, 'error') and response.error:
            print(f"Error code: {response.error.code}")
            print(f"Error data: {response.error.data}")
    
    # Проверка успешности
    assert_success(response, "Health check сервиса digital loan")
    
    print("\n✅ Health check сервиса digital loan пройден успешно!")

