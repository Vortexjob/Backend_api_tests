"""
Job для регистрации пользователя через Admin API
GET запрос для получения данных пользователя
POST запрос для регистрации нового пользователя
Запускается отдельно, не участвует в общем цикле тестов
Использует статичный session-key из data.py
"""
import os
import json
import uuid
import random
import string
import pytest
import requests
from datetime import datetime, timedelta

# Импорт данных
import data as app_data

# Статичный session-key для админки (отдельный от gRPC переводов)
STATIC_SESSION_KEY = app_data.ADMIN_SESSION_KEY


def generate_random_phone_number():
    """Генерация случайного номера телефона в формате +996XXXXXXXXX"""
    # Генерируем случайные 9 цифр
    random_digits = ''.join([str(random.randint(0, 9)) for _ in range(9)])
    return f"+996{random_digits}"


def generate_random_cyrillic_name(length: int = 8):
    """Генерация случайного имени на кириллице"""
    cyrillic_letters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    return ''.join(random.choice(cyrillic_letters) for _ in range(length)).capitalize()


def generate_random_latin_name(length: int = 8):
    """Генерация случайного имени на латинице"""
    latin_letters = string.ascii_lowercase
    return ''.join(random.choice(latin_letters) for _ in range(length)).capitalize()


def generate_random_inn():
    """Генерация случайного ИНН (14 цифр для корпоративных)"""
    return ''.join([str(random.randint(0, 9)) for _ in range(14)])


def generate_random_passport_number():
    """Генерация случайного номера паспорта"""
    return f"ID{''.join([str(random.randint(0, 9)) for _ in range(7)])}"


def generate_future_date(days_ahead: int = 365):
    """Генерация даты в будущем в формате DD-MM-YYYY"""
    future_date = datetime.now() + timedelta(days=days_ahead)
    return future_date.strftime("%d-%m-%Y")


def get_user_registration_data(user_id: str):
    """GET запрос для получения данных регистрации пользователя"""
    url = f"{app_data.ADMIN_API_URL}/adminApi/ibankUsers/registration/{user_id}"
    
    headers = {
        'Content-Type': 'application/json',
        'device-type': 'web',
        'ref-id': str(uuid.uuid4()),
        'session-key': STATIC_SESSION_KEY,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
        'user-agent-c': 'chrome',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'ru,en-US;q=0.9,en;q=0.8,ru-RU;q=0.7',
        'connection': 'keep-alive',
        'referer': f'http://192.168.190.46:55556/admin-ui/register?id={user_id}'
    }
    
    response = requests.get(url, headers=headers, timeout=30.0)
    return response


def register_user(user_data: dict):
    """POST запрос для регистрации нового пользователя (физические лица и ИП)"""
    url = f"{app_data.ADMIN_API_URL}/adminApi/ibankUsers/registration/new"
    
    headers = {
        'Content-Type': 'application/json',
        'device-type': 'web',
        'ref-id': str(uuid.uuid4()),
        'session-key': STATIC_SESSION_KEY,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
        'user-agent-c': 'chrome',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'ru,en-US;q=0.9,en;q=0.8,ru-RU;q=0.7',
        'connection': 'keep-alive',
        'referer': 'http://192.168.190.46:55556/admin-ui/register'
    }
    
    response = requests.post(url, headers=headers, json=user_data, timeout=30.0)
    return response


def register_corp_user(corp_data: dict):
    """POST запрос для регистрации корпоративного пользователя"""
    url = f"{app_data.ADMIN_API_URL}/adminApi/ibankUsers/registration/corp"
    
    headers = {
        'Content-Type': 'application/json',
        'device-type': 'web',
        'ref-id': str(uuid.uuid4()),
        'session-key': STATIC_SESSION_KEY,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
        'user-agent-c': 'chrome',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'ru,en-US;q=0.9,en;q=0.8,ru-RU;q=0.7',
        'connection': 'keep-alive',
        'referer': 'http://192.168.190.46:55556/admin-ui/register'
    }
    
    response = requests.post(url, headers=headers, json=corp_data, timeout=30.0)
    return response


