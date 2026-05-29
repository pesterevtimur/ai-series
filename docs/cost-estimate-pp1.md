---
id: cost-estimate-pp1
title: Cost estimate ПП1 в USD — Opus 4.7 + extended thinking, smoke-test 4 артефакта
date: 2026-05-29
status: resolved
resolves: decisions/D-002-spec-corrections-and-golden-plan.md § P-6
relates_to:
  - docs/specs/2026-05-24-infrastructure-and-skills-design.md § 9 (smoke-test) § 11.4 (cost commitment)
  - decisions/D-001-bootstrap-architecture.md § R-4
  - docs/extended-thinking-mechanism.md
verification:
  pricing_source: https://platform.claude.com/docs/en/about-claude/pricing
  pricing_fetched_on: 2026-05-29
  method: fetch-verbatim + bottom-up token estimate per call type
---

# Cost-estimate ПП1 — итог в долларах

## 0. TL;DR

| Сценарий | Smoke-test (4 артефакта) | + Regression | + Pressure-tests | + 2 раунда rework | **ИТОГО** |
|---|---|---|---|---|---|
| **Low (агрессивная оптимизация)** | $8 | +$3 | +$2 | +$3 | **≈ $16** |
| **Mid (базовый, реалистичный)** | $11 | +$6 | +$4 | +$19 | **≈ $40** |
| **High (волатильность thinking + retry)** | $18 | +$9 | +$7 | +$28 | **≈ $62** |

**Базовая ставка для R-4 cost commitment в D-001: $40 USD** на полный ПП1
smoke-test pipeline. Коридор $16-$62 учитывает неопределённость adaptive
thinking budget на Opus 4.7 + retry rate critics_report_validator'а.

**Самая большая статья — резерв на rework** (~$19 mid). Без обязательной
переработки на concern/veto критиков (R-2 enforcement) сумма падает до ~$21
mid. Это **не предложение убрать rework** — это понимание что концентрация
оптимизации должна быть здесь.

---

## 1. Тарифы Opus 4.7 (verbatim, fetched 2026-05-29)

