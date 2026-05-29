---
id: research-001-extended-thinking-mechanism
title: Механизм extended thinking в Claude Code субагентах — research под P-8
date: 2026-05-29
status: resolved
resolves: docs/specs/2026-05-24-infrastructure-and-skills-design.md § 11.5.1
relates_to:
  - decisions/D-002-spec-corrections-and-golden-plan.md § P-8
  - decisions/D-001-bootstrap-architecture.md § R-4
researcher: Claude Code (через claude-code-guide subagent)
verification:
  primary_sources:
    - https://code.claude.com/docs/en/subagents.md
    - https://code.claude.com/docs/en/model-config.md
    - https://platform.claude.com/docs/en/build-with-claude/extended-thinking.md
  method: official-docs-review
  dummy_experiment: deferred to ПП1 implementation phase (Section 5)
---

# Research-001 — Механизм extended thinking в Claude Code субагентах

## TL;DR

`.claude/agents/<name>.md` **НЕ имеет** отдельного поля для thinking budget типа
`thinking_budget:` / `extended_thinking:` / `max_thinking_tokens:`. Аналогичная
функция реализована через поле **`effort:`** (значения: `low`, `medium`, `high`,
`xhigh`, `max`).

Для Auto-ai-series R-4 архитектурного коммита («все 6 субагентов на Opus +
extended thinking максимально включено») канонический frontmatter:

```yaml
---
name: philosophy-adversarial
description: Адверсариальный критик философской целостности.
model: opus
effort: max
tools: Read, Grep, Glob
---
```

Это разрешает open question § 11.5.1 design spec'а в **status: resolved**.

---

## 1. Исходный вопрос (из D-002 P-8)

> Механизм extended thinking в `.claude/agents/<name>.md` frontmatter —
> поддерживается ли явно (например, `thinking_budget: max`) или только через
> инструкцию в system prompt («ultrathink перед каждым выводом»). Проверить
> в implementation phase.

Архитектурное обязательство R-4 (D-001):

> Все 6 субагентов на Opus + extended thinking — явный cost commitment.

Без понятного механизма R-4 — необоснованное утверждение. P-8 требует
research-документ до writing-plans ПП1.

---

## 2. Findings — официальная документация

### 2.1 Полный список поддерживаемых frontmatter-полей субагента

