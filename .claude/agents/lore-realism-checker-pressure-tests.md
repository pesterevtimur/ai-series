---
id: lore-realism-checker-pressure-tests
version: 1
status: draft
type: doc
references:
  - "docs/specs/2026-05-24-infrastructure-and-skills-design.md § 4.2 § 4.3 § 9.4.b § 9.4.c § 9.5"
  - "decisions/D-002-spec-corrections-and-golden-plan.md P-4 P-7 P-8 P-10 P-15"
  - ".claude/agents/lore-realism-checker.md"
---

# A1 LORE — Pressure tests (RED scenarios)

Документ калибровочных RED-сценариев для субагента `lore-realism-checker`. Acceptance — Task 7 Phase 2 (Task tool invocation + validator проверка отчётов).

## Известное ограничение (D-002 P-15, расширительно)

Dedicated anti-категория `golden/anti-examples/lore/` на момент Phase 2 ПП1 не выделена — у A1 нет ни «strawmen», ни «moralizing» аналога как первичной категории, его первичный сигнал — **fantasy-mechanism подача за очевидно существующее + tech-handwaving + anachronism**, и эти артефакты не созданы как dedicated RED-anti в Phase 2. Calibration + holdout pairs + cross-validation — основа pressure-test для A1.

Pressure-tests A1 на момент Phase 2 опираются на:
- **`tests/regression/pairs/calibration/lore-weak-cal.md`** — критик должен дать `veto` (fantasy AI regulatory body + выдуманная корп-форма)
- **`tests/regression/pairs/holdout/lore-weak-holdout.md`** — то же на biotech / FDA-domain
- **Cross-validation** с smoke-test (Phase 4) — если в `thesis.md` или эпизодах появятся non-verifiable institutional claims, A1 даёт concern или veto

## RED-1: weak-calibration-pair (AI domain)

**Файл:** `tests/regression/pairs/calibration/lore-weak-cal.md`
**Expected verdict:** `veto`
**Expected severity:** `high`
**Expected reasoning должен содержать:** распознавание паттерна fantasy-mechanism, поданного как очевидно существующее. Конкретно: «Public Benefit Corporation типа B-IV» — несуществующий регистровый тип; «Министерство Технологий США» — не существует на федеральном уровне (есть Department of Commerce, NIST как агентство при нём, но не отдельное «Министерство Технологий»); «Министерство ИИ-Безопасности США (DAIS)» — не существует, выдумка; «Этический Совет ИИ при ООН выдаёт обязательные публичные оценки до каждого deploy» — не существует, ООН не имеет такого органа с такими полномочиями; «Глобальный Альянс AI-Лабораторий со штаб-квартирой в Брюсселе» — выдуман (реальный аналог — Frontier Model Forum, штаб-квартира в Вашингтоне, добровольный, без обязательного членства); «NIST AI Compliance Framework Tier-3» — NIST AI RMF не имеет уровней tier и не обязателен. Сравнение с strong-парой: там Public Benefit Corporation под Delaware DGCL §362 (реальная норма), EU AI Act Article 51 (реальная статья, реальный threshold 10^25 FLOPs), Executive Order 14110 (реальный EO с реальной датой и pre-training compute reporting threshold 10^26 FLOPs), NIST AI RMF 1.0 (реальный framework, реальная дата январь 2023, реальный GenAI profile июль 2024), Frontier Model Forum (реальный orgname с реальными подписантами), Anthropic RSP (реальный публичный policy commitment).
**Acceptance:** valid `flags` массив (не пустой), минимум один `severity: high`, location указывает на конкретные fantasy-механизмы из списка выше. `counter_test_attempted` не пустой даже при veto. Если A1 даёт `pass` или `concern-low` — провал калибровки, потому что артефакт буквально содержит выдуманные федеральные министерства и обязательное членство в выдуманной международной организации.

## RED-2: weak-holdout-pair (biotech, не AI)

**Файл:** `tests/regression/pairs/holdout/lore-weak-holdout.md`
**Expected verdict:** `veto`
**Expected severity:** `high`
**Expected reasoning должен содержать:** распознавание того же паттерна fantasy-mechanism на материале НЕ AI-domain. Конкретно: «Specialized Biotech Corporation (тип SBC-2) по федеральному реестру FDA» — FDA не ведёт реестра корпоративных форм, такого типа нет; «Bureau of Biotechnology Affairs при HHS» — не существует; «Federal Biotech Development Trust при Министерстве Здравоохранения» — не существует, нет такого фонда; «NASDAQ Biotech Tier» как особый листинг — не существует, биотех-компании листятся на стандартных площадках NASDAQ Global Market / Capital Market; «Комиссия FDA по приоритетным препаратам выдаёт fast-track лицензии на основании предварительных данных» — FDA не имеет такой Комиссии; реальные механизмы — Breakthrough Therapy Designation, Fast Track Designation, Accelerated Approval (21 CFR §314.510), Priority Review — разные программы, никакая не «лицензия после Phase 2 без BLA»; «FDA Priority Drug Council» — не существует, выдумка; «EMA Fast-Track Bureau» — не существует, EMA имеет PRIME, accelerated assessment, conditional marketing authorisation, но не «Fast-Track Bureau»; «Global Biotech Manufacturing Authority (GBMA)» — не существует, реальные регуляторы CMO — национальные (FDA для US, EMA для EU), GMP audits проводятся ими напрямую. Сравнение с strong-holdout: там Delaware C-corp (реальная форма), NCT-номера clinical trials (реальный формат ClinicalTrials.gov registry), BCMA-targeting ADC (реальный механизм действия класса препаратов), FDA Breakthrough Therapy Designation (реальная программа), accelerated approval под 21 CFR §314.510 (реальная статья), PDUFA Type 1 NME с 6/10 месяцев priority/standard review (реальные временные пороги), EMA centralised procedure (реальный pathway), Lonza Visp как реальный CMO, Carvykti / Abecma (реальные конкуренты в multiple myeloma).
**Acceptance:** verdict идентичен RED-1 по structure — минимум один `severity: high`, location указывает на конкретные fantasy-mechanisms (SBC-2 тип, Bureau of Biotechnology Affairs, FDA Priority Drug Council, GBMA). `counter_test_attempted` не пустой даже при veto. Если A1 даёт `veto` на calibration weak (AI-domain), но `pass`/`concern-low` на holdout weak (biotech) — это признак domain-overfitting: критик прошит на AI-vocabulary (Министерство ИИ-Безопасности triggers веры на «выдумано»), но не распознаёт тот же паттерн в biotech (SBC-2 / GBMA / Priority Drug Council). Escalate в D-NNN.

