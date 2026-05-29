---
id: D-002
title: Правки spec ПП1 (15 пунктов) и план до-наполнения golden корпуса
date: 2026-05-24
revised: 2026-05-25
revision: v2
revision_history:
  - "v1 (2026-05-24): первая редакция — P-1..P-10 + B.1..B.6 audit на 8 партий / 30 файлов"
  - "v2 (2026-05-25): добавлены P-11..P-15 после deeper audit; Часть B переписана после Cowork-итерации 2026-05-24 (19 партий, 70 файлов); большая часть B.4 запросов v1 закрыта Cowork-ом самостоятельно"
status: accepted
accepted_on: 2026-05-29
decided_by: Claude Code (предложено), Timur (strategic acceptance 2026-05-29)
relates_to:
  - decisions/D-001-bootstrap-architecture.md
  - docs/specs/2026-05-24-infrastructure-and-skills-design.md
adversarial_review:
  type: timur-strategic-acceptance
  date: 2026-05-29
  note: |
    Codex выключен (D-001 B-1); внутренние субагенты ещё не существуют (ПП1 не имплементирован);
    промежуточный режим адверсариального прохода — strategic acceptance Тимура — выполнено.
    Cowork-партии B.4.1 (anti-examples-batch-02) и B.4.2 (institutional voice) сознательно
    пропущены — flagged risk: A3/A5 R-3 калибровка на нижнем bootstrap-пороге, добор отложен
    до ПП2 если smoke-test покажет систематический pass / confuse этих критиков.
---

# D-002 — Правки spec ПП1 + план до-наполнения golden корпуса

## Контекст

**v1 (2026-05-24).** После fresh re-read спека и D-001 (без шлейфа предыдущих обсуждений) и audit состояния `raw/_cowork-dumps/` выявлены:

- **10 точек коррекции** в spec / D-001 — 4 прямых противоречия, 5 недооценённых рисков, 1 двусмысленность формулировки. Все либо блокируют smoke-test, либо смещают acceptance criteria в сторону overfit или pseudo-success.
- **Существенный перекос состава golden:** категория `scenes` saturated; `conflicts` пуст полностью; anti-examples — 3 файла на весь корпус против цели 18-30 (5.7 спека).

**v2 (2026-05-25).** После deeper audit golden материалов (9 файлов оригинального контента + 19 manifests + cumulative report) и завершения Cowork-итерации 2026-05-24 (19 партий, 70 content-файлов) добавлены **5 новых правок P-11..P-15** и **существенно переписана Часть B**: большая часть Cowork-запросов v1 закрыта Cowork-ом самостоятельно без явного запроса (`conflicts-batch-01`, sceptic balance, characters diversity); остаточный gap — anti distribution (`conflicts` anti = 0, `adversarial-passes` anti = 0) и institutional voice в adversarial-passes.

D-002 — пакет конкретных правок spec/D-001 + план остаточных Cowork-партий. Не replan ПП1 (scope сохраняется), а его уточнение **перед** writing-plans implementation.

---

## Часть A. Правки spec и D-001 (P-1..P-10)

### P-1. A5 — часть `adversarial-review-pass`, отдельный `philosophy-stress-test` отменяется

**Проблема.** Section 3.3 включает A5 в `adversarial-review-pass`; Section 8.1 разводит `philosophy-stress-test` (шаг 3) и `adversarial-review-pass` (шаг 5, без A5). При буквальном чтении A5 вызывается дважды на каждый артефакт.

**Принято.** A5 вызывается только через `adversarial-review-pass`. Скилл `philosophy-stress-test` удаляется из Section 3.3 (становится 8 скиллов вместо 9). Поток A шаг 3 удаляется; нумерация шагов 4-13 сдвигается на −1.

**Cost-impact:** −1 Opus+ext.thinking вызов на артефакт smoke-test (≈ −4 за весь ПП1).

---

### P-2. R-1 generation — это шляпы в основной сессии, не параллельные субагенты

**Проблема.** R-1 требует 3 параллельных Task-вызова с уклонами LORE/PHILOSOPHY/CHARACTER-dominant, но в Section 4 описаны только 6 критиков (все READ-ONLY). Генератор-субагентов нет.

