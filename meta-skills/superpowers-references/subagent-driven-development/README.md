# subagent-driven-development — pinned reference

**Origin:** obra/superpowers@f2cbfbef (== local v5.1.0)
**Pinned on:** 2026-05-30
**Used as:** используется напрямую, pinned для drift-detection

## Зачем pinned

Архитектурно критична: 6 субагентов A1-A6 + Cowork workflow + Phase 1/2/3 implementation выполнены через subagent-driven-development. НЕ адаптируется — используется как методологический скелет ПП2+ execution. Pinned для drift-detection.

## Как используется

- Напрямую через Skill tool (`Skill subagent-driven-development`)
- Шаблон implementer-prompt.md / spec-reviewer-prompt.md / code-quality-reviewer-prompt.md — лежат в upstream skill, не дублируются здесь
- Локальная копия здесь — снимок для сравнения с upstream

## Workflow обновления (spec § 7.4)

1. Не обновляем автоматически.
2. Проверяем upstream drift периодически.
3. Если обновляем — bump SHA, re-validate все адаптации через pressure-testing.
4. Если НЕ обновляем — фиксируем reason здесь.

## Адаптации

Нет (`adapted_to: null` в METADATA.json).
