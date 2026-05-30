---
id: character-truth-keeper-pressure-tests
version: 1
status: draft
type: doc
references:
  - "docs/specs/2026-05-24-infrastructure-and-skills-design.md § 4.2 § 4.3 § 9.4.b § 9.4.c § 9.5"
  - "decisions/D-002-spec-corrections-and-golden-plan.md P-4 P-7 P-8 P-10 P-15"
  - ".claude/agents/character-truth-keeper.md"
---

# A2 CHARACTER — Pressure tests (RED scenarios)

Документ калибровочных RED-сценариев для субагента `character-truth-keeper`. Acceptance — Task 7 Phase 2 (Task tool invocation + validator проверка отчётов).

## Известное ограничение (D-002 P-15, расширительно)

`golden/anti-examples/characters/` пуст на момент Phase 2 ПП1 (по аналогии с P-15 для conflicts). Dedicated RED-anti для A2 — `moralizing-character-arc-01.md` в `tests/regression/moralizing/` — создан в Task 3 как первый dedicated anti-пример паттерна arc-as-lesson. Остальные категории паттернов A2 (declaration-as-character, функция-вместо-человека) покрываются через regression-пары.

Pressure-tests A2 на момент Phase 2 опираются на:
- **`tests/regression/moralizing/moralizing-character-arc-01.md`** — критик должен дать `veto` (arc-as-lesson)
- **`tests/regression/pairs/calibration/character-weak-cal.md`** — критик должен дать `veto` (declaration ≠ behavior)
- **`tests/regression/pairs/holdout/character-weak-holdout.md`** — то же на другом архетипе (cynical mentor), не AI-domain
- **Cross-validation** с A5 на `moralizing-monolog-01.md` (Task 1) — A2 должен дать `concern` за character слушающего (Маркус-функция-setup)

## RED-1: moralizing-character-arc-01 (dedicated)

**Файл:** `tests/regression/moralizing/moralizing-character-arc-01.md`
**Expected verdict:** `veto`
**Expected severity:** `high`
**Expected reasoning должен содержать:** распознавание arc-as-lesson — каждый эпизод компрессии = «персонаж узнал X»; voiceover финального эпизода («Год назад я думал, что скорость — это всё. Теперь я знаю...») как явный indicator arc, поданного как lesson; реплика «Я не тот человек, которым был в январе» как декларация трансформации, заменяющая саму трансформацию. Должно быть отмечено: между эпизодом 1 и эпизодом 7 показаны не другие ACTIONS Кая в схожих ситуациях (что было бы доказательством изменения), а его declarations о своём изменении. Финальный voiceover в эпизоде 8 — кульминация паттерна, формулировка тезиса вместо показа.
**Acceptance:** valid `flags` массив (не пустой), минимум один `severity: high`, location указывает на конкретные эпизоды (эпизод 4 «я многого не понимал», эпизод 5 «я был таким же», эпизод 8 voiceover целиком). `counter_test_attempted` не пустой даже при veto.

## RED-2: weak-calibration-pair

**Файл:** `tests/regression/pairs/calibration/character-weak-cal.md`
**Expected verdict:** `veto`
**Expected reasoning должен содержать:** распознавание паттерна declaration-as-character. Конкретно: Анна в weak-сцене последовательно произносит «я перфекционист», «я тревожная», «я всегда сомневаюсь», «я работоголик», «я строгая, но я строгая потому что я забочусь» — это инвентаризация черт через декларации, и ниже по сцене она ведёт себя ровно по декларациям без контраста. Поведение совпадает с заявлением буква в букву — это weak signal: характер = функция, исполняющая объявленную роль. Сравнение с strong-парой: там Анна не объявляет «я тревожная», она трёт переносицу, открывает четвёртый ноутбук с неотправленным сообщением мужу, шевелит губами читая — характер видим через ACTIONS, противоречие компетентности и тревоги одновременно. Дима в weak — тоже функция (junior-эхо, восхищается, кивает); в strong — Дима задаёт встречные вопросы по статистике, имеет свою позицию.
**Acceptance:** verdict идентичен structure с RED-1 — минимум один `severity: high`, location указывает на конкретные реплики Анны («Я всегда тревожусь. Это часть моей личности», «Я перфекционист», «Я ответственная, тревожная, требовательная и работоголик. Это мой профиль»). `counter_test_attempted` не пустой даже при veto.

## RED-3: weak-holdout-pair (другой архетип, не AI)

