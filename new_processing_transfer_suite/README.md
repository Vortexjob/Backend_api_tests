# New Processing Transfer Suite

Изолированный live-suite для нового процессинга переводов.
Этот suite является основной точкой развития нового процессинга; старые root-level live тесты не считаются основным местом для дальнейшего наращивания покрытия.

Этот набор живет отдельно от корневых `tests/` и `jobs/`:
- не импортирует код из корня репозитория;
- использует собственные helper-модули, proto и data-файлы;
- запускается только при `RUN_LIVE_NEW_PROCESSING=1`;
- перестраивает runtime route-матрицы из одного master JSON с route templates.

## Принцип выполнения

- active route-матрица в suite теперь card-focused;
- в active набор попадают только кейсы, где участвует карта `COMPASS` или `IPC`;
- для покрытия `MPC` в suite используется существующий processor-label `IPC`;
- pure current-only кейсы не попадают в active runtime;
- master JSON теперь хранит route templates и selector-правила, а не только вручную выписанные sender/recipient пары;
- runtime-набор теперь DB-first и latency-optimized: из master templates выбираются самые перспективные реальные пары по живому сигналу из БД;
- для каждого route/card-system family suite старается оставить до двух лучших кейсов с недавней положительной историей;
- если счет на route вида `счет -> карта` не садится на карту, на которую другие транзакции садятся, такой sender считается плохим кандидатом и заменяется альтернативой из того же DB-пула;
- route-группы без недавнего положительного live-сигнала вообще не попадают в generated runtime JSON;
- для `MAKE_OWN_ACCOUNTS_TRANSFER` действует жесткий инвариант: `sender.customer_no == recipient.customer_no`;
- если запрос реально доходит до backend, кейс остается частью master-набора;
- ошибки `create`, business/internal ошибки и `txn FAILURE` остаются обычными `pytest` failures;
- `route summary` показывает и рабочие, и падающие маршруты.
- `card sync` через admin endpoint считается best-effort: если endpoint недоступен, тест продолжает проверку по БД.
- async-маршруты завершаются раньше: как только зафиксирован допустимый processing-state, suite не дожидается полного timeout.

## Базовые пулы v1

- основной IPC/MPC sender pool: `00575749 / 1285110000646290`;
- preferred PAN для `CARD_NO` кейсов на этом счете: `4446791000084945`;
- fallback PAN на этом же счете: `4446791000075141`;
- основной Compass counterparty pool: `00909471`;
- secondary Compass counterparty pool: `00909472`;
- `00909473` не входит в основной active pool и используется только как резервный источник, если это будет включено отдельно.

## Покрытие v1

- `MAKE_BANK_CLIENT_TRANSFER`
  - `card_to_card`
  - `account_to_card`
  - `card_to_account`
  - `account_to_account`
- `MAKE_OWN_ACCOUNTS_TRANSFER`
  - `same_currency`
  - `fx`
- `MAKE_OTHER_BANK_TRANSFER`
  - `clearing`
  - `gross`
- `MAKE_QR_PAYMENT`
  - `static_qr`

Пока не реализованы в isolated suite:
- `MAKE_SWIFT_TRANSFER`
- `MAKE_IPC_CARD_TRANSFER`

## Структура

- `data/master/all_cases.json` — единственный вручную редактируемый source-of-truth; хранит route templates, selector-правила и fixed payload patterns
- `data/master/active_card_case_names.md` — generated coverage-index с именами активных тесткейсов и краткими счетчиками Compass/IPC
- `data/bank_client_transfer/*.json` — generated runtime-кейсы для внутренних переводов
- `data/own_accounts_transfer/*.json` — generated runtime-кейсы для own transfers
- `data/other_bank_transfer/*.json` — generated runtime-кейсы для other bank flows
- `data/qr_payment/*.json` — generated runtime-кейсы для QR flows
- `support/` — изолированное ядро suite
- `proto/` — локальные proto и gRPC stubs
- `contracts/main.js` — локальная копия контрактов

`data/catalog/` можно хранить как legacy bootstrap-данные, но active runtime-матрица больше не строится из catalog.

## Как редактировать кейсы

1. Открываешь `data/master/all_cases.json`.
2. Правишь template:
   - `enabled`
   - `sender_selector` / `recipient_selector`
   - `request`
   - `verification`
3. При необходимости задаешь fixed `sender` / `recipient` для special-case шаблонов.
4. Перестраиваешь runtime JSON:

```bash
python -m support.matrix_builder
```

5. При необходимости смотришь coverage-index в `data/master/active_card_case_names.md`.
6. Запускаешь pytest.

## Почему тесты скипаются

Все live-тесты в isolated suite помечены маркером `live_new_processing`.
Если не выставить `RUN_LIVE_NEW_PROCESSING=1`, pytest специально пропустит все кейсы.

PowerShell-запуск:

