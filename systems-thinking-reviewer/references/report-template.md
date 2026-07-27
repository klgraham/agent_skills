# Systems Thinking Review Report Template

Preserve this information architecture. Adapt headings or omit empty optional sections when the user requests a different format, but never omit the required fields of a detailed finding.

## Contents

1. Review target
2. Executive summary
3. System model
4. Key system dynamics
5. Findings summary
6. Detailed findings
7. Positive system patterns
8. Cross-cutting recommendations
9. Open questions and uncertainties
10. Suggested validation plan

## Report

```markdown
# Systems Thinking Review

## Review target

- **Mode:** Repository | Pull request/diff | Architecture | Combined
- **Target:** [repository, PR, revision range, document, or supplied description]
- **Baseline:** [base revision or current architecture, when applicable]
- **Reviewed scope:** [directories, files, components, flows, sections]
- **Excluded or unavailable:** [material not reviewed]
- **Important assumptions:** [material assumptions]

## Executive summary

[Summarize the system shape, important strengths, most consequential risks,
and the highest-leverage recommended action. Do not merely repeat the table.]

## System model

### Purpose and actors

[State intended behavior, users, operators, and external actors.]

### Components, state, and boundaries

[Describe major components, authoritative state, queues or other
accumulations, external dependencies, trust boundaries, and ownership.]

### Consequential flows

[Trace the representative normal path and important failure/recovery branches.]

[Include a Mermaid diagram only when it materially clarifies the relationships.
Label inferred or unknown edges.]

## Key system dynamics

[Describe only evidence-supported feedback loops, delays, bottlenecks,
shared constraints, accumulations, or failure-propagation paths.]

## Findings summary

| ID | Severity | Finding | Affected system behavior | Status | Confidence |
|---|---|---|---|---|---|
| ST-001 | High | [Brief title] | [Concrete qualities] | [Change attribution] | High |

## Detailed findings

### ST-001 — [Finding title]

**Severity:** Critical | High | Medium | Low | Positive

**Confidence:** High | Medium | Low

**Status:** Introduced by change | Made more severe by change | Pre-existing, exposed by change | Unrelated pre-existing architecture | Architectural | Positive pattern

**Evidence class:** Observed | Inferred

#### Relevant context

**Source:** `path/to/file.ext:120-148` — `SymbolOrSection`

```text
[Include the smallest excerpt that preserves enough context to understand the
comment. Redact secrets. Keep source spelling intact.]
```

[For a diff, indicate added, removed, and unchanged context. For architecture
input, quote the relevant section or identify diagram nodes and edges. If
multiple locations support the finding, include a source and excerpt block for
each one.]

#### Comment

[State the issue or positive observation directly. Make it understandable
without the rest of the report.]

#### Why this matters

[Give concise, decision-relevant causal reasoning. Connect the evidence to the
system behavior. Name feedback, delay, coupling, accumulation, propagation,
incentive, or reversibility mechanisms where relevant.]

```text
[evidence-supported condition]
→ [intermediate system effect]
→ [concrete outcome]
```

[Do not expose hidden scratch work or use vague language such as "this could
cause problems."]

#### Affected system behavior

- **Qualities:** [correctness, consistency, reliability, latency, throughput,
  recoverability, security, observability, maintainability, operator workload,
  development velocity, or coordination]
- **Affected actors/components:** [specific scope]
- **Blast radius:** [request, tenant, service, region, organization, etc.]

#### Recommendation

[Recommend the smallest actionable intervention likely to change the system
behavior. State ownership or invariants precisely.]

#### Tradeoffs and alternatives

[State implementation and operating cost, meaningful alternatives, conditions
under which the current design is acceptable, and overengineering risk.]

#### Verification

[Specify a targeted test, failure-injection experiment, load test, schema or
trace analysis, runtime metric, migration rehearsal, rollback exercise, or
owner clarification.]

#### Assumptions

[Required for Medium or Low confidence. Omit only when confidence is High and
no material assumption remains.]

[Repeat the exact detailed-finding structure for each finding.]

## Positive system patterns

[Optional. Include only consequential strengths such as bounded queues,
explicit ownership, canonical truth, reversible migration, fault isolation,
safe degradation, objective-linked observability, or reusable paved paths.]

## Cross-cutting recommendations

[List only actions that address multiple findings or change system-wide
behavior. Order by leverage and dependency.]

## Open questions and uncertainties

| Question | Why it matters | Current assumption | How the answer changes the review |
|---|---|---|---|
| [Question] | [Decision consequence] | [Assumption] | [Possible change] |

## Suggested validation plan

1. **[Highest-risk validation]** — [what it proves or falsifies]
2. **[Next validation]** — [what uncertainty it reduces]
3. **[Later validation]** — [why it is lower priority]
```

## Context rules

- Put source context immediately before its comment and causal rationale.
- Prefer a narrow excerpt plus exact location over a large undifferentiated code block.
- Preserve enough surrounding control flow or data definition to make the comment fair.
- For removed code, label it as removed; for proposed architecture, label it as proposed.
- If line numbers are unavailable, cite the narrowest stable symbol, heading, diagram node, or quoted input passage.
- If evidence is too large to quote usefully, show the decisive excerpt and summarize the relationship to other cited locations.
- Never quote secret values, credentials, private keys, tokens, or sensitive personal data.

## Finding quality check

Before including a finding, confirm:

- source and context are specific;
- the comment stands alone;
- causal reasoning is explicit;
- affected system behavior and blast radius are named;
- change attribution is accurate;
- recommendation is proportionate;
- tradeoffs are real rather than ceremonial;
- confidence matches evidence;
- verification could prove or disprove the claim.

Move unsupported concerns to open questions. Delete generic advice.