def attach_file_to_requisition(req_id: int, file_base64: str, file_type: str = "application/pdf", extension: str = "pdf", filename: str = "Квитанция (43).pdf", name: str = ""):
    """POST запрос для прикрепления файла к заявке"""
    url = f"{app_data.ADMIN_API_URL}/adminApi/requisitions/file"
    
    headers = {
        'Content-Type': 'application/json',
        'device-type': 'web',
        'ref-id': str(uuid.uuid4()),
        'session-key': STATIC_SESSION_KEY,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
        'user-agent-c': 'chrome',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'ru,en-US;q=0.9,en;q=0.8,ru-RU;q=0.7',
        'connection': 'keep-alive',
        'referer': 'http://192.168.190.46:55556/admin-ui/register'
    }
    
    data = {
        "fileType": file_type,
        "reqId": req_id,
        "file": file_base64,
        "extension": extension,
        "filename": filename,
        "name": name
    }
    
    response = requests.post(url, headers=headers, json=data, timeout=30.0)
    return response


def update_requisition_status(req_id: int, status: str, comment: str = ""):
    """PUT запрос для обновления статуса заявки"""
    url = f"{app_data.ADMIN_API_URL}/adminApi/requisitions/status"
    
    headers = {
        'Content-Type': 'application/json',
        'device-type': 'web',
        'ref-id': str(uuid.uuid4()),
        'session-key': STATIC_SESSION_KEY,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
        'user-agent-c': 'chrome',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'ru,en-US;q=0.9,en;q=0.8,ru-RU;q=0.7',
        'connection': 'keep-alive',
        'referer': 'http://192.168.190.46:55556/admin-ui/register'
    }
    
    data = {
        "reqId": req_id,
        "status": status,
        "comment": comment
    }
    
    response = requests.put(url, headers=headers, json=data, timeout=30.0)
    return response


def load_user_ids_from_json():
    """Загрузка user_id (customerNo) из JSON для регистрации"""
    json_path = os.path.join(os.path.dirname(__file__), 'user_ids_for_registration.json')
    if not os.path.exists(json_path):
        return []
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            parsed_data = json.load(f)
            # Если это список, возвращаем его
            if isinstance(parsed_data, list):
                return [str(item) for item in parsed_data if item]
            # Если это строка, возвращаем список с одним элементом
            elif isinstance(parsed_data, str):
                return [parsed_data] if parsed_data else []
            return []
    except (json.JSONDecodeError, ValueError) as e:
        print(f"⚠️  Ошибка при загрузке JSON файла {json_path}: {e}")
        return []


