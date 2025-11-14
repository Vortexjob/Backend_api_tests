import uuid
import json
import time
import pytest
from datetime import datetime

from conftest import make_grpc_request, assert_success
from data import CODE_MAKE_SHOP_OPERATION, CODE_CONFIRM_TRANSFER
from database_collector import DatabaseConfig, DataCollector


PARTIAL_REPAYMENT_TEST_DATA = [
    {
        "test_name": "Partial early repayment – exchange",
        "account_debit_id": 17735,
        "loan_id": 948139,
        "estimated_maturity_date": "2024-12-31",
        "loan_principal": "10000",
        "accrued_interest": "0",
        "due_amount": "11",
        "reason_for_repayment": "Early repayment via API",
        "user_id": 26,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    },
    {
        "test_name": "Partial early repayment – no exchange",
        "account_debit_id": 2799,
        "loan_id": 948139,
        "estimated_maturity_date": "2024-12-31",
        "loan_principal": "10000",
        "accrued_interest": "0",
        "due_amount": "11",
        "reason_for_repayment": "Early repayment via API",
        "user_id": 26,
        "device_type": "ios",
        "user_agent": "12; iPhone12MaxProDan"
    }
]


def _get_session_key(user_id: int) -> str:
    config = DatabaseConfig()
    collector = DataCollector(config)
    session_key = collector.get_valid_session_key(user_id=user_id)
    if not session_key:
        pytest.skip(f"Нет валидного session_key для user_id={user_id}")
    return session_key


def _build_metadata(session_key: str, device_type: str, user_agent: str):
    return (
        ("refid", str(uuid.uuid1())),
        ("sessionkey", session_key),
        ("device-type", device_type),
        ("user-agent-c", user_agent),
    )


def _confirm_operation(operation_id: str, metadata: tuple, otp: str = "111111"):
    confirm_payload = {
        "operationId": operation_id,
        "otp": otp,
    }
    response = make_grpc_request(CODE_CONFIRM_TRANSFER, confirm_payload, metadata)
    assert_success(response, "Подтверждение частичного погашения кредита")
    return response


@pytest.mark.parametrize("test_data", PARTIAL_REPAYMENT_TEST_DATA)
def test_partial_early_loan_repayment(test_data):
    test_name = test_data["test_name"]
    user_id = test_data["user_id"]

    print(f"\n=== {test_name} ===")
    print(f"Получаем session_key для user_id={user_id}")

    session_key = _get_session_key(user_id=user_id)
    metadata = _build_metadata(session_key, test_data["device_type"], test_data["user_agent"])

    operation_id = str(uuid.uuid1())
    repayment_payload = {
        "operationId": operation_id,
        "productType": "makePartialEarlyLoanRepayment",
        "data": {
            "accountDebitId": test_data["account_debit_id"],
            "loanId": test_data["loan_id"],
            "estimatedMaturityDate": test_data["estimated_maturity_date"],
            "loanPrincipal": test_data["loan_principal"],
            "accruedInterest": test_data["accrued_interest"],
            "dueAmount": test_data["due_amount"],
            "reasonForRepayment": test_data["reason_for_repayment"],
        },
    }

    print(f"Отправляем запрос MAKE_SHOP_OPERATION с operationId={operation_id}")
    create_response = make_grpc_request(CODE_MAKE_SHOP_OPERATION, repayment_payload, metadata)
    print(f"Ответ на создание: {create_response}")

    assert_success(create_response, "Создание частичного досрочного погашения")

    # Парсим данные ответа
    operation_data = None
    if create_response.data:
        try:
            parsed = json.loads(create_response.data)
            operation_data = parsed.get("operationData")
            needs_otp = parsed.get("needsOtp")
            print(f"Результат операции: {parsed}")
            assert parsed.get("operationId") == operation_id, "operationId в ответе не совпадает"
            assert needs_otp is True, "Ожидаем, что операция потребует OTP"
        except (ValueError, TypeError) as err:
            pytest.fail(f"Не удалось распарсить тело ответа: {err}")

    # Небольшая пауза перед подтверждением
    time.sleep(2)

    print("Подтверждаем операцию OTP...")
    confirm_response = _confirm_operation(operation_id, metadata)
    print(f"Ответ на подтверждение: {confirm_response}")

    # Дополнительные проверки по operationData
    if operation_data:
        expected_fields = [
            "accountIdDebit",
            "dueAmount",
            "estimatedMaturityDate",
            "loanPrincipal",
            "accruedInterest",
            "loanId",
            "loanNumber",
            "amountDebit",
            "comissionAmount",
            "commissionRateCcy",
            "accountDebitInfoCcy",
        ]
        missing = [field for field in expected_fields if field not in operation_data]
        assert not missing, f"В operationData отсутствуют поля: {missing}"

        assert str(operation_data["accountIdDebit"]) == str(test_data["account_debit_id"])
        assert str(operation_data["dueAmount"]) == str(test_data["due_amount"])
        assert str(operation_data["loanId"]) == str(test_data["loan_id"])

    print(f"=== ✅ {test_name} выполнен успешно ===\n")


def pytest_sessionfinish(session, exitstatus):
    timestamp = datetime.now().isoformat()
    print(f"\n[{timestamp}] Завершение сессии pytest. Статус: {exitstatus}")

