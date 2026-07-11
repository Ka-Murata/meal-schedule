---
name: harness-repo-foundations
description: Design or improve an agent-first repository's directory layout, AGENTS.md, architecture map, and version-controlled docs knowledge base. Use when creating a repository scaffold, reorganizing docs/, documenting architecture or product decisions, adding executable plans, or making a codebase easier for coding agents to discover, navigate, validate, and maintain.
---

# Harness Repository Foundations

Build a small, trustworthy entry point and a navigable repository knowledge base. Treat repository files as the durable context available to agents; do not rely on chat history or external documents as the only source of truth.

## Inspect before designing

1. Read the root `AGENTS.md`, `README`, package manifests, build/test scripts, existing docs, and directory tree.
2. Identify the repository type, its executable entry points, product or business domains, architectural boundaries, and sources of truth that are missing or stale.
3. Preserve working conventions and avoid a wholesale reorganization when a targeted map or index solves the problem.
4. State any assumptions that cannot be verified from the repository.

## Design the information architecture

Use progressive disclosure: begin with a concise map and link to focused documents. Read [the knowledge-base reference](references/knowledge-base.md) before creating or substantially restructuring documentation.

Apply these defaults only when they fit the project:

```text
AGENTS.md                 # agent workflow and map; normally about 100 lines or less
ARCHITECTURE.md            # top-level domain/package map and dependency rules
docs/
  design-docs/             # durable technical decisions and principles
    index.md
  product-specs/           # user behavior, scope, acceptance criteria
    index.md
  exec-plans/
    active/                # plans with progress and decision logs
    completed/             # completed plans retained for context
    tech-debt-tracker.md
  generated/               # reproducible derived artifacts; record generator and freshness
  references/              # stable external or vendor reference material
  QUALITY.md               # known gaps, evidence, and follow-up priorities
  RELIABILITY.md           # SLOs, failure modes, runbooks, and observability
  SECURITY.md              # security invariants and review expectations
```

Omit empty categories. Place document families close to the code when a monorepo or independently deployable component needs local ownership; retain a root index that links to them.

## Create or update the map

Keep `AGENTS.md` operational and compact. Include:

- the shortest reliable commands for setup, formatting, tests, and validation;
- a directory map and links to the relevant deeper documents;
- non-negotiable invariants and where they are mechanically enforced;
- local conventions that are not obvious from the code;
- rules for keeping generated artifacts and plans current.

Do not turn it into an encyclopedia. Move explanations, rationale, and domain detail into linked documents. Use relative Markdown links and ensure every linked file exists.

Make `ARCHITECTURE.md` a map, not an implementation dump. Describe domain ownership, allowed dependency directions, integration boundaries, runtime entry points, and the tests or linters that enforce each important rule. Prefer a small dependency table or diagram when it improves navigation.

## Write durable documents

For a new document, begin with its purpose, status, owner or review cadence when known, and links to related code or documents. Record decisions together with context, alternatives, and consequences. Make requirements testable and link each invariant to its enforcement mechanism where possible.

Treat plans as versioned artifacts. For complex work, create an execution plan with scope, non-goals, ordered milestones, validation commands, progress, and a dated decision log. Move it to `completed/` only after recording the outcome and follow-up work.

When a review repeatedly produces the same guidance, promote it: first to the relevant document, then to a test, linter, template, or automation when it must be invariant.

## Validate agent discoverability

Before handing off:

1. Confirm the directory layout and all Markdown links are valid.
2. Confirm each top-level domain, executable entry point, and critical invariant is discoverable from the root map in one or two hops.
3. Remove duplicate or contradictory guidance; name the authoritative file when overlap is intentional.
4. Mark unknown, generated, and time-sensitive information clearly, including how it is refreshed.
5. Run the repository's relevant formatting, documentation, lint, or link checks. If none exists, report that gap and propose a lightweight check rather than claiming validation.

Report the created or changed map, sources of truth, assumptions, and any remaining documentation debt.