**Принято.** R-1 — 3 **последовательных** "шляпы" внутри основной Claude Code сессии: шоураннер запускает три prompt-цикла с разными стартовыми установками, между ними — явный context-marker ("сейчас я возвращаюсь к LORE-уклону…" / отдельный сессионный пасс через `/clear` если эффективно). Принцип divergence сохраняется (3 структурно разных стартовых промпта); параллельность теряется.

**Альтернатива (отклонена):** 3 generator-субагента с `Write/Edit`. Нарушает инвариант "шоураннер — единственный writer" (8.3.1).

---

### P-3. Smoke-test — 4 артефакта, не 3 (добавляется мини-сценка для A4)

**Проблема.** Section 9.4 требует все 6 субагентов на каждом из 3 артефактов; но A4 калибруется на парах реплик `**ИМЯ:** реплика`, а тезис/character-sheet/world-rules — не диалоги.

**Принято.** Smoke-test = 4 артефакта:

1. `story-bible/thesis.md` (~150 слов)
2. `story-bible/world-rules.md` (5 правил мира)
3. `characters/<one>.md` (1 character-sheet — "тревожная компетентность")
4. **(новое)** `scenes/smoke-test-dialogue.md` (минимальная сценка с 2-3 говорящими, 300-500 слов)

A1, A3, A2, A5, A6 — на всех 4. A4 — только на 4-м; на остальных в отчёте `adversarial-review-pass` явно фиксируется `not_applicable: <reason>` для A4 (валидно через `critic_report_validator.py`).

---

### P-4. `golden_calibration_used: []` валиден при наличии `golden_unavailable_reason`

**Проблема.** `critic_report_validator.py` требует `golden_calibration_used ≥ 1`. На пустых категориях golden (`characters/`, `theses/`, `conflicts/` на момент smoke-test) — FAIL → infinite retry.

**Принято.**

1. Поле `golden_calibration_used` остаётся обязательным.
2. `[]` валиден **только** при непустом `golden_unavailable_reason:` ∈ { `category-empty`, `category-bootstrap`, `category-irrelevant` }.
3. `golden_unavailable_reason: category-bootstrap` допустимо **только** во время smoke-test ПП1; после ПП1 acceptance — блокер commit'а.

---

### P-5. R-3 регрессия разделяется на calibration set и holdout set

**Проблема.** TF-IDF порог `voice_dissimilarity.py` калибруется на R-3 парах (11.5.3); те же пары — acceptance criterion (9.5). Circular validation, overfit гарантирован.

**Принято.**

1. `tests/regression/pairs/` делится на два поднабора, документировано в README:
   - `calibration/` — на этих парах подгоняются любые числовые пороги (TF-IDF и т.д.); ≈50% пар.
   - `holdout/` — на этих парах проверяется acceptance; ≈50% пар; материал из других шоу/контекстов, не пересекается с calibration.
2. Acceptance 9.5.b (verdicts разошлись на парах) применяется только к holdout.
3. Если holdout-набор недостаточен на момент smoke-test — фиксируется в `tests/regression/README.md` через явное `regression_unavailable_reason:` и acceptance ослабляется с явным флагом риска.

---

### P-6. Cost-estimate ПП1 в долларах — обязательный артефакт перед writing-plans

**Проблема.** R-4 "explicit cost commitment" принят Тимуром без числа.

**Принято.** До writing-plans ПП1 создаётся `docs/cost-estimate-pp1.md` со структурой:

- Один прогон Потока A на 1 артефакт: разбивка по вызовам (R-1 шляпы × 3, A1, A2, A3, A5, A6, плюс A4 для сцены) × средний размер input/output × тариф Opus 4.7 1M (+extended thinking).
- Smoke-test = 4 артефакта × Поток A + regression-runs + pressure-tests.
- Резерв на пересборку (≥2 повтора по правкам критиков).
- Итоговый долларовый коридор.

Без этого документа writing-plans не стартует. Пункт уходит в acceptance 9.1 (структурные критерии).

---

### P-7. 9.4 порог "≥3 concern/veto" заменяется на качественную валидацию `counter_test_attempted`