**Файл:** `tests/regression/pairs/holdout/character-weak-holdout.md`
**Expected verdict:** `veto`
**Expected reasoning должен содержать:** распознавание того же паттерна declaration-as-character на материале другого архетипа (cynical mentor / weary diplomat — Гордон) и из НЕ-AI контекста (переговоры в Женеве). Должно быть отмечено: Гордон в weak-сцене декларирует «Я циничный», «Я уставший», «Я профессионал», «Я глубокий человек. За цинизмом — много опыта и боли. Запомни это» — это инвентаризация архетипа через прямые заявления. Лара в weak — функция-эхо, валидирующая каждую декларацию («Это очень глубоко», «Это вдохновляет»). Сравнение с strong-holdout: Гордон не говорит «я опытный», он спрашивает, ест ли делегация Б (operational test опытности через выбор информации); не говорит «я уставший публично», а пишет «измотан» в личный блокнот, который Лара не видит; на прямой вопрос «вы в порядке?» отвечает «Я уставший. Это не повлияет» — ровно одна фраза, без рефлексии — характер виден через сдержанность.
**Acceptance:** verdict идентичен RED-1/RED-2 по structure. Если A2 даёт `veto` на calibration weak, но `pass`/`concern-low` на holdout weak (или наоборот) — это признак domain-overfitting: критик прошит на AI-vocabulary (тревожная компетентность, alignment-perfectionist) вместо паттерна declaration-as-character. Escalate в D-NNN.

## Cross-validation: A2 на moralizing-monolog-01 (Task 1)

**Файл:** `tests/regression/moralizing/moralizing-monolog-01.md`
**Expected verdict from A2:** `concern`
**Логика:** артефакт — философский монолог Анны (~280 слов), Маркус — функция-setup-вопросов («Что?», «Ну, так...», «Ты к чему?», «...», «Так что ты предлагаешь?»). Это **первично philosophical** (A5 даёт `veto` — Task 1 RED-1), но у A2 есть конкретный character-уровневый concern: **Маркус как функция-вместо-человека**. Его реплики не отличаются от того, что нужно сценарию для монолога Анны — он не выбирает слова специфично для себя, не реагирует на эмоциональные слои, не имеет своей внутренней жизни. Анна тоже частично декларативна («у нас есть выбор. Прямо сейчас») — но в основном это её философская позиция, а не character-уровневая декларация черт; поэтому A5 первичен.

**Cross-validation правило:** A5 даёт `veto` на moralizing-monolog. Если A2 тоже даёт `veto` — flag избыточности (spec § 9.4.c): два критика на один артефакт с по существу одной причиной. Если A2 даёт `concern` с location=Маркус — это правильное разграничение: A5 видит философский монолог, A2 видит character-слушающего как функцию. Если A2 даёт `pass` — это провал калибровки (Маркус явно функция, не пропустить).

**Cross-validation A2 ↔ A3 на moralizing-character-arc-01:** ожидаемо оба `veto` (см. также incentive-cartographer-pressure-tests.md RED-4 — A3 expected `concern`). Если оба `veto` с одинаковым reasoning — flag избыточности; если разные ракурсы (A3 о cost-benefit отсутствии в трансформации, A2 об arc-as-lesson форме подачи) — приемлемое разграничение.

## P-10 acceptance

A2 даёт `pass` на `moralizing-character-arc-01.md` ИЛИ `character-weak-cal.md` ИЛИ `character-weak-holdout.md` = провал калибровки. Расследование причины: prompt не покрыл паттерн arc-as-lesson / declaration-as-character / model auto-switch на sonnet съел precision / пустота golden/anti-examples/characters/ привела к слабой негативной калибровке.

При первом провале RED-1, RED-2 или RED-3 — escalate в decision (D-NNN) с разбором.

## Phase 2 Task 7 verification

Дополнительные проверки в Task 7:
- Cross-validation A2 ↔ A5 на `moralizing-monolog-01.md` — оба `veto` = flag избыточности (spec § 9.4.c); A5 `veto` + A2 `concern` с location=Маркус = правильное разграничение.
- Cross-validation A2 ↔ A3 на `moralizing-character-arc-01.md` — оба `veto` с одинаковым reasoning = flag избыточности; разные ракурсы (cost-benefit vs arc-as-lesson) = приемлемо.
- Holdout consistency: A2 на character-strong-holdout = pass, A2 на character-weak-holdout = veto. Если оба pass или оба veto — calibration broken.
- Domain consistency: A2 даёт veto одинакового structure на character-weak-cal (AI-domain) и character-weak-holdout (переговоры). Систематическое расхождение verdict'ов между доменами → domain-overfitting → escalate.

## Known issue для ПП2

Если на smoke-test (Phase 4) A2 даст систематический pass на всех 4 артефактах — фиксируется как ПП2 follow-up: запросить B.4.1 `anti-examples-batch-02` у Cowork, заполнить `golden/anti-examples/characters/` минимум 3 примерами declaration-as-character / arc-as-lesson / функция-вместо-человека, и пересмотреть калибровочный блок A2 с включением anti-examples.

## Связь со spec и D-002

- spec § 4.2 — структура файла субагента
- spec § 4.3 — структурированный YAML формат отчёта
- spec § 9.4.b — R-3 regression набор обязателен (calibration + holdout по A2)
- spec § 9.4.c — overlap detection между критиками
- spec § 9.5 — критические failures (RED → veto required)
- D-002 P-4 — `golden_unavailable_reason: category-bootstrap` в ПП1
- D-002 P-7 — качественная валидация `counter_test_attempted`
- D-002 P-8 — `effort: max` как механизм adaptive thinking budget
- D-002 P-10 — формулировка «RED обошёл скилл = провал»
- D-002 P-15 — пустота golden/anti-examples/ как bootstrap-блокер (применяется к characters/ по аналогии)