```powershell
$env:RUN_LIVE_NEW_PROCESSING="1"
pytest -v
```

Одной строкой:

```powershell
$env:RUN_LIVE_NEW_PROCESSING="1"; pytest -v
```

Пример запуска только QR card-cases:

```powershell
$env:RUN_LIVE_NEW_PROCESSING="1"; pytest -v tests/test_qr_payment_live.py
```

## Настройка окружения

По умолчанию suite ходит в новый контур:
- host: `newibankdevcorp.kicb.net`
- gRPC default: `newibankdevcorp.kicb.net:443`
- Admin API default: `https://newibankdevcorp.kicb.net`

При необходимости можно переопределить:
- `IBANK_HOST`
- `GRPC_SERVER_URL`
- `ADMIN_API_URL`

Важно:
- если в локальном `.env` уже прописаны `GRPC_SERVER_URL` или `ADMIN_API_URL`, они перекроют новый дефолт;
- чтобы реально идти в `newibankdevcorp.kicb.net`, обнови локальный `.env` или передай override при запуске.

Пример `.env`:

```env
RUN_LIVE_NEW_PROCESSING=0
IBANK_HOST=newibankdevcorp.kicb.net
GRPC_SERVER_URL=newibankdevcorp.kicb.net:443
ADMIN_API_URL=https://newibankdevcorp.kicb.net
ADMIN_SESSION_KEY=replace-with-admin-session-key

DB_HOST=localhost
DB_PORT=5434
DB_NAME=ibank
DB_USER=postgres
DB_PASSWORD=postgres
DB_SCHEMA=ibank

OTP_CODE=111111
DEVICE_TYPE=ios
USER_AGENT=12; iPhone12MaxProDan
SESSION_RETRY_LIMIT=5
POLL_INTERVAL_SECONDS=1
BALANCE_SYNC_TIMEOUT_SECONDS=30
TRANSACTION_TIMEOUT_SECONDS=30
```

## Команды

Из папки suite:

```bash
python -m support.matrix_builder
```

## Copy-Paste запуск

Ниже команды в готовом виде под PowerShell.
Самый надежный вариант: запускать из папки suite через явный `python.exe`.

Пересобрать runtime JSON:

```powershell
cd C:\Backend_api_tests\new_processing_transfer_suite
C:\Python313\python.exe -m support.matrix_builder
```

Проверить, сколько тестов соберется:

```powershell
cd C:\Backend_api_tests\new_processing_transfer_suite
$env:RUN_LIVE_NEW_PROCESSING="1"
C:\Python313\python.exe -m pytest --collect-only -q
```

Запустить весь isolated suite:

```powershell
cd C:\Backend_api_tests\new_processing_transfer_suite
$env:RUN_LIVE_NEW_PROCESSING="1"
C:\Python313\python.exe -m pytest -v tests
```

Запустить только `Bank Client Transfer`:

```powershell
cd C:\Backend_api_tests\new_processing_transfer_suite
$env:RUN_LIVE_NEW_PROCESSING="1"
C:\Python313\python.exe -m pytest -v tests/test_bank_client_transfer_live.py
```

Запустить только `Own Accounts Transfer`:

```powershell
cd C:\Backend_api_tests\new_processing_transfer_suite
$env:RUN_LIVE_NEW_PROCESSING="1"
C:\Python313\python.exe -m pytest -v tests/test_own_accounts_transfer_live.py
```

Запустить только `QR Payment`:

```powershell
cd C:\Backend_api_tests\new_processing_transfer_suite
$env:RUN_LIVE_NEW_PROCESSING="1"
C:\Python313\python.exe -m pytest -v tests/test_qr_payment_live.py
```

Запустить один конкретный кейс по `-k`:

```powershell
cd C:\Backend_api_tests\new_processing_transfer_suite
$env:RUN_LIVE_NEW_PROCESSING="1"
C:\Python313\python.exe -m pytest -v tests/test_bank_client_transfer_live.py -k "bank_client_same_currency_card_to_card_by_card_no_cross_provider_kgs_card_compass_c00909471_a1469_to_kgs_card_ipc_c00575749_a6290"
```

Если хочешь запускать из корня репозитория:

```powershell
cd C:\Backend_api_tests
$env:RUN_LIVE_NEW_PROCESSING="1"
C:\Python313\python.exe -m pytest -c .\new_processing_transfer_suite\pytest.ini .\new_processing_transfer_suite\tests -v
```

```powershell
$env:RUN_LIVE_NEW_PROCESSING="1"; pytest --collect-only -q
```

```powershell
$env:RUN_LIVE_NEW_PROCESSING="1"; pytest -v
```

После генерации быстро проверить покрытие по именам кейсов:

```powershell
Get-Content .\data\master\active_card_case_names.md
```

Примечание по терминам:
- в suite label `IPC` сохраняется как существующее обозначение MPC-стороны;
- route keys и expected.processor не переименовываются в `MPC`.
