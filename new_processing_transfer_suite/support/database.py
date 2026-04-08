from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from support.config import get_config

CARD_SYSTEM_KEYWORDS = (
    ("ELCARD_UPI", ("elcard/upi", "elcard/ upi")),
    ("MASTERCARD", ("mastercard",)),
    ("VISA", ("visa",)),
    ("ELCARD", ("elcard",)),
    ("UPI", ("upi",)),
)


def derive_processor(destination: str | None) -> str:
    normalized = (destination or "").strip().lower()
    if normalized == "ipc":
        return "IPC"
    if normalized == "compass":
        return "COMPASS"
    return "NONE"


def derive_account_kind(account: dict[str, Any]) -> str:
    account_class = str(account.get("account_class") or "")
    if account_class.startswith("0"):
        return "CURRENT"
    if account_class.startswith("3"):
        return "CARD"

    description = (account.get("account_class_description") or "").lower()
    if "current account" in description:
        return "CURRENT"
    if "card account" in description:
        return "CARD"
    if account.get("ipc_card_pan") or account.get("destination"):
        return "CARD"
    return "UNKNOWN"


def derive_card_system(account: dict[str, Any]) -> str:
    description = (account.get("account_class_description") or "").lower()
    for system_name, keywords in CARD_SYSTEM_KEYWORDS:
        if any(keyword in description for keyword in keywords):
            return system_name
    return "UNKNOWN"


