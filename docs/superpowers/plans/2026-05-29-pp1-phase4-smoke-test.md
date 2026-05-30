# Phase 4 — Smoke-test End-to-End Implementation Plan (full TDD detail)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> ✅ **EXPANDED 2026-05-30** после Phase 3 files acceptance (commit `757c757` + Layer-1 review `2ae2fb4`). Outline → full TDD detail per phased-plan-before-code discipline.

**Goal:** прогнать Поток A (spec § 8.1 v0.2) на 4 артефактах для acceptance ПП1 (spec § 9.7 Definition of Done) — это финал ПП1, после которого ПП1 ACCEPTED и разблокирован ПП2.

**Architecture:** end-to-end execution через все скиллы Phase 3 — brainstorming → R-1 шляпы → adversarial-review-pass (P-9 tmp/critic-reports) → consistency-check → concern_resolution_validator → evidence-before-action → write → commit → archive critic-reports. Каждый артефакт — отдельный полный прогон Потока A.

**Tech Stack:** все артефакты Phase 1-3. Никаких новых файлов в `tools/`, `.claude/skills/`, `.claude/agents/`, `meta-skills/`. Создаются только контентные артефакты + bootstrap files (CLAUDE.md, README.md, .mcp.json) + golden material из 19 cowork batches.

**Language policy (spec § 10):**
- Все артефакты творческого слоя (`story-bible/`, `characters/`, `scenes/`) — **на русском**
- CLAUDE.md, README.md — **на русском** (это наши, не нарративные но проектные)
- Frontmatter поля + IDs — английский kebab-case
- Critic reports + cowork-notes — на русском
- Commit messages — на русском

---

## CRITICAL: Execution context

Phase 4 ВСЯ требует **fresh Auto-ai-series session** (запуск Claude Code с `cwd = C:/Users/user/Documents/Claude/Projects/Auto-ai-series/`) потому что:

1. Все 8 скиллов из `.claude/skills/` проектно-scoped — недоступны в других sessions
2. Все 6 субагентов A1-A6 из `.claude/agents/` проектно-scoped
3. `tmp/critic-reports/` живёт в рабочем дереве проекта

**Phase 4 не может быть выполнен из leadecho-leadgen session**, в которой написан этот plan. План — preparation работа; execution — отдельная сессия.

**Перед стартом Phase 4 fresh session — выполнить deferred Phase 2 Task 7 + Phase 3 Layer-2 acceptance:** убедиться что 6 субагентов A1-A6 реально работают (Phase 2 Task 7) и 3 BLOCKER скилла реально блокируют RED-сценарии (Phase 3 Layer-2). Эти deferred acceptances — prerequisite для smoke-test.

---

## File Structure (планируется к созданию)

### Pre-smoke-test setup (Task 0)

| Файл | Назначение | Размер |
|---|---|---|
| `CLAUDE.md` | Контракт проекта + 4-5 законов (адаптированных из spec) | ~80 строк |
| `README.md` | Одна страница: что это, как стартовать | ~40 строк |
| `.mcp.json` | filesystem-MCP для Claude Desktop | ~15 строк |

### Golden corpus bootstrap (Task 1)

| Where | Что | Объём |
|---|---|---|
| `golden/scenes/*.md` | через `add-golden-example` на 19 партиях | ~19 файлов (bootstrap 3+) |
| `golden/characters/*.md` | ... | ~20 файлов |
| `golden/conflicts/*.md` | ... | ~10 файлов |
| `golden/dialogues/*.md` | ... | ~7 файлов |
| `golden/adversarial-passes/*.md` | ... | ~7 файлов |
| `golden/theses/*.md` | ... | ~3 файла |
| `golden/anti-examples/*/*.md` | derived → cowork-notes; real anti в anti-examples | ~7 файлов |
| `docs/cowork-notes/<batch>.md` | × 19 — рекомендации к нашему сериалу (P-11) | ~19 файлов |
| `docs/cowork-notes/derived-anti-lessons/*.md` | derived anti из positive (P-13) | variable |

### Smoke-test artefacts (Tasks 2-5)

| Файл | Тип Потока A | Объём | Критики |
|---|---|---|---|
| `story-bible/thesis.md` | non-scene | ~150 слов | A5, A1, A3, A2, A6 (A4 not_applicable, P-3) |
| `story-bible/world-rules.md` | non-scene | 5 правил мира | A5, A1, A3, A2, A6 (A4 not_applicable) |
| `characters/<one>.md` | non-scene | 1 character-sheet (тревожная компетентность) | A5, A1, A3, A2, A6 (A4 not_applicable) |
| `scenes/smoke-test-dialogue.md` | scene | 300-500 слов, 2-3 говорящих | All 6 (A4 включён) |

### Workflow side-effects (создаваемые автоматически)

| Файл | Где | Назначение |
|---|---|---|
| `tmp/critic-reports/<artifact-id>/<critic>-<timestamp>.yaml` | `tmp/` (gitignored) | P-9 — рабочие YAML до commit |
| `docs/critic-reports-archive/<artifact-id>/*.yaml` | tracked | P-9 — архив после commit |
| `decisions/D-NNN-*.md` | tracked | если есть concern/veto который шоураннер решил оставить |
| `docs/cowork-notes/<batch>.md` + `derived-anti-lessons/` | tracked | если `add-golden-example` отделил рекомендации (P-11/P-13) |

---

## Базовый шаблон Поток A (применяется для Tasks 2, 3, 4, 5)

Каждый из 4 артефактов выполняется по одному и тому же Поток A v0.2 (spec § 8.1, шаги 0-13 с удалённым шагом 3 P-1):

### Step A.0: Trigger

Тимур или шоураннер формулирует ТЗ артефакта.

### Step A.1: brainstorming (Superpowers, при необходимости)

```
Skill brainstorming
```

Используется ТОЛЬКО если есть ⩾2 содержательные альтернативы. Если уклон ясен из ТЗ — skip.

### Step A.2: draft-* скилл с R-1 шляпами (P-2)

Для thesis / world-rules → `draft-story-bible-section` (шляпы LORE/PHILOSOPHY/CHARACTER).
Для character-sheet → `draft-character-sheet` (шляпы CHARACTER/CONFLICT/PHILOSOPHY).
Для scene → можно `draft-story-bible-section` адаптированный либо напрямую творческое написание (scene не имеет dedicated draft-скилла в ПП1).