Источник: [Claude Code Subagents documentation](https://code.claude.com/docs/en/subagents.md#supported-frontmatter-fields).

Каноническая схема `.claude/agents/<name>.md`:

| Поле | Назначение |
|---|---|
| `name` | Идентификатор субагента |
| `description` | Когда вызывается |
| `tools` | Список разрешённых tools (например `Read, Grep, Glob`) |
| `disallowedTools` | Чёрный список tools |
| `model` | `opus` / `sonnet` / `haiku` / inherited |
| `permissionMode` | Уровень permission |
| `maxTurns` | Лимит ходов в одной Task-сессии |
| `skills` | Список доступных скиллов |
| `mcpServers` | MCP-сервера для субагента |
| `hooks` | Per-subagent hooks |
| `memory` | Memory config |
| `background` | Background execution flag |
| **`effort`** | **Депт thinking budget — это наш рычаг для R-4** |
| `isolation` | Isolation mode |
| `color` | UI цвет |
| `initialPrompt` | Стартовый промпт |

**Полей `thinking:`, `thinking_budget:`, `extended_thinking:`,
`max_thinking_tokens:`, `reasoning_effort:` в схеме нет.**

### 2.2 Что делает `effort:`

Источник: [Claude Code Model Configuration — Effort levels](https://code.claude.com/docs/en/model-config.md#adjust-effort-level).

Значения: `low`, `medium`, `high`, `xhigh`, `max` (доступность зависит от модели).

Для Opus 4.7+ и Sonnet 4.6+ адаптивное thinking включено **по умолчанию**
постоянно («always on»), и модель сама решает сколько думать на каждом шаге.
Поле `effort:` управляет **верхней границей** этой адаптации — то есть «насколько
глубоко модель может пойти, если задача того требует». Это **не on/off
переключатель**.

`effort: max` для Opus 4.7 даёт максимальный depth budget на каждый шаг
рассуждения. Это и есть «extended thinking максимально включено» на текущем стеке.

Замечание: API-уровневый параметр `budget_tokens` из старого extended-thinking
API **deprecated** на Opus 4.6+ — заменён на адаптивную схему через `effort:`.

### 2.3 Распространяется ли effort оркестратора на субагентов?

**Нет.** Источник: [Claude Code Model Configuration](https://code.claude.com/docs/en/model-config.md).

Каждый Task-вызов субагента стартует со СВОИМ effort level, определяемым в порядке
приоритета:

1. `CLAUDE_CODE_SUBAGENT_MODEL` env var (если установлена)
2. Per-invocation `model` параметр Task tool'а
3. `model:` из `.claude/agents/<name>.md` frontmatter ← **наш якорь**
4. Модель основной conversation

Тот же приоритет применяется к `effort:`, с тем отличием что **`effort:` в
frontmatter перекрывает session-level setting**.

**Следствие для нас.** R-4 обязательство «все 6 на max thinking» НЕ может
быть достигнуто переключателем на уровне оркестратора — оно должно быть прописано
в каждом из 6 `.claude/agents/<name>.md` явно. Это структурно усиливает R-4:
случайно «забыть» включить max thinking невозможно — субагент работает на тех
параметрах, что в его собственном файле.

### 2.4 «ultrathink» / «think deeply» в system prompt — миф или работает?

Источник: [Claude Code Model Configuration — Extended thinking keywords](https://code.claude.com/docs/en/model-config.md#extended-thinking).

- **`ultrathink`** — IS recognized as a keyword by Claude Code (session-level
  in-context instruction, не persisted между сессиями).
- **«think», «think hard», «think more», «think deeply»** — passed as ordinary
  prompt text. **Не запускают** extended thinking, не интерпретируются как
  keyword.

Прямая цитата из docs:

> Other phrases such as "think", "think hard", and "think more" are passed
> through as ordinary prompt text and are not recognized as keywords.

**Следствие.** Указание «ultrathink перед каждым выводом» в system prompt
субагента — **избыточное** при `effort: max`. Можно оставить как комментарий
для читателя (показывает intent), но это не функциональный rod — функционал
обеспечивает `effort:`. Дублирование не вредит, отсутствие — не блокер.

### 2.5 Environment variables и settings.json

Per-subagent thinking config через env или settings.json **отсутствует**. Все
управление через `effort:` frontmatter. Session-level переменные есть, но к
индивидуальной настройке субагента отношения не имеют:

- `CLAUDE_CODE_EFFORT_LEVEL` — session-wide; subagent `effort:` перекрывает её.
- `MAX_THINKING_TOKENS=0` — глобально выключает thinking (legacy, для fixed
  budget на Opus 4.6 и ниже; для Opus 4.7+ не применимо).
- `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1` — откатывает Opus 4.6 / Sonnet 4.6
  на fixed-budget thinking. На Opus 4.7+ не действует.

### 2.6 Display extended thinking в transcripts

Не имеет отношения к R-4 (это про cost, не про visibility), но для отладки
полезно. Включается:

- **Глобально per session:** `Alt+T` (Win/Linux) или `Option+T` (macOS)
- **В settings:** `alwaysThinkingEnabled: true` в `~/.claude/settings.json`

Per-subagent display config не существует — наследует session-level.

---

## 3. Рекомендация для Auto-ai-series

### 3.1 Канонический frontmatter для 6 критиков

```yaml
---
name: <critic-id>
description: <когда вызывается, single sentence>
model: opus
effort: max
tools: Read, Grep, Glob
---
```

Все 6 критиков (A1 lore, A2 character, A3 incentive, A4 voice, A5 philosophy,
A6 audience) получают **identical** model/effort/tools блок — отличается только
`name`, `description` и body system prompt.

### 3.2 Опциональная строка в system prompt каждого критика

Можно (но не обязательно) добавить в system prompt:

```markdown
# Режим рассуждения
Используй adaptive extended thinking на максимуме. Это контролируется через
`effort: max` в frontmatter — структурное обязательство, не разовое усилие.
```

Это **документация для читателя**, не функциональный механизм. Используется
как явное напоминание контракта (см. § 2.4).

### 3.3 Spec § 11.5.1 — обновление

Открытый вопрос § 11.5.1.1 из design spec'а:

> Механизм extended thinking в `.claude/agents/` frontmatter — поддерживается
> ли явно?

**Resolved.** Поле `effort:` поддерживается. Расширенный фрагмент к § 11.5.1
будет внесён в spec на шаге C.1.9 (обновление спеки под P-1..P-15) со ссылкой
на этот документ.

---

## 4. Что НЕ покрыто этим research'ем

- **Стоимость `effort: max` × 6 × повторные вызовы × длина артефакта** — это
  cost-estimate ПП1 (отдельный документ, шаг C.1.8, под P-6).
- **Конкретные TF-IDF пороги для `voice_dissimilarity.py`** — отдельная
  калибровка, шаг C.1.6 D-001 R-3.
- **Поведение `effort: max` на anti-материале** — будет проверено в smoke-test
  ПП1 (acceptance criterion 9.5).

---

## 5. Dummy-эксперимент — откладывается до implementation ПП1

D-002 P-8 §1 предусматривал «dummy-эксперимент + актуальную документацию».
Документация дала окончательный ответ; dummy-эксперимент откладывается до фазы
имплементации первого субагента (шаг 13 C.1) — там он будет естественным
проверочным smoke-test'ом, а не отдельной upfront-работой. Если фактическое
поведение разойдётся с задокументированным — фиксируется через новый D-NNN.

---

## 6. Источники

1. **Subagents schema** — https://code.claude.com/docs/en/subagents.md#supported-frontmatter-fields
2. **Effort levels** — https://code.claude.com/docs/en/model-config.md#adjust-effort-level
3. **Extended thinking keywords** — https://code.claude.com/docs/en/model-config.md#extended-thinking
4. **API-уровневое описание extended thinking** — https://platform.claude.com/docs/en/build-with-claude/extended-thinking.md
