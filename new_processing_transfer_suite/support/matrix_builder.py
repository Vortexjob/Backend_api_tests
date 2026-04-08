from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from functools import lru_cache
from pathlib import Path
from typing import Any

from support.cases import validate_cases
from support.database import DataCollector, DatabaseConfig

SUITE_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = SUITE_ROOT / "data"
MASTER_DIR = DATA_ROOT / "master"
MASTER_CASES_PATH = MASTER_DIR / "all_cases.json"
COVERAGE_INDEX_PATH = MASTER_DIR / "active_card_case_names.md"

INTERNAL_DIR = DATA_ROOT / "bank_client_transfer"
OWN_DIR = DATA_ROOT / "own_accounts_transfer"
OTHER_BANK_DIR = DATA_ROOT / "other_bank_transfer"
QR_DIR = DATA_ROOT / "qr_payment"

RUNTIME_OUTPUTS: tuple[Path, ...] = (
    INTERNAL_DIR / "card_to_card.json",
    INTERNAL_DIR / "account_to_card.json",
    INTERNAL_DIR / "card_to_account.json",
    INTERNAL_DIR / "account_to_account.json",
    OWN_DIR / "same_currency.json",
    OWN_DIR / "fx.json",
    OTHER_BANK_DIR / "clearing.json",
    OTHER_BANK_DIR / "gross.json",
    QR_DIR / "static_qr.json",
)

