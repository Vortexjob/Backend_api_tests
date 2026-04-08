# Active Card Case Names

Generated from `data/master/all_cases.json`.

## Summary
- Total active cases: 67
- Compass debit: 36 (53.7%)
- Compass credit: 48 (71.6%)
- IPC debit: 16 (23.9%)
- IPC credit: 7 (10.4%)
- Exact history: 61 (91.0%)
- Same-family history: 1 (1.5%)
- Forced matrix: 5 (7.5%)

## Coverage Buckets (21)
- `own_accounts_fx_c2c_same_provider_account_id`: 10
- `bank_client_fx_c2c_cross_provider_account_no`: 6
- `own_accounts_same_currency_c2c_same_provider_account_id`: 6
- `bank_client_fx_c2c_same_provider_account_no`: 4
- `bank_client_same_currency_c2c_cross_provider_account_no`: 4
- `bank_client_same_currency_c2c_same_provider_account_no`: 4
- `own_accounts_fx_a2c_not_applicable_account_id`: 4
- `own_accounts_fx_c2a_not_applicable_account_id`: 4
- `bank_client_same_currency_a2c_not_applicable_account_no`: 3
- `own_accounts_same_currency_a2c_not_applicable_account_id`: 3
- `own_accounts_same_currency_c2a_not_applicable_account_id`: 3
- `qr_same_currency_c2c_cross_provider_qr_account`: 3
- `bank_client_fx_a2c_not_applicable_account_no`: 2
- `bank_client_same_currency_c2a_not_applicable_account_no`: 2
- `bank_client_same_currency_c2c_cross_provider_card_no`: 2
- `qr_same_currency_c2a_not_applicable_qr_account`: 2
- `bank_client_fx_a2c_not_applicable_account_no_probe`: 1
- `bank_client_fx_a2c_not_applicable_card_no_probe`: 1
- `bank_client_fx_c2a_not_applicable_account_no`: 1
- `bank_client_fx_c2c_cross_provider_card_no`: 1
- `bank_client_same_currency_a2c_not_applicable_card_no`: 1

