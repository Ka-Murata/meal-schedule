# Repository Knowledge Base Reference

Use this reference when selecting documentation categories, writing indexes, or reviewing a repository's discoverability.

## Principles

- Keep the entry point short and stable; make it a map to authoritative detail.
- Store durable project knowledge in version-controlled files beside the code it governs.
- Prefer explicit, local ownership and relative links over implicit knowledge in tickets or chat.
- Reveal context in layers: root map, area map, focused document, then code or generated evidence.
- Encode high-value rules mechanically. A document explains a rule; a test, linter, or CI check preserves it.
- Preserve decisions and completed plans when they explain current constraints; delete only obsolete duplication.

## Document families

| Family | Purpose | Include | Exclude |
| --- | --- | --- | --- |
| `design-docs/` | Durable technical decisions | status, context, alternatives, consequences, links to enforcement | transient task notes |
| `product-specs/` | Product intent and acceptance | user behavior, scope, non-goals, measurable acceptance criteria | implementation guesses presented as requirements |
| `exec-plans/active/` | Coordinate complex work | milestones, validation, progress, dated decisions | vague TODO lists |
| `exec-plans/completed/` | Preserve execution context | outcome, evidence, follow-ups | unfinished or unreviewed work |
| `generated/` | Store derived facts | generator command/source, generation date, freshness policy | hand-edited outputs without provenance |
| `references/` | Retain stable third-party knowledge | source, version/date, relevance | unbounded copies of external documentation |
| quality/reliability/security docs | Track operational expectations | invariants, evidence, current gaps, owners or review cadence | aspirational claims without verification |

## Index rules

Each document family should have an `index.md` if it contains more than a few files. List a one-line purpose, status, and link for each item. Make active and completed plans separately visible. Link cross-cutting documents from the root map, but avoid repeating their content.

## Freshness and authority

For every document that can become stale, state one of: its owner, review cadence, source command, source URL/version, or event that triggers review. When two documents overlap, explicitly label the authority boundary. Do not silently copy configuration values or API contracts into prose; link to the source and explain only the intent that code cannot convey.

## Minimal execution-plan template

```markdown
# <Outcome>

Status: active
Owner: <if known>
Related: <links>

## Scope

## Non-goals

## Milestones and validation

1. <milestone> — validate with `<command>`

## Progress

- YYYY-MM-DD: <evidence-based update>

## Decisions

- YYYY-MM-DD: <decision, rationale, consequence>

## Follow-ups
```