CARD_PROCESSORS = {"COMPASS", "IPC"}
CANONICAL_IPC_CARD_ACCOUNTS = {
    ("00575749", "1285110000646290"),
}
COMPASS_ONLY_CUSTOMERS = {
    "00909472",
}
DEFAULT_SELECTION_LIMIT = 2
POSITIVE_SIGNAL_MAX_AGE_DAYS = 90
SELECTION_SIGNAL_RANK = {
    "exact_history": 3,
    "same_family_history": 2,
    "forced_matrix": 1,
    None: 0,
}
QR_DIRECT_MATCH_FIELDS = (
    "qrMerchantProviderId",
    "qrServiceId",
    "qrType",
    "qrAccount",
    "qrCcy",
)
REQUEST_RECIPIENT_ACCOUNT_SENTINEL = "__RECIPIENT_ACCOUNT_NO__"
REQUEST_RECIPIENT_CUSTOMER_SENTINEL = "__RECIPIENT_CUSTOMER_NO__"
SECTION_TITLES = {
    "MAKE_BANK_CLIENT_TRANSFER": "Bank Client Transfer",
    "MAKE_OWN_ACCOUNTS_TRANSFER": "Own Accounts Transfer",
    "MAKE_OTHER_BANK_TRANSFER": "Other Bank Transfer",
    "MAKE_QR_PAYMENT": "QR Payment",
}


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _write_json(path: Path, payload: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    current = path.read_text(encoding="utf-8") if path.exists() else None
    if current != serialized:
        path.write_text(serialized, encoding="utf-8")


def _write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    current = path.read_text(encoding="utf-8") if path.exists() else None
    if current != payload:
        path.write_text(payload, encoding="utf-8")


def _deep_copy(value: Any) -> Any:
    return json.loads(json.dumps(value, ensure_ascii=False, default=str))


def _slug(value: Any) -> str:
    prepared = str(value or "").strip().lower()
    return (
        prepared.replace(" ", "_")
        .replace("-", "_")
        .replace("/", "_")
        .replace(">", "_")
        .replace("(", "")
        .replace(")", "")
    )


def _load_master_cases() -> list[dict[str, Any]]:
    if not MASTER_CASES_PATH.exists():
        raise FileNotFoundError(
            f"Master case file not found: {MASTER_CASES_PATH}. "
            "Create data/master/all_cases.json before building runtime matrices."
        )

    payload = _load_json(MASTER_CASES_PATH)
    if not isinstance(payload, list):
        raise ValueError(f"Master case file must contain a JSON array. source={MASTER_CASES_PATH}")

    return validate_cases(payload, source=MASTER_CASES_PATH)


def _is_template_case(case: dict[str, Any]) -> bool:
    return isinstance(case.get("sender_selector"), dict) or isinstance(case.get("recipient_selector"), dict)


def _digits_only(value: str | None) -> str:
    return "".join(char for char in value or "" if char.isdigit())


def _extract_visible_pan_edges(masked_pan: str | None) -> tuple[str, str]:
    prepared = "".join(char for char in masked_pan or "" if char.isdigit() or char == "*")

    prefix: list[str] = []
    for char in prepared:
        if char.isdigit():
            prefix.append(char)
            continue
        break

    suffix: list[str] = []
    for char in reversed(prepared):
        if char.isdigit():
            suffix.append(char)
            continue
        break

    return "".join(prefix), "".join(reversed(suffix))


def _pan_hint_matches(masked_pan: str | None, hint: str | None) -> bool:
    masked_digits = _digits_only(masked_pan)
    hint_digits = _digits_only(hint)
    if not hint_digits:
        return False
    if not masked_digits and "*" not in (masked_pan or ""):
        return False

    prefix, suffix = _extract_visible_pan_edges(masked_pan)
    if prefix and not hint_digits.startswith(prefix):
        return False
    if suffix and not hint_digits.endswith(suffix):
        return False

    if "*" not in (masked_pan or "") and masked_digits:
        return masked_digits == hint_digits
    return True


def _parse_decimal(value: Decimal | str | int | float | None) -> Decimal:
    if value is None:
        return Decimal("0")
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _is_recent_enough(value: str | None, *, days: int = POSITIVE_SIGNAL_MAX_AGE_DAYS) -> bool:
    timestamp = _parse_timestamp(value)
    if timestamp is None:
        return False
    now = datetime.now(timezone.utc).astimezone(timestamp.tzinfo or timezone.utc)
    return timestamp >= now - timedelta(days=days)


def _party_account_kind(party: dict[str, Any] | None, *, role: str) -> str:
    expected = (party or {}).get("expected") or {}
    account_kind = expected.get("account_kind")
    if account_kind not in {"CARD", "CURRENT"}:
        raise ValueError(
            f"{role} party must define expected.account_kind as CARD or CURRENT. "
            f"party={json.dumps(party, ensure_ascii=False, default=str)}"
        )
    return account_kind


def _party_currency(party: dict[str, Any] | None, *, role: str) -> str:
    expected = (party or {}).get("expected") or {}
    currency = expected.get("currency")
    if not currency:
        raise ValueError(
            f"{role} party must define expected.currency. "
            f"party={json.dumps(party, ensure_ascii=False, default=str)}"
        )
    return str(currency)


def _party_kind_slug(party: dict[str, Any] | None, *, role: str) -> str:
    return "card" if _party_account_kind(party, role=role) == "CARD" else "account"


def _party_processor(party: dict[str, Any] | None) -> str:
    expected = (party or {}).get("expected") or {}
    return str(expected.get("processor") or "NONE")


def _party_is_scoped_card(party: dict[str, Any] | None) -> bool:
    expected = (party or {}).get("expected") or {}
    return expected.get("account_kind") == "CARD" and expected.get("processor") in CARD_PROCESSORS


def _case_is_card_focused(case: dict[str, Any]) -> bool:
    return _party_is_scoped_card(case.get("sender")) or _party_is_scoped_card(case.get("recipient"))


def _success_status(transaction: dict[str, Any]) -> bool:
    return (
        transaction.get("txn_status_internal") == "SUCCESS"
        and transaction.get("txn_status_external") == "SUCCESS"
    )


def _processing_status(transaction: dict[str, Any]) -> bool:
    return (
        transaction.get("txn_status_internal") == "ACCEPTED_NOT_PROCESSED"
        and transaction.get("txn_status_external") == "IN_PROCESS"
    )


def _failure_status(transaction: dict[str, Any]) -> bool:
    return (
        transaction.get("txn_status_internal") == "FAILURE"
        or transaction.get("txn_status_external") == "FAILURE"
    )


def _is_transferish_transaction(transaction: dict[str, Any]) -> bool:
    txn_code = str(transaction.get("txn_code") or "")
    return any(
        marker in txn_code
        for marker in (
            "OTHER_EXCH",
            "OWN_EXC",
            "CLEARING",
            "GROSS",
            "ELQR",
            "SWIFT",
            "GENERIC_PAYMENT",
            "MONEY_TRANSFER",
        )
    )


def _latest_timestamp(transactions: list[dict[str, Any]]) -> str:
    timestamps = [str(item.get("created_at") or "") for item in transactions if item.get("created_at")]
    return max(timestamps) if timestamps else ""


def _latest_transaction(transactions: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not transactions:
        return None
    return max(
        transactions,
        key=lambda item: _parse_timestamp(str(item.get("created_at") or ""))
        or datetime.min.replace(tzinfo=timezone.utc),
    )


def _direct_state_rank(transaction: dict[str, Any] | None) -> int:
    if not transaction:
        return 0
    if _success_status(transaction):
        return 2
    if _processing_status(transaction):
        return 1
    if _failure_status(transaction):
        return -1
    return 0


def _selector_customer_nos(selector: dict[str, Any] | None) -> list[str]:
    if not isinstance(selector, dict):
        return []
    return [str(item) for item in selector.get("customer_nos", []) if item]


def _collect_pool_customer_nos(master_cases: list[dict[str, Any]]) -> list[str]:
    customer_nos: set[str] = set()
    for case in master_cases:
        for selector in (case.get("sender_selector"), case.get("recipient_selector")):
            customer_nos.update(_selector_customer_nos(selector))
            for item in (selector or {}).get("known_cards", []):
                customer_no = str(item.get("customer_no") or "")
                if customer_no:
                    customer_nos.add(customer_no)
        for party in (case.get("sender"), case.get("recipient")):
            if isinstance(party, dict) and party.get("customer_no"):
                customer_nos.add(str(party["customer_no"]))
    return sorted(customer_nos)


def _build_pool(master_cases: list[dict[str, Any]]) -> dict[str, Any]:
    collector = DataCollector(DatabaseConfig.from_env())
    customer_nos = _collect_pool_customer_nos(master_cases)
    accounts = collector.get_accounts_by_customer_nos(customer_nos)
    sessions = collector.get_valid_session_records_by_customer_nos(customer_nos)
    user_ids = collector.get_user_ids_by_customer_nos(customer_nos)
    card_account_nos = sorted({account["account_no"] for account in accounts if account.get("account_kind") == "CARD"})
    card_numbers_by_account = collector.get_recent_card_numbers_by_account_nos(card_account_nos)

    accounts_by_customer: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for account in accounts:
        accounts_by_customer[account["customer_no"]].append(account)

    return {
        "collector": collector,
        "accounts": accounts,
        "accounts_by_customer": dict(accounts_by_customer),
        "session_records_by_customer": sessions,
        "user_ids_by_customer": user_ids,
        "card_numbers_by_account": card_numbers_by_account,
    }


def _account_class_matches(account: dict[str, Any], prefixes: list[str]) -> bool:
    if not prefixes:
        return True
    account_class = str(account.get("account_class") or "")
    return any(account_class.startswith(prefix) for prefix in prefixes)


def _account_allowed_by_active_pool_rules(account: dict[str, Any]) -> bool:
    customer_no = str(account.get("customer_no") or "")
    account_no = str(account.get("account_no") or "")
    account_kind = str(account.get("account_kind") or "")
    processor = str(account.get("processor") or "")

    if account_kind == "CARD" and processor == "IPC":
        return (customer_no, account_no) in CANONICAL_IPC_CARD_ACCOUNTS

    if customer_no in COMPASS_ONLY_CUSTOMERS:
        return account_kind == "CARD" and processor == "COMPASS"

    return True


def _selector_matches_account(
    account: dict[str, Any],
    selector: dict[str, Any],
    *,
    pool: dict[str, Any],
    role: str,
) -> bool:
    if not _account_allowed_by_active_pool_rules(account):
        return False

    customer_nos = _selector_customer_nos(selector)
    if customer_nos and account["customer_no"] not in customer_nos:
        return False

    prefixes = [str(prefix) for prefix in selector.get("account_class_prefixes", []) if prefix]
    if prefixes and not _account_class_matches(account, prefixes):
        return False

    account_kind = selector.get("account_kind")
    if account_kind and account.get("account_kind") != account_kind:
        return False

    processors = [str(item) for item in selector.get("processors", []) if item]
    if processors and account.get("processor") not in processors:
        return False

    currencies = [str(item) for item in selector.get("currencies", []) if item]
    if currencies and account.get("ccy") not in currencies:
        return False

    card_systems = [str(item) for item in selector.get("card_systems", []) if item]
    if card_systems and account.get("card_system") not in card_systems:
        return False

    if selector.get("require_valid_session") and account["customer_no"] not in pool["session_records_by_customer"]:
        return False

    if account.get("record_stat") != "O":
        return False
    if account.get("ac_stat_dormant"):
        return False
    if account.get("ac_stat_frozen"):
        return False

    if role == "sender":
        if account.get("ac_stat_no_dr"):
            return False
        if account.get("ac_stat_block"):
            return False
        min_balance = selector.get("min_balance")
        if min_balance is not None and _parse_decimal(account.get("acy_withdrawable_bal")) < _parse_decimal(min_balance):
            return False
    else:
        if account.get("ac_stat_no_cr"):
            return False

    return True


def _selector_known_cards_map(selector: dict[str, Any]) -> dict[tuple[str, str], list[dict[str, str]]]:
    result: dict[tuple[str, str], list[dict[str, str]]] = {}
    for item in selector.get("known_cards", []):
        customer_no = str(item.get("customer_no") or "")
        account_no = str(item.get("account_no") or "")
        card_no = str(item.get("card_no") or "")
        if not customer_no or not account_no or not card_no:
            continue
        result.setdefault((customer_no, account_no), []).append(
            {
                "card_no": card_no,
                "card_mask": item.get("card_mask"),
                "preferred": bool(item.get("preferred")),
            }
        )
    return result


def _base_party_from_account(account: dict[str, Any]) -> dict[str, Any]:
    party = {
        "customer_no": account["customer_no"],
        "account_no": account["account_no"],
        "expected": {
            "currency": account["ccy"],
            "account_kind": account["account_kind"],
            "processor": account["processor"],
        },
    }
    if account.get("account_kind") == "CARD":
        party["expected"]["card_system"] = account.get("card_system") or "UNKNOWN"
        if account.get("ipc_card_pan"):
            party["card_mask"] = account["ipc_card_pan"]
    return party


def _resolve_card_variants_for_account(
    account: dict[str, Any],
    selector: dict[str, Any],
    *,
    pool: dict[str, Any],
) -> list[dict[str, Any]]:
    base_party = _base_party_from_account(account)
    known_cards = _selector_known_cards_map(selector).get((account["customer_no"], account["account_no"]), [])
    require_card_number = bool(selector.get("require_card_number"))

    if not require_card_number:
        if known_cards and not base_party.get("card_mask"):
            base_party["card_mask"] = known_cards[0].get("card_mask") or base_party.get("card_mask")
        return [base_party]

    variants: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for item in known_cards:
        card_no = item["card_no"]
        card_mask = item.get("card_mask")
        if card_mask is None:
            card_mask = base_party.get("card_mask")
        if card_mask and not _pan_hint_matches(card_mask, card_no):
            continue
        party = _deep_copy(base_party)
        party["card_no"] = card_no
        if item.get("preferred"):
            party["preferred_card_used"] = True
        if card_mask:
            party["card_mask"] = card_mask
        signature = (party["account_no"], card_no)
        if signature not in seen:
            seen.add(signature)
            variants.append(party)

    account_mask = base_party.get("card_mask")
    if account_mask:
        for card_no in pool["card_numbers_by_account"].get(account["account_no"], []):
            if not _pan_hint_matches(account_mask, card_no):
                continue
            party = _deep_copy(base_party)
            party["card_no"] = card_no
            signature = (party["account_no"], card_no)
            if signature not in seen:
                seen.add(signature)
                variants.append(party)

    return variants


def _resolve_selector_parties(
    selector: dict[str, Any],
    *,
    pool: dict[str, Any],
    role: str,
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    customer_nos = _selector_customer_nos(selector)
    if customer_nos:
        accounts: list[dict[str, Any]] = []
        for customer_no in customer_nos:
            accounts.extend(pool["accounts_by_customer"].get(customer_no, []))
    else:
        accounts = list(pool["accounts"])

    filtered_accounts = [
        account for account in accounts if _selector_matches_account(account, selector, pool=pool, role=role)
    ]
    prefer_default = bool(selector.get("prefer_default"))
    filtered_accounts.sort(
        key=lambda account: (
            int(bool(account.get("is_default"))) if prefer_default else 0,
            _parse_decimal(account.get("acy_withdrawable_bal")),
            account["customer_no"],
            account["account_no"],
            account.get("ipc_card_pan") or "",
        ),
        reverse=True,
    )

    parties: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for account in filtered_accounts:
        variants = _resolve_card_variants_for_account(account, selector, pool=pool)
        for party in variants:
            parties.append((party, account))
    return parties


def _normalize_explicit_party(party: dict[str, Any]) -> dict[str, Any]:
    return _deep_copy(party)


def _party_route_fragment(party: dict[str, Any] | None) -> str:
    if not party:
        return "NONE"
    expected = party.get("expected") or {}
    kind = expected.get("account_kind") or "UNKNOWN"
    processor = expected.get("processor") or "NONE"
    currency = expected.get("currency") or "UNKNOWN"
    if kind == "CARD":
        card_system = expected.get("card_system") or "UNKNOWN"
        return f"CARD:{processor}:{card_system}:{currency}"
    return f"CURRENT:{processor}:{currency}"


def _build_route_key(template: dict[str, Any], sender: dict[str, Any], recipient: dict[str, Any] | None) -> str:
    operation_code = template["operation"]["code"]
    request = template["request"]

    if operation_code == "MAKE_BANK_CLIENT_TRANSFER":
        prop_type = str(request.get("accountCreditPropType") or "UNKNOWN")
        return f"{operation_code}:{prop_type}:{_party_route_fragment(sender)}->{_party_route_fragment(recipient)}"

    if operation_code == "MAKE_OWN_ACCOUNTS_TRANSFER":
        mode = "SAME_CCY"
        if recipient is not None and sender["expected"]["currency"] != recipient["expected"]["currency"]:
            mode = "FX"
        return f"{operation_code}:{mode}:{_party_route_fragment(sender)}->{_party_route_fragment(recipient)}"

    if operation_code == "MAKE_OTHER_BANK_TRANSFER":
        mode = "CLEARING" if request.get("transferClearingGross") == "C" else "GROSS"
        sender_currency = sender["expected"]["currency"]
        return f"{operation_code}:{mode}:{_party_route_fragment(sender)}->EXTERNAL:{sender_currency}"

    if operation_code == "MAKE_QR_PAYMENT":
        provider = str(request.get("qrMerchantProviderId") or "qr").replace(".", "_").upper()
        qr_type = str(request.get("qrType") or "UNKNOWN").upper()
        service_id = str(request.get("qrServiceId") or "UNKNOWN")
        if recipient:
            return f"{operation_code}:{provider}_{qr_type}_{service_id}:{_party_route_fragment(sender)}->{_party_route_fragment(recipient)}"
        qr_ccy = str(request.get("qrCcy") or sender["expected"]["currency"])
        return f"{operation_code}:{provider}_{qr_type}_{service_id}:{_party_route_fragment(sender)}->QR:{qr_ccy}"

    raise ValueError(f"Unsupported template operation.code={operation_code}")


def _party_case_token(party: dict[str, Any]) -> str:
    expected = party["expected"]
    return (
        f"{expected['currency'].lower()}_{expected['account_kind'].lower()}_{expected['processor'].lower()}_"
        f"c{party['customer_no']}_a{party['account_no'][-4:]}"
    )


def _build_case_name(template: dict[str, Any], sender: dict[str, Any], recipient: dict[str, Any] | None) -> str:
    base = template["name"]
    sender_token = _party_case_token(sender)
    if recipient is None:
        return f"{base}_{sender_token}"
    return f"{base}_{sender_token}_to_{_party_case_token(recipient)}"


def _apply_request_party_placeholders(request: dict[str, Any], recipient_party: dict[str, Any] | None) -> dict[str, Any]:
    if not recipient_party:
        return request

    normalized: dict[str, Any] = {}
    for key, value in request.items():
        if value == REQUEST_RECIPIENT_ACCOUNT_SENTINEL:
            normalized[key] = recipient_party["account_no"]
        elif value == REQUEST_RECIPIENT_CUSTOMER_SENTINEL:
            normalized[key] = recipient_party["customer_no"]
        else:
            normalized[key] = value
    return normalized


def _template_coverage(template: dict[str, Any]) -> dict[str, Any]:
    return _deep_copy(template.get("coverage") or {})


def _template_force_active(template: dict[str, Any]) -> bool:
    return bool(template.get("force_active"))


def _template_preferred_card_signatures(template: dict[str, Any]) -> set[tuple[str, str, str]]:
    result: set[tuple[str, str, str]] = set()
    for item in template.get("preferred_card_numbers", []):
        customer_no = str(item.get("customer_no") or "")
        account_no = str(item.get("account_no") or "")
        card_no = str(item.get("card_no") or "")
        if customer_no and account_no and card_no:
            result.add((customer_no, account_no, card_no))
    return result


def _coverage_bucket_from_template(template: dict[str, Any]) -> str:
    coverage = _template_coverage(template)
    parts = [
        coverage.get("family"),
        coverage.get("transfer_mode"),
        coverage.get("shape"),
        coverage.get("provider_relation"),
        coverage.get("credit_addressing_mode"),
    ]
    normalized = [_slug(part) for part in parts if part]
    return "_".join(normalized) if normalized else _slug(template["name"])


def _build_generated_case(
    template: dict[str, Any],
    *,
    sender_party: dict[str, Any],
    sender_account: dict[str, Any] | None,
    recipient_party: dict[str, Any] | None,
    recipient_account: dict[str, Any] | None,
) -> dict[str, Any]:
    request_payload = _apply_request_party_placeholders(_deep_copy(template["request"]), recipient_party)
    preferred_card_signatures = _template_preferred_card_signatures(template)
    preferred_card_used = any(
        bool(party and party.get("preferred_card_used"))
        or (
            party is not None
            and party.get("card_no")
            and (party["customer_no"], party["account_no"], party["card_no"]) in preferred_card_signatures
        )
        for party in (sender_party, recipient_party)
    )
    coverage_bucket = _coverage_bucket_from_template(template)
    case = {
        "name": _build_case_name(template, sender_party, recipient_party),
        "enabled": True,
        "route_key": _build_route_key(template, sender_party, recipient_party),
        "operation": _deep_copy(template["operation"]),
        "sender": _normalize_explicit_party(sender_party),
        "request": request_payload,
        "verification": _deep_copy(template["verification"]),
        "selection_limit": int(template.get("selection_limit", DEFAULT_SELECTION_LIMIT)),
        "force_active": _template_force_active(template),
        "coverage_bucket": coverage_bucket,
        "preferred_card_used": preferred_card_used,
        "selection_metadata": {
            "template_name": template["name"],
            "sender_is_default": bool(sender_account.get("is_default")) if sender_account else False,
            "recipient_is_default": bool(recipient_account.get("is_default")) if recipient_account else False,
            "coverage": _template_coverage(template),
            "coverage_bucket": coverage_bucket,
            "force_active": _template_force_active(template),
            "preferred_card_used": preferred_card_used,
        },
    }
    if recipient_party is not None:
        case["recipient"] = _normalize_explicit_party(recipient_party)

    for key in ("device_type", "user_agent", "otp", "skip_on_create_error_codes"):
        if key in template:
            case[key] = _deep_copy(template[key])
    return case


def _materialize_template_case(template: dict[str, Any], *, pool: dict[str, Any]) -> list[dict[str, Any]]:
    if isinstance(template.get("sender_selector"), dict):
        sender_variants = _resolve_selector_parties(template["sender_selector"], pool=pool, role="sender")
    elif isinstance(template.get("sender"), dict):
        sender_variants = [(_normalize_explicit_party(template["sender"]), None)]
    else:
        sender_variants = []

    if isinstance(template.get("recipient_selector"), dict):
        recipient_variants: list[tuple[dict[str, Any] | None, dict[str, Any] | None]] = _resolve_selector_parties(
            template["recipient_selector"],
            pool=pool,
            role="recipient",
        )
    elif isinstance(template.get("recipient"), dict):
        recipient_variants = [(_normalize_explicit_party(template["recipient"]), None)]
    else:
        recipient_variants = [(None, None)]

    allow_same_customer = bool(template.get("allow_same_customer"))
    match_currency = bool(template.get("match_currency"))
    different_currency = bool(template.get("different_currency"))
    request = template.get("request") or {}
    operation_code = template["operation"]["code"]
    requires_same_customer = operation_code == "MAKE_OWN_ACCOUNTS_TRANSFER"
    expected_provider_relation = str((_template_coverage(template).get("provider_relation") or "")).lower()

    generated: list[dict[str, Any]] = []
    seen_case_names: set[str] = set()
    for sender_party, sender_account in sender_variants:
        for recipient_party, recipient_account in recipient_variants:
            if recipient_party is not None:
                if requires_same_customer and sender_party["customer_no"] != recipient_party["customer_no"]:
                    continue
                if not allow_same_customer and sender_party["customer_no"] == recipient_party["customer_no"]:
                    continue
                if sender_party["account_no"] == recipient_party["account_no"]:
                    continue
                if match_currency and sender_party["expected"]["currency"] != recipient_party["expected"]["currency"]:
                    continue
                if different_currency and sender_party["expected"]["currency"] == recipient_party["expected"]["currency"]:
                    continue
                if expected_provider_relation in {"same_provider", "cross_provider"}:
                    sender_processor = _party_processor(sender_party)
                    recipient_processor = _party_processor(recipient_party)
                    if sender_processor not in CARD_PROCESSORS or recipient_processor not in CARD_PROCESSORS:
                        continue
                    providers_match = sender_processor == recipient_processor
                    if expected_provider_relation == "same_provider" and not providers_match:
                        continue
                    if expected_provider_relation == "cross_provider" and providers_match:
                        continue

            if operation_code == "MAKE_BANK_CLIENT_TRANSFER" and request.get("accountCreditPropType") == "CARD_NO":
                if recipient_party is None or not recipient_party.get("card_no"):
                    continue

            generated_case = _build_generated_case(
                template,
                sender_party=sender_party,
                sender_account=sender_account,
                recipient_party=recipient_party,
                recipient_account=recipient_account,
            )
            if generated_case["name"] in seen_case_names:
                continue
            seen_case_names.add(generated_case["name"])
            generated.append(generated_case)

    return generated


def _extract_qr_request_data(transaction: dict[str, Any]) -> dict[str, Any]:
    additional_data = transaction.get("additional_data") or {}
    qr_request = additional_data.get("qrRequestData") or additional_data
    return qr_request if isinstance(qr_request, dict) else {}


def _txn_family_matches_case(transaction: dict[str, Any], case: dict[str, Any]) -> bool:
    txn_code = str(transaction.get("txn_code") or "")
    operation_code = case["operation"]["code"]

    if operation_code == "MAKE_BANK_CLIENT_TRANSFER":
        if "OTHER" not in txn_code:
            return False
        prop_type = case["request"].get("accountCreditPropType")
        if prop_type and transaction.get("account_credit_prop_type"):
            return transaction.get("account_credit_prop_type") == prop_type
        return True

    if operation_code == "MAKE_OWN_ACCOUNTS_TRANSFER":
        if "OWN" not in txn_code:
            return False
        sender_currency = case["sender"]["expected"]["currency"]
        recipient_currency = (case.get("recipient") or {}).get("expected", {}).get("currency")
        if sender_currency and recipient_currency and sender_currency != recipient_currency:
            return "EXCY" in txn_code
        return "EXCN" in txn_code or "OWN" in txn_code

    if operation_code == "MAKE_OTHER_BANK_TRANSFER":
        transfer_mode = case["request"].get("transferClearingGross")
        if transfer_mode == "C":
            return "CLEARING" in txn_code
        if transfer_mode == "G":
            return "GROSS" in txn_code
        return False

    if operation_code == "MAKE_QR_PAYMENT":
        if "ELQR" not in txn_code:
            return False
        request_service_id = case["request"].get("qrServiceId")
        payment_code = transaction.get("payment_code")
        return not request_service_id or payment_code == request_service_id

    return False


def _txn_matches_operation_family(transaction: dict[str, Any], operation_code: str) -> bool:
    txn_code = str(transaction.get("txn_code") or "")
    if operation_code == "MAKE_BANK_CLIENT_TRANSFER":
        return "OTHER_EXCH" in txn_code
    if operation_code == "MAKE_OWN_ACCOUNTS_TRANSFER":
        return "OWN_EXC" in txn_code or "_OWN_" in txn_code
    if operation_code == "MAKE_QR_PAYMENT":
        return "ELQR_OUTGOING" in txn_code
    if operation_code == "MAKE_OTHER_BANK_TRANSFER":
        return "CLEARING" in txn_code or "GROSS" in txn_code
    return False


def _txn_matches_direct(transaction: dict[str, Any], case: dict[str, Any]) -> bool:
    if not _txn_family_matches_case(transaction, case):
        return False

    sender = case.get("sender") or {}
    if sender.get("account_no") and transaction.get("account_debit_no") != sender["account_no"]:
        return False

    operation_code = case["operation"]["code"]
    recipient = case.get("recipient") or {}

    if operation_code == "MAKE_QR_PAYMENT":
        request = case["request"]
        qr_request_data = _extract_qr_request_data(transaction)
        for field_name in QR_DIRECT_MATCH_FIELDS:
            expected_value = request.get(field_name)
            if expected_value is None:
                continue
            if qr_request_data.get(field_name) != expected_value:
                return False
        if recipient.get("account_no") and transaction.get("account_credit_no"):
            return transaction.get("account_credit_no") == recipient["account_no"]
        return True

    if recipient.get("account_no"):
        return transaction.get("account_credit_no") == recipient["account_no"]

    if operation_code == "MAKE_OTHER_BANK_TRANSFER":
        request = case["request"]
        if request.get("transferClearingGross") == "C":
            return (
                transaction.get("recipient_bank_bic") == request.get("recipientBankBic")
                and transaction.get("clearing_recipient_acc_no") == request.get("accountCreditNumber")
            )
        if request.get("transferClearingGross") == "G":
            return (
                transaction.get("recipient_bank_swift") == request.get("recipientBankSwift")
                and transaction.get("swift_recipient_acc_no") == request.get("accountCreditNumber")
            )

    return False


def _build_case_selector(cases: list[dict[str, Any]]):
    try:
        collector = DataCollector(DatabaseConfig.from_env())
        sender_account_nos = sorted({case["sender"]["account_no"] for case in cases if case.get("sender")})
        recipient_account_nos = sorted(
            {
                (case.get("recipient") or {}).get("account_no")
                for case in cases
                if (case.get("recipient") or {}).get("account_no")
            }
        )
        transactions = collector.get_recent_transactions_for_case_selection(
            sender_account_nos=sender_account_nos,
            recipient_account_nos=recipient_account_nos,
        )
        balances = collector.get_balances_by_account_nos(sender_account_nos)
        return collector, transactions, balances
    except Exception as exc:  # pragma: no cover - best effort optimization
        print(f"[matrix-builder] case selector fallback without DB ranking: {exc}")
        return None, [], {}


def _latest_recent_positive_timestamp(transactions: list[dict[str, Any]]) -> str:
    positive_transactions = [
        transaction
        for transaction in transactions
        if _success_status(transaction) or _processing_status(transaction)
    ]
    return _latest_timestamp(positive_transactions)


def _derive_selection_signal(case: dict[str, Any], metrics: dict[str, Any]) -> str | None:
    if metrics["direct_positive_recent"]:
        return "exact_history"
    if metrics["route_positive_recent"]:
        return "same_family_history"
    if case.get("force_active") and metrics["family_positive_recent"]:
        return "forced_matrix"
    return None


def _case_score(
    case: dict[str, Any],
    *,
    transactions: list[dict[str, Any]],
    balances: dict[str, Any],
) -> dict[str, Any]:
    sender_account_no = case["sender"]["account_no"]
    operation_code = case["operation"]["code"]
    sender_operation_transactions = [
        transaction
        for transaction in transactions
        if transaction.get("account_debit_no") == sender_account_no
        and _txn_matches_operation_family(transaction, operation_code)
    ]
    sender_route_transactions = [
        transaction
        for transaction in sender_operation_transactions
        if _txn_family_matches_case(transaction, case)
    ]
    direct_transactions = [
        transaction for transaction in sender_route_transactions if _txn_matches_direct(transaction, case)
    ]

    latest_direct_transaction = _latest_transaction(direct_transactions)
    latest_route_transaction = _latest_transaction(sender_route_transactions)
    latest_family_transaction = _latest_transaction(sender_operation_transactions)

    direct_latest_timestamp = str((latest_direct_transaction or {}).get("created_at") or "")
    route_latest_timestamp = str((latest_route_transaction or {}).get("created_at") or "")
    family_latest_timestamp = str((latest_family_transaction or {}).get("created_at") or "")

    direct_success = sum(1 for transaction in direct_transactions if _success_status(transaction))
    direct_processing = sum(1 for transaction in direct_transactions if _processing_status(transaction))
    direct_failures = sum(1 for transaction in direct_transactions if _failure_status(transaction))
    route_success = sum(1 for transaction in sender_route_transactions if _success_status(transaction))
    route_processing = sum(1 for transaction in sender_route_transactions if _processing_status(transaction))
    route_failures = sum(1 for transaction in sender_route_transactions if _failure_status(transaction))
    family_success = sum(1 for transaction in sender_operation_transactions if _success_status(transaction))
    family_processing = sum(1 for transaction in sender_operation_transactions if _processing_status(transaction))
    balance_value = _parse_decimal(balances.get(sender_account_no) or "0")
    selection_metadata = case.get("selection_metadata") or {}

    direct_positive_recent = (
        latest_direct_transaction is not None
        and _is_recent_enough(direct_latest_timestamp)
        and _direct_state_rank(latest_direct_transaction) >= 1
    )
    route_positive_recent = (
        latest_route_transaction is not None
        and _is_recent_enough(route_latest_timestamp)
        and _direct_state_rank(latest_route_transaction) >= 1
    )
    family_positive_recent = bool(family_success or family_processing) and _is_recent_enough(
        _latest_recent_positive_timestamp(sender_operation_transactions)
    )

    signal = _derive_selection_signal(
        case,
        {
            "direct_positive_recent": direct_positive_recent,
            "route_positive_recent": route_positive_recent,
            "family_positive_recent": family_positive_recent,
        },
    )

    return {
        "selection_signal": signal,
        "signal_rank": SELECTION_SIGNAL_RANK[signal],
        "direct_success": direct_success,
        "direct_processing": direct_processing,
        "direct_failures": direct_failures,
        "route_success": route_success,
        "route_processing": route_processing,
        "route_failures": route_failures,
        "family_success": family_success,
        "family_processing": family_processing,
        "direct_latest_timestamp": direct_latest_timestamp,
        "route_latest_timestamp": route_latest_timestamp,
        "family_latest_timestamp": family_latest_timestamp,
        "direct_state_rank": _direct_state_rank(latest_direct_transaction),
        "route_state_rank": _direct_state_rank(latest_route_transaction),
        "family_state_rank": _direct_state_rank(latest_family_transaction),
        "balance_value": balance_value,
        "sender_is_default": int(bool(selection_metadata.get("sender_is_default"))),
        "recipient_is_default": int(bool(selection_metadata.get("recipient_is_default"))),
        "case_name": case["name"],
    }


def _score_has_positive_signal(score: dict[str, Any]) -> bool:
    return score["selection_signal"] is not None


def _selection_group_key(case: dict[str, Any]) -> str:
    return case["route_key"]


def _case_sort_key(score: dict[str, Any]) -> tuple[Any, ...]:
    return (
        score["signal_rank"],
        score["direct_success"],
        score["direct_processing"],
        score["route_success"],
        score["route_processing"],
        score["family_success"],
        score["family_processing"],
        score["direct_latest_timestamp"],
        score["route_latest_timestamp"],
        score["family_latest_timestamp"],
        score["balance_value"],
        score["sender_is_default"],
        score["recipient_is_default"],
        -score["direct_failures"],
        -score["route_failures"],
        score["case_name"],
    )


def _pick_group_cases(scored_cases: list[tuple[dict[str, Any], dict[str, Any]]], limit: int) -> list[dict[str, Any]]:
    eligible_cases = [item for item in scored_cases if _score_has_positive_signal(item[1])]
    if not eligible_cases:
        return []

    ordered = sorted(eligible_cases, key=lambda item: _case_sort_key(item[1]), reverse=True)
    selected: list[dict[str, Any]] = []
    used_senders: set[tuple[str, str]] = set()

    for case, score in ordered:
        sender_signature = (case["sender"]["customer_no"], case["sender"]["account_no"])
        if sender_signature in used_senders:
            continue
        case["selection_signal"] = score["selection_signal"]
        case.setdefault("selection_metadata", {})["selection_signal"] = score["selection_signal"]
        selected.append(case)
        used_senders.add(sender_signature)
        if len(selected) >= limit:
            return selected

    for case, score in ordered:
        if case in selected:
            continue
        case["selection_signal"] = score["selection_signal"]
        case.setdefault("selection_metadata", {})["selection_signal"] = score["selection_signal"]
        selected.append(case)
        if len(selected) >= limit:
            return selected

    return selected


def _prefer_fast_cases(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    _, transactions, balances = _build_case_selector(cases)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for case in cases:
        grouped[_selection_group_key(case)].append(case)

    selected_cases: list[dict[str, Any]] = []
    dropped_route_keys: list[str] = []
    for route_key, grouped_cases in grouped.items():
        scored_cases = [
            (item, _case_score(item, transactions=transactions, balances=balances))
            for item in grouped_cases
        ]
        limit = max(int(item.get("selection_limit", DEFAULT_SELECTION_LIMIT)) for item in grouped_cases)
        chosen = _pick_group_cases(scored_cases, limit)
        if not chosen:
            dropped_route_keys.append(route_key)
            continue
        selected_cases.extend(chosen)

    if dropped_route_keys:
        preview = ", ".join(dropped_route_keys[:5])
        suffix = "" if len(dropped_route_keys) <= 5 else ", ..."
        print(
            "[matrix-builder] dropped "
            f"{len(dropped_route_keys)} route groups without positive history signal: "
            f"{preview}{suffix}"
        )

    return sorted(selected_cases, key=lambda item: item["name"])


def _bank_client_output_path(case: dict[str, Any]) -> Path:
    sender_kind = _party_kind_slug(case.get("sender"), role="sender")
    recipient_kind = _party_kind_slug(case.get("recipient"), role="recipient")
    return INTERNAL_DIR / f"{sender_kind}_to_{recipient_kind}.json"


def _own_accounts_output_path(case: dict[str, Any]) -> Path:
    sender_currency = _party_currency(case.get("sender"), role="sender")
    recipient_currency = _party_currency(case.get("recipient"), role="recipient")
    if sender_currency == recipient_currency:
        return OWN_DIR / "same_currency.json"
    return OWN_DIR / "fx.json"


def _other_bank_output_path(case: dict[str, Any]) -> Path:
    transfer_mode = case["request"].get("transferClearingGross")
    if transfer_mode == "C":
        return OTHER_BANK_DIR / "clearing.json"
    if transfer_mode == "G":
        return OTHER_BANK_DIR / "gross.json"
    raise ValueError(
        f"Unsupported MAKE_OTHER_BANK_TRANSFER transferClearingGross={transfer_mode}. "
        f"case={case['name']}"
    )


def _output_path_for_case(case: dict[str, Any]) -> Path:
    operation_code = case["operation"]["code"]
    if operation_code == "MAKE_BANK_CLIENT_TRANSFER":
        return _bank_client_output_path(case)
    if operation_code == "MAKE_OWN_ACCOUNTS_TRANSFER":
        return _own_accounts_output_path(case)
    if operation_code == "MAKE_OTHER_BANK_TRANSFER":
        return _other_bank_output_path(case)
    if operation_code == "MAKE_QR_PAYMENT":
        return QR_DIR / "static_qr.json"
    raise ValueError(f"Unsupported operation.code={operation_code} in case={case['name']}")


def build_case_matrices() -> dict[Path, list[dict[str, Any]]]:
    master_cases = _load_master_cases()
    outputs: dict[Path, list[dict[str, Any]]] = {path: [] for path in RUNTIME_OUTPUTS}
    enabled_cases: list[dict[str, Any]] = []
    pool = _build_pool(master_cases)

    for case in master_cases:
        if not case["enabled"]:
            continue
        if _is_template_case(case):
            enabled_cases.extend(_materialize_template_case(case, pool=pool))
            continue
        if not _case_is_card_focused(case):
            raise ValueError(
                "Enabled explicit case is outside the card-focused active suite. "
                f"case={case['name']}, route_key={case['route_key']}"
            )
        enabled_cases.append(_deep_copy(case))

    enabled_cases = [case for case in enabled_cases if _case_is_card_focused(case)]
    selected_cases = _prefer_fast_cases(enabled_cases)

    for case in selected_cases:
        output_path = _output_path_for_case(case)
        if output_path not in outputs:
            raise ValueError(f"Unexpected runtime output path for case {case['name']}: {output_path}")
        outputs[output_path].append(case)

    normalized_outputs: dict[Path, list[dict[str, Any]]] = {}
    seen_names: set[str] = set()
    for path, cases in outputs.items():
        ordered_cases = sorted(cases, key=lambda item: item["name"])
        validate_cases(ordered_cases, source=path)
        for case in ordered_cases:
            if case["name"] in seen_names:
                raise ValueError(f"Duplicate generated case name detected across files: {case['name']}")
            seen_names.add(case["name"])
        normalized_outputs[path] = ordered_cases

    return normalized_outputs


def _delete_stale_generated_files(expected_paths: set[Path]) -> None:
    generated_dirs = [INTERNAL_DIR, OWN_DIR, OTHER_BANK_DIR, QR_DIR]
    for directory in generated_dirs:
        if not directory.exists():
            continue
        for candidate in directory.glob("*.json"):
            if candidate not in expected_paths:
                candidate.unlink()


def _percentage(part: int, total: int) -> str:
    if total <= 0:
        return "0.0%"
    return f"{(part / total) * 100:.1f}%"


def _party_report_label(party: dict[str, Any] | None) -> str:
    if not party:
        return "EXTERNAL"
    expected = party.get("expected") or {}
    kind = expected.get("account_kind") or "UNKNOWN"
    processor = expected.get("processor") or "NONE"
    currency = expected.get("currency") or "UNKNOWN"
    if kind == "CARD":
        card_system = expected.get("card_system") or "UNKNOWN"
        return f"CARD/{processor}/{card_system}/{currency}"
    return f"CURRENT/{processor}/{currency}"


def _build_coverage_index(outputs: dict[Path, list[dict[str, Any]]]) -> str:
    active_cases = sorted(
        (case for cases in outputs.values() for case in cases),
        key=lambda item: (item["operation"]["code"], item["name"]),
    )
    total_active = len(active_cases)

    compass_debit = sum(
        1
        for case in active_cases
        if _party_is_scoped_card(case.get("sender")) and case["sender"]["expected"]["processor"] == "COMPASS"
    )
    compass_credit = sum(
        1
        for case in active_cases
        if _party_is_scoped_card(case.get("recipient")) and case["recipient"]["expected"]["processor"] == "COMPASS"
    )
    ipc_debit = sum(
        1
        for case in active_cases
        if _party_is_scoped_card(case.get("sender")) and case["sender"]["expected"]["processor"] == "IPC"
    )
    ipc_credit = sum(
        1
        for case in active_cases
        if _party_is_scoped_card(case.get("recipient")) and case["recipient"]["expected"]["processor"] == "IPC"
    )
    exact_history = sum(1 for case in active_cases if case.get("selection_signal") == "exact_history")
    same_family_history = sum(1 for case in active_cases if case.get("selection_signal") == "same_family_history")
    forced_matrix = sum(1 for case in active_cases if case.get("selection_signal") == "forced_matrix")
    bucket_counts: dict[str, int] = defaultdict(int)
    for case in active_cases:
        bucket_counts[str(case.get("coverage_bucket") or "uncategorized")] += 1

    lines = [
        "# Active Card Case Names",
        "",
        f"Generated from `data/master/{MASTER_CASES_PATH.name}`.",
        "",
        "## Summary",
        f"- Total active cases: {total_active}",
        f"- Compass debit: {compass_debit} ({_percentage(compass_debit, total_active)})",
        f"- Compass credit: {compass_credit} ({_percentage(compass_credit, total_active)})",
        f"- IPC debit: {ipc_debit} ({_percentage(ipc_debit, total_active)})",
        f"- IPC credit: {ipc_credit} ({_percentage(ipc_credit, total_active)})",
        f"- Exact history: {exact_history} ({_percentage(exact_history, total_active)})",
        f"- Same-family history: {same_family_history} ({_percentage(same_family_history, total_active)})",
        f"- Forced matrix: {forced_matrix} ({_percentage(forced_matrix, total_active)})",
    ]

    lines.extend(["", f"## Coverage Buckets ({len(bucket_counts)})"])
    if not bucket_counts:
        lines.append("- none")
    else:
        for bucket, count in sorted(bucket_counts.items(), key=lambda item: (-item[1], item[0])):
            lines.append(f"- `{bucket}`: {count}")

    for operation_code, title in SECTION_TITLES.items():
        section_cases = [case for case in active_cases if case["operation"]["code"] == operation_code]
        lines.extend(["", f"## {title} ({len(section_cases)})"])
        if not section_cases:
            lines.append("- none")
            continue
        for case in section_cases:
            signal = case.get("selection_signal") or "unknown"
            bucket = case.get("coverage_bucket") or "uncategorized"
            sender_label = _party_report_label(case.get("sender"))
            recipient_label = _party_report_label(case.get("recipient"))
            lines.append(
                f"- [{signal}] [`{bucket}`] {sender_label} -> {recipient_label} :: {case['name']}"
            )

    return "\n".join(lines) + "\n"


@lru_cache(maxsize=1)
def ensure_generated_matrices() -> tuple[str, ...]:
    outputs = build_case_matrices()
    expected_paths = set(outputs)
    _delete_stale_generated_files(expected_paths)
    for path, cases in outputs.items():
        _write_json(path, cases)
    _write_text(COVERAGE_INDEX_PATH, _build_coverage_index(outputs))
    return tuple(sorted([str(path) for path in outputs] + [str(COVERAGE_INDEX_PATH)]))


if __name__ == "__main__":
    built_paths = ensure_generated_matrices()
    print(f"master -> {MASTER_CASES_PATH.relative_to(SUITE_ROOT)}")
    for built_path in built_paths:
        path = Path(built_path)
        if path.suffix == ".json":
            cases = _load_json(path)
            print(f"{path.relative_to(SUITE_ROOT)} -> {len(cases)} cases")
        else:
            print(f"{path.relative_to(SUITE_ROOT)} -> generated")