3 последовательные шляпы в orchestrator-сессии:
- Context-marker между шляпами либо `/clear`
- Каждая шляпа читает: соответствующее golden/ + story-bible/ + CLAUDE.md
- Шоураннер собирает 3 варианта → synthesis (явный выбор или композиция)
- Результат записывается в файл

### Step A.3: (УДАЛЕН per P-1) — A5 встроена в Step A.4

### Step A.4: adversarial-review-pass (skill)

```
Skill adversarial-review-pass
```

Последовательно (через Task tool):
- **A5 philosophy-adversarial** (P-1: встроена сюда)
- **A1 lore-realism-checker**
- **A3 incentive-cartographer**
- **A2 character-truth-keeper**
- **A6 audience-bored-detector**
- **A4 voice-differentiator** — только если артефакт сцена; иначе skip + `verdict: pass + not_applicable_reason` фиксируется (P-3)

**После каждого critic-call:**
1. Получи YAML output от Task tool
2. **Запиши на диск (P-9):** `tmp/critic-reports/<artifact-id>/<critic>-<ISO-timestamp>.yaml`
3. Validate: `python -m tools.critic_report_validator tmp/critic-reports/<artifact-id>/<critic>-<timestamp>.yaml --smoke-test`
   - exit 0 → ок
   - exit 1 → re-invoke critic с инструкцией «Твой отчёт failed validation: <issues>. Переделай.»
4. **Acceptance checks per spec § 9.4:**
   - `verdict` ∈ {pass, concern, veto, pass+not_applicable}
   - `checked` ≥ 3
   - `evidence_from_artifact` ≥ 2
   - `golden_calibration_used` ≥ 1 ИЛИ `golden_unavailable_reason ∈ {category-empty, category-bootstrap, category-irrelevant}` (P-4)
   - `reasoning` ≥ 100 слов
   - **для verdict=pass:** `counter_test_attempted` все 3 элемента (P-7)
   - **для not_applicable:** `not_applicable_reason` заполнен (P-3)
   - `model_used` зафиксирован (P-8 audit)

### Step A.5: Шоураннер реагирует на каждый отчёт критика

- Несовместимые vето — экспоунятся Тимуру, не усредняются
- Concerns → решение: rework (next iteration) или decisions/D-NNN-*.md с обоснованием
- Pass без полного counter_test_attempted = retry, **не pass**

### Step A.6: consistency-check (skill)

```
Skill consistency-check
```

Запускает `tools/consistency_check.py --root .`. Exit 0 обязателен. Если exit 1 — fix или D-NNN.

### Step A.7: concern_resolution_validator (R-2)

```
python -m tools.concern_resolution_validator --artifact-id <id> --tmp-dir tmp/critic-reports --decisions-dir decisions
```

Парсит критик-отчёты из `tmp/critic-reports/<artifact-id>/` (P-9) + текущий git diff. Для каждого concern/veto требует либо адресующий diff, либо `decisions/D-NNN-*.md`. Exit 0 обязателен.

### Step A.8: evidence-before-action (skill — discipline-BLOCKER)

```
Skill evidence-before-action
```

Утверждение в commit message «adversarial-review-pass прошёл / consistency green / concern resolution clean» сопровождается ссылками на свежие выходы шагов A.4, A.6, A.7 в этой же сессии. Без этого — BLOCK.

### Step A.9: Write артефакт (Edit/Write tool)

Финализируй артефакт. Frontmatter: `id`, `version: 1`, `status: draft`, `references: [...]`.

### Step A.10: Commit

```bash
git add <artefact-path>
git commit -m "<type>: <name> v0.1 — <обоснование> [+ ссылка на adversarial-review summary]"
```

Типы: `bible:` (thesis/world-rules), `character:`, `scene:`.

### Step A.11: Архивация критик-отчётов (P-9)

```bash
mkdir -p docs/critic-reports-archive/<artifact-id>
mv tmp/critic-reports/<artifact-id>/* docs/critic-reports-archive/<artifact-id>/
# tmp/<artifact-id>/ опустеет, можно rmdir
rmdir tmp/critic-reports/<artifact-id>
```

Это переводит ephemeral tmp/ → tracked docs/critic-reports-archive/ для аудита.

### Step A.12: log entry

```
[YYYY-MM-DD] <type> | <artifact> v0.1 — <обоснование> + N critics (M concerns / K vетоs)
```

### Step A.13: decisions/D-NNN-*.md (если развилка значимая)

Если было содержательное столкновение vето или концепт решение — отдельный D-NNN.

---

## Task 0: Pre-smoke-test setup

**Roоль:** создать bootstrap-файлы проекта (CLAUDE.md / README.md / .mcp.json) которые ссылаются на 4-5 законов проекта.

**Files:**
- Create: `CLAUDE.md`
- Create: `README.md`
- Create: `.mcp.json`

### Steps

- [ ] **Step 0.1: CLAUDE.md**

Структура (на русском, ~80 строк):

