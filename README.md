# Johny_Trade

`Johny_Trade` — краткосрочный агент-сборщик и аналитик рыночной информации.

> Агент **не открывает сделки, не отправляет ордера и не гарантирует прибыль**. Он формирует объективный аналитический дайджест для краткосрочных решений.

## Что делает агент

- работает по окнам **15m, 1h, 4h**;
- использует **1d** как контекст;
- анализирует свежие данные (последние 24 часа), а более старые явно помечает как stale;
- хранит данные, корреляции, COT-сигналы, новости и отчёты в SQLite;
- ведёт журнал источников, UTC-время, `last update`, дедупликацию и проверку качества.

## Отслеживаемые инструменты

- FX: `EURUSD`, `GBPUSD`, `USDJPY`, `AUDUSD`, `USDCAD`, `USDCHF`, `NZDUSD`
- Индикаторы: `DXY`, `XAUUSD`, `WTI`, `US10Y`, `SPX` (S&P500), `NDX` (Nasdaq100), `VIX`

## Корреляционные группы

Агент рассчитывает rolling correlation для периодов **20/60/120 наблюдений** и выводит:
коэффициент, знак связи, силу, изменение к предыдущему окну и warning о нестабильности.

Ключевые пары:

- `DXY ↔ EURUSD`
- `DXY ↔ XAUUSD`
- `DXY ↔ USDJPY`
- `XAUUSD ↔ US10Y`
- `USDJPY ↔ US10Y`
- `AUDUSD ↔ USDCNH`
- `USDCAD ↔ WTI`
- `GBPUSD ↔ EURUSD`
- `SPX/NDX ↔ VIX`

## Формулы расчёта

- Доходность наблюдения: `r_t = (P_t - P_{t-1}) / P_{t-1}`
- Rolling correlation (Пирсон):

`corr(X,Y) = cov(X,Y) / (std(X) * std(Y))`

- COT net positioning: `net = long - short`
- Изменение COT: `delta_net = net_current - net_previous`

## Источники данных (ожидаемые)

- COT: официальный CFTC
- Макро: сайты ЦБ/статистических ведомств/календари
- Новости: BBC, Reuters, разрешённые RSS/API
- Market data: только разрешённые API

В коде предусмотрен контроль разрешённых доменов и журнал ссылок/времени публикации/резюме.

## Конфигурация

Скопируйте `.env.example` в `.env` и задайте переменные.

## Запуск

```bash
python -m johny_trade --db-path johny_trade.db --payload /absolute/path/to/payload.json
```

Где `payload.json` содержит `market_snapshots`, `correlation_inputs`, `cot_positions`, `macro_events`, `news_items`.

## Тесты

```bash
python -m unittest discover -s tests -v
```

Покрытие тестами:

- расчёты COT;
- rolling correlation;
- свежесть данных;
- дедупликация;
- отсутствующие поля;
- формирование финального отчёта.

## Пример краткосрочного отчёта (сокращённо)

```text
1) Report time (UTC): 2026-09-29T08:55:00+00:00
   Data freshness window: last 24 hours

2) Market state summary
   Mixed market conditions.

3) Instrument table
   instrument | direction | 15m/1h/4h | key driver | volatility | data quality
   EURUSD | uptrend | 0.1/0.2/0.3 | DXY pullback | moderate | fresh

4) DXY impact on EURUSD, XAUUSD, USDJPY
   DXY impact requires confirmation.
...
14) Neutral conclusion
   Data supports scenarios; signal absent without additional confirmation.
```