def build_corp_registration_body(customer_no: str, phone_number: str, email: str, user_data_from_get: dict):
    """Формирование body для регистрации корпоративного пользователя"""
    customer = user_data_from_get.get('data', {}).get('customer', {})
    accounts = user_data_from_get.get('data', {}).get('accounts', [])
    
    # Генерируем случайные данные для пользователя
    full_name_cyr = generate_random_cyrillic_name(8)
    full_name_lat = generate_random_latin_name(8)
    inn = generate_random_inn()
    position = generate_random_cyrillic_name(6)  # Должность на кириллице
    passport_number = generate_random_passport_number()
    passport_exp_date = generate_future_date(365 * 5)  # Дата через 5 лет
    
    # Формируем доступы к счетам
    acc_accesses = []
    for account in accounts:
        acc_accesses.append({
            "accountNo": account.get('accNo', ''),
            "isAvailableForOperations": True,
            "isAvailableForView": True
        })
    
    # Операции доступа
    operation_accesses = [
        {"operationType": "BANK_CLIENT", "isAvailable": True},
        {"operationType": "OWN_ACCOUNTS", "isAvailable": True},
        {"operationType": "CLEARING_GROSS", "isAvailable": True},
        {"operationType": "SWIFT", "isAvailable": True},
        {"operationType": "DEALS", "isAvailable": True},
        {"operationType": "BATCH_SALARY", "isAvailable": True},
        {"operationType": "PAYMENT", "isAvailable": True},
        {"operationType": "ORDER_ACC_STATEMENT", "isAvailable": True},
        {"operationType": "ORDER_CHECKBOOK", "isAvailable": True},
        {"operationType": "ORDER_LOAN_STATEMENT", "isAvailable": True},
        {"operationType": "REOPEN_CARD", "isAvailable": True},
        {"operationType": "OPEN_NEW_ACCOUNT", "isAvailable": True}
    ]
    
    corp_data = {
        "transactionSignatureCards": [{
            "limitType": "unlimited",
            "amount": None,
            "ccy": None,
            "numberOfSignatures": 1,
            "firstSignUserIdsArr": [],
            "secondSignUserIdsArr": []
        }],
        "customer": {
            "customerNo": customer_no,
            "hasMultilevelSignature": False,
            "ipAddresses": "",
            "codeWord": "test",
            "readOnly": False
        },
        "users": [{
            "firstSign": False,
            "secondSign": False,
            "fullNameCyr": full_name_cyr,
            "fullNameLat": full_name_lat,
            "inn": inn,
            "position": position,
            "passportNumber": passport_number,
            "passportExpDate": passport_exp_date,
            "phoneNumber": phone_number,
            "email": email,
            "readOnly": False,
            "isCorpEmployee": False,
            "isChecker": False,
            "isMaker": True,
            "otpDelivery": "google",
            "tokenId": None,
            "accessExpDate": "",
            "accAccesses": acc_accesses,
            "operationAccesses": operation_accesses,
            "restorePassword": False,
            "creditAccounts": [],
            "id": str(uuid.uuid4())
        }]
    }
    
    return corp_data


def build_user_registration_body(customer_no: str, phone_number: str, email: str, user_data_from_get: dict = None):
    """Формирование body для регистрации физических лиц и ИП"""
    # Базовый body для физических лиц и ИП
    user_data = {
        "phoneNumber": phone_number,
        "email": email,
        "readOnly": False,
        "codeWord": "test",
        "fTokenId": "",
        "isFTokenEnabled": False,
        "customerNo": customer_no,
        "isJointAccount": False,
        "isPEemployee": False,
        "isTrusted": False,
        "trustedUserData": {},
        "jointUserData": {}
    }
    
    return user_data


def save_successfully_registered_user(customer_no: str, req_id: int, phone_number: str, email: str):
    """Сохранение успешно зарегистрированного пользователя в файл"""
    json_path = os.path.join(os.path.dirname(__file__), 'successfully_registered_users.json')
    
    # Загружаем существующие данные
    registered_users = []
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                registered_users = json.load(f)
                if not isinstance(registered_users, list):
                    registered_users = []
        except (json.JSONDecodeError, ValueError):
            registered_users = []
    
    # Проверяем, нет ли уже этого пользователя
    user_exists = any(user.get('customerNo') == customer_no for user in registered_users)
    
    if not user_exists:
        # Добавляем нового пользователя
        user_data = {
            "customerNo": customer_no,
            "reqId": req_id,
            "phoneNumber": phone_number,
            "email": email,
            "registeredAt": __import__('datetime').datetime.now().isoformat()
        }
        registered_users.append(user_data)
        
        # Сохраняем обратно в файл
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(registered_users, f, indent=2, ensure_ascii=False)
            print(f"[{customer_no}] ✅ Пользователь добавлен в список успешно зарегистрированных")
        except Exception as e:
            print(f"[{customer_no}] ⚠️  Ошибка при сохранении в файл: {e}")
    else:
        print(f"[{customer_no}] ℹ️  Пользователь уже есть в списке успешно зарегистрированных")


# Загружаем user_ids для теста регистрации
_USER_IDS_FOR_REGISTRATION = load_user_ids_from_json()

# Загружаем user_ids для GET теста (можно использовать тот же файл)
_USER_IDS_FOR_TEST = _USER_IDS_FOR_REGISTRATION