```markdown
# Auto-ai-series — Claude Code контракт

Проект: психологическая социальная драма-сериал про эволюцию ИИ. Мультиагентная система — 6 субагентов-критиков + 8 скиллов + 6 lint-скриптов.

## 4-5 законов проекта

### Закон 1: Шоураннер — единственный writer
Все артефакты (story-bible, characters, scenes) пишет только orchestrator-сессия (Claude Code основная сессия). Критики (A1-A6) read-only через Task tool, Cowork — input через raw/_cowork-dumps/. (spec § 8.3.1)

### Закон 2: Адверсариальный проход обязателен перед финализацией
Любой narrative артефакт перед merge проходит `adversarial-review-pass` (5-6 субагентов) + `consistency-check` + `concern_resolution_validator` + `evidence-before-action`. (spec § 8.1)

### Закон 3: Counter-test обязателен для pass
Любой `verdict: pass` от критика требует `counter_test_attempted` со всеми 3 элементами (what_searched / why_this / why_not_found). Без них pass = retry, не acceptance. (D-002 P-7)

### Закон 4: Critic-отчёты на диске
Каждый YAML отчёт критика пишется в `tmp/critic-reports/<artifact-id>/<critic>-<timestamp>.yaml` НЕМЕДЛЕННО после получения от Task tool. После commit артефакта — переезжает в `docs/critic-reports-archive/`. Контекст сессии не считается evidence (P-9).

### Закон 5: Effort: max для всех критиков
Все 6 субагентов в `.claude/agents/` имеют `model: opus + effort: max` в frontmatter. Sonnet в `model_used` = R-4 escalation через D-NNN. (D-002 P-8)

## Ссылки

- spec: `docs/specs/2026-05-24-infrastructure-and-skills-design.md`
- D-001 bootstrap architecture: `decisions/D-001-bootstrap-architecture.md`
- D-002 spec corrections + golden plan: `decisions/D-002-spec-corrections-and-golden-plan.md`
- cost-estimate (Max 5x подписка): `docs/cost-estimate-pp1.md`
- extended thinking mechanism (P-8): `docs/extended-thinking-mechanism.md`
- log: `docs/log.md`

## Workflow

См. Поток A в spec § 8.1 v0.2 (13 шагов с удалённым шагом 3 per P-1).

## Связь с Superpowers

Superpowers (`obra/superpowers@f2cbfbef`) — методологический базис. Используем напрямую: `brainstorming`, `writing-plans`, `subagent-driven-development`, `test-driven-development`, `requesting-code-review`. Адаптируем через lineage: `writing-narrative-skills`, `evidence-before-action`. См. `meta-skills/superpowers-references/`.
```

- [ ] **Step 0.2: README.md**

Структура (на русском, ~40 строк):

```markdown
# Auto-ai-series

Психологическая социальная драма-сериал про эволюцию ИИ. Мультиагентная система написания.

## Старт

1. Открой Claude Code с cwd = этой папки
2. Прочитай `CLAUDE.md` (контракт проекта + законы)
3. Прочитай `docs/specs/2026-05-24-infrastructure-and-skills-design.md` для архитектуры

## Структура

- `story-bible/` — тезис, правила мира, регистр конфликтов
- `characters/` — character-sheets
- `scenes/` — сцены
- `golden/` — эталоны + anti-examples (калибровочный материал для критиков)
- `.claude/skills/` — наши 8 скиллов
- `.claude/agents/` — 6 субагентов-критиков (Opus + effort: max)
- `tools/` — 6 lint-скриптов (TDD, pytest зелёный)
- `tests/regression/` — RED + calibration + holdout regression artifacts
- `meta-skills/superpowers-references/` — 4 pinned Superpowers references
- `decisions/` — D-NNN-*.md
- `docs/specs/` — spec + cost-estimate + extended-thinking research
- `docs/superpowers/plans/` — 5 implementation plans (Phases 1-4)
- `docs/cowork-notes/` — Cowork рекомендации (P-11) + derived anti-lessons (P-13)
- `docs/critic-reports-archive/` — архив YAML отчётов критиков после commit (P-9)
- `tmp/` (gitignored) — рабочие critic-reports до commit (P-9)
- `raw/_cowork-dumps/` (gitignored) — input от Cowork

## Workflow

См. spec § 8.1 v0.2 — Поток A.

## Status

См. `docs/log.md` для текущего состояния.
```

- [ ] **Step 0.3: .mcp.json**

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "C:/Users/user/Documents/Claude/Projects/Auto-ai-series"
      ]
    }
  }
}
```

> Note: .mcp.json для Claude Desktop integration (если используется). Для Claude Code session с cwd проекта — не критично.

- [ ] **Step 0.4: Validate + commit**

```bash
python -m tools.frontmatter_validator --root . 2>&1 | tail -10
```

CLAUDE.md / README.md без frontmatter — пропускаются validator'ом (skip pattern).

```bash
git add CLAUDE.md README.md .mcp.json
git commit -m "$(cat <<'EOF'
infra: CLAUDE.md + README.md + .mcp.json — bootstrap files для Phase 4

Phase 4 ПП1 — Task 0:
- CLAUDE.md: контракт проекта + 5 законов (шоураннер единственный writer / адверсариальный проход обязателен / counter-test обязателен для pass / critic-отчёты на диске / effort: max для всех критиков)
- README.md: одна страница навигации
- .mcp.json: filesystem-MCP для Claude Desktop integration

Связь: spec § 8.3.1 + § 8.1; D-002 P-7 + P-8 + P-9.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 1: Golden corpus bootstrap — обработка 19 cowork batches

**Roоль:** прогнать через `add-golden-example` скилл 19 батчей из `raw/_cowork-dumps/` → наполнить `golden/<category>/` + `docs/cowork-notes/<batch>.md` + `docs/cowork-notes/derived-anti-lessons/`.

> **Важно:** Phase 4 не создаёт ни одного НОВОГО Cowork batch'а. Используются уже собранные 19 партий (70 файлов) от Cowork-итерации 2026-05-24, документированных в D-002 v2 Часть B.

**Acceptance:** после Task 1 — `tools/golden_freshness.py --root golden/ --min-positive 3 --min-anti 5` зелёный с bootstrap-порогом (либо diversity warnings acknowledged в `golden/README.md`).

### Steps

