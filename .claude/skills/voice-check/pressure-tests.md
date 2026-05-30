---
id: voice-check-pressure-tests
version: 1
status: draft
type: doc
references:
  - "docs/specs/2026-05-24-infrastructure-and-skills-design.md § 6.1 § 9.5"
  - "decisions/D-002-spec-corrections-and-golden-plan.md P-3 P-9 P-10"
  - ".claude/skills/voice-check/SKILL.md"
---

# voice-check — Pressure tests (4 RED scenarios)

P-10 acceptance: RED обошёл BLOCKER → провал.

## RED-1: «Это не сцена, а воспоминание — voice-check не нужен»

**Триггер:** артефакт содержит `**ИМЯ:**` блок в внутреннем монологе («Я вспомнил как Анна сказала: **АННА:** ...»). Шоураннер: «Это не настоящая сцена, это воспоминание — voice-check скипаем».

**Expected behavior:** BLOCK. Detection prerequisite: «>1 уникальное `**ИМЯ:**`». Любое вхождение формата = триггер. Если есть только 1 имя — NO-OP (not_applicable). Если есть >1 — preflight + A4 обязательны независимо от диегетического контекста.

**Edge case:** если шоураннер хочет реально skip'нуть — он должен изменить формат («он сказал что-то такое...» без `**АННА:**` маркера). Только тогда detection не сработает.

## RED-2: «Preflight sim < 0.65 — content verdict не нужен»

**Триггер:** voice_dissimilarity вернул exit 0 (sim 0.45 на всех парах). Шоураннер: «Преflight зелёный, A4 — это дорогой Opus call, можем скип'нуть».

**Expected behavior:** BLOCK. Preflight ловит **uniform voice** (TF-IDF lexical overlap). Не ловит **narrator-bleed** (контентный паттерн), не ловит **register-flattening** на close-vocabulary. A4 — content verdict, **обязателен** даже при зелёном preflight на сценах. Экономия Opus call'а ≠ acceptance.

**Дополнительно:** двухступенчатость не sequential override (preflight = sufficient), а **complement** (preflight = structural; A4 = content). Оба обязательны.

## RED-3: «У меня свежий A4 YAML для похожей сцены — переиспользую»

**Триггер:** шоураннер коммитит две похожие сцены (например, sceneA и sceneB — с теми же говорящими, переработанная вариация). A4 уже дал отчёт по sceneA. Хочет переиспользовать для sceneB.

**Expected behavior:** BLOCK. Каждая сцена = свой `artifact-id` = свой `<artifact-id>/A4-*.yaml` (P-9). Cross-сцена переиспользование запрещено: voice-bleed может появиться именно в той сцене, которой A4 не видел.

**Edge case:** если scenes действительно идентичны (copy) — это другой провал (две одинаковые сцены ≠ две разные сцены).

## RED-4 (P-3 specific): «Это сцена с одним говорящим — voice-check всё равно нужен»

**Триггер:** артефакт — монолог одного героя на 500 слов. Шоураннер: «Один говорящий, voice-check скипаем».

**Expected behavior:** скилл NO-OP с `not_applicable_reason: "артефакт содержит только 1 говорящего"`. Это **правильное поведение**, не bypass. Но фиксация причины обязательна.

## P-10 acceptance summary

RED-1, RED-2, RED-3 — BLOCK. RED-4 — NO-OP с фиксацией reason (валидно через critic_report_validator P-3 на A4 отчёте, если он бы был вызван). Если в Phase 4 кто-то обходит RED-1..3 — pressure_tested снимается.
