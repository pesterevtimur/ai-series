# verification-before-completion — pinned reference

**Origin:** obra/superpowers@f2cbfbef (== local v5.1.0)
**Pinned on:** 2026-05-30
**Used as:** база discipline-механизма для адаптации

## Зачем pinned

База discipline-механизма. Расширяется в `.claude/skills/evidence-before-action/` на narrative claims (тезис устоял в адверсариальном проходе, voice-check зелёный, consistency-check зелёный, concern_resolution_validator зелёный).

## Как используется

- Адаптируется в `.claude/skills/evidence-before-action/SKILL.md` через `lineage:` frontmatter
- Source-of-truth для discipline-семантики «evidence ≠ память»

## Workflow обновления (spec § 7.4)

1. Не обновляем автоматически.
2. Проверяем upstream drift периодически.
3. Если обновляем — bump SHA, re-validate все адаптации через pressure-testing.
4. Если НЕ обновляем — фиксируем reason здесь.

## Адаптации

См. `.claude/skills/evidence-before-action/SKILL.md` — frontmatter `lineage.ref:` указывает на этот файл.
