---
id: incentive-cartographer-pressure-tests
version: 1
status: draft
type: doc
references:
  - "docs/specs/2026-05-24-infrastructure-and-skills-design.md § 4.2 § 4.3 § 9.4.b § 9.4.c § 9.5"
  - "decisions/D-002-spec-corrections-and-golden-plan.md P-4 P-7 P-8 P-10 P-15"
  - ".claude/agents/incentive-cartographer.md"
---

# A3 INCENTIVE — Pressure tests (RED scenarios)

Документ калибровочных RED-сценариев для субагента `incentive-cartographer`. Acceptance — Task 7 Phase 2 (Task tool invocation + validator проверка отчётов).

## Известное ограничение (D-002 P-15)

`golden/anti-examples/conflicts/` пуст на момент Phase 2 ПП1. Dedicated RED-anti для A3 в `tests/regression/strawmen/` либо `moralizing/` не созданы — у A3 нет ни «strawman», ни «moralizing» аналога как первичной категории, его первичный сигнал — **decoration of conflict / declaration without incentive**, и эти артефакты не созданы как dedicated RED-anti в Phase 2.

Pressure-tests A3 на момент Phase 2 опираются на:
- **`tests/regression/pairs/calibration/incentive-weak-cal.md`** — критик должен дать `veto` или `concern-severity-high`
- **`tests/regression/pairs/holdout/incentive-weak-holdout.md`** — то же на не-AI контексте
- **Cross-validation** с A5 на `moralizing-monolog-01.md` и с A2 (Task 3) на character-сцене — для проверки разграничения incentive vs philosophical position vs character truth

## RED-1: weak-calibration-pair

**Файл:** `tests/regression/pairs/calibration/incentive-weak-cal.md`
**Expected verdict:** `veto` или `concern-severity-high`
**Expected reasoning должен содержать:** распознавание паттерна «декларация без cost-benefit» — конкретный персонаж + конкретная реплика, где declaration ≠ action. Например: «Йоав-аналог в AI-сетинге заявляет "я отвечаю за продукт и считаю это важным" — это статус, не cost-benefit. Что он готов потерять, чтобы продукт вышел? Что он считает дороже выхода продукта? Ни одного, ни другого в реплике нет». Должна быть отмечена симметрия декорации: все три персонажа произносят форму «я хочу X, потому что Y», но ни одно действие из этого не выводимо. Указание на финал («подумаю», «уважаю позицию», обнимаются) как индикатор decorative conflict.
**Acceptance:** valid `flags` массив (не пустой), минимум один `severity: high`, location указывает на конкретные реплики (Кай первая реплика, Анна первая реплика, СЕРГЕЙ итоговая «подумаю»). `counter_test_attempted` не пустой даже при veto.

## RED-2: weak-holdout-pair

**Файл:** `tests/regression/pairs/holdout/incentive-weak-holdout.md`
**Expected verdict:** `veto`
**Expected reasoning должен содержать:** распознавание того же паттерна декларации-без-incentive на материале из НЕ-AI контекста (наследство, семья). Должно быть отмечено: «Йоав говорит "я хочу управлять, потому что я работал" — это апелляция к прошлому, не cost-benefit. Дина говорит "мне нужны деньги для семьи" — без конкретики (сколько, на что, почему именно сейчас). Шира говорит "корни важны" — это ценность, не incentive». Финал (обнимаются, договариваются «подумать неделю») как явный indicator псевдоконфликта.
**Acceptance:** verdict идентичен по structure с RED-1 — критик распознаёт паттерн independently от domain (AI vs семейная драма). Если A3 даёт `veto` на AI weak-cal, но `pass`/`concern-low` на семейном weak-holdout, или наоборот — это признак domain-overfitting: критик прошит на AI-vocabulary («deceptive alignment», «evals») вместо incentive-структуры. Escalate в D-NNN.

## RED-3 (cross-critic): moralizing-monolog-01 (Task 1)

**Файл:** `tests/regression/moralizing/moralizing-monolog-01.md`
**Expected verdict from A3:** `concern` ИЛИ `pass+not_applicable`
**Логика:** артефакт — философский монолог Анны (~280 слов из ~320), Маркус — setup-реплики. Это **первично philosophical / character bleed**, не incentive issue. A3 может корректно дать:
- `concern` — потому что Маркус-без-incentive (только setup) — это decoration of partner, а не настоящий партнёр в конфликте
- `pass + not_applicable_reason: "сцена не претендует на incentive-структуру, чистая philosophical exchange"` — допустимо, P-3 case

**Cross-validation:** A5 даёт `veto` на этом артефакте (Task 1 RED-4). Если A3 тоже даёт `veto` — flag избыточности критиков (spec § 9.4.c): два критика на один и тот же артефакт с одной и той же причиной = overlap. Решается в Task 7 ревью.

## RED-4 (cross-critic, на Task 3): когда появится A2 character-truth-keeper

**Файл:** `tests/regression/moralizing/moralizing-character-arc-01.md` (создаётся в Task 3)
**Expected verdict from A3:** `concern`
**Логика:** character действует по сценарию, а не из incentive — это incentive issue, не только character-truth issue. A3 должен распознать, что декларации мотивов в character-arc не подкреплены cost-benefit.
**Acceptance:** A3 не молчит на character-shaped артефакте. Если A3 говорит «not_applicable, это character arc, не моя зона» — escalate, потому что character без incentive — это его зона.

## P-10 acceptance

A3 даёт `pass` на `incentive-weak-cal.md` ИЛИ `incentive-weak-holdout.md` = провал калибровки. Расследование причины: prompt не покрыл паттерн декларация-без-action / model auto-switch на sonnet съел precision / P-15 пустота golden/anti-examples/conflicts/ привела к слабой негативной калибровке.

При первом провале RED-1 или RED-2 — escalate в decision (D-NNN) с разбором.

## Phase 2 Task 7 verification

Дополнительные проверки в Task 7:
- Cross-validation A3 ↔ A5 на `moralizing-monolog-01.md` — оба `veto` = flag избыточности (spec § 9.4.c).
- Cross-validation A3 ↔ A2 на `moralizing-character-arc-01.md` — оба `veto` = такой же flag избыточности.
- Holdout consistency: A3 на strong-holdout = pass, A3 на weak-holdout = veto. Если оба pass или оба veto — calibration broken.

## Known issue для ПП2

Если на smoke-test (Phase 4) A3 даст систематический pass на всех 4 артефактах — фиксируется как ПП2 follow-up: запросить B.4.1 `anti-examples-batch-02` у Cowork, заполнить `golden/anti-examples/conflicts/` минимум 3 примерами decoration of conflict / declaration without incentive, и пересмотреть калибровочный блок A3 с включением anti-examples.

## Связь со spec и D-002

- spec § 4.2 — структура файла субагента
- spec § 4.3 — структурированный YAML формат отчёта
- spec § 9.4.b — R-3 regression набор обязателен (calibration + holdout по A3)
- spec § 9.4.c — overlap detection между критиками
- spec § 9.5 — критические failures (RED → veto required)
- D-002 P-4 — `golden_unavailable_reason: category-bootstrap` в ПП1
- D-002 P-7 — качественная валидация `counter_test_attempted`
- D-002 P-8 — `effort: max` как механизм adaptive thinking budget
- D-002 P-10 — формулировка «RED обошёл скилл = провал»
- D-002 P-15 — `golden/anti-examples/conflicts/` пуст на момент Phase 2, A3 калибруется на bootstrap-пороге
