# Review a software system

Review behavior across components, state, operations, people, and time. Prefer consequential system findings over local style or implementation preferences.

## Load

Read [review mode](../modes/review.md) and the applicable repository, pull-request, or architecture mode linked from the router. Start with [boundaries and purpose](../principles/boundaries-and-purpose.md). After mapping the system, select additional principles by the mechanisms present; do not load all principles.

Before accepting findings, read the [findings schema](../references/findings-schema.md) for the field contract, classification values, and verification states. Use that contract for conversational reviews as well as requested report files. Read the [report template](../references/report-template.md) for the section outline before drafting the formal report.

## Procedure

1. Establish intended behavior from primary evidence: purpose, users, success criteria, invariants, reliability and security requirements, state authority, dependencies, trust boundaries, environment, and ownership. Label inferred intent.
2. Build a compact model of actors, components, data and control flows, accumulations, synchronous and asynchronous boundaries, shared resources, reconciliation, operational controls, and relevant human handoffs.
3. Trace representative normal and failure or recovery paths at the depth required by the input mode. Record sampled paths and coverage limits. Inspect surrounding unchanged code for a diff; omitted behavior in a proposal is uncertainty.
4. Select relevant principles and investigate mechanisms such as retry amplification, unbounded accumulation, delayed control, divergent truth, contention, failure propagation, or exported operator cost. A lens without evidence is not a finding.
5. Build candidates with stable IDs and the narrowest source locations and excerpts that preserve context. State the affected behavior, causal mechanism, classification, recommendation, tradeoffs, assumptions, confidence, and a concrete verification method and state.
6. Challenge consequential candidate claims with [verify a system model](verify-system-model.md). Give the reader a concise causal rationale, not private scratch work. Move unsupported concerns to open questions.
7. Apply the evidence gate and classification rules in the findings schema. Rank by impact, likelihood, blast radius, and difficulty of later reversal. Return up to 12 substantive findings, including zero when none qualify. Do not hold a PR responsible for unrelated architecture.
8. Recommend proportionately. Prefer deleting unnecessary complexity, clarifying ownership or invariants, or reusing existing capability. Add bounds, containment, reconciliation, backpressure, recovery, or objective-linked observability when the mechanism warrants it. A new abstraction or platform needs evidence that reuse benefit exceeds coordination cost and loss of flexibility.
9. Produce the contextual Markdown report with source context immediately before each comment and rationale. Cross-cutting recommendations and validation items must reference finding IDs rather than introduce new claims.

Redact secrets and sensitive values while preserving structural evidence in excerpts. Unknown is not a finding evidence class; record unresolved uncertainty as an open question and reference affected finding IDs.

Do not recommend microservices, async work, caching, retries, rewrites, or platforms by default. Explain the condition that makes each intervention appropriate. Do not claim runtime behavior from static evidence alone.

## Deliver and stop

The report must expose scope, baseline, assumptions, model, sampled normal and failure paths, coverage limits, evidence-backed findings, tradeoffs, and verification states. Include consequential positive patterns under the same evidence contract. If no findings pass, say so and provide uncertainties.

For requested files, author one JSON payload using the schema, then run:

```bash
python3 <skill-dir>/scripts/build_report.py <findings.json> --out-dir <output-dir> --strict
```

The renderer derives interactive HTML and Obsidian Markdown from the same model. Fix payload errors and warnings rather than hand-editing outputs. Inspect the rendered artifacts, then provide both exact paths. Passing schema validation establishes payload structure, not the truth of its claims.
