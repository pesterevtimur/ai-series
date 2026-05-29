# Журнал проекта Auto-ai-series

Каждая сессия добавляет одну строку в формате:

```
[YYYY-MM-DD] <type> | <одно-предложение-что-сделано>
```

Типы: `setup`, `decision`, `spec`, `skill`, `agent`, `tool`, `bible`, `character`, `lore`, `conflict`, `episode`, `scene`, `golden`, `infra`, `docs`, `blocker`, `note`.

Сессия = один прогон Claude Code от старта до закрытия (или до `/clear`).

---

[2026-05-24] decision | bootstrap brainstorming session — design spec ПП1 v0.1, D-001-bootstrap-architecture, cowork prompt v1.0; git init на main; первый cowork batch (scenes-01) в raw/_cowork-dumps/ обработка ждёт ПП2
[2026-05-29] infra | git history cleanup: raw/_cowork-dumps/ исключён из bootstrap-коммита (1870237→2cf6b7b), raw/ добавлен в .gitignore (fair use only internal); push в pesterevtimur/ai-series — публичный repo
[2026-05-29] decision | D-002 v2 strategic acceptance Тимура (commit e066cd4); B.4.1/B.4.2 Cowork-партии сознательно пропущены — flagged risk на A3/A5 R-3 калибровку, добор отложен до ПП2
[2026-05-29] docs | P-8 resolved: docs/extended-thinking-mechanism.md — поле effort: max в .claude/agents/*.md frontmatter; design spec § 11.5.1 готов к обновлению на step C.1.9
[2026-05-29] docs | P-6 resolved: docs/cost-estimate-pp1.md — ПП1 smoke-test pipeline $40 mid в коридоре $16-$62 (Opus 4.7 effort: max все 6 критиков); R-4 cost commitment в D-001 обновляется на step C.1.9
[2026-05-29] docs | P-6 переписан под подписочный сценарий: Max 5x ($100/mo flat), marginal $0; ~200 messages mid (130-300 коридор); главный риск — auto-switch Opus→Sonnet при высоком usage окна, митигация через pacing 40-50 msg/день
[2026-05-29] spec | design spec → v0.2: применены все 15 правок D-002 v2 (P-1..P-15) — 9 скиллов→8, R-1 шляпы вместо Task'ей, smoke-test 4 артефакта, golden_unavailable_reason, R-3 calibration/holdout split, effort: max в frontmatter субагентов, tmp/critic-reports на диск, Cowork mandate boundary, primary/secondary категории, example_type, diversity warnings, anti-corpus flagged risk; .gitignore + tmp/
[2026-05-29] infra | .gitignore + tmp/ (P-9 — для tmp/critic-reports/ до архивации)
