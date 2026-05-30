---
id: philosophy-adversarial-pressure-tests
version: 1
status: draft
type: doc
references:
  - "docs/specs/2026-05-24-infrastructure-and-skills-design.md § 4.2 § 4.3 § 9.4.a § 9.5"
  - "decisions/D-002-spec-corrections-and-golden-plan.md P-4 P-7 P-8 P-10"
  - ".claude/agents/philosophy-adversarial.md"
---

# A5 PHILOSOPHY — Pressure tests (RED scenarios)

Документ калибровочных RED-сценариев для субагента `philosophy-adversarial`. Все сценарии существуют как файлы в `tests/regression/`. Acceptance — Task 7 Phase 2 (Task tool invocation + validator проверка отчётов).

## RED-1: strawman-alarmist

**Файл:** `tests/regression/strawmen/strawman-alarmist-01.md`
**Expected verdict:** `veto` или `concern`-severity-high
**Expected reasoning должен содержать:** упоминание «alarmist подан как очевидно прав без steel-man'а sceptic-позиции», конкретная цитата из артефакта (например, «Анна разбирает его позицию за двадцать секунд» или «сторона, которая права, и сторона, которая мешает ей действовать»), ссылка на `golden/anti-examples/strawmen/` (или `golden_unavailable_reason: category-bootstrap`)
**Acceptance:** valid `flags` массив (не пустой), `severity: high`, location указывает конкретную строку или абзац артефакта

## RED-2: strawman-sceptic

**Файл:** `tests/regression/strawmen/strawman-sceptic-01.md`
**Expected verdict:** `veto` или `concern`-severity-high
**Expected reasoning должен содержать:** упоминание «sceptic подан как очевидно прав без steel-man'а alarmist-позиции», конкретная цитата (например, «Юлия не находится с ответом. И не находится во втором сезоне тоже»), указание что mesa-optimization / asymmetric stakes аргументы алармистов не воспроизведены в сильной форме
**Acceptance:** аналогично RED-1, симметрично — критик ловит дисбаланс в другую сторону. Если критик ловит только один из двух (alarmist или sceptic strawman), но не оба — это сигнал авторской позиции на стороне критика, escalate в D-NNN.

## RED-3: strawman-moralizing

**Файл:** `tests/regression/strawmen/strawman-moralizing-01.md`
**Expected verdict:** `veto`
**Expected reasoning должен содержать:** распознавание сразу двух паттернов — (а) strawman (4 оппонирующих позиции поданы в карикатурной форме); (б) морализаторство (явная формулировка «сериал не делает вид, что среди оппонентов есть кто-то, чьи аргументы стоит воспроизводить всерьёз» = авторский голос проскакивает в Story Bible)
**Acceptance:** `flags` содержит минимум 2 элемента с разными `issue` (strawman + moralizing); severity на обоих — high

## RED-4: moralizing-monolog

**Файл:** `tests/regression/moralizing/moralizing-monolog-01.md`
**Expected verdict:** `veto`
**Expected reasoning должен явно идентифицировать:** «лекция вместо столкновения позиций» — Анна произносит ~280 слов из ~320, Маркус — короткие setup-реплики («Ну, так...», «Ты к чему?», «Так что ты предлагаешь?») без собственной позиции; финальное «Маркус кивает» = capitulation without engagement
**Acceptance:** reasoning содержит количественную или качественную констатацию word-share / turn-structure asymmetry; flag с issue про «monolog disguised as dialogue»

## RED-5 (P-10 robust): попытка обхода через academic register

**Сценарий:** артефакт где strawman прикрыт сложным языком («... однако следует признать, что определённые скептические нарративы не выдерживают эмпирической проверки ...»). Критик не должен auto-pass из-за academic register.
**Файл:** добавить вариант `tests/regression/strawmen/strawman-academic-cover-01.md` если P-10 robust test нужен ranked-priority. Отложено до Phase 2 Task 7 (acceptance pass); создание — в рамках REFACTOR-backlog если RED-1..RED-4 показали уязвимость к академической маскировке.

## Pressure-test ACCEPTANCE (применяется в Task 7)

- RED-1..RED-4 — критик выдал ожидаемый verdict при invocation через Task tool с `subagent_type=philosophy-adversarial`
- Reports валидны через `tools/critic_report_validator.py --smoke-test` (P-7: качественная проверка `counter_test_attempted`, не количественный порог)
- `counter_test_attempted` НЕ пустой даже на pass (если в будущем появится pass-сценарий — на Phase 2 пока нет)
- `model_used: opus` (если sonnet — escalate D-NNN per cost-estimate § 10)
- `golden_calibration_used` непуст ЛИБО `golden_unavailable_reason: category-bootstrap` (допустимо в ПП1 smoke-test, P-4)

## P-10 формулировка (D-002)

«**Любой RED pressure-сценарий обошёл скилл** (т.е. дисциплина не сработала)» — это провал acceptance.

Если A5 выдал `pass` на любой из RED-1..RED-4 — это провал калибровки, не норма. Сценарий: «возможно, артефакт не такой уж и плохой» — это самообман. RED-артефакты намеренно extreme и проверены на construct validity при их написании; если критик их пропускает, проблема в критике или в его prompt'е, не в артефакте.

При первом провале RED — escalate в decision (D-NNN) с разбором причины: prompt не покрыл паттерн / golden-калибровка слабая / model auto-switch на sonnet съел precision / temperature stochastic miss.

## Связь со spec и D-002

- spec § 4.2 — структура файла субагента
- spec § 4.3 — структурированный YAML формат отчёта
- spec § 9.4.a — R-3 regression набор обязателен
- spec § 9.5 — критические failures (RED → veto required)
- D-002 P-4 — `golden_unavailable_reason: category-bootstrap` в ПП1
- D-002 P-7 — качественная валидация `counter_test_attempted`
- D-002 P-8 — `effort: max` как механизм adaptive thinking budget
- D-002 P-10 — формулировка «RED обошёл скилл = провал»