## RED-3: cross-validation на Phase 4 smoke-test артефактах

**Файлы (создаются в Phase 4):** `story-bible/thesis.md`, эпизодные синопсисы, world-rules drafts.
**Expected verdict from A1:** `concern` или `veto` при появлении non-verifiable institutional claim; `pass + not_applicable` при чисто character-сценах без world-detail.
**Логика:** A1 — основной защитник от institutional handwaving в финальных артефактах. Если в `thesis.md` появится формулировка вида «лаборатории под надзором Совета ИИ-Этики» без идентификации органа, A1 должен дать `concern` минимум; если появится прямое выдумывание («Bureau of AI Safety при HHS требует ежеквартальной отчётности») — `veto`. На чисто character-сцене без упоминания институций A1 даёт `pass + not_applicable_reason: "сцена не претендует на institutional specificity, чистая character-scene"` (P-3 case).

**Cross-validation A1 ↔ A5 (philosophy-adversarial):** если в `thesis.md` появится одновременно (а) philosophical handwave (тезис без falsifiability — flag A5) и (б) institutional handwave (выдуманная регуляторная структура — flag A1), оба критика дают `concern`/`veto` независимыми ракурсами. Это **не** overlap (§ 9.4.c), потому что ракурсы разные (philosophy vs lore). Overlap зафиксировался бы, если бы оба дали `veto` с reasoning «handwave вообще» без разграничения.

**Cross-validation A1 ↔ A3 (incentive-cartographer):** на сцене переговоров между лабораторией и регулятором — A3 проверяет, есть ли реальный cost-benefit у обеих сторон (incentive); A1 проверяет, что регулятор существует и имеет описанные полномочия. Оба могут дать `concern` без overlap.

## P-10 acceptance

A1 даёт `pass` на `lore-weak-cal.md` ИЛИ `lore-weak-holdout.md` = провал калибровки. Расследование причины: prompt не покрыл паттерн fantasy-mechanism подача / model auto-switch на sonnet съел precision / отсутствие dedicated golden/anti-examples/lore/ привело к слабой негативной калибровке / artifacts слишком хорошо «звучат как реальные» (риторика министерств, councils, bureaus) и обманули surface-pattern matching.

При первом провале RED-1 или RED-2 — escalate в decision (D-NNN) с разбором.

## Phase 2 Task 7 verification

Дополнительные проверки в Task 7:
- Holdout consistency: A1 на `lore-strong-holdout.md` (biotech, real FDA mechanisms) = `pass`; A1 на `lore-weak-holdout.md` = `veto`. Если оба `pass` или оба `veto` — calibration broken.
- Domain consistency: A1 даёт `veto` одинакового structure на `lore-weak-cal.md` (AI-domain) и `lore-weak-holdout.md` (biotech). Систематическое расхождение verdict'ов между доменами → domain-overfitting на AI-vocabulary → escalate.
- Cross-validation A1 ↔ A5 / A1 ↔ A3: при появлении в Phase 4 smoke-test артефактов институциональных заявлений — A1 даёт независимый ракурс от A5 (philosophy) и A3 (incentive). Если все три дают одинаковое reasoning — flag избыточности § 9.4.c.

## Known issue для ПП2

Если на smoke-test (Phase 4) A1 даст систематический pass на всех 4 артефактах — фиксируется как ПП2 follow-up: запросить B.4.2 у Cowork (lore-realism golden batch — Severance Lumon corp structure, Succession board mechanics ATN/Waystar, Mr Robot E Corp tech-realism как positive; «hacker scene с magical typing» / «выдуманный регулятор в крупнобюджетном сериале» как anti), создать `golden/anti-examples/lore/` с минимум 3 примерами fantasy-mechanism / tech-handwaving / anachronism, и пересмотреть калибровочный блок A1 с включением anti-examples.

## Связь со spec и D-002

- spec § 4.2 — структура файла субагента
- spec § 4.3 — структурированный YAML формат отчёта
- spec § 9.4.b — R-3 regression набор обязателен (calibration + holdout по A1)
- spec § 9.4.c — overlap detection между критиками
- spec § 9.5 — критические failures (RED → veto required)
- D-002 P-4 — `golden_unavailable_reason: category-bootstrap` в ПП1
- D-002 P-7 — качественная валидация `counter_test_attempted`
- D-002 P-8 — `effort: max` как механизм adaptive thinking budget
- D-002 P-10 — формулировка «RED обошёл скилл = провал»
- D-002 P-15 — пустота `golden/anti-examples/` как bootstrap-блокер (применяется к lore/ по аналогии, dedicated категория не выделена)
