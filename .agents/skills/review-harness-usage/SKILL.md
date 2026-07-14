---
name: review-harness-usage
description: Review how a project has used its repository harness, identify evidence-backed friction and drift, and separate project-local fixes from improvements worth contributing to the upstream harness template. Use for periodic harness retrospectives, after a substantial execution plan or several pull requests, when agents repeatedly struggle with the same repository guidance, or when deciding which lessons from a fork should be generalized upstream.
---

# Review Harness Usage

Review the harness from observed project use. Prefer the smallest reusable improvement supported by evidence; do not turn generic best practices into findings without a repository-specific signal.

## Set the review scope

1. Work from the project repository root and read `AGENTS.md`, `README.md`, `ARCHITECTURE.md`, `docs/README.md`, `docs/QUALITY.md`, relevant document indexes, build or test settings, CI configuration, and applicable repository skills.
2. Determine the review window from a user-provided date or revision, a recorded previous review, or the most recent meaningful milestone. If none exists, choose a reasonable Git-history window and state it. Never invent a previous review boundary.
3. Inspect the changes and evidence in that window: Git history and diffs, completed and active execution plans, decision records, quality evidence, technical debt, and repeated review guidance. Use pull-request data when it is available and materially useful; do not make the review depend on network access.
4. Keep verified facts, inferences, and unavailable external state separate. Do not modify files or external systems unless the user explicitly asks to record or apply the findings.

## Evaluate the harness

Look for both successful behavior and friction in these areas:

- discoverability: important domains, entry points, invariants, and validation commands are reachable from the root map in one or two hops;
- authority and freshness: implementation, configuration, source-of-truth documents, indexes, and generated artifacts agree and have clear review triggers;
- feedback loops: repeated invariants have proportionate tests, linters, templates, or CI checks, and recorded validation matches what was actually run;
- traceability: requirements, decisions, plans, implementation, evidence, and follow-ups close together without unrelated changes;
- adaptive depth: small work stays lightweight while risky, uncertain, external, or hard-to-reverse work receives explicit decisions and deeper validation;
- operational boundaries: deployment, public exposure, sensitive data, reliability, and security are reviewed only when they are in scope.

Support every finding with a file, change, command result, review pattern, or other concrete artifact. Report practices that worked so the upstream template does not remove useful behavior while addressing a problem.

## Classify each finding

Classify a finding as **project-local**, **upstream candidate**, or **uncertain**.

Use **upstream candidate** only when all of these are true:

1. The problem can plausibly recur in unrelated projects.
2. The problem and proposed change can be explained without product-specific names, data, paths, or assumptions about one technology stack.
3. The improvement belongs to the shared harness shape, guidance, skill, document template, pull-request structure, or a stack-neutral invariant.
4. Observed evidence justifies the change; generality alone is not evidence.
5. The proposal preserves adaptive use and does not impose the same ceremony on every change.

Keep product behavior, application code, deployment choices, domain safety rules, and stack-specific commands in the project unless the user supplies evidence that the upstream template intentionally owns them.

When evidence is incomplete, classify the finding as **uncertain** and name the evidence needed. Do not force a binary decision.

## Recommend the smallest improvement

Choose the least mechanism that reliably addresses the observed problem:

1. Clarify existing guidance for a first, low-risk occurrence.
2. Improve a template or review prompt when the same information should be supplied consistently.
3. Add a deterministic check only for a recurring or high-value invariant that can be tested without product-specific assumptions.

For each upstream candidate, describe the generalized problem, evidence from the fork, smallest upstream change, expected benefit, and explicit non-goals. Do not copy a project commit wholesale. If the user later asks to implement a candidate, start from the upstream source and reimplement only the generalized change.

## Report the retrospective

Write the report in the user's language and lead with the outcome. Include:

1. review window and evidence inspected;
2. harness behavior that worked well;
3. findings with severity, evidence, classification, and recommendation;
4. upstream candidates ordered by expected value and effort;
5. project-local follow-ups;
6. assumptions and external state that could not be verified;
7. one recommended next action and the next review trigger.

Do not create a score unless the user requests one. Stop after presenting the review and candidates unless the user explicitly asks to save a durable report, change the current project, or prepare an upstream contribution.

Suggested review triggers are completion of a substantial execution plan, roughly five merged pull requests, repetition of the same review guidance, or a monthly review during active development. The skill performs the review when invoked; it does not create its own schedule.