## Bank Client Transfer (32)
- [exact_history] [`bank_client_fx_c2c_cross_provider_account_no`] CARD/IPC/VISA/KGS -> CARD/COMPASS/MASTERCARD/EUR :: bank_client_fx_card_to_card_by_account_cross_provider_kgs_card_ipc_c00575749_a6290_to_eur_card_compass_c00909471_a1974
- [exact_history] [`bank_client_fx_c2c_cross_provider_account_no`] CARD/IPC/VISA/KGS -> CARD/COMPASS/VISA/USD :: bank_client_fx_card_to_card_by_account_cross_provider_kgs_card_ipc_c00575749_a6290_to_usd_card_compass_c00909471_a1570
- [exact_history] [`bank_client_fx_c2c_cross_provider_account_no`] CARD/IPC/VISA/KGS -> CARD/COMPASS/MASTERCARD/USD :: bank_client_fx_card_to_card_by_account_cross_provider_kgs_card_ipc_c00575749_a6290_to_usd_card_compass_c00909471_a2176
- [exact_history] [`bank_client_fx_c2c_cross_provider_account_no`] CARD/IPC/VISA/KGS -> CARD/COMPASS/VISA/USD :: bank_client_fx_card_to_card_by_account_cross_provider_kgs_card_ipc_c00575749_a6290_to_usd_card_compass_c00909472_a2681
- [exact_history] [`bank_client_fx_c2c_cross_provider_account_no`] CARD/IPC/VISA/KGS -> CARD/COMPASS/MASTERCARD/USD :: bank_client_fx_card_to_card_by_account_cross_provider_kgs_card_ipc_c00575749_a6290_to_usd_card_compass_c00909472_a2984
- [exact_history] [`bank_client_fx_c2c_cross_provider_account_no`] CARD/COMPASS/VISA/USD -> CARD/IPC/VISA/KGS :: bank_client_fx_card_to_card_by_account_cross_provider_usd_card_compass_c00909471_a1570_to_kgs_card_ipc_c00575749_a6290
- [exact_history] [`bank_client_fx_c2c_same_provider_account_no`] CARD/COMPASS/VISA/KGS -> CARD/COMPASS/VISA/USD :: bank_client_fx_card_to_card_by_account_same_provider_kgs_card_compass_c00909471_a2277_to_usd_card_compass_c00909472_a2681
- [exact_history] [`bank_client_fx_c2c_same_provider_account_no`] CARD/COMPASS/VISA/KGS -> CARD/COMPASS/MASTERCARD/USD :: bank_client_fx_card_to_card_by_account_same_provider_kgs_card_compass_c00909471_a2277_to_usd_card_compass_c00909472_a2984
- [exact_history] [`bank_client_fx_c2c_same_provider_account_no`] CARD/COMPASS/VISA/USD -> CARD/COMPASS/VISA/KGS :: bank_client_fx_card_to_card_by_account_same_provider_usd_card_compass_c00909471_a1570_to_kgs_card_compass_c00909472_a2378
- [exact_history] [`bank_client_fx_c2c_same_provider_account_no`] CARD/COMPASS/VISA/USD -> CARD/COMPASS/VISA/KGS :: bank_client_fx_card_to_card_by_account_same_provider_usd_card_compass_c00909471_a1570_to_kgs_card_compass_c00909472_a2580
- [exact_history] [`bank_client_fx_c2c_cross_provider_card_no`] CARD/COMPASS/VISA/USD -> CARD/IPC/VISA/KGS :: bank_client_fx_card_to_card_by_card_no_cross_provider_usd_card_compass_c00909471_a1570_to_kgs_card_ipc_c00575749_a6290
- [exact_history] [`bank_client_fx_c2a_not_applicable_account_no`] CARD/IPC/VISA/KGS -> CURRENT/NONE/USD :: bank_client_fx_card_to_current_by_account_kgs_card_ipc_c00575749_a6290_to_usd_current_none_c00909471_a5513
- [exact_history] [`bank_client_fx_a2c_not_applicable_account_no`] CURRENT/NONE/KGS -> CARD/COMPASS/VISA/USD :: bank_client_fx_current_to_card_by_account_kgs_current_none_c00909471_a0964_to_usd_card_compass_c00909472_a2681
- [exact_history] [`bank_client_fx_a2c_not_applicable_account_no`] CURRENT/NONE/KGS -> CARD/COMPASS/MASTERCARD/USD :: bank_client_fx_current_to_card_by_account_kgs_current_none_c00909471_a0964_to_usd_card_compass_c00909472_a2984
- [exact_history] [`bank_client_fx_a2c_not_applicable_account_no_probe`] CURRENT/NONE/KGS -> CARD/COMPASS/VISA/USD :: bank_client_fx_current_to_card_probe_by_account_kgs_current_none_c00909469_a0762_to_usd_card_compass_c00909471_a1368
- [exact_history] [`bank_client_fx_a2c_not_applicable_card_no_probe`] CURRENT/NONE/KGS -> CARD/COMPASS/VISA/USD :: bank_client_fx_current_to_card_probe_by_card_no_kgs_current_none_c00909469_a0762_to_usd_card_compass_c00909471_a1368
- [exact_history] [`bank_client_same_currency_c2c_cross_provider_account_no`] CARD/COMPASS/VISA/KGS -> CARD/IPC/VISA/KGS :: bank_client_same_currency_card_to_card_by_account_cross_provider_kgs_card_compass_c00909471_a2277_to_kgs_card_ipc_c00575749_a6290
- [exact_history] [`bank_client_same_currency_c2c_cross_provider_account_no`] CARD/IPC/VISA/KGS -> CARD/COMPASS/MASTERCARD/KGS :: bank_client_same_currency_card_to_card_by_account_cross_provider_kgs_card_ipc_c00575749_a6290_to_kgs_card_compass_c00909471_a2075
- [exact_history] [`bank_client_same_currency_c2c_cross_provider_account_no`] CARD/IPC/VISA/KGS -> CARD/COMPASS/VISA/KGS :: bank_client_same_currency_card_to_card_by_account_cross_provider_kgs_card_ipc_c00575749_a6290_to_kgs_card_compass_c00909472_a2378
- [exact_history] [`bank_client_same_currency_c2c_cross_provider_account_no`] CARD/IPC/VISA/KGS -> CARD/COMPASS/VISA/KGS :: bank_client_same_currency_card_to_card_by_account_cross_provider_kgs_card_ipc_c00575749_a6290_to_kgs_card_compass_c00909472_a2580
- [exact_history] [`bank_client_same_currency_c2c_same_provider_account_no`] CARD/COMPASS/VISA/KGS -> CARD/COMPASS/VISA/KGS :: bank_client_same_currency_card_to_card_by_account_same_provider_kgs_card_compass_c00909471_a2277_to_kgs_card_compass_c00909472_a2378
- [exact_history] [`bank_client_same_currency_c2c_same_provider_account_no`] CARD/COMPASS/VISA/KGS -> CARD/COMPASS/VISA/KGS :: bank_client_same_currency_card_to_card_by_account_same_provider_kgs_card_compass_c00909471_a2277_to_kgs_card_compass_c00909472_a2580
- [exact_history] [`bank_client_same_currency_c2c_same_provider_account_no`] CARD/COMPASS/VISA/USD -> CARD/COMPASS/VISA/USD :: bank_client_same_currency_card_to_card_by_account_same_provider_usd_card_compass_c00909471_a1570_to_usd_card_compass_c00909472_a2681
- [exact_history] [`bank_client_same_currency_c2c_same_provider_account_no`] CARD/COMPASS/VISA/USD -> CARD/COMPASS/MASTERCARD/USD :: bank_client_same_currency_card_to_card_by_account_same_provider_usd_card_compass_c00909471_a1570_to_usd_card_compass_c00909472_a2984
- [exact_history] [`bank_client_same_currency_c2c_cross_provider_card_no`] CARD/COMPASS/VISA/KGS -> CARD/IPC/VISA/KGS :: bank_client_same_currency_card_to_card_by_card_no_cross_provider_kgs_card_compass_c00909471_a1469_to_kgs_card_ipc_c00575749_a6290
- [exact_history] [`bank_client_same_currency_c2c_cross_provider_card_no`] CARD/COMPASS/VISA/KGS -> CARD/IPC/VISA/KGS :: bank_client_same_currency_card_to_card_by_card_no_cross_provider_kgs_card_compass_c00909471_a2277_to_kgs_card_ipc_c00575749_a6290
- [exact_history] [`bank_client_same_currency_c2a_not_applicable_account_no`] CARD/IPC/VISA/KGS -> CURRENT/NONE/KGS :: bank_client_same_currency_card_to_current_by_account_kgs_card_ipc_c00575749_a6290_to_kgs_current_none_c00909471_a0964
- [exact_history] [`bank_client_same_currency_c2a_not_applicable_account_no`] CARD/IPC/VISA/KGS -> CURRENT/NONE/KGS :: bank_client_same_currency_card_to_current_by_account_kgs_card_ipc_c00575749_a6290_to_kgs_current_none_c00909471_a5210
- [exact_history] [`bank_client_same_currency_a2c_not_applicable_account_no`] CURRENT/NONE/KGS -> CARD/COMPASS/VISA/KGS :: bank_client_same_currency_current_to_card_by_account_kgs_current_none_c00909471_a0964_to_kgs_card_compass_c00909472_a2378
- [exact_history] [`bank_client_same_currency_a2c_not_applicable_account_no`] CURRENT/NONE/KGS -> CARD/COMPASS/VISA/KGS :: bank_client_same_currency_current_to_card_by_account_kgs_current_none_c00909471_a0964_to_kgs_card_compass_c00909472_a2580
- [exact_history] [`bank_client_same_currency_a2c_not_applicable_account_no`] CURRENT/NONE/KGS -> CARD/IPC/VISA/KGS :: bank_client_same_currency_current_to_card_by_account_kgs_current_none_c00909471_a0964_to_kgs_card_ipc_c00575749_a6290
- [exact_history] [`bank_client_same_currency_a2c_not_applicable_card_no`] CURRENT/NONE/KGS -> CARD/IPC/VISA/KGS :: bank_client_same_currency_current_to_card_by_card_no_kgs_current_none_c00909471_a0964_to_kgs_card_ipc_c00575749_a6290