def enrich_account_runtime(account: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(account)
    enriched["processor"] = derive_processor(enriched.get("destination"))
    enriched["account_kind"] = derive_account_kind(enriched)
    enriched["card_system"] = derive_card_system(enriched)
    return enriched


@dataclass(frozen=True)
class DatabaseConfig:
    user: str
    password: str
    host: str
    port: str
    database: str
    schema: str

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        config = get_config(validate_live=True)
        return cls(
            user=config.db_user,
            password=config.db_password,
            host=config.db_host,
            port=config.db_port,
            database=config.db_name,
            schema=config.db_schema,
        )


class DataCollector:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._session_record_cache: dict[tuple[int, int], dict[str, Any] | None] = {}
        self._user_id_cache: dict[str, int | None] = {}
        self._user_ids_by_customer_nos_cache: dict[tuple[str, ...], dict[str, int]] = {}
        self._accounts_by_customer_and_account_no_cache: dict[tuple[str, str], list[dict[str, Any]]] = {}
        self._accounts_by_customer_nos_cache: dict[tuple[str, ...], list[dict[str, Any]]] = {}
        self._recent_transactions_cache: dict[tuple[tuple[str, ...], tuple[str, ...], int], list[dict[str, Any]]] = {}
        self._balances_by_account_nos_cache: dict[tuple[str, ...], dict[str, Any]] = {}
        self._valid_session_records_by_customer_nos_cache: dict[tuple[str, ...], dict[str, dict[str, Any]]] = {}
        self._recent_card_numbers_by_account_nos_cache: dict[tuple[tuple[str, ...], int], dict[str, list[str]]] = {}

    @property
    def schema(self) -> str:
        return self.config.schema

    def connect(self):
        import psycopg2

        return psycopg2.connect(
            user=self.config.user,
            password=self.config.password,
            host=self.config.host,
            port=self.config.port,
            database=self.config.database,
        )

    def get_session_record(self, user_id: int, offset: int = 0) -> dict[str, Any] | None:
        from psycopg2.extras import RealDictCursor

        cache_key = (user_id, offset)
        if cache_key in self._session_record_cache:
            return self._session_record_cache[cache_key]

        with self.connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    f"""
                    SELECT session_key, session_id, created_at
                    FROM {self.schema}.sessions
                    WHERE user_id = %s AND is_valid = true
                    ORDER BY created_at DESC
                    LIMIT 1 OFFSET %s
                    """,
                    (user_id, offset),
                )
                result = cur.fetchone()
                self._session_record_cache[cache_key] = result
                return result

    def get_valid_session_key(self, user_id: int, offset: int = 0) -> str | None:
        result = self.get_session_record(user_id=user_id, offset=offset)
        return result["session_key"] if result else None

    def get_user_id_by_customer_no(self, customer_no: str) -> int | None:
        from psycopg2.extras import RealDictCursor

        if customer_no in self._user_id_cache:
            return self._user_id_cache[customer_no]

        with self.connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    f"""
                    SELECT id
                    FROM {self.schema}.users
                    WHERE customer_no = %s
                    ORDER BY updated_at DESC NULLS LAST, id DESC
                    LIMIT 1
                    """,
                    (customer_no,),
                )
                result = cur.fetchone()
                user_id = result["id"] if result else None
                self._user_id_cache[customer_no] = user_id
                return user_id

    def get_user_ids_by_customer_nos(self, customer_nos: list[str]) -> dict[str, int]:
        from psycopg2.extras import RealDictCursor

        normalized = tuple(sorted(set(customer_nos)))
        if not normalized:
            return {}
        if normalized in self._user_ids_by_customer_nos_cache:
            return self._user_ids_by_customer_nos_cache[normalized]

        with self.connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    f"""
                    SELECT DISTINCT ON (customer_no)
                        customer_no,
                        id
                    FROM {self.schema}.users
                    WHERE customer_no = ANY(%s)
                    ORDER BY customer_no, updated_at DESC NULLS LAST, id DESC
                    """,
                    (list(normalized),),
                )
                result = {row["customer_no"]: row["id"] for row in cur.fetchall()}
                self._user_ids_by_customer_nos_cache[normalized] = result
                for customer_no, user_id in result.items():
                    self._user_id_cache[customer_no] = user_id
                return result

    def get_valid_session_key_by_customer_no(self, customer_no: str, offset: int = 0) -> str | None:
        user_id = self.get_user_id_by_customer_no(customer_no)
        if user_id is None:
            return None
        return self.get_valid_session_key(user_id=user_id, offset=offset)

    def get_accounts_by_customer_and_account_no(self, customer_no: str, account_no: str) -> list[dict[str, Any]]:
        from psycopg2.extras import RealDictCursor

        cache_key = (customer_no, account_no)
        if cache_key in self._accounts_by_customer_and_account_no_cache:
            return self._accounts_by_customer_and_account_no_cache[cache_key]

        with self.connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    f"""
                    SELECT
                        a.id,
                        a.customer_no,
                        a.account_no,
                        a.ccy,
                        a.destination,
                        a.is_default,
                        a.account_class,
                        a.ipc_card_base_supp,
                        a.ac_stat_dormant,
                        a.ac_stat_no_dr,
                        a.ac_stat_no_cr,
                        a.ac_stat_block,
                        a.ac_stat_frozen,
                        a.record_stat,
                        a.acy_withdrawable_bal,
                        a.ipc_card_pan,
                        ac.description AS account_class_description,
                        ac.account_class_group,
                        ac.customer_type
                    FROM {self.schema}.accounts a
                    LEFT JOIN {self.schema}.account_classes ac ON ac.account_class_id = a.account_class
                    WHERE a.customer_no = %s AND a.account_no = %s
                    ORDER BY a.is_default DESC NULLS LAST, a.id
                    """,
                    (customer_no, account_no),
                )
                result = [enrich_account_runtime(row) for row in cur.fetchall()]
                self._accounts_by_customer_and_account_no_cache[cache_key] = result
                return result

    def get_accounts_by_customer_nos(self, customer_nos: list[str]) -> list[dict[str, Any]]:
        from psycopg2.extras import RealDictCursor

        normalized = tuple(sorted(set(customer_nos)))
        if not normalized:
            return []
        if normalized in self._accounts_by_customer_nos_cache:
            return self._accounts_by_customer_nos_cache[normalized]

        with self.connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    f"""
                    SELECT
                        a.id,
                        a.customer_no,
                        a.account_no,
                        a.ccy,
                        a.destination,
                        a.is_default,
                        a.account_class,
                        a.ipc_card_base_supp,
                        a.ac_stat_dormant,
                        a.ac_stat_no_dr,
                        a.ac_stat_no_cr,
                        a.ac_stat_block,
                        a.ac_stat_frozen,
                        a.record_stat,
                        a.acy_withdrawable_bal,
                        a.ipc_card_pan,
                        ac.description AS account_class_description,
                        ac.account_class_group,
                        ac.customer_type
                    FROM {self.schema}.accounts a
                    LEFT JOIN {self.schema}.account_classes ac ON ac.account_class_id = a.account_class
                    WHERE a.customer_no = ANY(%s)
                    ORDER BY a.customer_no, a.account_no, a.is_default DESC NULLS LAST, a.id
                    """,
                    (list(normalized),),
                )
                result = [enrich_account_runtime(row) for row in cur.fetchall()]
                self._accounts_by_customer_nos_cache[normalized] = result
                return result

    def get_valid_session_records_by_customer_nos(self, customer_nos: list[str]) -> dict[str, dict[str, Any]]:
        from psycopg2.extras import RealDictCursor

        normalized = tuple(sorted(set(customer_nos)))
        if not normalized:
            return {}
        if normalized in self._valid_session_records_by_customer_nos_cache:
            return self._valid_session_records_by_customer_nos_cache[normalized]

        with self.connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    f"""
                    SELECT DISTINCT ON (u.customer_no)
                        u.customer_no,
                        u.id AS user_id,
                        s.session_key,
                        s.session_id,
                        s.created_at
                    FROM {self.schema}.users u
                    INNER JOIN {self.schema}.sessions s ON s.user_id = u.id
                    WHERE u.customer_no = ANY(%s)
                      AND s.is_valid = true
                    ORDER BY u.customer_no, s.created_at DESC, s.id DESC
                    """,
                    (list(normalized),),
                )
                result = {row["customer_no"]: dict(row) for row in cur.fetchall()}
                self._valid_session_records_by_customer_nos_cache[normalized] = result
                for customer_no, record in result.items():
                    self._user_id_cache[customer_no] = record["user_id"]
                return result

    def get_account_balance(
        self,
        *,
        account_id: int | None = None,
        account_no: str | None = None,
        customer_no: str | None = None,
    ):
        from psycopg2.extras import RealDictCursor

        filters = []
        params: list[Any] = []

        if account_id is not None:
            filters.append("id = %s")
            params.append(account_id)
        if account_no is not None:
            filters.append("account_no = %s")
            params.append(account_no)
        if customer_no is not None:
            filters.append("customer_no = %s")
            params.append(customer_no)

        if not filters:
            raise ValueError("Need account_id or account_no to fetch balance")

        where_clause = " AND ".join(filters)
        with self.connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    f"""
                    SELECT acy_withdrawable_bal
                    FROM {self.schema}.accounts
                    WHERE {where_clause}
                    ORDER BY is_default DESC NULLS LAST, id
                    LIMIT 1
                    """,
                    tuple(params),
                )
                result = cur.fetchone()
                return result["acy_withdrawable_bal"] if result else None

    def get_transaction_by_operation_id(self, operation_id: str) -> dict[str, Any] | None:
        from psycopg2.extras import RealDictCursor

        with self.connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    f"""
                    SELECT
                        id,
                        operation_id,
                        txn_code,
                        txn_type,
                        txn_status_internal,
                        txn_status_external,
                        cbs_reference,
                        error_code,
                        err_desc,
                        backend_err_code,
                        add_text,
                        confirmed_at,
                        end_at,
                        account_debit_id,
                        account_debit_no,
                        account_debit_ccy,
                        account_credit_id,
                        account_credit_no,
                        account_credit_ccy,
                        account_credit_prop_value,
                        account_credit_prop_type,
                        amount_debit,
                        amount_debit_total,
                        amount_credit,
                        customer_no_debit,
                        customer_no_credit,
                        payment_purpose,
                        exchange_rate,
                        value_date,
                        service_provider_id,
                        prop_value,
                        recipient_bank_bic,
                        recipient_name,
                        clearing_recipient_acc_no,
                        recipient_bank_swift,
                        swift_recipient_acc_no,
                        swift_transfer_ccy,
                        swift_commission_type,
                        additional_data,
                        payment_code,
                        created_at,
                        updated_at
                    FROM {self.schema}.transactions
                    WHERE operation_id = %s
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    (operation_id,),
                )
                return cur.fetchone()

    def get_transaction_statement_by_reference(self, reference_no: str) -> list[dict[str, Any]]:
        from psycopg2.extras import RealDictCursor

        with self.connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    f"""
                    SELECT
                        trn_ref_no,
                        account_no,
                        customer_no,
                        dr,
                        cr,
                        contra_ac,
                        details,
                        trn_code,
                        created_at
                    FROM {self.schema}.transaction_statement
                    WHERE trn_ref_no = %s
                    ORDER BY created_at DESC, id DESC
                    """,
                    (reference_no,),
                )
                return cur.fetchall()

    def get_recent_transactions_for_case_selection(
        self,
        *,
        sender_account_nos: list[str],
        recipient_account_nos: list[str] | None = None,
        days: int = 180,
    ) -> list[dict[str, Any]]:
        from psycopg2.extras import RealDictCursor

        if not sender_account_nos and not recipient_account_nos:
            return []

        cache_key = (
            tuple(sorted(set(sender_account_nos))),
            tuple(sorted(set(recipient_account_nos or []))),
            days,
        )
        if cache_key in self._recent_transactions_cache:
            return self._recent_transactions_cache[cache_key]

        with self.connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    f"""
                    SELECT
                        created_at,
                        txn_code,
                        txn_status_internal,
                        txn_status_external,
                        error_code,
                        account_debit_no,
                        account_credit_no,
                        account_credit_prop_type,
                        recipient_bank_bic,
                        clearing_recipient_acc_no,
                        recipient_bank_swift,
                        swift_recipient_acc_no,
                        payment_code,
                        additional_data
                    FROM {self.schema}.transactions
                    WHERE created_at >= now() - (%s || ' days')::interval
                      AND (
                        account_debit_no = ANY(%s)
                        OR (%s IS NOT NULL AND account_credit_no = ANY(%s))
                      )
                    ORDER BY created_at DESC
                    """,
                    (
                        str(days),
                        sender_account_nos or [""],
                        recipient_account_nos or None,
                        recipient_account_nos or [""],
                    ),
                )
                result = cur.fetchall()
                self._recent_transactions_cache[cache_key] = result
                return result

    def get_balances_by_account_nos(self, account_nos: list[str]) -> dict[str, Any]:
        from psycopg2.extras import RealDictCursor

        if not account_nos:
            return {}

        cache_key = tuple(sorted(set(account_nos)))
        if cache_key in self._balances_by_account_nos_cache:
            return self._balances_by_account_nos_cache[cache_key]

        with self.connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    f"""
                    SELECT DISTINCT ON (account_no)
                        account_no,
                        acy_withdrawable_bal,
                        is_default,
                        id
                    FROM {self.schema}.accounts
                    WHERE account_no = ANY(%s)
                    ORDER BY account_no, is_default DESC NULLS LAST, id DESC
                    """,
                    (account_nos,),
                )
                result = {row["account_no"]: row["acy_withdrawable_bal"] for row in cur.fetchall()}
                self._balances_by_account_nos_cache[cache_key] = result
                return result

    def get_recent_card_numbers_by_account_nos(
        self,
        account_nos: list[str],
        *,
        days: int = 365,
    ) -> dict[str, list[str]]:
        from psycopg2.extras import RealDictCursor

        normalized = tuple(sorted(set(account_nos)))
        if not normalized:
            return {}

        cache_key = (normalized, days)
        if cache_key in self._recent_card_numbers_by_account_nos_cache:
            return self._recent_card_numbers_by_account_nos_cache[cache_key]

        with self.connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    f"""
                    SELECT
                        account_credit_no AS account_no,
                        account_credit_prop_value AS card_no,
                        created_at
                    FROM {self.schema}.transactions
                    WHERE created_at >= now() - (%s || ' days')::interval
                      AND account_credit_no = ANY(%s)
                      AND account_credit_prop_type = 'CARD_NO'
                    ORDER BY created_at DESC
                    """,
                    (str(days), list(normalized)),
                )
                result: dict[str, list[str]] = {}
                for row in cur.fetchall():
                    card_no = str(row["card_no"] or "").strip()
                    if not (card_no.isdigit() and 12 <= len(card_no) <= 19):
                        continue
                    bucket = result.setdefault(row["account_no"], [])
                    if card_no not in bucket:
                        bucket.append(card_no)
                self._recent_card_numbers_by_account_nos_cache[cache_key] = result
                return result
