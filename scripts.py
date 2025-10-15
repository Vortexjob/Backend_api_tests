import uuid
import grpc
import json
from conftest import webTransferApi_pb2, webTransferApi_pb2_grpc
from data import (
    GRPC_SERVER_URL, GRPC_OPTIONS,
    CODE_CREATE_TRANSFER, CODE_CONFIRM_TRANSFER,
    DEVICE_TYPE, USER_AGENT, SESSION_KEY,
    ACCOUNT_ID_DEBIT, ACCOUNT_CREDIT, ACCOUNT_CREDIT_PROP_TYPE,
    AMOUNT, PAYMENT_PURPOSE, OTP_CODE
)


# ===== КЛАСС 1: СОЗДАНИЕ ПЕРЕВОДА =====
class CreateTransferRequest:
    """Класс для создания банковского перевода"""
    
    def __init__(self):
        self.operation_id = str(uuid.uuid1())
        
    def _build_metadata(self):
        """Построение метаданных для запроса"""
        return (
            ('refid', str(uuid.uuid1())),
            ('sessionkey', SESSION_KEY),
            ('device-type', DEVICE_TYPE),
            ('user-agent-c', USER_AGENT),
        )
    
    def _build_transfer_data(self):
        """Построение данных для перевода"""
        return {
            "operationId": self.operation_id,
            "accountIdDebit": ACCOUNT_ID_DEBIT,
            "accountCreditPropValue": ACCOUNT_CREDIT,
            "accountCreditPropType": ACCOUNT_CREDIT_PROP_TYPE, 
            "paymentPurpose": PAYMENT_PURPOSE,
            "amountDebit": AMOUNT,
        }
    
    def execute(self):
        """Выполнение запроса на создание перевода"""
        metadata = self._build_metadata()
        transfer_data = self._build_transfer_data()
        
        request = webTransferApi_pb2.IncomingWebTransfer(
            code=CODE_CREATE_TRANSFER,
            data=json.dumps(transfer_data)
        )
        
        print(f"\n=== ЗАПРОС 1: Создание перевода ===")
        print(f"Operation ID: {self.operation_id}")
        print(f"Данные: {transfer_data}")
        
        with grpc.secure_channel(
                GRPC_SERVER_URL,
                grpc.ssl_channel_credentials(),
                options=GRPC_OPTIONS
        ) as channel:
            client = webTransferApi_pb2_grpc.WebTransferApiStub(channel)
            response = client.makeWebTransfer(request, metadata=metadata)
            print(f"Ответ: {response}")
            return response


# ===== КЛАСС 2: ПОДТВЕРЖДЕНИЕ ПЕРЕВОДА =====
class ConfirmTransferRequest:
    """Класс для подтверждения банковского перевода"""
    
    def __init__(self, operation_id: str):
        self.operation_id = operation_id
        
    def _build_metadata(self):
        """Построение метаданных для запроса"""
        return (
            ('refid', str(uuid.uuid1())),
            ('sessionkey', SESSION_KEY),
            ('device-type', DEVICE_TYPE),
            ('user-agent-c', USER_AGENT),
        )
    
    def _build_confirm_data(self):
        """Построение данных для подтверждения"""
        return {
            "operationId": self.operation_id,
            "otp": OTP_CODE
        }
    
    def execute(self):
        """Выполнение запроса на подтверждение перевода"""
        metadata = self._build_metadata()
        confirm_data = self._build_confirm_data()
        
        request = webTransferApi_pb2.IncomingWebTransfer(
            code=CODE_CONFIRM_TRANSFER,
            data=json.dumps(confirm_data)
        )

        print(f"\n=== ЗАПРОС 2: Подтверждение перевода ===")
        print(f"Operation ID: {self.operation_id}")
        print(f"Данные: {confirm_data}")
        
        with grpc.secure_channel(
                GRPC_SERVER_URL,
                grpc.ssl_channel_credentials(),
                options=GRPC_OPTIONS
        ) as channel:
            client = webTransferApi_pb2_grpc.WebTransferApiStub(channel)
            response = client.makeWebTransfer(request, metadata=metadata)
            print(f"Ответ: {response}")
            return response


# Классы можно импортировать и использовать в других модулях и тестах

    