## Own Accounts Transfer (30)
- [exact_history] [`own_accounts_fx_c2c_same_provider_account_id`] CARD/COMPASS/VISA/KGS -> CARD/COMPASS/MASTERCARD/EUR :: own_accounts_fx_card_to_card_same_provider_kgs_card_compass_c00909471_a1469_to_eur_card_compass_c00909471_a1974
- [exact_history] [`own_accounts_fx_c2c_same_provider_account_id`] CARD/COMPASS/VISA/KGS -> CARD/COMPASS/VISA/USD :: own_accounts_fx_card_to_card_same_provider_kgs_card_compass_c00909471_a1469_to_usd_card_compass_c00909471_a1570
- [exact_history] [`own_accounts_fx_c2c_same_provider_account_id`] CARD/COMPASS/VISA/KGS -> CARD/COMPASS/MASTERCARD/USD :: own_accounts_fx_card_to_card_same_provider_kgs_card_compass_c00909471_a1469_to_usd_card_compass_c00909471_a2176
- [exact_history] [`own_accounts_fx_c2c_same_provider_account_id`] CARD/COMPASS/VISA/KGS -> CARD/COMPASS/MASTERCARD/EUR :: own_accounts_fx_card_to_card_same_provider_kgs_card_compass_c00909471_a2277_to_eur_card_compass_c00909471_a1974
- [same_family_history] [`own_accounts_fx_c2c_same_provider_account_id`] CARD/COMPASS/VISA/KGS -> CARD/COMPASS/VISA/USD :: own_accounts_fx_card_to_card_same_provider_kgs_card_compass_c00909471_a2277_to_usd_card_compass_c00909471_a1368
- [exact_history] [`own_accounts_fx_c2c_same_provider_account_id`] CARD/COMPASS/VISA/KGS -> CARD/COMPASS/MASTERCARD/USD :: own_accounts_fx_card_to_card_same_provider_kgs_card_compass_c00909471_a2277_to_usd_card_compass_c00909471_a2176
- [exact_history] [`own_accounts_fx_c2c_same_provider_account_id`] CARD/COMPASS/VISA/USD -> CARD/COMPASS/MASTERCARD/EUR :: own_accounts_fx_card_to_card_same_provider_usd_card_compass_c00909471_a1570_to_eur_card_compass_c00909471_a1974
- [exact_history] [`own_accounts_fx_c2c_same_provider_account_id`] CARD/COMPASS/VISA/USD -> CARD/COMPASS/VISA/KGS :: own_accounts_fx_card_to_card_same_provider_usd_card_compass_c00909471_a1570_to_kgs_card_compass_c00909471_a1469
- [exact_history] [`own_accounts_fx_c2c_same_provider_account_id`] CARD/COMPASS/VISA/USD -> CARD/COMPASS/MASTERCARD/KGS :: own_accounts_fx_card_to_card_same_provider_usd_card_compass_c00909471_a1570_to_kgs_card_compass_c00909471_a2075
- [exact_history] [`own_accounts_fx_c2c_same_provider_account_id`] CARD/COMPASS/VISA/USD -> CARD/COMPASS/VISA/KGS :: own_accounts_fx_card_to_card_same_provider_usd_card_compass_c00909471_a1570_to_kgs_card_compass_c00909471_a2277
- [exact_history] [`own_accounts_fx_c2a_not_applicable_account_id`] CARD/COMPASS/VISA/KGS -> CURRENT/NONE/USD :: own_accounts_fx_card_to_current_kgs_card_compass_c00909471_a1469_to_usd_current_none_c00909471_a5513
- [exact_history] [`own_accounts_fx_c2a_not_applicable_account_id`] CARD/COMPASS/VISA/KGS -> CURRENT/NONE/USD :: own_accounts_fx_card_to_current_kgs_card_compass_c00909471_a2277_to_usd_current_none_c00909471_a5513
- [exact_history] [`own_accounts_fx_c2a_not_applicable_account_id`] CARD/COMPASS/VISA/USD -> CURRENT/NONE/KGS :: own_accounts_fx_card_to_current_usd_card_compass_c00909471_a1570_to_kgs_current_none_c00909471_a0964
- [exact_history] [`own_accounts_fx_c2a_not_applicable_account_id`] CARD/COMPASS/VISA/USD -> CURRENT/NONE/KGS :: own_accounts_fx_card_to_current_usd_card_compass_c00909471_a1570_to_kgs_current_none_c00909471_a5210
- [exact_history] [`own_accounts_fx_a2c_not_applicable_account_id`] CURRENT/NONE/KGS -> CARD/COMPASS/MASTERCARD/EUR :: own_accounts_fx_current_to_card_kgs_current_none_c00909471_a0964_to_eur_card_compass_c00909471_a1974
- [exact_history] [`own_accounts_fx_a2c_not_applicable_account_id`] CURRENT/NONE/KGS -> CARD/COMPASS/VISA/USD :: own_accounts_fx_current_to_card_kgs_current_none_c00909471_a0964_to_usd_card_compass_c00909471_a1368
- [exact_history] [`own_accounts_fx_a2c_not_applicable_account_id`] CURRENT/NONE/KGS -> CARD/COMPASS/VISA/USD :: own_accounts_fx_current_to_card_kgs_current_none_c00909471_a0964_to_usd_card_compass_c00909471_a1570
- [exact_history] [`own_accounts_fx_a2c_not_applicable_account_id`] CURRENT/NONE/KGS -> CARD/COMPASS/MASTERCARD/USD :: own_accounts_fx_current_to_card_kgs_current_none_c00909471_a0964_to_usd_card_compass_c00909471_a2176
- [exact_history] [`own_accounts_same_currency_c2c_same_provider_account_id`] CARD/COMPASS/VISA/KGS -> CARD/COMPASS/MASTERCARD/KGS :: own_accounts_same_currency_card_to_card_same_provider_kgs_card_compass_c00909471_a1469_to_kgs_card_compass_c00909471_a2075
- [exact_history] [`own_accounts_same_currency_c2c_same_provider_account_id`] CARD/COMPASS/VISA/KGS -> CARD/COMPASS/VISA/KGS :: own_accounts_same_currency_card_to_card_same_provider_kgs_card_compass_c00909471_a1469_to_kgs_card_compass_c00909471_a2277
- [exact_history] [`own_accounts_same_currency_c2c_same_provider_account_id`] CARD/COMPASS/VISA/KGS -> CARD/COMPASS/VISA/KGS :: own_accounts_same_currency_card_to_card_same_provider_kgs_card_compass_c00909471_a2277_to_kgs_card_compass_c00909471_a1469
- [exact_history] [`own_accounts_same_currency_c2c_same_provider_account_id`] CARD/COMPASS/VISA/KGS -> CARD/COMPASS/MASTERCARD/KGS :: own_accounts_same_currency_card_to_card_same_provider_kgs_card_compass_c00909471_a2277_to_kgs_card_compass_c00909471_a2075
- [exact_history] [`own_accounts_same_currency_c2c_same_provider_account_id`] CARD/COMPASS/VISA/USD -> CARD/COMPASS/VISA/USD :: own_accounts_same_currency_card_to_card_same_provider_usd_card_compass_c00909471_a1570_to_usd_card_compass_c00909471_a1368
- [exact_history] [`own_accounts_same_currency_c2c_same_provider_account_id`] CARD/COMPASS/VISA/USD -> CARD/COMPASS/MASTERCARD/USD :: own_accounts_same_currency_card_to_card_same_provider_usd_card_compass_c00909471_a1570_to_usd_card_compass_c00909471_a2176
- [exact_history] [`own_accounts_same_currency_c2a_not_applicable_account_id`] CARD/COMPASS/VISA/KGS -> CURRENT/NONE/KGS :: own_accounts_same_currency_card_to_current_kgs_card_compass_c00909471_a1469_to_kgs_current_none_c00909471_a5210
- [exact_history] [`own_accounts_same_currency_c2a_not_applicable_account_id`] CARD/COMPASS/VISA/KGS -> CURRENT/NONE/KGS :: own_accounts_same_currency_card_to_current_kgs_card_compass_c00909471_a2277_to_kgs_current_none_c00909471_a5210
- [exact_history] [`own_accounts_same_currency_c2a_not_applicable_account_id`] CARD/COMPASS/VISA/USD -> CURRENT/NONE/USD :: own_accounts_same_currency_card_to_current_usd_card_compass_c00909471_a1570_to_usd_current_none_c00909471_a5513
- [exact_history] [`own_accounts_same_currency_a2c_not_applicable_account_id`] CURRENT/NONE/KGS -> CARD/COMPASS/VISA/KGS :: own_accounts_same_currency_current_to_card_kgs_current_none_c00909471_a0964_to_kgs_card_compass_c00909471_a1469
- [exact_history] [`own_accounts_same_currency_a2c_not_applicable_account_id`] CURRENT/NONE/KGS -> CARD/COMPASS/MASTERCARD/KGS :: own_accounts_same_currency_current_to_card_kgs_current_none_c00909471_a0964_to_kgs_card_compass_c00909471_a2075
- [exact_history] [`own_accounts_same_currency_a2c_not_applicable_account_id`] CURRENT/NONE/KGS -> CARD/COMPASS/VISA/KGS :: own_accounts_same_currency_current_to_card_kgs_current_none_c00909471_a0964_to_kgs_card_compass_c00909471_a2277

