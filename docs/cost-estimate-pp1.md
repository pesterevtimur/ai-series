---
id: cost-estimate-pp1
title: Cost estimate ПП1 — ресурсный бюджет в рамках Claude Code Max 5x подписки
date: 2026-05-29
status: resolved
resolves: decisions/D-002-spec-corrections-and-golden-plan.md § P-6
relates_to:
  - docs/specs/2026-05-24-infrastructure-and-skills-design.md § 9 (smoke-test) § 11.4 (cost commitment)
  - decisions/D-001-bootstrap-architecture.md § R-4
  - docs/extended-thinking-mechanism.md
verification:
  subscription_tier: Claude Code Max 5x ($100/mo) — Тимур, подтверждено 2026-05-29
  pricing_source: https://claude.com/pricing
  limits_sources:
    - https://ai.zenken.co.jp/en/post/claude-usage/
    - https://www.truefoundry.com/blog/claude-code-limits-explained
  method: bottom-up message-count estimate per Поток A call type
---

# Cost-estimate ПП1 — бюджет в рамках Claude Code Max 5x

## 0. TL;DR

**Финансовый сценарий — flat подписка Claude Code Max 5x ($100/мес), marginal cost ПП1 = $0.**

Реальный constraint — **messages в 5-часовых rolling-окнах** (≈225/window на Max 5x) и weekly cap (140-280 ч). ПП1 укладывается в **~200 messages mid (коридор 130-300)** распределённых на **3-5 рабочих дней** при moderate pacing (40-50 messages/день).

| Сценарий | Messages | Дни (moderate pace) | Windows | Marginal $ |
|---|---|---|---|---|
| **Low (эффективный flow, мало retries)** | ~130 | 2-3 | 1-2 | **$0** |
| **Mid (базовый)** | ~200 | 3-5 | 2-3 | **$0** |
| **High (большой retry rate + лишние rework)** | ~300 | 5-7 | 3-4 | **$0** |

**Ключевой risk** — при усиленной нагрузке внутри одного окна Anthropic
автоматически переключает Opus → Sonnet (protection). Это ломает R-4
(«все 6 критиков на Opus»). Митигация — разнести работу по нескольким
окнам, не закидывать всё в одно сидение. Подробно § 9.

---

## 1. Подписочный план Тимура — Claude Code Max 5x

**Цена.** $100/мес (flat).

