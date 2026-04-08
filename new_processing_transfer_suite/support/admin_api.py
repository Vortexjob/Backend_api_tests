from __future__ import annotations

import json
import uuid
from typing import Any, Mapping

import pytest

from support.config import get_config

CARD_SYNC_OBSERVABLE_PROCESSORS = {"IPC", "COMPASS"}


def build_admin_headers() -> dict[str, str]:
    config = get_config(validate_live=True)
    return {
        "Content-Type": "application/json",
        "device-type": "web",
        "ref-id": str(uuid.uuid4()),
        "session-key": config.admin_session_key,
        "user-agent": config.admin_browser_user_agent,
        "user-agent-c": config.admin_browser_user_agent_c,
        "accept": "*/*",
        "referer": f"{config.admin_api_url}/admin-ui/cards",
        "origin": config.admin_api_url,
    }


def count_sync_cards(payload: dict[str, Any]) -> int:
    sync_cards = ((payload.get("data") or {}).get("syncCards") or [])
    total = 0
    for item in sync_cards:
        if isinstance(item, list):
            total += len(item)
        else:
            total += 1
    return total


def sync_account_view(account: Mapping[str, Any] | None) -> dict[str, Any] | None:
    import requests

    if not account:
        return None
    if account.get("account_kind") != "CARD":
        return None
    if account.get("processor") not in CARD_SYNC_OBSERVABLE_PROCESSORS:
        return None

    config = get_config(validate_live=True)
    try:
        response = requests.post(
            f"{config.admin_api_url}/adminApi/others/cards",
            headers=build_admin_headers(),
            json={"accountNo": account["account_no"]},
            timeout=30.0,
        )
    except requests.RequestException as exc:
        print(
            f"[card-sync-skip] account_no={account['account_no']}, "
            f"reason=request_error, details={exc}"
        )
        return None

    try:
        payload = response.json()
    except ValueError as exc:
        print(
            f"[card-sync-skip] account_no={account['account_no']}, "
            f"reason=non_json_response, http_status={response.status_code}, details={exc}"
        )
        return None

    if response.status_code != 200 or payload.get("error"):
        print(
            f"[card-sync-skip] account_no={account['account_no']}, "
            f"http_status={response.status_code}, payload={payload}"
        )
        return None

    print(
        f"[card-sync] account_no={account['account_no']}, "
        f"sync_cards_count={count_sync_cards(payload)}, "
        f"payload={json.dumps(payload, ensure_ascii=False, default=str)}"
    )
    return payload
