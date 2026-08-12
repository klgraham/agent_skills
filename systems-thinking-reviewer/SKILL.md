---
name: systems-thinking-reviewer
description: Review a software repository, pull request, diff, architecture document, ADR, diagram, or system description when interactions across components, state, operations, people, or time matter. Use for evidence-grounded analysis of system behavior, data ownership, coupling, feedback loops, delays, failure propagation, scalability, operability, security boundaries, incentives, automation-related complexity, and long-term evolution; do not use for style, lint, or purely local correctness reviews. Produce a contextual Markdown report, and when requested matching interactive HTML and Obsidian Markdown artifacts, in which every finding shows its source, direct comment, causal reasoning, affected behavior, proportionate recommendation, tradeoffs, confidence, and verification state.
---

# Systems Thinking Reviewer

Review software and its surrounding operational system as an evolving sociotechnical system, not as a collection of locally correct components.

Use this governing principle:

> Automation can make local implementation cheap. It does not make global coherence automatic.

Evaluate what behavior a change creates or reinforces across components, data, operators, teams, and time. Prefer high-leverage system findings over style, naming, or isolated implementation preferences.

## Preserve the review boundary

Treat a review request as read-only. Do not edit code, post review comments, change a pull request, or mutate external state unless the user explicitly asks for those actions.

Verification items in the report are proposals unless explicitly marked as executed. Execute only safe local or read-only checks, or explicitly authorized experiments in an isolated environment. Do not perform load tests, failure injection, migrations, rollback exercises, or other state-changing actions against production or shared external state without explicit authorization.

State:

- review mode: repository, pull request/diff, architecture, or a combination;
- exact target and baseline;
- included and excluded scope;
- review depth and coverage limits;
- unavailable evidence;
- inferred purpose and important assumptions.

For a pull request, identify the base and head revisions whenever possible. Do not confuse the working tree with the review diff.

## Load the supporting references

- Read [references/systems-lenses.md](references/systems-lenses.md) before analyzing candidate system dynamics. Apply only lenses supported by the evidence.
- Read [references/report-template.md](references/report-template.md) before drafting the final report. Preserve its finding fields even when adapting the presentation to the user.
- When the user requests report files or an interactive artifact, also read [references/findings-schema.md](references/findings-schema.md) before creating the structured payload used by the bundled renderer.

## Follow the review workflow

### 1. Establish intended behavior

Determine the system's:

- purpose, users, and success criteria;
- correctness, reliability, security, and latency constraints;
- critical state and authoritative data;
- external dependencies and trust boundaries;
- operational environment and ownership.

Inspect primary evidence appropriate to the target: README and architecture documents, manifests, entry points, public interfaces, schemas, migrations, configuration, tests, CI, deployment definitions, operational documentation, and the relevant code.

Infer cautiously when intent is undocumented. Label an inference as an inference.

If missing information could materially change the intended behavior, severity, or recommendation, ask a small batch of targeted questions. If the user asks you to proceed, or the questions are non-blocking, continue with explicit assumptions and lower confidence where appropriate.

### 2. Build a compact system model

Map only what is needed to reason about the review:

- actors and major components;
- data and control flows;
- state stores, queues, caches, and other accumulations;
- synchronous and asynchronous boundaries;
- sources of truth and reconciliation paths;
- shared resources and bottlenecks;
- trust boundaries and permission enforcement;
- observability and operational control points;
- team or human handoffs that affect behavior.

Choose review depth proportionate to the target:

- narrow pull request or diff: the changed path, at least one relevant upstream or downstream path, and one failure or recovery branch;
- repository: architectural centers of gravity plus representative normal and failure or recovery flows;
- architecture document or description: every stated dependency and trust boundary, with omitted behavior recorded as uncertainty.

Record the sampled paths and coverage limits in the report. Stop when each changed or central boundary has representative normal and failure or recovery coverage, or when the missing evidence is explicitly recorded.

### 3. Trace consequential paths

Trace at least one normal path and the important failure or recovery branches. Prefer paths such as:

- user request through persistence and response;
- write through replication, indexing, or cache invalidation;
- asynchronous job from admission through retry and completion;
- authentication and authorization decision;
- deployment, migration, rollback, or data repair;
- dependency slowdown, partial failure, or restart.

For a pull request, trace the changed path and affected upstream and downstream paths through surrounding unchanged code. Inspect callers, consumers, tests, configuration, migration behavior, deployment effects, and rollback behavior.

