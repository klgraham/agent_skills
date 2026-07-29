# Work Analyzer

Extract the subject's repeatable methods, standards, and domain knowledge independently from their persona style. The output should tell another capable agent what to do, how to judge quality, and when not to extrapolate.

## Output contract

Return:

1. scope and non-scope;
2. standards and evaluation criteria;
3. recurring workflows;
4. domain heuristics and principles;
5. anti-patterns and rejection criteria;
6. representative cases;
7. evidence gaps and conflicts.

Every major item needs an evidence label, source labels, confidence, and contextual limit.

## 1. Scope and ownership

Extract:

- domains in which the subject has demonstrated expertise;
- decisions they repeatedly make or influence;
- artifacts they create or review;
- responsibilities they accept;
- work they delegate, refuse, or leave to specialists;
- historical expertise that may not transfer to current facts.

Do not equate a title with demonstrated scope. Mark unsupported areas as unknown.

## 2. Standards and quality bars

Turn preferences into testable criteria:

- What does “good” mean to this subject?
- What defects block acceptance?
- What tradeoffs are acceptable?
- What evidence changes a decision?
- What must be measured, reviewed, prototyped, or documented?
- Which constraints are hard and which are negotiable?

Prefer operational language:

```text
A proposal is not ready until it names the owner, failure mode, rollback path, and measurable success condition.
```

Avoid vague language:

```text
Values quality and ownership.
```

## 3. Workflows

Reconstruct sequence, decision points, and stop conditions for supported activities such as:

- receiving or framing new work;
- research and source evaluation;
- design or proposal development;
- implementation or production;
- review and critique;
- debugging and incident response;
- prioritization;
- teaching or mentoring;
- organizational decision-making.

For each workflow specify:

```text
Trigger
Inputs
Steps
Decision points
Outputs
Acceptance criteria
Escalation or stop conditions
Evidence and confidence
```

If sources show several approaches, model the conditions selecting among them rather than forcing one universal process.

## 4. Knowledge and heuristics

Extract:

- explicit principles;
- rules of thumb;
- named frameworks;
- recurring analogies that guide decisions;
- case-based lessons;
- anti-patterns;
- counterexamples and exceptions.

Separate timeless method from time-sensitive fact. The echo may reuse a principle but must verify current external facts rather than repeat outdated claims from the subject's era.

## 5. Cases

Cases preserve context that abstract rules lose. For each useful case record:

- situation;
- action or decision;
- stated or inferred rationale;
- result, if known;
- derived lesson;
- whether the lesson is quoted, observed, secondary, or inferred.

Do not claim causation when a source only reports sequence or correlation.

## 6. Anti-patterns and boundaries

Capture what the subject warns against or rejects, but state the causal reason when known. For example:

```text
Rejects broad rewrites without an incremental migration path because they concentrate delivery and rollback risk.
```

Avoid converting dislike into a universal prohibition.

## 7. Evidence gate

Keep an item only if at least one is true:

- the subject states it directly;
- the subject demonstrates it repeatedly;
- a well-documented case supports it;
- the user explicitly asks that it be part of the desired model, in which case label it User-provided.

Otherwise mark it Unknown or omit it.

## Confidence guide

- **High:** repeated primary evidence or a clear explicit method with corroborating cases.
- **Medium:** a clear explicit statement or several context-limited examples.
- **Low:** one case, secondary description, or cautious inference.
- **Unknown:** no adequate evidence.
