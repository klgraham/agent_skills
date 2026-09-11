# Review evidence contract

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

## Classification

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

## Ranking

Use judgment guided by:

```text
priority ≈ impact × likelihood × blast radius × difficulty of later reversal
```

Use these confidence levels:

- **High:** directly supported by clear source evidence.
- **Medium:** evidence-supported but dependent on stated reasonable assumptions.
- **Low:** plausible and decision-relevant, but requiring missing runtime, organizational, or domain evidence.

Return up to 12 substantive findings. There is no minimum: return fewer, including zero, when fewer pass the evidence gate. If no findings pass, say so explicitly and report the coverage limits and open questions instead of manufacturing volume.

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
- **Review depth:** [narrow | representative | broad]
- **Coverage limits:** [sampled paths, unavailable evidence, or other limits]
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

| ID | Kind | Severity | Finding | Affected system behavior | Status or attribution | Confidence |
|---|---|---|---|---|---|---|
| ST-001 | Risk | High | [Brief title] | [Concrete qualities] | [Change attribution] | High |

If no findings pass the evidence gate, state **No evidence-backed findings**
and retain the coverage limits and open questions.

## Detailed findings

### ST-001 — [Finding title]

**Confidence:** High | Medium | Low

**Kind:** Risk | Positive pattern

**Severity:** Critical | High | Medium | Low | — (use — for positive patterns)

**Status or attribution:** For pull request or diff risks: Introduced by change | Made more severe by change | Pre-existing, exposed by change | Unrelated pre-existing architecture; for repository or architecture risks: Architectural; for positive patterns: Positive pattern

**Evidence class:** Observed | Inferred

**Verification state:** Proposed | Executed | Blocked

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

[Specify a proposed or explicitly authorized targeted test, failure-injection
experiment, load test, schema or trace analysis, runtime metric, migration
rehearsal, rollback exercise, or owner clarification.]

#### Assumptions

[Required for Medium or Low confidence. Omit only when confidence is High and
no material assumption remains.]

[Repeat the exact detailed-finding structure for each finding.]

## Positive system patterns

[Optional. Include only consequential strengths such as bounded queues,
explicit ownership, canonical truth, reversible migration, fault isolation,
safe degradation, objective-linked observability, or reusable paved paths.
Report each material pattern as a detailed Positive pattern finding so it
receives the same evidence contract; use this section only to summarize or
cross-reference those findings.]

## Cross-cutting recommendations

[List only actions that address multiple findings or change system-wide
behavior. Reference the affected finding IDs. Order by leverage and
dependency, and do not introduce uncited new claims.]

## Open questions and uncertainties

| Related finding(s) | Question | Why it matters | Current assumption | How the answer changes the review |
|---|---|---|---|---|
| ST-001 | [Question] | [Decision consequence] | [Assumption] | [Possible change] |

## Suggested validation plan

1. **Proposed — ST-001:** [Highest-risk validation] — [what it proves or falsifies]
2. **Proposed — ST-002:** [Next validation] — [what uncertainty it reduces]
3. **Blocked — ST-003:** [Later validation] — [why it is lower priority]
```

## Context rules

- Put source context immediately before its comment and causal rationale.
- Prefer a narrow excerpt plus exact location over a large undifferentiated code block.
- Preserve enough surrounding control flow or data definition to make the comment fair.
- For removed code, label it as removed; for proposed architecture, label it as proposed.
- If line numbers are unavailable, cite the narrowest stable symbol, heading, diagram node, or quoted input passage.
- If evidence is too large to quote usefully, show the decisive excerpt and summarize the relationship to other cited locations.
- Never quote secret values, credentials, private keys, tokens, or sensitive personal data.
- Verification actions are proposed unless explicitly labeled Executed, and state-changing experiments require explicit authorization and an isolated environment.

## Finding quality check

Before including a finding, confirm:

- source and context are specific;
- the comment stands alone;
- causal reasoning is explicit;
- kind, severity, status or attribution, and verification state match the review mode;
- affected system behavior and blast radius are named;
- change attribution or architecture status is accurate;
- recommendation is proportionate;
- tradeoffs are real rather than ceremonial;
- confidence matches evidence;
- verification could prove or disprove the claim.

Move unsupported concerns and unknown evidence to open questions. Delete generic advice.
