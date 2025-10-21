import sys
import os
import uuid
import grpc
import json
import pytest

# ===== НАСТРОЙКА PROTOBUF =====
# Путь к директории с protobuf файлами
PROTOBUF_PATH = os.path.join(os.path.dirname(__file__), 'protofiles')

sys.path.append(PROTOBUF_PATH)

# Импорт protobuf файлов
import protofile_pb2 as webTransferApi_pb2
import protofile_pb2_grpc as webTransferApi_pb2_grpc

# Импорт данных для использования в фикстурах (модульно, чтобы обновлять SESSION_KEY динамически)
import data as app_data
from database_collector import DatabaseConfig, DataCollector


# ===== PYTEST ФИКСТУРЫ =====

@pytest.fixture(autouse=True, scope="function")
def _load_session_key_before_test():
    """Авто-фикстура: перед каждым тестом загружает валидный session_key из БД в app_data.SESSION_KEY.
    При ошибке оставляет текущее значение app_data.SESSION_KEY без изменений.
    """
    try:
        config = DatabaseConfig()
        collector = DataCollector(config)
        session_key = collector.get_valid_session_key(user_id=134)
        if session_key:
            app_data.SESSION_KEY = session_key
            print(f"[session_key_loader] ✅ Обновлен session_key: {session_key[:10]}...")
        else:
            print(f"[session_key_loader] ⚠️ Не найден валидный session_key для user_id=134")
    except Exception as e:
        # Логируем и продолжаем с текущим ключом
        print(f"[session_key_loader] ❌ Ошибка: {e}")

@pytest.fixture
def grpc_metadata():
    """Фикстура для генерации метаданных запроса"""
    def _create_metadata():
        return (
            ('refid', str(uuid.uuid1())),
            ('sessionkey', app_data.SESSION_KEY),
            ('device-type', app_data.DEVICE_TYPE),
            ('user-agent-c', app_data.USER_AGENT),
        )
    return _create_metadata


@pytest.fixture
def grpc_client():
    """Фикстура для создания gRPC клиента"""
    def _get_client():
        channel = grpc.secure_channel(
            app_data.GRPC_SERVER_URL,
            grpc.ssl_channel_credentials(),
            options=app_data.GRPC_OPTIONS
        )
        return webTransferApi_pb2_grpc.WebTransferApiStub(channel), channel
    return _get_client


# ===== HELPER ФУНКЦИИ =====

def make_grpc_request(code: str, data: dict, metadata: tuple):
    """
    Общая функция для выполнения gRPC запроса
    
    Args:
        code: Код операции
        data: Данные запроса (dict)
        metadata: Метаданные запроса (tuple)
    
    Returns:
        Response от сервера
    """
    request = webTransferApi_pb2.IncomingWebTransfer(
        code=code,
        data=json.dumps(data)
    )
    
    with grpc.secure_channel(
            app_data.GRPC_SERVER_URL,
            grpc.ssl_channel_credentials(),
            options=app_data.GRPC_OPTIONS
    ) as channel:
        client = webTransferApi_pb2_grpc.WebTransferApiStub(channel)
        response = client.makeWebTransfer(request, metadata=metadata)
        return response


def create_metadata():
    """Создает метаданные для gRPC запроса"""
    return (
        ('refid', str(uuid.uuid1())),
        ('sessionkey', app_data.SESSION_KEY),
        ('device-type', app_data.DEVICE_TYPE),
        ('user-agent-c', app_data.USER_AGENT),
    )


def confirm_operation(operation_id: str, otp: str = app_data.OTP_CODE):
    """
    Подтверждение операции через OTP
    
    Args:
        operation_id: ID операции для подтверждения
        otp: OTP код (по умолчанию из data.py)
    
    Returns:
        Response от сервера
    """
    metadata = create_metadata()
    
    confirm_data = {
        "operationId": operation_id,
        "otp": otp
    }
    
    return make_grpc_request(app_data.CODE_CONFIRM_TRANSFER, confirm_data, metadata)


def assert_success(response, error_message: str = "Запрос завершился с ошибкой"):
    """
    Проверка успешности ответа от сервера
    
    Args:
        response: Ответ от сервера
        error_message: Сообщение об ошибке
    """
    assert response is not None, f"{error_message}: Ответ не получен"
    assert response.success is True, f"{error_message}: {response.error}"


# Экспорт для использования в других файлах
__all__ = [
    'webTransferApi_pb2', 
    'webTransferApi_pb2_grpc',
    'make_grpc_request',
    'create_metadata',
    'confirm_operation',
    'assert_success'
]