**Проблема.** "Суммарно ≥3 concern/veto на 18 verdicts" создаёт обратный incentive: шоураннер манипулирует промпты критиков, чтобы поднять флаги.

**Принято.** Section 9.4 переформулируется:

- **Старое:** "Если все 18 verdicts = pass — это сигнал auto-approval bias".
- **Новое:** "Для каждого `verdict: pass` поле `counter_test_attempted` обязано содержать (а) что именно искал, (б) почему именно это, (в) почему не нашёл. `critic_report_validator.py` проверяет наличие всех трёх элементов структурно. Количественный порог concern/veto более не acceptance criterion."

Auto-approval bias детектируется качеством counter_test, не количеством флагов.

---

### P-8. Open question 11.5.1 (extended thinking в frontmatter) решается до writing-plans

**Проблема.** Поддержка `thinking_budget:` или эквивалента в `.claude/agents/<name>.md` — открытый вопрос, на котором висит вся R-4 архитектура.

**Принято.** До writing-plans ПП1:

1. Claude Code проверяет через dummy-эксперимент + актуальную документацию Anthropic / Claude Code release notes.
2. Результат → `docs/extended-thinking-mechanism.md`.
3. Если frontmatter не поддерживает явно — все 6 субагентов получают инструкцию "ultrathink перед каждым выводом" в system prompt как fallback, явно зафиксировано в каждом `.claude/agents/<name>.md`.
4. Спек 11.5.1 обновляется на status: resolved со ссылкой на исследовательский документ.

---

### P-9. Отчёты критиков сохраняются на диск немедленно — concern resolution переживает auto-compaction

**Проблема.** Контекст-budget шоураннера большой; при auto-compaction отчёты критиков (нужные R-2 для `concern_resolution_validator.py`) могут потеряться из активного контекста.

**Принято.**

1. Каждый полный YAML-отчёт критика записывается в `tmp/critic-reports/<artifact-id>/<critic>-<timestamp>.yaml` **сразу** после получения от Task-tool. Папка `tmp/` в `.gitignore`, файлы физически существуют.
2. `concern_resolution_validator.py` читает из этой папки, не из контекста сессии.
3. После commit артефакта папка перемещается в `docs/critic-reports-archive/<artifact-id>/` (не gitignored — для аудита).

**Дисковая нагрузка:** ничтожна; контекст-budget — снимаемая зависимость.

---

### P-10. Section 9.5 строка про pressure-test — переформулировка

**Проблема.** "Любой discipline-BLOCKER скилл прошёл хотя бы один RED pressure-сценарий" — двусмысленно (прошёл = выдержал? или прошёл = обошёл?).

**Принято.** Замена: "Любой RED pressure-сценарий **обошёл** discipline-BLOCKER скилл (т.е. дисциплина не сработала)".

---

### P-11. Cowork mandate — описание эталонов, не проектирование сериала

**Проблема.** Каждый файл из `_cowork-dumps/` содержит блок «Что нужно от шоураннера» с **прямыми рекомендациями к нашему сериалу** (Schmidt: «спроектировать catharsis-сцены через истощение исполнительной мощности»; Brooker: «применить Third limb metaphor — одна из ключевых сцен может разворачивать эту метафору»; Fleabag/Damon: 14 прямых указаний от «AI-narrator with fourth-wall break» до «discomfort + fooled-feeling audience-affect aim»).

Это выходит за рамки spec § 5.4 («Researcher описывает что в сцене сильно, шоураннер пишет наш собственный пример») и фактически смещает creative authorship на внешнего агента. Также противоречит D-001 § B-1 (Codex выключен потому что «адверсариальная критика полностью переезжает на внутренние субагенты»): если Cowork решает что делать, она де-факто внешний автор.

**Принято.**

