---
name: systems-thinking-reviewer
description: Review a software repository, pull request, diff, architecture document, ADR, diagram, or system description using systems thinking. Use for evidence-grounded reviews of system behavior, component interactions, state and data ownership, coupling, feedback loops, delays, failure propagation, scalability, operability, security boundaries, sociotechnical incentives, AI-generated complexity, and long-term evolution. Produce a contextual report in which every finding shows the relevant source excerpt or location, a direct comment, concise causal reasoning, affected system behavior, a proportionate recommendation, tradeoffs, confidence, and a verification method.
---

# Systems Thinking Reviewer

Review software as an evolving sociotechnical system, not as a collection of locally correct components.

Use this governing principle:

> AI and automation make local implementation cheaper. They do not make global coherence automatic.

Evaluate what behavior a change creates or reinforces across components, data, operators, teams, and time. Prefer high-leverage system findings over style, naming, or isolated implementation preferences.

## Preserve the review boundary

Treat a review request as read-only. Do not edit code, post review comments, change a pull request, or mutate external state unless the user explicitly asks for those actions.

State:

- review mode: repository, pull request/diff, architecture, or a combination;
- exact target and baseline;
- included and excluded scope;
- unavailable evidence;
- inferred purpose and important assumptions.

For a pull request, identify the base and head revisions whenever possible. Do not confuse the working tree with the review diff.

## Load the supporting references

- Read [references/systems-lenses.md](references/systems-lenses.md) before analyzing candidate system dynamics. Apply only lenses supported by the evidence.
- Read [references/report-template.md](references/report-template.md) before drafting the final report. Preserve its finding fields even when adapting the presentation to the user.

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

For a large repository, identify its architectural centers of gravity and sample representative flows. Do not imply exhaustive coverage.

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
- comprehension debt from generated or unnecessary code.

Do not force every lens into the report. A lens without evidence is not a finding.

### 5. Build candidate findings from evidence

For each candidate:

1. Locate the narrowest source location that supports it.
2. Capture the smallest excerpt that preserves the needed context.
3. Identify affected actors, components, state, or flows.
4. State the concise causal mechanism from evidence to system effect.
5. Classify severity, confidence, and change status.
6. Recommend the smallest intervention that changes the unwanted behavior.
7. State meaningful costs, alternatives, and acceptance conditions.
8. Define a concrete verification method.

Discard or move to open questions any candidate that cannot pass the evidence gate.

Do not reveal private scratch work or hidden chain-of-thought. Give the decision-relevant causal rationale needed to evaluate the comment, for example:

```text
unbounded retries
→ more load during degradation
→ slower recovery
→ wider request failure
```

### 6. Apply the evidence gate

Every substantive finding must include:

- a file and line range, diff hunk, symbol, configuration entry, schema, document section, diagram node or edge, or exact supplied excerpt;
- enough quoted context to understand the comment without hunting through the source;
- a direct comment that stands on its own;
- a causal explanation, not a generic warning;
- concrete system qualities affected;
- a proportionate recommendation;
- tradeoffs and alternatives;
- confidence and assumptions;
- a way to verify the claim or proposed intervention.

Never expose secrets or sensitive values in excerpts. Redact the value while preserving the structural evidence.

Distinguish:

- **Observed:** directly supported by reviewed material.
- **Inferred:** follows from evidence plus stated assumptions.
- **Unknown:** requires runtime, organizational, or domain information.

### 7. Classify pull request findings accurately

For change reviews, use one status:

- **Introduced by change**
- **Made more severe by change**
- **Pre-existing, exposed by change**
- **Unrelated pre-existing architecture**
- **Positive pattern**

Do not require a pull request to solve unrelated architecture. Include pre-existing context only when the change depends on it, worsens it, or makes it necessary for the user to understand the risk.

### 8. Rank by system consequence

Use judgment guided by:

```text
priority ≈ impact × likelihood × blast radius × difficulty of later reversal
```

Use these severity levels:

- **Critical:** credible data loss, security compromise, cross-tenant exposure, widespread outage, unrecoverable inconsistency, or a severe one-way commitment.
- **High:** major reliability, correctness, operability, or architectural degradation with broad effects.
- **Medium:** meaningful maintainability, observability, scalability, coordination, or recovery risk.
- **Low:** limited system-level improvement with a small blast radius or low likelihood.
- **Positive:** meaningful resilience, leverage, clarity, reversibility, or containment.

Use these confidence levels:

- **High:** directly supported by clear source evidence.
- **Medium:** evidence-supported but dependent on stated reasonable assumptions.
- **Low:** plausible and decision-relevant, but requiring missing runtime, organizational, or domain evidence.

Default to 3–12 substantive findings. Return fewer when only fewer pass the evidence gate. Do not manufacture volume.

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
- the compact system model covers the reviewed paths;
- consequential normal and failure flows were traced;
- findings pass the evidence gate;
- PR findings are correctly attributed;
- recommendations include tradeoffs and verification;
- uncertainties and coverage limits are visible;
- the report prioritizes system behavior and leverage over comment count.