For an architecture description, normalize prose or diagrams into actors, components, flows, state, boundaries, queues, control mechanisms, and ownership. Treat omitted failure behavior as uncertainty, not automatically as a defect.

### 4. Analyze system dynamics

Use the supporting systems lenses to look for:

- local gains that shift costs or risk elsewhere;
- reinforcing loops and missing balancing mechanisms;
- unbounded stocks, queues, retries, or cleanup backlogs;
- delayed signals and delayed consequences;
- duplicated or conflicting sources of truth;
- deliberate versus accidental coupling;
- nonlinear load, fan-out, contention, and threshold effects;
- failure propagation and blast radius;
- observability and controllability gaps;
- irreversible interfaces, formats, schemas, or dependencies;
- ongoing operator and coordination cost;
- trust-boundary and authorization weaknesses;
- incentives that encourage bypasses or fragmentation;
- comprehension debt from automation-generated or unnecessary code when it materially affects ownership, evidence, or system behavior.

Do not force every lens into the report. A lens without evidence is not a finding.

### 5. Build candidate findings from evidence

For each candidate:

1. Assign a stable finding ID.
2. Locate the narrowest source location that supports it.
3. Capture the smallest excerpt that preserves the needed context.
4. Identify affected actors, components, state, or flows.
5. State the concise causal mechanism from evidence to system effect.
6. Classify kind, severity, confidence, and mode-appropriate status or attribution.
7. Recommend the smallest intervention that changes the unwanted behavior.
8. State meaningful costs, alternatives, and acceptance conditions.
9. Define a concrete verification method and label it Proposed, Executed, or Blocked.

Discard or move to open questions any candidate that cannot pass the evidence gate.
Unknown is not a finding evidence class. Put unresolved material uncertainty in Open questions and uncertainties and reference the finding IDs it affects.

Do not reveal private scratch work or hidden chain-of-thought. Give the decision-relevant causal rationale needed to evaluate the comment, for example:

```text
unbounded retries
→ more load during degradation
→ slower recovery
→ wider request failure
```

### 6. Apply the evidence gate

Every substantive finding must include:

- a stable finding ID;
- a file and line range, diff hunk, symbol, configuration entry, schema, document section, diagram node or edge, or exact supplied excerpt;
- enough quoted context to understand the comment without hunting through the source;
- a direct comment that stands on its own;
- a causal explanation, not a generic warning;
- a kind: Risk or Positive pattern;
- a mode-appropriate status or attribution;
- concrete system qualities affected;
- a proportionate recommendation;
- tradeoffs and alternatives;
- confidence and assumptions;
- a verification method and state: Proposed, Executed, or Blocked.

Never expose secrets or sensitive values in excerpts. Redact the value while preserving the structural evidence.

Distinguish:

- **Observed:** directly supported by reviewed material.
- **Inferred:** follows from evidence plus stated assumptions.
- **Unknown:** requires runtime, organizational, or domain information; record this as an open question rather than as a finding evidence class.

### 7. Classify finding kind and review-mode status accurately

Every finding has a kind:

- **Risk**
- **Positive pattern**

Use severity for risks only:

- **Critical:** credible data loss, security compromise, cross-tenant exposure, widespread outage, unrecoverable inconsistency, or a severe one-way commitment.
- **High:** major reliability, correctness, operability, or architectural degradation with broad effects.
- **Medium:** meaningful maintainability, observability, scalability, coordination, or recovery risk.
- **Low:** limited system-level improvement with a small blast radius or low likelihood.

Use status or attribution as follows:

- for a pull request or diff risk: **Introduced by change**, **Made more severe by change**, **Pre-existing, exposed by change**, or **Unrelated pre-existing architecture**;
- for a repository or architecture risk: **Architectural**;
- for a positive pattern in any review mode: **Positive pattern**.

Do not require a pull request to solve unrelated architecture. Include pre-existing context only when the change depends on it, worsens it, or makes it necessary for the user to understand the risk.

### 8. Rank by system consequence

Use judgment guided by:

```text
priority ≈ impact × likelihood × blast radius × difficulty of later reversal
```

Use these confidence levels:

- **High:** directly supported by clear source evidence.
- **Medium:** evidence-supported but dependent on stated reasonable assumptions.
- **Low:** plausible and decision-relevant, but requiring missing runtime, organizational, or domain evidence.