1. В `docs/cowork/prompt.md` добавляется блок «Mandate boundary»: Cowork описывает эталоны и формулирует **возможные применения** (опционально, как notes), но **не предписывает дизайн нашего сериала**.
2. Блок «Что нужно от шоураннера» в файлах остаётся, но переименовывается в **«Возможные применения (notes, не предписания)»**. Скилл `add-golden-example` при обработке batch'а сохраняет этот блок как secondary, не как acceptance criterion.
3. Шоураннер при обработке через `add-golden-example` явно **отделяет описание эталона** (идёт в golden) от **рекомендаций к нашему сериалу** (идёт в `docs/cowork-notes/<batch>.md` — для возможного использования в ПП2/ПП3 как seed-материал, но не как авторитет).
4. Существующие 70 файлов в `_cowork-dumps/` обрабатываются по новому правилу при `add-golden-example` (не требуется пересборка batch'ей).

---

### P-12. Multi-category placement — primary + secondary через frontmatter

**Проблема.** Каждый положительный файл предлагается на 2-3 категории golden (Karnofsky → `adversarial-passes` + `theses` + `dialogues`; Brooker → `dialogues` + `theses` + `characters`; Fleabag/Damon → `characters` + `scenes` + `dialogues` + `theses`). Спек `add-golden-example` (§ 3.3) workflow не определяет, как материал размещается в нескольких категориях.

**Принято.** Frontmatter golden-файла расширяется:

```yaml
primary_category: characters
secondary_categories: [scenes, dialogues, theses]
```

- Файл физически лежит в `golden/<primary_category>/`.
- `golden_freshness.py` учитывает файл при подсчёте «есть ли материал в категории X»: считается для primary полностью + для secondary с весом 0.5.
- Skill `add-golden-example` валидирует, что `primary_category` ∈ 6 валидных категорий, `secondary_categories` ⊂ оставшихся 5, без дубликатов.
- Критик при калибровке через `golden_calibration_used` указывает файл с его primary_category, не вычитает «дробной» доли.

**Альтернатива (отклонена).** Symlinks `golden/dialogues/<file>.md → golden/characters/<file>.md`. Отклонено из-за платформенной нестабильности (symlinks плохо работают на Windows без elevated rights; в git они хранятся как regular files с указателем).

---

### P-13. «Возможные anti-lessons» в positive ≠ real anti-examples

**Проблема.** Каждый positive-файл содержит блок «Возможные anti-lessons из источника» — это derived mental exercise (что было бы плохо, если бы Sorkin сделал X), не реальный anti-материал. При беглом просмотре можно посчитать, что anti-corpus уже укомплектован — но R-3 regression set (§ 9.4.a) требует **отдельных файлов с `example_type: anti-example`**.

**Принято.**

1. `critic_report_validator.py` при подсчёте anti для калибровки учитывает **только файлы с `example_type: anti-example` в frontmatter**.
2. Derived anti-lessons из positive файлов **не считаются** для acceptance criterion 9.4.a / 9.5.
3. Скилл `add-golden-example` при обработке positive файла **переносит** блок «Возможные anti-lessons» в `docs/cowork-notes/derived-anti-lessons/<file>.md` (отдельный архив, не часть golden), чтобы шоураннер мог использовать их как **подсказки для будущих anti-партий**, но не как замену.
4. В `golden/README.md` явно фиксируется: «derived anti-lessons ≠ anti-example, не пересчитываются для acceptance».

---

### P-14. Diversity warnings в `golden_freshness.py`

**Проблема.** Перекосы выявлены post-hoc по партиям: scenes-batch-01 — 3 из 4 positive Mr Robot; scenes-batch-04 — 3 из 3 Mad Men, причём Schmidt × 2. Это не блокирует acceptance, но **критики калибруются на monoculture** в части категорий.

**Принято.** `golden_freshness.py` добавляются warnings (не fail):

- `author_share > 50%` в любой категории → warning «author X dominates Y category».
- `show_share > 60%` в категории `scenes` / `characters` / `conflicts` → warning «show X dominates Y».
- Одна партия (по `batch:` поле frontmatter) содержит ≥3 файла одного `source_author` → warning «author X concentrated in batch Y».

Warnings выводятся в JSON-отчёт `golden_freshness.py` отдельной секцией `diversity_warnings:`. Они **не** блокируют commit, но шоураннер обязан их прочесть и либо признать (через явный `diversity_acknowledged: <reason>` в `golden/README.md`), либо запросить добивочную партию.

---

### P-15. Anti-corpus completeness — dedicated anti для conflicts и adversarial-passes

**Проблема (на 2026-05-25).** Cowork собрал anti-examples-batch-01 с 4 файлами, но distribution: 1 theses (Lost), 1 dialogues (TD2), 2 characters (Dexter, GoT). **`conflicts` anti = 0, `adversarial-passes` anti = 0.** Это значит R-3 regression set для критиков A3 (`incentive-cartographer`) и A5 (`philosophy-adversarial`) недокалиброван — на двух из шести критиков нет anti-материала для калибровки.

Также: 3 из 4 anti — про «плохие финалы» (Lost / Dexter / GoT). Тип провала «плохой финал» переcollected, типы «voice-bleed внутри сезона», «strawman в дискуссии», «morализаторство в монологе» — недокачаны.

**Принято.** Запросить у Cowork **`anti-examples-batch-02`** с явным распределением:

- `conflicts` anti — 2-3 файла (false stakes / soap-opera structural collapse внутри сезона, не финал; например критики plot-driven seasons of The Walking Dead или late Westworld)
- `adversarial-passes` anti — 2-3 файла (steel-man «слабо» обеих позиций: плохой alarmist, плохой sceptic; не сатира — см. инструкцию ниже)
- `dialogues` anti voice-bleed specifically — 1-2 файла (House of Cards Underwood-voice critique; либо Aaron Sorkin Newsroom revisited на voice level, не на moralizing level)
- `adversarial-passes` Anthropic/institutional voice (positive) — 2 файла (Constitutional AI paper, Sleeper Agents, RSP — institutional voice, отличный от individual blogger voice)

**Особая инструкция Cowork для adversarial-passes anti.** «Steel-man слабо», не сатира: «как бы выглядел плохой alarmist, если бы он реально пытался быть прав, но не справился» / «как бы выглядел плохой sceptic в той же ситуации». Не пародия на позицию, а её слабая искренняя версия. Иначе anti-example становится straw-man самого strawman'а.

---

## Часть B. План до-наполнения golden корпуса

### B.1 Audit состояния на 2026-05-25 (после завершения Cowork-итерации 2026-05-24)

Между первой редакцией D-002 (2026-05-24) и этой (2026-05-25) Cowork завершил большую итерацию: 19 партий, 70 content-файлов + 19 manifests + 1 cumulative report = 89-90 файлов. Состояние golden корпуса принципиально изменилось.

**Cumulative status по spec § 5.7 целям (5-8 positive + 3-5 anti на категорию):**

| Категория | Positive | Anti | Цель | Статус |
|---|---|---|---|---|
| `scenes` | 19 | 3 (в b01) | 5-8 + 3-5 | **Saturated** |
| `characters` | 20 | 2 (в anti-batch-01: Dexter, GoT) | 5-8 + 3-5 | **Покрыта** (20 файлов / 11 шоу) |
| `conflicts` | 10 | 0 | 5-8 + 3-5 | **Положительно покрыта**, anti = 0 |
| `dialogues` | 7 | 1 (TD2 в anti-batch-01) | 5-8 + 3-5 | Покрыта, anti недо- |
| `adversarial-passes` | 7 | 0 | 5-8 + 3-5 | Balanced (alarmist + sceptic), anti = 0 |
| `theses` | 3 | 1 (Lost в anti-batch-01) | 5-8 + 3-5 | Открыта, по нижней границе |
| `gap-filling` | 5 | — | — | bonus material (Sopranos closure, Yudkowsky lethalities, Mittell Wire) |
| **Anti суммарно** | — | **7** | 18-30 | **Существенный gap для R-3** |

**Diversity (по `_OVERALL-REPORT-2026-05-24.md`).** 17 шоу покрыто характерами + конфликтами; gender gap закрыт (Carmela, Peggy, Fleabag, Nora Durst, Kim Wexler, Shiv Roy = 6+ female centrals); origin gap частично закрыт (Fleabag — UK; остальные US prestige TV). 7 AI-safety primary voices (Karnofsky, Raemon, Marcovitz, Yudkowsky direct lethalities 1-6, Mitchell, LeCun via Weldon, Hanson).

### B.2 Что Cowork закрыл сам (до утверждения D-002 v1)

Большая часть **B.4.1-B.4.3** запросов из первой редакции D-002 уже выполнена Cowork-ом без явного запроса от Тимура:

- ~~**B.4.1 (старая) `conflicts-batch-01` HIGHEST priority.**~~ **Выполнено.** `conflicts-batch-01` (6 файлов) + `conflicts-batch-02` (4 файла) = 10 файлов. Succession siblings, Stringer-Avon, Walt-Hank, Severance innie/outie, Mr Robot revolution-trap, Mad Men 7 pitches, GoT 5 kings — практически весь шорт-лист B.4.1 закрыт.
- ~~**B.4.3 (старая) `adversarial-passes-batch-03` sceptic voices.**~~ **Выполнено через `adversarial-passes-batch-02`.** Mitchell LLM reasoning, LeCun via Weldon, Hanson «still don't get foom» — прямой sceptic spectrum. Balanced steelman achieved.
- ~~**P-15 (первой редакции) characters diversity.**~~ **Выполнено через characters-batch-04 и -05.** Carmela, Peggy, Fleabag, Nora, Kim, Shiv, BoJack — gender и архетипическое разнообразие достигнуто.
- **Anti-vacuum частично закрыт.** Появилась `anti-examples-batch-01` (4 файла: Lost finale, TD2 dialogue, Dexter finale, GoT S8). Но distribution неравномерное (см. B.4 ниже).
- **Theses открыта** — `theses-batch-01` (Syme «Trouble With Golden Age», Keeble+Thomas «New Literary TV», Herrman «Asshole Theory»).

**Следствие.** Запросы B.4.1 и B.4.3 первой редакции D-002 снимаются — отмечено в Части C operational sequence.

### B.3 Качество — расширенный sample

Проверены: все 19 манифестов + `_OVERALL-REPORT-2026-05-24.md` + 9 файлов оригинального контента из разных батчей (Karnofsky / Knibbs-Sorkin / Esmail / Krueger-GoT / Brooker / Raemon / Schmidt / Fleabag-Damon / Mancuso-TD2-anti). Картина:

- **+** Frontmatter консистентный во всех 9 проверенных файлах: 15 полей, заполнены везде, верификация через Web Fetch явно зафиксирована.
- **+** Citation budget соблюдается: реально 300-450 слов прямых выдержек при заявленном ≤500, с запасом.
- **+** Шаблон файла унифицирован (8 блоков): summary → ключевые выдержки → элементы ремесла → кандидат-категория → возможные anti-lessons → что нужно от шоураннера → метаданные верификации.
- **+** Cross-references работают (`[[scenes-creativescreenwriting-mrrobot-esmail]]` цитируется из 3 других файлов; все ссылки указывают на реально существующие материалы).
- **+** Anti-examples — **реальные anti** (Mancuso даёт конкретные bad lines, не общие правила). Это закрывает риск, что вместо anti окажутся derived anti-lessons.
- **+** Cowork честно фиксирует пробелы: «Что не нашлось» в каждом манифесте; cumulative report явно перечисляет «не покрыто / отложено» (Atlanta, The Crown, Anthropic alignment papers, audience category, etc).
- **+** Cumulative cross-cutting themes по 10 темам (pain-as-love compass, active-complicity-vs-passive-failure, stasis-as-feature, etc) — Cowork делает мета-агрегацию по всему корпусу, а не только per batch.
- **−** Перекос anti-batch-01 на «плохие финалы» (3 из 4 — Lost / Dexter / GoT финалы). Voice-bleed внутри сезона / strawman в дискуссии / moralizing монолог — типы провала недо.
- **−** `conflicts` и `adversarial-passes` anti = **0**. Это блокирует R-3 калибровку A3 и A5.
- **−** «Возможные anti-lessons» в positive файлах (см. P-13) могут вводить в заблуждение при поверхностном audit'е.

**Вывод.** Качество отдельного файла — образцовое, держится при scale-up с 30 до 70 файлов. Главный остаточный gap — **anti distribution**, не общий объём.

### B.4 Запросы к Cowork — пересмотренные после Cowork-итерации 2026-05-24

#### B.4.1 (новая) anti-examples-batch-02 — закрытие anti-distribution gap

**Цель.** Закрыть R-3 калибровочный gap для A3 (`incentive-cartographer`) и A5 (`philosophy-adversarial`) + добить voice-bleed как явный тип провала.

**Целевой состав (5-7 файлов):**

- **`conflicts` anti — 2-3 файла.** Кандидаты: критики plot-driven seasons (The Walking Dead post-S5 — фокус не на финале, а на структурном разложении конфликтов внутри сезонов); late Westworld confusion; House of Cards post-Spacey — soap-opera collapse of political structural conflict.
- **`adversarial-passes` anti — 2 файла.** Steel-man «слабо»: один плохой alarmist (например, plokhie versions of doomer-talking-points), один плохой sceptic (например, dismissive «just autocomplete» argument поданный как single take). **НЕ сатира** — слабая искренняя версия позиции.
- **`dialogues` anti (voice-bleed) — 1-2 файла.** Критики House of Cards Underwood-voice-everywhere; либо revisitation of The Newsroom на voice level (не на moralizing level — moralizing уже есть в b01 Knibbs).

#### B.4.2 (новая) adversarial-passes — institutional voice gap

**Цель.** Текущие 7 файлов в `adversarial-passes` — все **individual** voices (бloggers, researchers, commentators). **Institutional** voice (Anthropic papers, OpenAI safety statements, DeepMind alignment posts) отсутствует. Для PHILOSOPHY критика это **отдельная ось**: голос исследовательской организации, говорящей от своей коллективной policy, звучит структурно иначе, чем individual researcher.

**Целевой состав (2-3 файла):**

- Anthropic Constitutional AI paper (arXiv) — institutional methodological voice.
- Anthropic Sleeper Agents paper — institutional research voice с дискуссионной impact.
- OpenAI или DeepMind safety blog post (один из) — comparator.
- Альтернативно: Paul Christiano direct alignment writing (отмечен в overall report как gap).

**Целевой состав.** 2-3 positive, sub_category: `institutional-voice`.

#### B.4.3 (новая, низкий приоритет) audience category — открыть или явно отказаться

**Проблема.** В spec § 5.2 директория `golden/` содержит 6 категорий + anti. `audience` отдельной директории нет — но A6 (`audience-bored-detector`) калибруется на чём-то. Cowork-overall-report упоминает «audience / reception categories not opened». В существующих positive файлах есть «audience-affect» observations (Schmidt про «HARRIS. OLSON.» emotional peak earned through setup), но они разбросаны.

**Развилка:**

- (a) Открыть `golden/audience/` как 7-ю категорию. Заказать 3-4 файла critics-on-audience-response (например, Nussbaum Bad Fan, Sepinwall on viewers' active-engagement, critiques of fandom-as-co-author).
- (b) Не открывать. A6 калибруется через cross-references из других категорий (audience-affect observations в scenes / characters / theses). Зафиксировать в `golden/README.md`.

**Принято в D-002:** **(b) — не открывать в ПП1**. A6 как 6-й критик отличается от остальных — он не имеет собственного эталонного материала, а калибруется на audience-affect наблюдениях из других категорий. Если в smoke-test A6 покажет систематический pass или confuse, открывать audience category в ПП2.

#### B.4.4 (отложено до ПП2+) video-essay transcripts

Без изменений к первой редакции — структурный блок Web Fetch, требует manual transcription или Claude in Chrome.

### B.5 Что НЕ запрашиваем у Cowork

- **Доп. positive scenes / characters / conflicts** — категории положительно покрыты, дальнейший сбор без conkretной цели = bloat.
- **Видео-эссе transcripts** — см. B.4.4.
- **Bostrom direct excerpts** — paywall.
- **Twitter threads LeCun direct** — Twitter block; есть через Weldon в b02.
- **Long-form literary essays LARB / Aeon / The Believer** — consistent Web Fetch block.
- **Scott Alexander «Yudkowsky Contra Christiano»** — отмечен в overall report как source too large; partial coverage achieved.
- **Анти-positive examples (good craft taken too far)** — Sorkin walk-and-talk overuse, Pizzolatto philosophy-monologue overload — отмечены в anti-batch-01 manifest «Что отложено». Не запрашиваем в ПП1 (ниже приоритет, чем B.4.1).

### B.6 Обновление acceptance 9.3 шаг 1

**Заменить** в спеке:

> 1. Подготовка golden: минимум 4-5 positive + 2-3 anti в категориях, для которых Cowork собрал материал (scenes — есть; dialogues/characters/theses — параллельно).

**На:**

> 1. Подготовка golden: после `add-golden-example` обработки 19 партий (70 content + 19 manifests) + завершения B.4.1 (anti-batch-02) — все 6 positive категорий имеют **≥3 файла**, anti — **≥1 файл на 5 категорий** (scenes / characters / dialogues / theses + любая из conflicts / adversarial-passes). `golden_freshness.py` зелёный с этим bootstrap-порогом. **Diversity warnings** (P-14) — выведены и явно acknowledged в `golden/README.md` либо устранены через дополнительные партии.

---

## Часть C. Операционные следствия

### C.1 Порядок действий до старта implementation (обновлено 2026-05-25)

Cowork завершил большую итерацию между первой и второй редакцией D-002. Шаги пересмотрены:

1. **Тимур:** strategic acceptance D-002 v2 (целиком или с правками).
2. ~~Cowork: завершить 4 in-flight партии.~~ **Выполнено** (19 партий, 70 content-файлов).
3. ~~Тимур → Cowork: `conflicts-batch-01`.~~ **Выполнено самостоятельно Cowork-ом** (10 conflicts файлов).
4. **Тимур → Cowork:** запросить `anti-examples-batch-02` (B.4.1) — закрытие anti distribution gap (conflicts anti + adversarial-passes anti steel-man + voice-bleed dialogues).
5. **Тимур → Cowork:** запросить `adversarial-passes-batch-03` (B.4.2) — institutional voice (Anthropic Constitutional AI + Sleeper Agents + Christiano).
6. ~~Тимур → Cowork: `adversarial-passes-batch-03` sceptic balancing.~~ **Выполнено через batch-02** (Mitchell + LeCun + Hanson).
7. **Claude Code:** проверить extended thinking механизм (P-8) → `docs/extended-thinking-mechanism.md`.
8. **Claude Code:** написать `docs/cost-estimate-pp1.md` (P-6).
9. **Claude Code:** обновить spec по правкам P-1..P-15 (отдельный commit с типом `decision:` со ссылкой на D-002).
10. **Claude Code:** обновить `docs/cowork/prompt.md` по правке P-11 (mandate boundary).
11. **Claude Code:** обновить `golden/README.md` (заготовка) — diversity-acknowledged раздел для P-14 warnings + явная политика P-11 / P-13.
12. **Claude Code:** writing-plans ПП1 (`docs/superpowers/plans/2026-XX-XX-pp1-implementation.md`).
13. Implementation стартует только после 1-12.

**Параллельно (не блокирует 7-12):** обработка через `add-golden-example` 70 collected файлов начнётся после имплементации скилла (часть ПП1 implementation), не до. До этого они остаются в `raw/_cowork-dumps/` как append-only inbox.

### C.2 Что D-002 НЕ решает

- Конкретные prompt'ы 6 субагентов — implementation phase.
- Точные pressure-tests файлы — implementation.
- Финальное TF-IDF пороговое значение voice_dissimilarity — после calibration на R-3 calibration set (P-5).
- Дизайн `session-bootstrap` скилла (§ 11.3 митигация) — ПП2+.
- Выбор финального SHA Superpowers — D-001 зафиксировал `f2cbfbef`, не пересматриваем.
- Конкретные shows/themes для следующих positive партий — Cowork-итерация 2026-05-24 покрыла достаточно для ПП1, дальнейший positive-сбор отложен до ПП2.

### C.3 Открытые вопросы для следующих D-NNN

- **D-003 (потенциально).** Если cost-estimate (P-6) покажет, что 4 артефакта smoke-test переcomplete по бюджету, может потребоваться дальнейшее урезание (например, 3 артефакта + meta-сценка для A4).
- **D-004 (потенциально).** Если первый smoke-test покажет систематический bias одного из критиков (например, A6 всегда pass) — пересмотр калибровки и/или открытие `golden/audience/` (B.4.3 alternative).
- **D-005 (потенциально).** Если P-11 (Cowork mandate clarification) на практике вызовет сопротивление формата у Cowork — пересмотр workflow.