Источник: [https://platform.claude.com/docs/en/about-claude/pricing](https://platform.claude.com/docs/en/about-claude/pricing).

| Категория | Цена $/MTok |
|---|---|
| Input (base) | **$5** |
| Output (включая thinking tokens) | **$25** |
| 5-min cache write | $6.25 (1.25× base input) |
| 1-hr cache write | $10 (2× base input) |
| Cache hit / refresh | $0.50 (0.1× base input) |
| Batch API input | $2.50 (50% off) |
| Batch API output | $12.50 (50% off) |

**Важные оговорки:**
- 1M context window — **standard pricing** на полный 1M. Размер запроса не
  меняет per-token ставку.
- Extended thinking tokens биллятся как **output** (не отдельный rate).
- Opus 4.7 использует новый tokenizer — **до +35% токенов** для того же
  фиксированного текста vs Opus 4.6. В оценках ниже это учтено (умеренный
  inflate в сторону high).
- Sonnet 4.6 для сравнения: $3 / $15 input/output — экономия ~40% если
  заменять часть критиков на Sonnet (отклонённый вариант D-001 R-4).

---

## 2. Поток A breakdown — стоимость одного артефакта

Поток A после правок D-002 §A (P-1: A5 в adversarial-review-pass; P-2: R-1
как 3 шляпы в orchestrator session, не параллельные Task'и):

| Шаг | Где исполняется | Input tok | Output tok (incl. thinking) | Cost USD |
|---|---|---|---|---|
| 1. Brainstorming session | Orchestrator | 8 000 | 3 000 | $0.12 |
| 2. R-1 drafting (3 шляпы) | Orchestrator (cumulative) | 25 000 | 6 000 | $0.28 |
| 4. Synthesis по 3 драфтам | Orchestrator | 12 000 | 3 000 | $0.14 |
| 5a. A1 lore-realism Task | Subagent (Opus + effort: max) | 10 000 | 11 000 | $0.33 |
| 5b. A3 incentive Task | Subagent | 10 000 | 11 000 | $0.33 |
| 5c. A2 character-truth Task | Subagent | 10 000 | 11 000 | $0.33 |
| 5d. A5 philosophy Task | Subagent | 10 000 | 13 000 | $0.38 |
| 5e. A6 audience Task | Subagent | 10 000 | 11 000 | $0.33 |
| 5f. critic_report_validator retries | Subagent | 20% × 5 critics | (~retry once) | $0.35 |
| 6. Шоураннер реакция на critic flags | Orchestrator | 30 000 | 4 000 | $0.25 |
| 9. evidence-before-action self-check | Orchestrator | 12 000 | 2 000 | $0.11 |
| 10-12. Write/commit/log | local | 0 | 0 | $0.00 |
| **Подытог non-scene артефакт** | — | ~155 000 | ~75 000 | **$2.95** |
| 5g. A4 voice-check (только сцена) | Subagent | 12 000 | 13 000 | $0.39 |
| **Подытог scene-артефакт** | — | ~167 000 | ~88 000 | **$3.34** |

**Где сидят токены:**

- **Critic input ~10k:** system prompt критика (≈2k) + golden_calibration_used
  чтение 3-5 файлов (≈5-7k) + артефакт под review (≈0.5-1k) + tool-use system
  overhead (675 для Opus 4.7) + repo context (1-2k).
- **Critic thinking ~10-13k:** adaptive thinking на effort: max при «найди
  слабости философской позиции / counter-test»; это complex reasoning, модель
  пойдёт глубоко. Для A5 (philosophy) бюджет выше — это самый абстрактный
  критик.
- **Orchestrator R-1 3 шляпы 25k input:** контекст растёт между шляпами
  (drafts накапливаются); это **single session**, не три отдельных calls.

---

## 3. Smoke-test = 4 артефакта × Поток A

D-002 P-3: smoke-test расширен до 4 артефактов (добавлена сценка для A4):

| Артефакт | Тип | Базовая стоимость |
|---|---|---|
| `story-bible/thesis.md` (~150 слов) | non-scene | $2.95 |
| `story-bible/world-rules.md` (5 правил) | non-scene | $2.95 |
| `characters/<one>.md` (1 character-sheet) | non-scene | $2.95 |
| `scenes/smoke-test-dialogue.md` (300-500 слов) | **scene** | $3.34 |
| **Итого smoke-test base** | — | **$12.19** |

Округлённо: **$11 mid** (с учётом частичного prompt-caching на повторяющемся
golden chunk'е между критиками — экономия ~10%).

---

## 4. Regression runs (R-3 calibration + holdout)

Спека § 9.4 + D-002 P-5: regression сет делится на calibration / holdout.
Bootstrap-минимум для ПП1:

| Набор | Файлы | Что прогоняем | Cost |
|---|---|---|---|
| `strawmen/` | 3 файла | A5 на каждом, должен veto | 3 × $0.38 = $1.14 |
| `moralizing/` | 2 файла | A5 + A4 на каждом | 4 × $0.39 = $1.56 |
| `voice-bleed/` | 2 файла | A4 на каждом | 2 × $0.39 = $0.78 |
| `pairs/` (6 критиков × strong+weak пара, holdout) | 12 calls | по 1 критику на каждой паре | 12 × $0.33 = $3.96 |
| critic_validator retries (≈10% rate) | — | — | $0.70 |
| **Итого regression** | — | — | **≈ $8** |

Если pairs полная sample (B.4.1 не выполнен → bootstrap-порог), оставляем
≈$6. С полной B.4.1 партией добор был бы ~$2 сверху.

---

## 5. Pressure-tests для discipline-BLOCKER скиллов

3 discipline-BLOCKER скилла (`philosophy-stress-test` отменён P-1 →
адверсариальная критика встроена в `adversarial-review-pass`. Остаются:
`voice-check`, `consistency-check`, плюс `evidence-before-action`). Каждый
× 3 RED-сценария (минимум) = 9 сессий orchestrator-времени:

| Сценарий | Cost per | Total |
|---|---|---|
| 9 RED-сценариев × orchestrator 20k input / 5k output | $0.225 | $2.03 |
| critic-validator + lint runs в составе | — | $0.50 |
| Pressure-test ulay log writing | $0.20 | $0.20 |
| **Итого pressure-tests** | — | **≈ $3** |

---

## 6. Резерв на пересборку (rework rounds)

D-002 P-7 / R-2: на каждый concern/veto критика шоураннер **обязан**
либо переписать артефакт, либо зарегистрировать D-NNN. Перезапись = повторный
проход Потока A на этом артефакте.

**Допущение:** в среднем 2 rework round'а на артефакт за smoke-test (1 round
по R-2 минимуму + 1 для общей доводки):

| Параметр | Значение |
|---|---|
| Rework rounds per артефакт | 2 |
| Артефактов | 4 |
| Total rework cycles | 8 |
| Cost per rework cycle (без brainstorm и retake R-1) | ~$2.40 |
| **Итого rework reserve** | **≈ $19** |

Это **самая большая статья**. Если бы убрать R-2 enforcement (отклонено) или
сократить до 1 round per артефакт — экономия ~$10. Не делаем: R-2 — это
core invariant дизайна.

---

## 7. Итоговый коридор

### 7.1 Mid estimate (базовый сценарий)

| Статья | $ |
|---|---|
| Smoke-test base | $11 |
| Regression | $6 |
| Pressure-tests | $4 |
| Rework reserve (2 round × 4 artifacts) | $19 |
| **Mid total** | **$40** |

### 7.2 Low estimate (агрессивная оптимизация)

Предположения: prompt caching на golden_calibration (5-min cache write один
раз → 5 hits × $0.50/MTok input, не $5); thinking budget на каждом критике
по нижнему краю adaptive (3-5k); retry rate 5%; 1 rework round/артефакт.

| Статья | $ |
|---|---|
| Smoke-test base (с caching) | $8 |
| Regression (с caching) | $3 |
| Pressure-tests | $2 |
| Rework reserve (1 round × 4) | $3 |
| **Low total** | **$16** |

### 7.3 High estimate (волатильность + worst-case retry)

Thinking budget upper bound (15-20k per call); retry rate 30%; 3 rework
round per артефакт.

| Статья | $ |
|---|---|
| Smoke-test base | $18 |
| Regression | $9 |
| Pressure-tests | $7 |
| Rework reserve (3 round × 4) | $28 |
| **High total** | **$62** |

### 7.4 Коридор: **$16 — $62**, central **$40**

---

## 8. Сравнение с отклонённой альтернативой (D-001 R-4)

R-4 отклонил альтернативу «Opus для A5/A3/A1 (PHILOSOPHY + INCENTIVE + LORE),
Sonnet для A2/A4/A6». Что она дала бы по деньгам?

| Параметр | All-Opus (принято) | Hybrid (отклонено) |
|---|---|---|
| Critic call cost (3 Opus + 3 Sonnet) | 5 × $0.33 + $0.38 = $2.03 | 3 × $0.33 + 3 × $0.20 = $1.59 |
| Mid total smoke+reg+pressure+rework | **$40** | **~$31** |
| Экономия | — | **$9 mid** |

**Качественный аргумент за all-Opus сохраняется** (D-001 R-4): A2/A4/A6
несут sub-textual нагрузку (character truth, voice differentiation, audience
boredom detection) которая требует deep adaptive thinking так же, как
PHILOSOPHY. $9 экономии vs риск понизить калибровку трёх критиков из шести —
неприемлемый tradeoff для bootstrap-этапа. **All-Opus принято**, цифра
зафиксирована в R-4 cost commitment как **$40 mid с коридором $16-62**.

Альтернатива пересматривается **только** если фактический smoke-test ПП1
выйдет в high-зону ($55+) И при этом A2/A4/A6 покажут систематический pass
без качественного counter_test'а (тогда они либо неэффективны на Opus, либо
тратят бюджет впустую).

---

## 9. Рычаги оптимизации

### 9.1 Prompt caching (приоритет №1)

5-min cache write один раз × 5 cache hits = 1.25 + 5 × 0.1 = 1.75× базовой
input ставки вместо 5×. **Экономия 65% на input** при повторном чтении
golden_calibration внутри adversarial-review-pass.

**Условие применимости.** Все 5 критиков работают **последовательно в окне
5 минут** и читают общий golden chunk. Это требует:
- Orchestrator зовёт Task для A1, A3, A2, A5, A6 без длинного перерыва
  между ними (`<5min` между первым и последним вызовом).
- Каждый критик пишет cache_control breakpoint на одном и том же блоке
  (golden_calibration).
- Schema: golden как первый блок системного prompt'а, переиспользуется.

**Risk.** Если adversarial-review-pass перебивается длинным retry-циклом
(critic_report_validator FAIL на одном из критиков), cache может истечь.
Митигация: использовать 1-hr cache write для критичных артефактов (×2 input
вместо ×5 — выгодно при 2+ reads).

### 9.2 Batch API (приоритет №2 для regression)

Regression runs (R-3) не требуют интерактивности — это калибровочные пробеги.
Batch API даёт **50% off** на input и output: $2.50 / $12.50 vs $5 / $25.

Экономия на regression set: ~$3-4 если перевести все 12 holdout pair calls
+ regression-плохие на batch. Не применим к smoke-test (нужна интерактивность
для R-2 rework).

### 9.3 Что НЕ оптимизируем

- ❌ Fast mode — $30/$150, 6× стандарта. Не нужен; смотрим качество, не
  скорость.
- ❌ Сокращение thinking budget (effort: high вместо max) — нарушает R-4.
  Снижение калибровки критиков перекрывает любую экономию.
- ❌ Перевод A2/A4/A6 на Sonnet — отклонено в R-4 (см. § 8).

---

## 10. Sensitivity / risks

| Риск | Воздействие на cost | Митигация |
|---|---|---|
| Thinking budget adaptive variability (3k vs 20k per call) | ±$15-20 на итог | Накопить метрики на первых 2 артефактах smoke-test, скорректировать high estimate |
| critic_report_validator retry rate выше плана (>30%) | +$5-10 на итог | Improve critic prompt'ы в соответствующих субагентах; не cost-issue, а quality-issue |
| Rework rounds > 2 per артефакт | +$10/round/артефакт | Если ≥3 rounds на 2+ артефактах — пересмотреть критиков либо R-1 drafting качество |
| Opus 4.7 tokenizer +35% сверх 4.6 | +30% на input estimate если my counts были в "4.6 эквиваленте" | Уже неявно учтено через накидку на input estimate |
| Cache write но без hits (одиночные вызовы) | +1.25× на write без экономии | Использовать batched adversarial-review-pass; не оптимизировать кэш если артефакт «1-shot» |

---

## 11. Что НЕ покрыто этим estimate

- **Implementation cost** (написание скиллов, субагентов, lint-скриптов
  через Claude Code в orchestrator-режиме) — отдельная статья **не входит**
  в ПП1 R-4 cost commitment, это часть development cost. Грубая оценка:
  $15-25 на implementation 9 скиллов + 6 субагентов + 6 lint скриптов через
  TDD.
- **Cowork (Claude.ai web)** — Claude.ai subscription cost не считается per
  call; это flat fee.
- **Stage past ПП1** (ПП2 = Story Bible v0.1 = 5-10 артефактов Bible × Поток A
  + N character sheets) — оценивать после фактических метрик ПП1.

---

## 12. Definition of "R-4 cost commitment" для D-001

После этого estimate'а R-4 переписывается с конкретикой:

> **R-4 (D-001) cost commitment.** ПП1 smoke-test pipeline (4 артефакта +
> regression + pressure-tests + 2 rework rounds/артефакт) стоит **$40 mid
> в коридоре $16-$62** на Opus 4.7 1M с effort: max во всех 6 критиках.
> Alternative с Sonnet для A2/A4/A6 экономит $9 mid и отклонена. Пересмотр
> только при фактическом выходе в high-зону + одновременно systematic pass
> у sub-Opus критиков. Реальные траты track'ятся через token-usage отчёты
> Anthropic в течение smoke-test'а.

Это обновление R-4 вносится в D-001 на шаге C.1.9 (обновление спеки и
related decisions под P-1..P-15).

---

## 13. Источники

1. **Anthropic API pricing** (fetched 2026-05-29) — https://platform.claude.com/docs/en/about-claude/pricing
2. **Prompt caching** — https://platform.claude.com/docs/en/build-with-claude/prompt-caching
3. **Batch processing** — https://platform.claude.com/docs/en/build-with-claude/batch-processing
4. **Extended thinking mechanism** — `docs/extended-thinking-mechanism.md` (research-001)
5. **Design spec § 9 (smoke-test acceptance)** — `docs/specs/2026-05-24-infrastructure-and-skills-design.md`
6. **D-001 § R-4 (cost commitment)** — `decisions/D-001-bootstrap-architecture.md`
7. **D-002 § P-6 (cost-estimate obligation)** — `decisions/D-002-spec-corrections-and-golden-plan.md`