## Other Bank Transfer (0)
- none

## QR Payment (5)
- [forced_matrix] [`qr_same_currency_c2a_not_applicable_qr_account`] CARD/IPC/VISA/KGS -> CURRENT/NONE/KGS :: qr_internal_card_to_account_kgs_card_ipc_c00575749_a6290_to_kgs_current_none_c00909471_a0964
- [forced_matrix] [`qr_same_currency_c2a_not_applicable_qr_account`] CARD/IPC/VISA/KGS -> CURRENT/NONE/KGS :: qr_internal_card_to_account_kgs_card_ipc_c00575749_a6290_to_kgs_current_none_c00909471_a5210
- [forced_matrix] [`qr_same_currency_c2c_cross_provider_qr_account`] CARD/IPC/VISA/KGS -> CARD/COMPASS/MASTERCARD/KGS :: qr_internal_card_to_card_cross_provider_kgs_card_ipc_c00575749_a6290_to_kgs_card_compass_c00909471_a2075
- [forced_matrix] [`qr_same_currency_c2c_cross_provider_qr_account`] CARD/IPC/VISA/KGS -> CARD/COMPASS/VISA/KGS :: qr_internal_card_to_card_cross_provider_kgs_card_ipc_c00575749_a6290_to_kgs_card_compass_c00909472_a2378
- [forced_matrix] [`qr_same_currency_c2c_cross_provider_qr_account`] CARD/IPC/VISA/KGS -> CARD/COMPASS/VISA/KGS :: qr_internal_card_to_card_cross_provider_kgs_card_ipc_c00575749_a6290_to_kgs_card_compass_c00909472_a2580