- [ ] **Step 1.1: Inventory raw/_cowork-dumps/**

```bash
ls raw/_cowork-dumps/
cat raw/_cowork-dumps/_OVERALL-REPORT-2026-05-24.md
```

Identify 19 batches. Per batch read `_manifest.md`.

- [ ] **Step 1.2: Per-batch processing через add-golden-example**

Для каждого из 19 batches (рекомендация — батчами по 4-5 за окно по pacing):

```
Skill add-golden-example
```

Workflow per batch (per Поток D в spec § 8.2):
1. Read `raw/_cowork-dumps/<batch>/_manifest.md`
2. Per файл в batch:
   - Read frontmatter
   - Identify primary_category + secondary_categories (P-12)
   - Identify example_type (positive | anti-example) (P-13)
   - Identify source_author + source_show (P-14)
3. **P-11 split:** «описание эталона» → `golden/<primary_category>/<file>.md`; «возможные применения» → `docs/cowork-notes/<batch>.md`
4. **P-13 split:** «возможные anti-lessons» в positive → `docs/cowork-notes/derived-anti-lessons/<file>.md`
5. Reconstruction для paywalled — наш аналог «в стиле» + `reconstruction: true`
6. Frontmatter validation: `python -m tools.frontmatter_validator --root golden/`

### Step 1.3: Per-batch commit

```bash
git add golden/<modified-categories>/ docs/cowork-notes/<batch>.md
git commit -m "golden: ... — <batch-id> — N positive + M anti для <categories>"
```

Per spec § 8.3.1 commit conventions: `golden:` для golden/, отдельный `docs:` для cowork-notes/ если уместно.

- [ ] **Step 1.4: golden_freshness check**

После всех 19 batches:

```bash
python -m tools.golden_freshness --root golden/ --min-positive 3 --min-anti 5
```

Анализ:
- `issues` (error): если категория не достигла bootstrap-порога → flag в `golden/README.md`
- `diversity_warnings` (warning): per P-14
  - Author dominance > 50%
  - Show dominance > 60% в scenes/characters/conflicts
  - Batch concentration ≥ 3 files same author
  - **Acknowledge каждый в `golden/README.md`** с reason

### Step 1.5: Diversity warnings acknowledgement (если есть)

Append в `golden/README.md` секцию:

```markdown
## Diversity warnings acknowledged (P-14)

- [batch-id] author X dominates Y category: причина — <reason>; митигация в ПП2 через batch Z
- ...
```

- [ ] **Step 1.6: Task 1 commit (если acknowledge нужен)**

```bash
git add golden/README.md
git commit -m "golden: README diversity warnings acknowledged (P-14, bootstrap state)"
```

- [ ] **Step 1.7: Log entry**

```
[YYYY-MM-DD] golden | Task 1 ПП1 Phase 4 — 19 batches обработаны через add-golden-example: N positive в 6 категориях, M anti в 5 категориях. golden_freshness exit 0 с bootstrap-порогом. Diversity warnings: <N acknowledged / 0>. P-15 flagged risk: conflicts anti = 0, audience категория не открыта.
```

### Pacing

19 батчей — не за одно окно. Recommended pacing (cost-estimate § 9.4):
- Окно 1: batches 1-5 (scenes batch 1-4 + conflicts batch 1) — categories покрытие
- Окно 2: batches 6-10 (характеры + диалоги + theses)
- Окно 3: batches 11-15 (adversarial-passes + дополнительные характеры)
- Окно 4: batches 16-19 (anti + cumulative report consideration)

Каждое окно < 60% capacity (избегаем auto-switch Opus → Sonnet).

---

## Task 2: thesis.md — non-scene artefact (Поток A)

**Roоль:** Создать `story-bible/thesis.md` (~150 слов) — центральный тезис сериала про эволюцию ИИ. Прогнать полный Поток A.

**Files:**
- Create: `story-bible/thesis.md`
- Create: `tmp/critic-reports/thesis-001/A5-*.yaml` (× 5 minimum)
- After commit: `docs/critic-reports-archive/thesis-001/*.yaml`

### Steps

- [ ] **Step 2.1: brainstorming (Skill, при необходимости)**

Если центральный тезис уже сформулирован (например, из D-001 или ранних обсуждений) — skip. Если требуется выбор между несколькими формулировками — invoke `brainstorming`.

- [ ] **Step 2.2: draft-story-bible-section с R-1 шляпами (Skill)**

```
Skill draft-story-bible-section
```

3 ПОСЛЕДОВАТЕЛЬНЫЕ шляпы в orchestrator-сессии (P-2):

**Шляпа A — LORE-dominant:**
- Стартовый промпт: «Тезис первичен через мир. Я пишу из того, что технические/корп/политические структуры реального AI-domain первичны.»
- Калибровка: `golden/theses/` (Karnofsky, Brooker, Mancuso если есть) + `golden/scenes/` (Severance Lumon, Mr Robot E Corp) для понимания «как структура мира формулирует тезис»
- Драфт ~150-200 слов

**Context-marker:**
> «Сейчас я возвращаюсь к другому уклону. Предыдущий draft был LORE-dominant. Следующий — PHILOSOPHY-dominant.»

**Шляпа B — PHILOSOPHY-dominant:**
- «Тезис как центральная философская позиция о ИИ-эволюции. Мир и характеры — иллюстрации.»
- Калибровка та же + Anthropic Constitutional AI / Yudkowsky / Christiano из adversarial-passes
- Драфт ~150-200 слов

**Context-marker.**

**Шляпа C — CHARACTER-dominant:**
- «Тезис как то, что персонажи воплощают через их incentive-структуру. Тезис первичен как опыт.»
- Калибровка + `golden/characters/` (Carmela, Peggy, Fleabag — характеры с моральной сложностью)
- Драфт ~150-200 слов

**Synthesis:** шоураннер собирает 3 варианта, явно выбирает один как основу ИЛИ синтезирует. Финальный ~150 слов.

- [ ] **Step 2.3: Write черновик в story-bible/thesis.md (НЕ commit)**

Frontmatter:
```yaml
---
id: thesis-001
version: 1
status: draft
references:
  - "golden/theses/..."
  - "CLAUDE.md"
---
```

Body ~150 слов.

- [ ] **Step 2.4: adversarial-review-pass (Skill)**

```
Skill adversarial-review-pass
```

5 критиков (A4 not_applicable, P-3):
- **A5 philosophy-adversarial** → ищет strawmen, морализаторство, авторскую позицию через ИИ-голос
- **A1 lore-realism-checker** → ищет fantasy mechanisms, tech-handwaving
- **A3 incentive-cartographer** → проверяет что тезис связан с реальными конфликтами интересов
- **A2 character-truth-keeper** → проверяет что тезис не reduce к «лекция»
- **A6 audience-bored-detector** → проверяет hook'и, momentum, stake

Для каждого critic-call:
1. Task tool invocation: `Task(subagent_type="philosophy-adversarial", description="...", prompt="Прочитай story-bible/thesis.md ...")`
2. **Запиши YAML на диск (P-9):** `mkdir -p tmp/critic-reports/thesis-001 && write tmp/critic-reports/thesis-001/A5-<ISO>.yaml`
3. **Validate:** `python -m tools.critic_report_validator tmp/critic-reports/thesis-001/A5-<ISO>.yaml --smoke-test` (exit 0)
4. Если exit 1 → re-invoke A5 с «Твой отчёт failed validation: <issues>. Переделай.»

A4 specifically: `Task(subagent_type="voice-differentiator", ...)` → expected `verdict: pass + not_applicable_reason: "артефакт не содержит диалога в формате **ИМЯ:** реплика"`. Записать YAML аналогично + валидировать.

- [ ] **Step 2.5: Шоураннер реагирует на отчёты**

Per spec § 8.1 шаг 5:
- Несовместимые vето → expose Тимуру
- Concerns → rework decision (next iteration thesis.md) или D-NNN
- Pass без полного counter_test_attempted → retry critic

Если критик дал concern/veto — **rework**: вернись к Step 2.2 (новая шляпа с фокусом на адресуемом concern), пере-Write thesis.md, повторно Step 2.4 для затронутых критиков (НЕ для всех — экономия). Максимум 2 rework round'а (cost-estimate § 9.4).

- [ ] **Step 2.6: consistency-check (Skill)**

```
Skill consistency-check
```

```bash
python -m tools.consistency_check --root .
```

Exit 0. Если exit 1 — fix references.

- [ ] **Step 2.7: concern_resolution_validator (R-2)**

```bash
python -m tools.concern_resolution_validator --artifact-id thesis-001 --tmp-dir tmp/critic-reports --decisions-dir decisions
```

Exit 0. Если concern/veto не адресован — D-NNN или rework.

- [ ] **Step 2.8: evidence-before-action (Skill)**

```
Skill evidence-before-action
```

Verify в commit message ссылки на свежие выходы adversarial-review-pass + consistency-check + concern_resolution_validator (все из этой сессии, не из памяти).

- [ ] **Step 2.9: Финализируй thesis.md**

`status: draft` → возможно остаётся draft до ПП2 (Bible finalization). Это нормально per spec § 9.6 (полный Story Bible — ПП2).

- [ ] **Step 2.10: Commit**

```bash
git add story-bible/thesis.md
git commit -m "$(cat <<'EOF'
bible: thesis v0.1 — центральный тезис проекта (smoke-test ПП1 артефакт #1)

Phase 4 ПП1 — Task 2 (Поток A на thesis.md):
- R-1 шляпы: LORE-dominant + PHILOSOPHY-dominant + CHARACTER-dominant synthesis
- adversarial-review-pass: A5 + A1 + A3 + A2 + A6 (A4 not_applicable, P-3)
- N concerns / K vето адресованы через [rework | decisions/D-NNN-*.md]
- consistency-check зелёный (exit 0)
- concern_resolution_validator зелёный (exit 0)
- evidence-before-action: все claims с свежими выходами (P-9 YAML в tmp/critic-reports/thesis-001/)

Связь: spec § 8.1 v0.2 Поток A + § 9.7 DoD; D-002 P-1 + P-3 + P-7 + P-8 + P-9.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 2.11: Архивация critic-reports**

```bash
mkdir -p docs/critic-reports-archive/thesis-001
mv tmp/critic-reports/thesis-001/* docs/critic-reports-archive/thesis-001/
rmdir tmp/critic-reports/thesis-001

git add docs/critic-reports-archive/thesis-001/
git commit -m "docs: archive critic-reports для thesis-001 (P-9)"
```

- [ ] **Step 2.12: Log entry**

```
[YYYY-MM-DD] bible | thesis v0.1 (Task 2 Phase 4) — Поток A прошёл; A5+A1+A3+A2+A6 (A4 not_applicable), N concerns, K vето; consistency + concern_resolution + evidence-before-action green; arc P-9 → archive. ПП1 smoke-test артефакт 1/4 ✅.
```

- [ ] **Step 2.13: D-NNN (если развилка значимая)**

Если был содержательный конфликт vето между критиками — отдельный `decisions/D-NNN-thesis-decision.md`.

---

## Task 3: world-rules.md — non-scene artefact (Поток A)

**Roоль:** аналогично Task 2, но для `story-bible/world-rules.md` (5 правил мира).

**Files:**
- Create: `story-bible/world-rules.md`
- Create: `tmp/critic-reports/world-rules-001/<critic>-*.yaml` (× 5)
- After commit: `docs/critic-reports-archive/world-rules-001/`

### Steps

Применить базовый шаблон **Поток A** (Steps A.0-A.13 выше) с подменами:

- **Step A.2:** R-1 шляпы (LORE / PHILOSOPHY / CHARACTER) но фокус — 5 правил мира AI-domain (regulatory landscape / corporate structures / tech limits / human-AI interaction protocols / cultural attitudes). Калибровка через `golden/scenes/` (Severance Lumon procedures, Mr Robot tech-realism), `golden/conflicts/` (corporate vs alignment dynamics).
- **Step A.4:** 5 критиков (A4 not_applicable). A1 LORE — особенно важен здесь (мир = его территория).
- **Step A.4 cross-validation:** world-rules должен соотноситься с thesis.md (Task 2) — frontmatter `references: ["story-bible/thesis.md"]`. consistency-check проверит на step A.6.
- **commit message:** `bible: world-rules v0.1 — 5 правил мира (smoke-test ПП1 артефакт #2)`
- **Log entry:** `bible | world-rules v0.1 (Task 3 Phase 4) — Поток A прошёл; cross-validated с thesis-001; ... 2/4 ✅`

**Acceptance:** аналогично Task 2 + явный cross-reference на thesis-001.

---

## Task 4: characters/<one>.md — character-sheet artefact (Поток A)

**Roоль:** создать 1 character-sheet ("AI-safety исследовательница, тревожная компетентность") через `draft-character-sheet` + полный Поток A.

**Files:**
- Create: `characters/anna-mats-alumna.md` (~200-400 слов)
- Create: `tmp/critic-reports/character-anna-001/<critic>-*.yaml`
- After commit: `docs/critic-reports-archive/character-anna-001/`

### Steps

Применить базовый шаблон **Поток A** с подменами:

- **Step A.2:** **`draft-character-sheet`** (НЕ draft-story-bible-section). 3 ПОСЛЕДОВАТЕЛЬНЫЕ шляпы CHARACTER / CONFLICT / PHILOSOPHY-dominant (P-2 для characters):

  - **Шляпа A — CHARACTER-dominant:** «Декларируемая ценность + incentive. Анна декларирует X, реально движет Y, разрыв виден в Z.»
  - **Шляпа B — CONFLICT-dominant:** «С кем сильнейшее столкновение incentives. Анна vs deploy-команда vs CEO vs board — какие интересы несовместимы.»
  - **Шляпа C — PHILOSOPHY-dominant:** «Позиция по ИИ в сильнейшей формулировке. Анна — воплощение какого аргумента в проекте.»

  Калибровка: `golden/characters/` (Carmela, Peggy, Fleabag, Kim Wexler — характеры с моральной сложностью + тревожной компетентностью паттерном), `golden/conflicts/` + `golden/theses/` (secondary с весом 0.5 per P-12).

  Synthesis ~200-400 слов.

- **Step A.4:** 5 критиков (A4 not_applicable). A2 CHARACTER особенно важен — ловит declaration-as-character.
- **Step A.4 cross-validation:** character `references: ["story-bible/thesis.md", "story-bible/world-rules.md"]`. consistency-check проверит.
- **commit message:** `character: anna-mats-alumna v0.1 — AI-safety исследовательница тревожная компетентность (smoke-test ПП1 #3)`
- **Log entry:** `character | anna v0.1 (Task 4 Phase 4) — Поток A прошёл; ... 3/4 ✅`

---

## Task 5: scenes/smoke-test-dialogue.md — scene artefact (+ A4 VOICE)

**Roоль:** создать сценку 300-500 слов с 2-3 говорящими через творческий процесс + полный Поток A **с A4** (не not_applicable).

**Files:**
- Create: `scenes/smoke-test-dialogue.md` (300-500 слов, 2-3 говорящих в формате `**ИМЯ:** реплика`)
- Create: `tmp/critic-reports/scene-001/<critic>-*.yaml` (× 6 critics!)
- After commit: `docs/critic-reports-archive/scene-001/`

### Steps

Применить базовый шаблон **Поток A** с подменами:

- **Step A.2:** Творческий процесс — нет dedicated `draft-scene` скилла в ПП1 (это ПП5+). Используется либо адаптированный `draft-story-bible-section` (адаптировать шляпы к сценному формату), либо напрямую orchestrator-сессия пишет сцену через R-1 принципы:

  - **Шляпа A — DIALOGUE-dominant:** сцена через voice-distinguishing — Анна (researcher academic-careful), CEO (corporate soft-questions), engineer (compact-technical). Voice-bleed = катастрофа.
  - **Шляпа B — CONFLICT-dominant:** сцена через структуру incentive collision — Анна не может ship, CEO должен ship, engineer ловит quarter pressure.
  - **Шляпа C — TENSION-dominant:** сцена через момент когда decision shifts — какая мелочь меняет dynamic.

  Калибровка: `golden/dialogues/` (Sorkin walk-and-talk anti, Fleabag fourth-wall, Mad Men HARRIS-OLSON), `golden/scenes/` Mr Robot momentum, `golden/conflicts/`.

- **Step A.3.5 (специальный для scene):** `voice-check` (Skill — discipline-BLOCKER) ПЕРЕД adversarial-review-pass:

  ```
  Skill voice-check
  ```

  Internally:
  1. Detect: ≥2 уникальных `**ИМЯ:**` (если 0-1 — NO-OP not_applicable; для smoke-test scene должно быть 2-3)
  2. Preflight: `python -m tools.voice_dissimilarity scenes/smoke-test-dialogue.md --threshold 0.65`
     - exit 0 (sim < 0.65) — структурно ОК
     - exit 1 (sim > 0.65) — voice-bleed flagged → ПЕРЕПИСАТЬ сценку перед adversarial-review-pass
  3. Content verdict (A4 voice-differentiator): `Task(subagent_type="voice-differentiator", ...)`
  4. YAML A4 → `tmp/critic-reports/scene-001/A4-<ISO>.yaml` (P-9)

  **Voice-check ДО adversarial-review-pass** — дешёвая защита: бессмысленно гонять остальных 5 критиков на voice-bleed-broken сценке.

- **Step A.4:** Остальные 5 критиков (A5, A1, A3, A2, A6). A4 уже отработал в Step A.3.5. В adversarial-review-pass summary все 6 critics включены.

- **Step A.4 cross-validation:** scene `references: ["story-bible/thesis.md", "story-bible/world-rules.md", "characters/anna-mats-alumna.md"]`. consistency-check проверит.
- **commit message:** `scene: smoke-test-dialogue v0.1 — 2-3 говорящих, voice-check + A4 + 5 critics (smoke-test ПП1 #4)`
- **Log entry:** `scene | smoke-test-dialogue v0.1 (Task 5 Phase 4) — Поток A прошёл; voice-check sim X, A4 verdict Y; ... 4/4 ✅`

---

## Task 6: Phase 4 acceptance + smoke-test verification

**Roоль:** проверить что smoke-test прошёл per spec § 9.5 (critical failures) + § 9.7 (Definition of Done).

**Files:**
- Update: `docs/log.md` (acceptance entry)
- Optional: `tests/regression/README.md` если нашлись gaps requiring follow-up

### Steps

- [ ] **Step 6.1: Acceptance checklist per spec § 9.5**

Verify:
- ✅ pytest зелёный на всех 6 lint-скриптах
- ✅ Никакой RED pressure-сценарий не обошёл discipline-BLOCKER скилл (P-10) — Phase 3 Layer-2 acceptance prerequisite
- ✅ НЕ все 6 субагентов auto-approve все 4 артефакта (если все pass без content concerns — flag bias)
- ✅ Каждый pass'нувший verdict имеет полный 3-element `counter_test_attempted` (P-7)
- ✅ Каждый pass'нувший verdict имеет `golden_calibration_used` непуст ИЛИ `golden_unavailable_reason ∈ {category-empty, category-bootstrap, category-irrelevant}` (P-4)
- ✅ R-3.a regression veto: критики выдали veto на соответствующие RED артефакты (Phase 2 Task 7 prerequisite)
- ✅ R-3.b holdout pairs: verdicts разошлись на holdout (P-5)
- ✅ `consistency_check.py` зелёный на собственных fixtures
- ✅ `golden_freshness.py` зелёный (diversity_warnings acknowledged)
- ✅ Каждый адаптированный скилл имеет `lineage:` и `pressure_tested: yes`
- ✅ Каждый субагент READ-ONLY (tools: Read, Grep, Glob)
- ✅ Каждый субагент имеет `effort: max` в frontmatter (P-8)
- ✅ `adversarial-review-pass` валидирует структуру отчётов
- ✅ critic-reports живут в tmp/ → docs/critic-reports-archive/ (P-9)
- ✅ `model_used` поле — если на ≥20% critic-вызовов Sonnet → escalate D-NNN

- [ ] **Step 6.2: Spec § 9.4 cross-validation check**

В 4 артефактах × 5-6 критиков = ~20-24 verdicts. Verify:
- Минимум один случай где **A3 и A5 разошлись** структурно (если систематически согласны — flag избыточности)
- Минимум один случай где A6 расходится с A2/A5

- [ ] **Step 6.3: model_used audit**

Per cost-estimate § 10:
- Count critic-calls where `model_used: opus` vs `sonnet` vs `haiku`
- Если ≥20% sonnet → escalate через D-NNN (upgrade Max 5x → 20x или direct API)
- Document в acceptance log

- [ ] **Step 6.4: Known issues fixation**

Если P-15 risk материализовался (A3 систематический pass из-за пустого conflicts anti) — известный flagged risk per D-002 v2 acceptance. Документируется:

```
[YYYY-MM-DD] note | ПП2 follow-up: A3/A5 показали systematic pass — нужна Cowork-партия B.4.1 (anti-examples-batch-02)
```

Если A6 систематический pass — D-004 trigger (открыть golden/audience/ в ПП2):

```
[YYYY-MM-DD] note | ПП2 follow-up: A6 систематический pass — D-004 trigger, открыть audience категорию
```

Если Sonnet в model_used ≥20%:

```
[YYYY-MM-DD] note | D-NNN escalation: model_used Sonnet на N/M critic-calls — upgrade Max 5x → 20x
```

- [ ] **Step 6.5: Phase 4 Task 6 acceptance log entry**

```
[YYYY-MM-DD] milestone | Phase 4 ПП1 acceptance ✅ — 4 артефакта прошли Поток A: thesis (Task 2) + world-rules (Task 3) + character anna (Task 4) + scene (Task 5). N concerns / K vето адресованы через rework и/или D-NNN-*.md. Acceptance § 9.5 verified, § 9.4 cross-validation OK. model_used audit: opus X/Y. Known issues для ПП2 (если есть): [list]. ПП1 готов к Task 7 Definition of Done.
```

---

## Task 7: ПП1 acceptance Definition of Done

**Roоль:** финальная фиксация ПП1 acceptance per spec § 9.7.

**Files:**
- Update: `docs/log.md` (DoD entry)
- Optional: update spec § 9.1 (структурные acceptance — отметить [x] последние пункты)

### Steps

- [ ] **Step 7.1: spec § 9.7 DoD checklist**

Verify per spec § 9.7 v0.2:

> ПП1 готов, когда:
> - На четырёх живых артефактах (тезис + world-rules + 1 character + scene; P-3) каждый из 6 субагентов был вызван минимум раз с валидным structured отчётом
> - counter_test_attempted 3-element для pass (P-7)
> - golden_calibration_used или golden_unavailable_reason (P-4)
> - model_used зафиксирован
> - Regression-плохие артефакты с veto
> - Holdout regression-пары с расходящимися verdicts (P-5)
> - Все 6 lint-скриптов прошли pytest зелёным + реальный прогон
> - golden_freshness P-12/P-13/P-14 OK
> - critic/concern validator'ах P-7/P-4/P-9
> - Все 3 discipline-скилла (voice-check, consistency-check, evidence-before-action) прошли pressure-tests
> - Critic-отчёты живут в `tmp/` → `docs/critic-reports-archive/` (P-9)
> - decisions/D-001 + decisions/D-002 v2 фиксируют все принятые архитектурные решения

- [ ] **Step 7.2: Update spec § 9.1 structural acceptance (отметить [x])**

Open `docs/specs/2026-05-24-infrastructure-and-skills-design.md` § 9.1, отметить:
- [x] `CLAUDE.md` с 4-5 законами проекта (Task 0)
- [x] `README.md`, `.mcp.json` (Task 0)
- [x] Вся структура папок согласно Section 2

Все остальные `[x]` уже отмечены в предыдущих фазах.

```bash
git add docs/specs/2026-05-24-infrastructure-and-skills-design.md
git commit -m "spec: § 9.1 structural acceptance — последние пункты отмечены [x] после Phase 4"
```

- [ ] **Step 7.3: ПП1 acceptance log entry**

```
[YYYY-MM-DD] milestone | ПП1 ACCEPTANCE ✅ — Definition of Done пройдено: 4 артефакта прошли полный Поток A, 6 критиков калиброваны через regression + holdout (P-5), все 6 lint-скриптов зелёные, 3 discipline-BLOCKER скилла прошли pressure-tests (Layer-1 + Layer-2), critic-reports flow tmp/ → archive (P-9), D-001 + D-002 v2 архитектурные решения зафиксированы. Готов к ПП2 (Story Bible expansion).
```

- [ ] **Step 7.4: ПП1 ACCEPTED commit**

```bash
git add docs/log.md
git commit -m "$(cat <<'EOF'
milestone: ПП1 ACCEPTED — infra + skills + subagents + smoke-test done; ready for ПП2

ПП1 (под-проект 1) ACCEPTANCE ✅:
- Phase 1: 6 lint-скриптов через TDD (45/45 pytest, 76% coverage)
- Phase 2: 6 субагентов A1-A6 + pressure-tests + 31 regression artifact
- Phase 3: 8 скиллов + 4 pinned references; 3 BLOCKER pressure-tested (Layer-1 + Layer-2)
- Phase 4: 4 smoke-test артефакта (thesis + world-rules + character + scene) прошли Поток A

spec § 9.7 Definition of Done — все criteria выполнены.
D-001 bootstrap-architecture + D-002 v2 spec-corrections accepted.

Готов к ПП2 (Story Bible expansion + 6-8 кор-каст персонажей + регистр конфликтов).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 7.5: Push (с Тимуром approval)**

```bash
git push origin main
```

⚠️ Push требует явного approval Тимура per master CLAUDE.md.

---

## Dependencies + execution constraints

- **До старта Phase 4:** 
  - Phase 1 acceptance (✅ `025bb3f`)
  - Phase 2 files acceptance (✅ `207dbca`) + **Phase 2 Task 7 runtime invocation acceptance (DEFERRED, fresh session prerequisite)**
  - Phase 3 files + Layer-1 acceptance (✅ `2ae2fb4`) + **Phase 3 Layer-2 pressure-testing runtime acceptance (DEFERRED, fresh session prerequisite)**
- **Auto-switch мониторинг — критично.** Phase 4 — самая дорогая фаза (4 артефакта × Поток A + ~2 rework rounds). 5-7 окон по cost-estimate § 9.4. Каждое окно держать < 60% capacity. Если `model_used` показывает Sonnet — пауза до reset.
- **Pacing рекомендация (cost-estimate § 9.4):**
  - **День 5 окно 1:** Task 0 (bootstrap) + Task 1 batches 1-5 (~25 messages)
  - **День 5 окно 2:** Task 1 batches 6-10 + golden_freshness check (~25 messages)
  - **День 6 окно 1:** Task 1 batches 11-15 + Task 2 (thesis Поток A) (~30 messages)
  - **День 6 окно 2:** Task 1 batches 16-19 + Task 3 (world-rules Поток A) (~25 messages)
  - **День 7 окно 1:** Task 4 (character Поток A) + Task 5 voice-check (~30 messages)
  - **День 7 окно 2:** Task 5 adversarial-review-pass + Task 6 acceptance verification + Task 7 ПП1 ACCEPTED + push (~25 messages)
- **Resource budget.** ~80-100 messages на Phase 4 (cost-estimate § 9.4); ~$0 marginal под Max 5x подписку (Тимур).
- **Если P-15 материализуется** (A3 systematic pass из-за пустого conflicts anti) — это **известный flagged risk** per D-002 v2 acceptance. НЕ блокер acceptance — фиксируется как ПП2 follow-up, ПП1 закрывается как «accepted with known issues».
- **rework rounds limit:** максимум 2 rework round'а per артефакт (cost-estimate budget). После 2 rework — если concerns остаются — D-NNN-*.md с принятием compromise.

---

## Self-review (per writing-plans skill)

**Spec coverage:**
- ✅ § 8.1 v0.2 Поток A — 13 шагов (с удалённым шагом 3 P-1) применены в Tasks 2-5
- ✅ § 8.2 Поток D — применён в Task 1 (add-golden-example для 19 batches)
- ✅ § 8.3 cross-cutting правила — все commit conventions использованы
- ✅ § 9.1 structural acceptance — Task 0 (CLAUDE.md, README.md, .mcp.json) + Task 7 markdown updates
- ✅ § 9.4 multi-agent acceptance — Tasks 2-5 включают all checks
- ✅ § 9.5 critical failures — Task 6 verification
- ✅ § 9.7 Definition of Done — Task 7 markdown
- ✅ D-002 P-1 — A5 в adversarial-review-pass (не отдельный philosophy-stress-test)
- ✅ D-002 P-2 — R-1 шляпы последовательно в Tasks 2-5 Step A.2
- ✅ D-002 P-3 — A4 not_applicable в Tasks 2-4 (non-scenes), активен в Task 5 (scene)
- ✅ D-002 P-4 — golden_unavailable_reason в Tasks 2-5 critic acceptance
- ✅ D-002 P-5 — calibration/holdout split — prerequisite Phase 2 Task 7
- ✅ D-002 P-7 — counter_test_attempted 3-element в Tasks 2-5 Step A.4
- ✅ D-002 P-8 — model_used audit в Task 6 Step 6.3
- ✅ D-002 P-9 — tmp/critic-reports → archive в Tasks 2-5 Step A.11
- ✅ D-002 P-10 — pressure-test acceptance Phase 3 Layer-2 (prerequisite)
- ✅ D-002 P-11 — Mandate boundary в Task 1 add-golden-example
- ✅ D-002 P-12 — primary + secondary в Task 1
- ✅ D-002 P-13 — derived anti-lessons split в Task 1
- ✅ D-002 P-14 — diversity warnings в Task 1 Step 1.5
- ✅ D-002 P-15 — flagged risks Task 6 Step 6.4 (A3 conflicts anti = 0; A6 audience не открыта)

**Placeholder scan:**
- ⚠️ Creative content (thesis 150 слов, world-rules 5 правил, character ~300 слов, scene 300-500 слов) — описан **structurally** (что должно быть, какой паттерн, какая калибровка). Actual текст пишется orchestrator-сессией в fresh Auto-ai-series session по Поток A. Это **не placeholder** — это specification для execution.
- ⚠️ Task 5 «творческий процесс через адаптированный draft-story-bible-section или напрямую» — некоторая гибкость, потому что ПП1 не имеет dedicated draft-scene скилла. Specification что есть валидный fallback.

**Type/path consistency:**
- ✅ artefact-id'ы consistent: `thesis-001`, `world-rules-001`, `character-anna-001`, `scene-001`
- ✅ tmp/critic-reports/<artifact-id>/ + docs/critic-reports-archive/<artifact-id>/ paths consistent
- ✅ Skill names совпадают с Phase 3 SKILL.md frontmatter
- ✅ Subagent names совпадают с Phase 2 .claude/agents/ files
- ✅ Phase 1 tool invocations используют те же флаги (`--smoke-test`, `--root`, `--threshold`, `--artifact-id`, etc.)

---

## Expansion DONE — готов к execution в fresh Auto-ai-series session

**Execution prerequisite:** fresh Claude Code session с `cwd = C:/Users/user/Documents/Claude/Projects/Auto-ai-series/`.

**Deferred acceptances для выполнения ДО Phase 4:**
1. Phase 2 Task 7: runtime invocation acceptance 6 субагентов на ~30 RED-сценариях
2. Phase 3 Layer-2: pressure-testing 3 BLOCKER × 4 RED в orchestrator-сессии

**Recommended execution mode:** `superpowers:executing-plans` (НЕ subagent-driven-development) — Phase 4 — orchestrator-heavy work (Поток A в основной сессии, R-1 шляпы в основной сессии, Skills как procedural blocker'ы). Subagent-driven подходит для file creation; Phase 4 — это process execution.

После ПП1 acceptance (Task 7 commit + push) — **ПП2 starts**: Story Bible expansion + 6-8 кор-каст персонажей + регистр конфликтов через writing-plans для ПП2.