@pytest.mark.parametrize("user_id", _USER_IDS_FOR_TEST if _USER_IDS_FOR_TEST else ["00203091"])
def test_user_registration(user_id):
    """GET запрос для получения данных регистрации пользователя"""
    response = get_user_registration_data(user_id)
    
    print(f"\n[{user_id}] Status Code: {response.status_code}")
    print(f"[{user_id}] Response Headers: {dict(response.headers)}")
    print(f"[{user_id}] Response Text: {response.text}")
    
    if response.status_code == 200:
        try:
            print(f"[{user_id}] Response JSON: {response.json()}")
        except:
            pass


@pytest.mark.parametrize("customer_no", _USER_IDS_FOR_REGISTRATION if _USER_IDS_FOR_REGISTRATION else ["00203091"])
def test_register_new_user(customer_no):
    """POST запрос для регистрации нового пользователя и обновление статуса заявки"""
    # Сначала получаем данные пользователя, чтобы определить тип
    print(f"\n[{customer_no}] ===== ПОЛУЧЕНИЕ ДАННЫХ ПОЛЬЗОВАТЕЛЯ =====")
    user_data_response = get_user_registration_data(customer_no)
    
    user_type = None  # 'physical', 'ip', 'corp'
    user_data_from_get = None
    
    if user_data_response.status_code == 200:
        try:
            user_data_from_get = user_data_response.json()
            customer = user_data_from_get.get('data', {}).get('customer', {})
            customer_type = customer.get('customerType', '').upper()
            customer_category = customer.get('customerCategory', '')
            print(f"[{customer_no}] Тип пользователя: {customer_type} ({customer_category})")
        except Exception as e:
            print(f"[{customer_no}] ⚠️  Ошибка при парсинге данных пользователя: {e}")
            user_data_from_get = None
    else:
        print(f"[{customer_no}] ⚠️  Не удалось получить данные пользователя (Status: {user_data_response.status_code})")
        print(f"[{customer_no}] Response: {user_data_response.text}")
        user_data_from_get = None
    
    max_retries = 5  # Максимальное количество попыток с разными номерами
    
    # Переменные для сохранения данных успешной регистрации
    phone_number = None
    email = None
    
    for attempt in range(max_retries):
        # Генерируем случайный номер телефона
        phone_number = generate_random_phone_number()
        # Генерируем email на основе номера пользователя
        email = f"autotests{customer_no}@kicb.net"
        
        # Определяем тип пользователя и формируем соответствующий body
        customer_type = None
        if user_data_from_get and 'data' in user_data_from_get:
            customer = user_data_from_get['data'].get('customer', {})
            customer_type = customer.get('customerType', '').upper()
        
        if customer_type == 'C':  # Корпоративный пользователь
            # Формируем body для корпоративного пользователя
            corp_data = build_corp_registration_body(customer_no, phone_number, email, user_data_from_get)
            
            if attempt == 0:
                print(f"\n[{customer_no}] ===== НАЧАЛО РЕГИСТРАЦИИ КОРПОРАТИВНОГО ПОЛЬЗОВАТЕЛЯ =====")
            else:
                print(f"\n[{customer_no}] Попытка {attempt + 1}/{max_retries}: Генерация нового номера телефона")
            
            print(f"[{customer_no}] Request URL: {app_data.ADMIN_API_URL}/adminApi/ibankUsers/registration/corp")
            print(f"[{customer_no}] Phone Number: {phone_number}")
            print(f"[{customer_no}] Email: {email}")
            print(f"[{customer_no}] Request Body: {json.dumps(corp_data, indent=2, ensure_ascii=False)}")
            print(f"[{customer_no}] Session Key: {STATIC_SESSION_KEY[:20] if STATIC_SESSION_KEY else 'None'}...")
            
            # Шаг 1: Регистрация корпоративного пользователя
            response = register_corp_user(corp_data)
        else:
            # Формируем body для физических лиц и ИП
            user_data = build_user_registration_body(customer_no, phone_number, email, user_data_from_get)
            
            if attempt == 0:
                print(f"\n[{customer_no}] ===== НАЧАЛО РЕГИСТРАЦИИ =====")
            else:
                print(f"\n[{customer_no}] Попытка {attempt + 1}/{max_retries}: Генерация нового номера телефона")
            
            print(f"[{customer_no}] Request URL: {app_data.ADMIN_API_URL}/adminApi/ibankUsers/registration/new")
            print(f"[{customer_no}] Phone Number: {phone_number}")
            print(f"[{customer_no}] Email: {email}")
            print(f"[{customer_no}] Request Body: {json.dumps(user_data, indent=2, ensure_ascii=False)}")
            print(f"[{customer_no}] Session Key: {STATIC_SESSION_KEY[:20] if STATIC_SESSION_KEY else 'None'}...")
            
            # Шаг 1: Регистрация пользователя
            response = register_user(user_data)
        
        print(f"\n[{customer_no}] Status Code: {response.status_code}")
        print(f"[{customer_no}] Response Headers: {dict(response.headers)}")
        print(f"[{customer_no}] Response Text: {response.text}")
        
        req_id = None
        if response.status_code == 200:
            try:
                response_json = response.json()
                print(f"[{customer_no}] Response JSON: {response_json}")
                
                # Извлекаем reqId из ответа
                if isinstance(response_json, dict):
                    # Может быть в data.reqId или просто reqId
                    if 'data' in response_json and isinstance(response_json['data'], dict):
                        req_id = response_json['data'].get('reqId') or response_json['data'].get('requestId')
                    else:
                        req_id = response_json.get('reqId') or response_json.get('requestId')
                
                if req_id:
                    print(f"[{customer_no}] ✅ Извлечен reqId: {req_id}")
                else:
                    print(f"[{customer_no}] ⚠️  reqId не найден в ответе")
            except Exception as e:
                print(f"[{customer_no}] ❌ Ошибка при парсинге ответа: {e}")
        elif response.status_code == 401:
            print(f"[{customer_no}] ⚠️  Ошибка авторизации: нужен валидный session-key")
            return
        elif response.status_code == 400:
            # Проверяем, если ошибка "Данный номер занят" или "номер занят", пробуем снова
            try:
                response_json = response.json()
                error_obj = response_json.get('error', {})
                error_message = error_obj.get('message', '').lower() if error_obj.get('message') else ''
                error_code = error_obj.get('code', '')
                
                # Сначала проверяем "пользователь уже существует" или "клиент уже зарегистрирован" - пропускаем тест
                if 'пользователь уже существует' in error_message or 'клиент уже зарегестрирован' in error_message or 'клиент уже зарегистрирован' in error_message:
                    pytest.skip(f"Пользователь с customerNo={customer_no} уже существует или зарегистрирован")
                elif 'номер занят' in error_message or 'данный номер занят' in error_message:
                    print(f"[{customer_no}] ⚠️  Номер телефона занят, пробуем с новым номером...")
                    continue  # Пробуем с новым номером
                else:
                    # Другая ошибка валидации - выводим полную информацию
                    error_msg = error_obj.get('message', '')
                    if not error_msg:
                        # Если нет message, формируем сообщение из кода ошибки
                        error_msg = f"Error code: {error_code}"
                    
                    # Проверяем, является ли это ошибкой валидации данных (не критично)
                    validation_errors = [
                        'срок истечения паспорта',
                        'паспорт',
                        'invalid_request',
                        'invalid_credentials'
                    ]
                    
                    is_validation_error = any(val_err in error_message.lower() or val_err in error_code.lower() 
                                            for val_err in validation_errors)
                    
                    if is_validation_error or error_code == 'INVALID_REQUEST':
                        # Ошибка валидации данных - пропускаем тест
                        print(f"[{customer_no}] ⚠️  Ошибка валидации данных: {error_msg}")
                        print(f"[{customer_no}] Полный ответ: {response.text}")
                        pytest.skip(f"Ошибка валидации данных для customerNo={customer_no}: {error_msg}")
                    else:
                        # Критическая ошибка - падаем
                        print(f"[{customer_no}] ❌ Критическая ошибка: {error_msg}")
                        print(f"[{customer_no}] Полный ответ: {response.text}")
                        pytest.fail(f"Ошибка регистрации для customerNo={customer_no}: {error_msg}")
            except Exception as e:
                # Если не удалось распарсить JSON, падаем с ошибкой
                print(f"[{customer_no}] ❌ Ошибка 400, не удалось распарсить ответ: {e}")
                print(f"[{customer_no}] Полный ответ: {response.text}")
                pytest.fail(f"Ошибка 400 при регистрации, не удалось распарсить ответ: {e}")
        else:
            # Другая ошибка - не пробуем дальше
            print(f"[{customer_no}] ⚠️  Неожиданный статус код: {response.status_code}")
            return
        
        # Если дошли сюда, значит получили req_id, выходим из цикла
        if req_id:
            break
    
    # Если после всех попыток req_id не получен
    if req_id is None:
        print(f"[{customer_no}] ❌ Не удалось зарегистрировать пользователя после {max_retries} попыток")
        return
    
    # Шаг 2: Прикрепление файла к заявке
    if req_id:
        print(f"\n[{customer_no}] ===== ПРИКРЕПЛЕНИЕ ФАЙЛА =====")
        print(f"[{customer_no}] Прикрепление файла к reqId: {req_id}")
        
        # Простой PDF файл в base64 (минимальный валидный PDF)
        # Это минимальный PDF документ размером ~100 байт
        minimal_pdf_base64 = "JVBERi0xLjQKJeLjz9MKMyAwIG9iaiA8PAovTGVuZ3RoIDQ0ID4+CnN0cmVhbQpCVAovRjEgMTIgVGYKNTAgNzAwIFRkCihIZWxsbyBXb3JsZCkgVGoKRVQKZW5kc3RyZWFtCmVuZG9iago0IDAgb2JqIDw8Ci9UeXBlIC9QYWdlCi9QYXJlbnQgMSAwIFIKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KL1Jlc291cmNlcyAyIDAgUgovQ29udGVudHMgMyAwIFIKPj4KZW5kb2JqCjEgMCBvYmogPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFs0IDAgUl0KL0NvdW50IDEKPD4KZW5kb2JqCjIgMCBvYmogPDwKL0ZvbnQgPDwKL0YxIDw8Ci9UeXBlIC9Gb250Ci9TdWJ0eXBlIC9UeXBlMQovTmFtZSAvRjEKL0Jhc2VGb250IC9IZWx2ZXRpY2EKPj4KPj4KPj4KZW5kb2JqCnhyZWYKMCA1CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAxNSAwMDAwMCBuIAowMDAwMDAwMDY5IDAwMDAwIG4gCjAwMDAwMDAxNzMgMDAwMDAgbiAKMDAwMDAwMDQ1NyAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDUKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjU0NQolJUVPRg=="
        
        file_response = attach_file_to_requisition(
            req_id=req_id,
            file_base64=minimal_pdf_base64,
            file_type="application/pdf",
            extension="pdf",
            filename="Квитанция (43).pdf",
            name=""
        )
        
        print(f"[{customer_no}] File Attachment Status Code: {file_response.status_code}")
        print(f"[{customer_no}] File Attachment Response Text: {file_response.text}")
        
        if file_response.status_code == 200:
            try:
                print(f"[{customer_no}] File Attachment Response JSON: {file_response.json()}")
            except:
                pass
        else:
            error_msg = "Unknown error"
            try:
                response_json = file_response.json()
                error_msg = response_json.get('error', {}).get('message', 'Unknown error')
            except:
                pass
            print(f"[{customer_no}] ❌ Ошибка при прикреплении файла: {error_msg}")
            pytest.fail(f"Ошибка при прикреплении файла к заявке reqId={req_id}: {error_msg}")
    
    # Шаг 3: Обновление статуса заявки на "ON_VERIFICATION", если reqId получен
    if req_id:
        print(f"\n[{customer_no}] ===== ОБНОВЛЕНИЕ СТАТУСА =====")
        print(f"[{customer_no}] Шаг 1: Обновление статуса на ON_VERIFICATION для reqId: {req_id}")
        status = "ON_VERIFICATION"
        comment = ""
        
        status_response = update_requisition_status(req_id, status, comment)
        
        print(f"[{customer_no}] Status Code: {status_response.status_code}")
        print(f"[{customer_no}] Response Text: {status_response.text}")
        
        if status_response.status_code == 200:
            try:
                print(f"[{customer_no}] Response JSON: {status_response.json()}")
            except:
                pass
        else:
            error_msg = "Unknown error"
            try:
                response_json = status_response.json()
                error_msg = response_json.get('error', {}).get('message', 'Unknown error')
            except:
                pass
            print(f"[{customer_no}] ❌ Ошибка при обновлении статуса на ON_VERIFICATION: {error_msg}")
            pytest.fail(f"Ошибка при обновлении статуса на ON_VERIFICATION для reqId={req_id}: {error_msg}")
        
        # Шаг 4: Обновление статуса заявки на "VERIFIED"
        print(f"\n[{customer_no}] Шаг 2: Обновление статуса на VERIFIED для reqId: {req_id}")
        status_verified = "VERIFIED"
        comment_verified = ""
        
        verified_response = update_requisition_status(req_id, status_verified, comment_verified)
        
        print(f"[{customer_no}] Status Code: {verified_response.status_code}")
        print(f"[{customer_no}] Response Text: {verified_response.text}")
        
        if verified_response.status_code == 200:
            try:
                print(f"[{customer_no}] Response JSON: {verified_response.json()}")
            except:
                pass
            print(f"\n[{customer_no}] ===== РЕГИСТРАЦИЯ ЗАВЕРШЕНА УСПЕШНО =====")
            
            # Сохраняем успешно зарегистрированного пользователя
            if phone_number and email:
                save_successfully_registered_user(
                    customer_no=customer_no,
                    req_id=req_id,
                    phone_number=phone_number,
                    email=email
                )
        else:
            error_msg = "Unknown error"
            try:
                response_json = verified_response.json()
                error_msg = response_json.get('error', {}).get('message', 'Unknown error')
            except:
                pass
            print(f"[{customer_no}] ❌ Ошибка при обновлении статуса на VERIFIED: {error_msg}")
            pytest.fail(f"Ошибка при обновлении статуса на VERIFIED для reqId={req_id}: {error_msg}")
    else:
        print(f"[{customer_no}] ⚠️  Пропуск обновления статуса: reqId не получен")


def test_update_requisition_status():
    """PUT запрос для обновления статуса заявки"""
    req_id = 3743
    status = "ON_VERIFICATION"
    comment = ""
    
    print(f"\n[update_requisition_status] Request URL: {app_data.ADMIN_API_URL}/adminApi/requisitions/status")
    print(f"[update_requisition_status] Request Body: {json.dumps({'reqId': req_id, 'status': status, 'comment': comment}, indent=2, ensure_ascii=False)}")
    print(f"[update_requisition_status] Session Key: {STATIC_SESSION_KEY[:20] if STATIC_SESSION_KEY else 'None'}...")
    
    response = update_requisition_status(req_id, status, comment)
    
    print(f"\n[update_requisition_status] Status Code: {response.status_code}")
    print(f"[update_requisition_status] Response Headers: {dict(response.headers)}")
    print(f"[update_requisition_status] Response Text: {response.text}")
    
    if response.status_code == 200:
        try:
            print(f"[update_requisition_status] Response JSON: {response.json()}")
        except:
            pass
    elif response.status_code == 401:
        print(f"[update_requisition_status] ⚠️  Ошибка авторизации: нужен валидный session-key")