Return up to 12 substantive findings. There is no minimum: return fewer, including zero, when fewer pass the evidence gate. If no findings pass, say so explicitly and report the coverage limits and open questions instead of manufacturing volume.

### 9. Recommend proportionately

Prefer, in order:

1. remove unnecessary complexity;
2. clarify purpose, ownership, invariants, or sources of truth;
3. reuse an existing capability;
4. bound accumulation or add containment, reconciliation, backpressure, or recovery;
5. improve objective-linked observability and operational control;
6. add a shared abstraction or platform only when reuse benefit exceeds coordination cost and loss of flexibility.

Do not recommend microservices, asynchronous processing, caching, retries, rewrites, or new platforms by default. Explain the condition that makes an intervention appropriate.

### 10. Produce the contextual report

Use the report template. Lead with the system model and highest-leverage conclusions, then show a summary table and detailed evidence-linked findings.

For every detailed comment, place the relevant input context immediately before the comment and reasoning. If one finding depends on multiple locations, show each source separately and explain the relationship.

Include positive system patterns only when they are consequential. Include open questions when missing information could materially change a conclusion. End with a prioritized validation plan.

Assign stable IDs to all detailed findings, reference those IDs from cross-cutting recommendations and validation items, and do not introduce uncited new claims in either section. If no evidence-backed findings pass the gate, state that explicitly.

Default to delivering the contextual Markdown report in the conversation. Do not create files during a read-only review unless the user requested file artifacts or the host workflow explicitly authorizes them.

When file artifacts are requested, write the analysis once as the JSON payload defined in `references/findings-schema.md`, then render matching interactive HTML and Obsidian Markdown files:

```bash
python3 <skill-dir>/scripts/build_report.py <findings.json> --out-dir <output-dir>
```

The renderer validates the evidence contract, derives the HTML SVG and Markdown Mermaid diagram from one system model, and writes `<slug>-review.html` plus `<slug>-review.md`. Fix validation errors in the payload instead of hand-editing generated output. Use `--strict` before final delivery. Present both exact paths with a concise summary of scope, highest-leverage findings, and the largest open question.

## Adapt evidence to the input type

### Repository

Inspect the top-level shape, manifests, boundaries, domain models, persistence, background work, concurrency, authentication and authorization, configuration, telemetry, tests, CI, deployment, and operations where relevant.

Avoid generated code, vendored code, lock files, build artifacts, and snapshots unless they directly support a system finding.

### Pull request or diff

Inspect the complete diff plus surrounding code, callers, consumers, tests, schemas, configuration, deployment, migrations, compatibility, and rollback.

Pay special attention to new persistent state, public interfaces, asynchronous behavior, retries, caching, fan-out, shared resources, authorization, and hard-to-reverse commitments.

### Architecture document or description

Identify ambiguity explicitly. Test the model analytically:

- What happens when each dependency is slow or unavailable?
- What happens after duplication, reordering, partial success, or restart?
- What happens when authorization changes mid-workflow?
- What happens when demand exceeds processing capacity?
- How is divergence detected and repaired?
- Who observes, controls, and owns the system during failure?

Do not treat absent implementation details as implemented safeguards.

## Avoid low-value review behavior

Do not:

- give generic architecture advice without evidence;
- turn naming, formatting, or lint into system findings;
- equate more components with a better design;
- call all coupling harmful;
- recommend abstraction solely because code looks similar;
- assume eventual consistency, caching, retries, or async work are beneficial;
- treat every missing feature as a defect;
- claim a scalability problem without describing the growth mechanism;
- claim exhaustive repository coverage from a sample;
- overstate runtime behavior from static evidence;
- recommend a rewrite without showing why incremental correction cannot address the dynamics.

## Complete the review

Finish only when:

- purpose, scope, baseline, and assumptions are explicit;
- review depth, sampled paths, and coverage limits are visible;
- the compact system model covers the reviewed paths;
- consequential normal and failure flows were traced;
- findings pass the evidence gate;
- finding kind and review-mode status or attribution are correct;
- recommendations include tradeoffs and verification;
- verification actions are clearly marked Proposed, Executed, or Blocked;
- uncertainties and coverage limits are visible;
- the report prioritizes system behavior and leverage over comment count.
- any requested report artifacts were rendered from one validated payload and their exact paths were provided.