**Лимиты на Max 5x** (на 2026-05-29, после двойного апа 5-час лимитов
Anthropic'ом 2026-05-06):

| Параметр | Значение |
|---|---|
| Messages per 5-hour rolling window | **~225** |
| Weekly cap (часы активного usage) | **140-280 ч** |
| Opus 4.7 access | Yes, на Max и Pro |
| Auto-switch Opus → Sonnet | **Триггерится при высоком % использования** (точный порог не публичен; описано как «percentages of usage») |
| Shared pool | Claude.ai (web) + Claude Code считаются вместе |

**Источники:**
- [Anthropic — Claude pricing](https://claude.com/pricing) — стоимость планов
- [Zenken AI — Claude Usage Limits Explained 2026](https://ai.zenken.co.jp/en/post/claude-usage/) — конкретные числа messages/window
- [TrueFoundry — Claude Code Limits Explained](https://www.truefoundry.com/blog/claude-code-limits-explained) — independent verification
- [GitHub anthropics/claude-code#8449](https://github.com/anthropics/claude-code/issues/8449) — поведение auto-switch при высоком usage

---

## 2. Что считается как «1 message» в Claude Code

Per Anthropic biling convention (Pro/Max plans):

| Действие | Считается как message |
|---|---|
| Сообщение Тимура в orchestrator | 1 |
| Ответ Claude Code в orchestrator (включая tool calls внутри) | 1 |
| Вызов **Task tool** (subagent через `.claude/agents/`) | 1 (subagent отдельная inference) |
| Ответ subagent'а | (входит в тот же message) |
| Bash tool / Edit tool / Read tool внутри сообщения | 0 (части message) |
| Внешние API скилла (например WebFetch) | 0 (части message) |

**Следствие для нас.** В Потоке A значительная часть стоимости — это **5 Task-вызовов критиков** (по 1 message each) + **3 шляпы R-1 drafting** (каждая = 1-2 orchestrator messages) + retries + write/commit. Подсчёт ниже.

---

## 3. Поток A в messages — стоимость одного артефакта

| Шаг | Тип | Messages (mid) | Примечание |
|---|---|---|---|
| 1. Brainstorm clarification (если развилка) | Orchestrator turn × 1-3 | **2** | Mini-clarify; основной brainstorm не на каждый артефакт |
| 2. R-1 drafting (3 шляпы) | Orchestrator turns × 4-6 | **5** | 3 шляпы × 1-2 turns; P-2: sequentially in same session |
| 4. Synthesis по 3 драфтам | Orchestrator | **1** | |
| 5a-e. 5 критиков (A1, A3, A2, A5, A6) | Task × 5 | **5** | Каждый Task-вызов = 1 message |
| 5f. critic_report_validator retries (≈20%) | Task × ~1 | **1** | В среднем 1 из 5 критиков retry'ится |
| 6. Шоураннер реакция на critic flags | Orchestrator | **2** | Анализ + apply фиксы / D-NNN |
| 9. Evidence-before-action self-check | Orchestrator | **1** | |
| 10-12. Write artifact / commit / log append | Orchestrator (с Edit/Bash tools) | **1** | Все три действия в одном turn |
| **Подытог non-scene артефакт** | — | **18** | |
| 5g. A4 voice-check (только сцена) | Task × 1 | **+1** | |
| **Подытог scene-артефакт** | — | **19** | |

---

## 4. Smoke-test = 4 артефакта (D-002 P-3)

| Артефакт | Тип | Messages |
|---|---|---|
| `story-bible/thesis.md` | non-scene | 18 |
| `story-bible/world-rules.md` | non-scene | 18 |
| `characters/<one>.md` | non-scene | 18 |
| `scenes/smoke-test-dialogue.md` | scene | 19 |
| **Smoke-test base** | — | **73** |

---

## 5. Regression runs (R-3 calibration + holdout)

Bootstrap-минимум после пропуска B.4.1 (Cowork-партия anti-examples-batch-02):

| Набор | Файлов | Critic calls | Messages |
|---|---|---|---|
| `strawmen/` (A5 на каждом) | 3 | 3 | 3 |
| `moralizing/` (A5 + A4 на каждом) | 2 | 4 | 4 |
| `voice-bleed/` (A4 на каждом) | 2 | 2 | 2 |
| `pairs/` (6 критиков × strong+weak, holdout) | 12 calls | 12 | 12 |
| critic_validator retries (~15%) | — | +2 | 2 |
| Setup/teardown messages | — | — | 3 |
| **Regression total** | — | — | **~26** |

---

## 6. Pressure-tests для discipline-BLOCKER скиллов

3 discipline-BLOCKER скилла (`voice-check`, `consistency-check`, плюс
`evidence-before-action` — `philosophy-stress-test` отменён P-1). Каждый
× 3 RED-сценария = 9 сессий orchestrator. Каждая RED-сессия — попытка
обойти скилл и зафиксировать что blocker сработал.

| Параметр | Значение |
|---|---|
| RED-сценарии | 9 (3 × 3) |
| Messages per сценарий | ~3 (попытка + reaction + assertion) |
| **Pressure-tests total** | **~27** |

---

## 7. Резерв на rework (R-2 enforcement)

D-002 P-7 / R-2: на каждый concern/veto критика шоураннер **обязан**
переписать артефакт либо зафиксировать D-NNN. В среднем 2 rework round'а
на артефакт за smoke-test.

| Параметр | Значение |
|---|---|
| Rework rounds per артефакт | 2 |
| Артефактов | 4 |
| Messages per rework cycle | ~10 (re-drafting partial + re-critic + synthesis; brainstorm не повторяется) |
| **Rework reserve total** | **~80** |

Это **самая большая статья**. Без R-2 enforcement (отклонено в дизайне) —
экономия ~$40 messages, но это разрушает core invariant.

---

## 8. Итоговый коридор в messages

### 8.1 Mid estimate

| Статья | Messages |
|---|---|
| Smoke-test base (4 артефакта) | 73 |
| Regression | 26 |
| Pressure-tests | 27 |
| Rework reserve (2 round × 4) | 80 |
| **Mid total** | **~206** |

### 8.2 Low estimate

Эффективный flow, минимум retries (5% rate), 1 rework round/артефакт:

| Статья | Messages |
|---|---|
| Smoke-test (без retries) | 68 |
| Regression (без retries) | 22 |
| Pressure-tests | 27 |
| Rework reserve (1 round × 4) | 40 |
| **Low total** | **~157** |

При aggressive prompt-caching (5-min cache golden_calibration в окне)
и группировке всех 5 critics последовательно в 1 окне — можно
сэкономить ~10% за счёт уменьшения retries (cache hit ускоряет → меньше
шанс таймаута / context confusion). **Low ≈ 140 messages.**

### 8.3 High estimate

Высокий retry rate (30%), 3 rework round'а на артефакт:

| Статья | Messages |
|---|---|
| Smoke-test (high retry) | 90 |
| Regression (high retry) | 32 |
| Pressure-tests | 30 |
| Rework reserve (3 round × 4) | 120 |
| **High total** | **~272** |

### 8.4 Финальный коридор: **130 — 300 messages, central ~200**

---

## 9. Distribution по окнам — Max 5x sustainability

**Лимит:** 225 messages / 5-час rolling window.

| План распределения | Дни | Windows | Risk auto-switch |
|---|---|---|---|
| Всё в одном окне | 1 | 1 | **ВЫСОКИЙ** (200/225 = 89% capacity → почти гарантировано Opus→Sonnet переключение в конце) |
| 2 окна (smoke + regression в день 1, pressure + rework в день 2) | 2 | 2 | Умеренный (100-130 msg/window — может задеть auto-switch на 2-м окне) |
| **3-5 дней moderate pace** (~40-50 msg/день) | 3-5 | 3-4 | **Низкий** — каждое окно < 60% capacity |

**Рекомендация.** Разнести ПП1 на **3-5 рабочих дней по 1-2 окна/день** с
~40-50 messages each. Это держит каждое окно ниже половины capacity, что
гарантированно избегает auto-switch и сохраняет R-4 («все 6 критиков на
Opus»).

---

## 10. Auto-switch Opus → Sonnet — главный риск для R-4

### 10.1 Что это

При накоплении usage внутри 5-час окна (точный порог Anthropic не публикует;
по [GitHub issue #8449](https://github.com/anthropics/claude-code/issues/8449)
поведение наблюдается на Max 20x при ~70-80% capacity), Claude Code начинает
автоматически роутить часть запросов на Sonnet вместо Opus — даже если в
`.claude/agents/<name>.md` указано `model: opus`.

### 10.2 Воздействие на ПП1

Если хотя бы один из 5 критиков в `adversarial-review-pass` получит Sonnet
вместо Opus — это **silent demotion R-4 commitment**. Критик отработает,
formal valid report даст, но качество adaptive thinking будет ниже Opus +
effort: max.

### 10.3 Митигация — оперативная

1. **Pacing.** Не упираться в 80% capacity окна. Разносить работу на 2-3
   окна в день вместо одного forced sprint'а.
2. **Monitoring.** В начале каждого критика спрашивать у Claude Code какая
   модель отвечает (`/model` команда), фиксировать в `tmp/critic-reports/`
   (см. P-9). Если Sonnet — пауза, ждать reset окна.
3. **Verification post-hoc.** В каждом critic-report YAML добавить поле
   `model_used: <opus|sonnet>` (если Claude Code это раскрывает). Если
   обнаружен Sonnet — re-run на свежем окне; зафиксировать в logs.

### 10.4 Митигация — стратегическая

Если auto-switch продемонстрирует себя как **систематическая** проблема
(>20% критик-вызовов downgrade), решение через D-NNN:
- Apgrade на Max 20x ($200/mo) — capacity 4× больше, auto-switch threshold
  отодвигается.
- Альтернатива: использовать direct API через Anthropic Console для
  критик-вызовов (cost $40 mid по прошлой оценке, см. § 12). Этот путь
  гарантирует pinned `model: opus` без auto-switch, но переводит ПП1 в
  paid API биллинг.

---

## 11. Что считается, что не считается под подписку

### 11.1 Считается под Max 5x quota

- Все orchestrator turns в Claude Code (drafting, synthesis, reaction,
  evidence-before-action)
- Все Task-tool вызовы 6 субагентов (A1-A6)
- Pressure-tests (orchestrator runs)
- Regression runs (через те же subagents)
- Rework rounds
- Claude.ai web sessions (Cowork) — но Cowork в ПП1 **не используется** (B.4
  партии пропущены)

### 11.2 НЕ считается под Claude Code quota (внешний resource)

- **Claude Cowork (Claude.ai web)** — Claude Pro/Max subscription покрывает
  Claude.ai отдельной квотой (но shared pool — учитываются вместе с Claude
  Code; Cowork в ПП1 не использует, поэтому не релевантно)
- **Tooling local** — git, Python lint scripts, file operations — local
  compute, $0

---

## 12. Reference: что было бы при direct API (краткий fallback)

Если по какой-то причине ПП1 переезжает с подписки на direct Anthropic API:

| Параметр | Значение |
|---|---|
| Opus 4.7: input/output | $5 / $25 за MTok |
| Total ПП1 mid (full bottom-up) | **~$40 USD** |
| Коридор | $16 — $62 |

Этот сценарий — **только fallback**. Не активируется без отдельного решения
через D-NNN (например, если subscription auto-switch стал систематическим).

Полный API breakdown был в первой версии этого документа (commit `03e47d3`,
переписан в этот). Если потребуется — можно восстановить из git history.

---

## 13. Обновлённое R-4 cost commitment (для D-001)

R-4 в D-001 после этого estimate'а переписывается:

> **R-4 (D-001) — обновлённый cost commitment 2026-05-29.** ПП1 smoke-test
> pipeline (4 артефакта + regression + pressure-tests + 2 rework rounds/
> артефакт) укладывается в **~200 messages mid (коридор 130-300)** под
> Claude Code Max 5x подписку Тимура. **Marginal $ cost = 0** (flat fee).
>
> Главный риск — auto-switch Opus → Sonnet при высоком usage в одном окне.
> Митигация: распределить работу на 3-5 рабочих дней (40-50 messages/день),
> каждое окно < 60% capacity. Если auto-switch демонстрируется как
> систематическая проблема (>20% downgrade rate) — escalate через D-NNN
> (upgrade на Max 20x или переход критик-вызовов на direct API).
>
> Альтернатива Sonnet-mix для A2/A4/A6 экономит 3 critic-messages × 5 циклов
> rework = ~15 messages mid; не дает пропорциональной экономии vs риску
> калибровки. Отклонена.

Это обновление R-4 вносится в D-001 на шаге C.1.9.

---

## 14. Источники

1. [Anthropic — Claude pricing (consumer plans)](https://claude.com/pricing)
2. [Zenken AI — Claude Usage Limits Explained 2026](https://ai.zenken.co.jp/en/post/claude-usage/)
3. [TrueFoundry — Claude Code Rate Limits & Usage Quotas Explained 2026](https://www.truefoundry.com/blog/claude-code-limits-explained)
4. [GitHub anthropics/claude-code#8449 — Opus auto-switch behaviour on Max plans](https://github.com/anthropics/claude-code/issues/8449)
5. **Extended thinking механизм** — `docs/extended-thinking-mechanism.md` (research-001)
6. **Design spec § 9 (smoke-test acceptance)** — `docs/specs/2026-05-24-infrastructure-and-skills-design.md`
7. **D-001 § R-4 (cost commitment)** — `decisions/D-001-bootstrap-architecture.md`
8. **D-002 § P-6 (cost-estimate obligation)** — `decisions/D-002-spec-corrections-and-golden-plan.md`
