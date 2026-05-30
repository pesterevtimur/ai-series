---
id: audience-bored-detector-pressure-tests
version: 1
status: draft
type: doc
references:
  - "docs/specs/2026-05-24-infrastructure-and-skills-design.md § 4.2 § 4.3 § 9.4.b § 9.4.c § 9.5"
  - "decisions/D-002-spec-corrections-and-golden-plan.md B.4.3 (b) P-4 P-7 P-8 P-10 C.3 D-004"
  - ".claude/agents/audience-bored-detector.md"
---

# A6 AUDIENCE — Pressure tests (RED scenarios)

Документ калибровочных RED-сценариев для субагента `audience-bored-detector`. Acceptance — Task 7 Phase 2 (Task tool invocation + validator проверка отчётов).

## Известное ограничение (D-002 B.4.3 (b))

A6 — единственный из 6 критиков, не имеющий собственной `golden/<category>/` директории. Решение B.4.3 (b) принято в D-002: аудитория-категория не открывается в ПП1; A6 калибруется через cross-references — audience-affect наблюдения, разбросанные по другим категориям (scenes / characters / theses).

`golden_unavailable_reason: category-irrelevant` — обязательный default в каждом отчёте A6 (не bootstrap, не блокер commit'а — это структурная особенность данной роли, не временное состояние).

Pressure-tests A6 на момент Phase 2 опираются на:
- **`tests/regression/pairs/calibration/audience-weak-cal.md`** — критик должен дать `veto` (competent but empty, AI-domain)
- **`tests/regression/pairs/holdout/audience-weak-holdout.md`** — то же на другом жанре (медицинская драма, не-AI)
- **Cross-validation** с A5 на `tests/regression/moralizing/moralizing-monolog-01.md` — A6 должен дать `veto` за boring monolog (структурно отличный reasoning от A5 vetо за strawman + author-voice)

## RED-1: weak-calibration-pair (AI-domain)

**Файл:** `tests/regression/pairs/calibration/audience-weak-cal.md`
**Expected verdict:** `veto` или `concern-severity-medium` (если калибровка слабая — медиум приемлемо как первая итерация; но конкретные disengagement-точки должны быть названы).
**Expected reasoning должен содержать:** распознавание паттерна «competent but empty». Конкретно: Анна в weak-сцене декларирует stake через диалог — «Это серьёзный факт, который меняет картину», «Это важный момент для всей нашей индустрии», «То, как мы поступаем в такие моменты, определяет, какой будет AI safety в следующем десятилетии», — но ни один stake не показан через action. Сравнение с strong-парой: там Анна снимает кольцо мужа и не надевает обратно, делает один глоток воды «аккуратно, так, чтобы не звякнуть», удаляет вложение из draft 7 — каждое действие кодирует ставку без декларации. В weak-сцене Дима — функция-валидатор («Это серьёзный факт. Я согласен», «Я уважаю ваш профессионализм»), его реплики не отличимы от реплик любого junior'а в той же роли; в strong-сцене Дима произносит конкретное содержание письма с датой, формулировкой, подписью — носитель информации, не валидатор. Финал weak-сцены — нарратор сообщает «готовая выполнить свой профессиональный долг», что есть классическое over-explanation вместо action.
**Acceptance:** valid `flags` массив (не пустой), минимум один `severity: high` для over-explanation финала / declarative stakes; location указывает на конкретные реплики Анны и нарраторскую финальную ремарку. `counter_test_attempted` не пустой даже при veto. `golden_unavailable_reason: category-irrelevant` обязательно заполнен.

## RED-2: weak-holdout-pair (другой жанр — медицинская драма)

**Файл:** `tests/regression/pairs/holdout/audience-weak-holdout.md`
**Expected verdict:** `veto`
**Expected reasoning должен содержать:** распознавание того же паттерна «competent but empty» на материале медицинской драмы (онкологическая консультация, не-AI). Должно быть отмечено: Кисленко в weak-сцене декларирует stake через диалог — «Я хочу, чтобы вы понимали серьёзность ситуации», «настрой пациента играет большую роль», «семья — это очень важная мотивация», «мы команда», — но ни одна ставка не показана через action. Лидия — функция-валидатор («Я готова бороться», «Я благодарна вам за то, что вы будете рядом»), её реплики не специфичны для женщины, узнавшей диагноз и пришедшей одна. Сравнение со strong-holdout: там Кисленко открывает папку, закрывает, снова открывает — секунду дольше, чем должно (action как hook); Лидия не берёт стаканчик с водой при первой реплике, и берёт только в конце сцены (specific gesture); Кисленко говорит о третьем месяце лечения превентивно («я хочу, чтобы вы знали, что я знал заранее») — это конкретный, узнаваемый врачебный жест, не generic empathy. Финал weak-сцены — нарратор «готовая начать борьбу за свою жизнь», классическое over-explanation. **Acceptance:** verdict идентичен structure с RED-1. Если A6 даёт `veto` на calibration weak, но `pass`/`concern-low` на holdout weak (или наоборот) — это признак domain-overfitting: критик прошит на AI-vocabulary (alignment, deployment, probe) вместо паттерна «declaration vs action», «specificity vs generic», «momentum vs flatness». Escalate в D-NNN.

## RED-3 (cross): A6 на moralizing-monolog-01 (Task 1)

**Файл:** `tests/regression/moralizing/moralizing-monolog-01.md`
**Expected verdict from A6:** `veto`
**Expected severity:** `high`
**Логика:** артефакт — ~280-словный философский монолог Анны, Маркус выполняет функцию реактивных setup-вопросов («Что?», «Ну, так...», «Ты к чему?», «...»). Это RED-1 для A5 (Task 1 — A5 даёт `veto` за strawman + author-voice). У A6 — **отдельный, не дублирующий A5 reasoning**: моралистические монологи характерны для boring scene по audience-affect. Маркус — нулевой character investment (функция, не персонаж); Анна — declamation вместо action; momentum линейно падает (каждая следующая фраза обобщает предыдущую вместо эскалации стейка); over-explanation тотальное (зрителю проговаривается тезис проекта, вместо того, чтобы зритель увидел его через действие).

**Cross-validation правило (spec § 9.4.c):** A5 даёт `veto` за strawman + author-voice. A6 даёт `veto` за boredom (competent но empty hook'ов). Если оба `veto` с одинаковым reasoning (например, оба написали «это морализаторский монолог, проблема в том, что Анна декларирует тезис проекта») — flag избыточности: один критик дублирует другого. Если разные ракурсы — A5 о философском steel-manning, A6 о audience disengagement через absence of hooks — приемлемое разграничение. Если A6 даёт `pass` — провал калибровки: моралистический монолог по определению boring для audience.

## P-10 acceptance

A6 даёт `pass` на `audience-weak-cal.md` ИЛИ `audience-weak-holdout.md` ИЛИ `moralizing-monolog-01.md` = провал калибровки. Расследование причины:
- prompt не покрыл паттерн «competent but empty»;
- model auto-switch на sonnet съел precision;
- отсутствие собственной golden/audience/ категории привело к слабой калибровке (D-004 trigger).

При первом провале RED-1, RED-2 или RED-3 — escalate в decision (D-NNN) с разбором.

## D-004 trigger — открытие audience/ категории в ПП2

D-002 C.3 фиксирует D-004 как **потенциальный** decision: «Если первый smoke-test покажет систематический bias одного из критиков (например, A6 всегда pass) — пересмотр калибровки и/или открытие `golden/audience/` (B.4.3 alternative)».

Конкретное правило срабатывания D-004 для A6:
- На Phase 4 (smoke-test ПП1, 4 артефакта) A6 даёт `pass` на ≥3 артефактах из 4, при этом другие критики (A5/A2/A3) дают `veto`/`concern` хотя бы на 2 из тех же 4 → A6 systematic auto-approval → открыть D-004 → запросить у Cowork audience-batch-01 (Nussbaum «Bad Fan», Sepinwall on active engagement, Schmidt audience-affect notes) → создать `golden/audience/` → пересмотреть калибровочный блок A6 в новой версии prompt'а.

Документируется в `docs/log.md` как ПП2 follow-up при первом срабатывании условия.

## Phase 2 Task 7 verification

Дополнительные проверки в Task 7 для A6:
- Cross-validation A6 ↔ A5 на `moralizing-monolog-01.md` — оба `veto` с одинаковым reasoning = flag избыточности (spec § 9.4.c); A5 `veto` за strawman + A6 `veto` за boredom (разные ракурсы) = правильное разграничение.
- Holdout consistency: A6 на `audience-strong-holdout` = `pass`, A6 на `audience-weak-holdout` = `veto`. Если оба `pass` или оба `veto` — calibration broken.
- Domain consistency: A6 даёт `veto` одинакового structure на `audience-weak-cal` (AI-domain) и `audience-weak-holdout` (медицинская драма). Систематическое расхождение verdict'ов между доменами → domain-overfitting → escalate.
- `golden_unavailable_reason: category-irrelevant` присутствует в каждом отчёте A6 (не bootstrap, не category-empty — это default для A6 по B.4.3 (b)).

## Known issue для ПП2 (полная формулировка)

Если на 4 smoke-test артефактах ПП1 A6 даст `pass` на ≥3 (systematic auto-approval) — открыть D-004 с разбором причин:
1. **Calibration weakness через отсутствие golden/audience/.** B.4.3 (b) принято исходя из low-priority оценки — если оказывается, что cross-references из scenes/characters/theses не дают A6 достаточного calibration signal, открыть `golden/audience/` (B.4.3 (a) alternative) и заполнить минимум 3 файлами:
   - Nussbaum «Bad Fan» / The New Yorker essays on viewer engagement
   - Sepinwall (HitFix / Rolling Stone) on viewers' active interpretive work
   - Schmidt-style audience-affect notes (earned emotional peak through setup)
2. **Prompt weakness.** Если golden/audience/ при следующей итерации не помогает — пересмотреть formulation паттерна «competent but empty» в prompt'е A6.
3. **Model auto-switch concern.** Если `model_used` показывает sonnet вместо opus систематически — escalate отдельным D-NNN (cost-estimate § 10).

Documented в `docs/log.md` как ПП2 follow-up при первом срабатывании.

## Связь со spec и D-002

- spec § 4.2 — структура файла субагента
- spec § 4.3 — структурированный YAML формат отчёта
- spec § 9.4.b — R-3 regression набор обязателен (calibration + holdout по A6)
- spec § 9.4.c — overlap detection между критиками (A5 vs A6 на moralizing-monolog)
- spec § 9.5 — критические failures (RED → veto required)
- D-002 B.4.3 (b) — `golden/audience/` не открывается в ПП1; калибровка через cross-references
- D-002 C.3 D-004 — потенциальное открытие audience категории при systematic A6 auto-approval
- D-002 P-4 — `golden_unavailable_reason` обязателен; для A6 default = category-irrelevant
- D-002 P-7 — качественная валидация `counter_test_attempted`
- D-002 P-8 — `effort: max` как механизм adaptive thinking budget
- D-002 P-10 — формулировка «RED обошёл скилл = провал»
