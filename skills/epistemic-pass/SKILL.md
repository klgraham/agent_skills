---
name: epistemic-pass
description: >-
  Use when a claim, diagnosis, design, or draft answer needs a rigorous
  epistemic pass: observe without inference, infer with cited basis, derive a
  first-principles mechanism, then verify what safely survives. Replaces the
  Anne / Holmes / Aristotle / Socrates bot quartet as sequential reasoning
  lenses. Anne may still run solo as a fair-witness bot when hard observe-only
  isolation is needed.
---
# Epistemic pass

Run four lenses **in order**. Each lens produces one artifact. Later lenses may only consume earlier artifacts plus the raw evidence and user task. Do not skip a lens unless the user names a shorter pass (e.g. observe-only, verify-only).

Lens names (legacy bots): **Anne** (observe) → **Holmes** (infer) → **Aristotle** / **Newton** (first principles) → **Socrates** (verify). Socrates still calls Aristotle’s step **Newton**; the artifact title is **First-Principles Report**.

Hard isolation (optional): if observation must not bleed inference, run Lens 1 in a fresh subagent or dedicated fair-witness bot (Anne), then continue here from the Observation Record.

---

## Pipeline

```
Raw evidence + user task
  → Observation Record          (Anne)
  → Inference Report              (Holmes)
  → First-Principles Report       (Aristotle / Newton)
  → Verifier Report + final answer (Socrates)
```

Preserve the chain: evidence → observation → inference → mechanism → answer. Flag breaks; never silently repair by inventing evidence.

---

## Lens 1 — Anne (Fair Witness / observe only)

**Job:** Faithful report of *directly present* input only. Answer “What was observed?” — not “What happened?”

**Forbidden:** Infer, explain, diagnose, interpret, summarize intent, assign cause, identify hidden states, generalize, fill gaps, convert claims to facts, collapse to narrative, use outside knowledge, judge truth.

**Allowed:** Transcribe; describe visible objects/colors/shapes/positions/motions/relations; report timestamps/logs/errors/filenames/metadata/source text; quote or paraphrase sources; count; report sequences; report non-observation within scope + limits; note perceptual uncertainty (unreadable, occluded, blurred).

**Anne Rule:** Partial view (e.g. house color): “Visible side is white.” Never generalize beyond observed scope.

**Distinctions (keep separate):**
- **Observed** — directly present
- **Stated** — claimed by a source (including the user); never adopt as fact
- **Not observed** — absent in the supplied evidence
- **Observation limits** — evidence boundaries

No `Inferred` section. No hypotheses.

**Absence:** “I do not observe X in the supplied input.” Non-observation ≠ non-existence.

**Source claims:** “Document states revenue increased 12%.” Never “Revenue increased 12%.”

**Multimodal:** Keep Visual / Text / Audio / Metadata separate. Cross-channel notes without causal claims. Captions and filenames do not rewrite the primary channel.

**Sequential:** Video/audio/logs in order with timestamps (“At 0:03… At 0:07…”). Order OK; causality only if directly visible.

**Language:** Use “I observe…”, “Input shows…”, “Document states…”, “I do not observe…”, “Within supplied input…”. Avoid means / suggests / probably / likely / because / therefore / clearly / appears caused by / seems intended / is evidence that.

**Output — Observation Record:**

```markdown
# Observation Record
## Source
- Input type:
- Identifier:
- Time range:
- Scope:
## Observed
...
## Stated
...
## Not Observed
...
## Observation Limits
...
```

Omit inapplicable sections. When a conclusion is requested at this stage, still provide *only* the Observation Record.

---

## Lens 2 — Holmes (Abductive inference)

**Job:** From the Observation Record, construct grounded explanations, hypotheses, diagnoses, or questions. Every inference cites record items. Never present inferences as observations.

**Fair Witness vs this lens:** FW = what was observed. This lens = what might follow. FW never infers. This lens must show evidentiary basis.

**Evidence categories:** Observation | Source claim | Non-observation | Limit | Inference | Assumption | Outside knowledge.

**Each inference must include:**
1. **Inference** — proposed conclusion or hypothesis
2. **Basis** — supporting Observation Record items
3. **Support level** — qualitative only (below)
4. **Alternatives** — other compatible explanations
5. **Limits** — what the record does not establish

**Support levels:** Directly established | Strongly supported | Moderately supported | Weakly supported | Speculative | Not supported / Contradicted. No numerical scores unless from explicit stats in the evidence.

**Disciplines:**
- Source claims: “document states X” or “if accurate, X” — never silent verification
- Absence: “No X observed” OK; “X did not occur” only if completeness is established
- Causality: order ≠ causation; “A preceded B”; “A caused B” needs explicit support + alternatives + limits
- Assumptions and outside knowledge: list in their own sections; never bury in prose

**Output — Inference Report:**

```markdown
# Inference Report

## Candidate Inferences

### Inference 1: <name>
**Inference:** ...
**Basis:**
- Observation: ...
- Source claim: ...
**Support level:** ...
**Alternatives:** ...
**Limits:** ...

## Assumptions
- ...

## Outside Knowledge Used
- ...

## Questions That Would Reduce Uncertainty
- ...
```

Include only relevant sections.

---

## Lens 3 — Aristotle / Newton (First principles)

**Job:** Derive the simplest correct mechanism from irreducible facts, constraints, and objectives. Do not begin from analogy, precedent, inherited architecture, habit, fashion, or convention.

Socrates’ input name for this artifact: **Newton report**. Title the artifact **First-Principles Report**.

**Start from:** irreducible entities, invariant constraints, required transformations, inputs/outputs, conservation/consistency requirements, failure conditions, measurable success criteria.

**Label every claim:** Observed fact | Derived conclusion | Assumption | Design judgment | Convention | Open question. Never present assumptions or judgments as derived truths.

**Sequence:**
1. Define problem, objective, success condition, boundaries.
2. Separate known / assumed / unknown / convention-borrowed; never treat unknowns as facts.
3. Smallest set of entities, I/O, state variables, operations, transformations, invariants, constraints, failure modes.
4. Causal chain: Input → transformation → state change → observable behavior → success metric.
5. Smallest system that satisfies objective + invariants (required components only).
6. Add only if classified Necessary / Risk-reducing / Performance-improving / Ergonomic / Speculative / Conventional — never add resilience/scale/flexibility before naming concrete pressure.
7. Fixed vs arbitrary choices; collapse layers when possible.
8. Stress-test: failure points, hidden dependencies, circular assumptions, bottlenecks, edge cases, falsifiers.
9. Reduction challenge: prefer deletion unless a component survives removal.
10. Recommend fewest parts/dependencies, shortest chains, direct measurement, reversible decisions.

**Heuristics:** Cannot name invariant or causal mechanism → not first principles. Two layers collapse → collapse. Dependency only manages self-created complexity → delete both. Elegant but untestable or precedent-only → invalid. Unfalsifiable or metric cannot change decisions → untrustworthy. Vague boundary → accidental complexity.

**Analogy/precedent:** Only *after* the mechanism is derived — for comparison, failure modes, tradeoffs, history. Never as foundation.

**Output — First-Principles Report** (unless the user wants speed): Problem, Objective, Success Condition, Known Facts, Assumptions, Invariants, Irreducible Elements, Causal Mechanism, Minimum Viable Mechanism, What to Delete, Justified Additions, Degrees of Freedom, Reduction Challenge, Stress Test, Simplest Correct Path, What to Measure, Open Questions.

---

## Lens 4 — Socrates (Verifier / critic)

**Job:** Audit upstream outputs before the final answer. Protect the user from unsupported certainty. Decide what safely survives.

**Inputs (use what exists; state limits if missing):** User task, raw evidence, Observation Record, Inference Report, First-Principles Report (Newton), draft final answer.

**A claim is earned only if:** directly observed, labeled source claim, properly inferred from cited evidence/assumptions, derived from constraints/first principles, or labeled speculative.

**Check each upstream lens:** Fair Witness (no inference) | Inference (explicit basis, correct claim treatment) | Newton (first-principles from objective) | Final answer (preserves distinctions, does not overstate).

**Allowed:** Flag unsupported claims, hidden assumptions, inference-as-observation, source-claim laundering, correlation-as-causation, missing alternatives, weak support, contradictions, missing observations, overcomplicated reasoning, fake constraints; recommend edit / relabel / weaken / remove; produce a corrected final answer if requested.

**Forbidden:** Silently add evidence or outside knowledge; replace upstream content unmarked; convert source claims to facts; treat non-observation as proof of absence; treat temporal order as causality; treat confidence/elegance/plausibility as proof; ignore limits; overstate confidence.

**Audit categories:** Observation-boundary violations, source-claim laundering, unsupported inferences, missing alternatives, scope/absence/causal overreach, unlabeled assumptions/outside knowledge, first-principles failures, fake constraints, missing mechanisms, unjustified components, final-answer drift.

**Severity:**
- **Blocking** — misleading/unsafe/materially incorrect unless fixed
- **Major** — usable but missing important caveat/alternative/assumption/limit
- **Minor** — clarity/wording; does not materially change the answer

**Verdict:**
- **Pass** — no blocking/major; safe as written
- **Pass with revisions** — no blocking; needs caveats/relabeling/weakening
- **Fail** — blocking issue; central conclusion unsupported; chain broken; would mislead; needs missing evidence that cannot be assumed

**Missing inputs:** No Observation Record → cannot verify separation; treat direct evidence as unverified. No Inference Report → cannot verify traceability; require citation/weakening. No Newton → cannot verify derivation (do not Fail solely for that unless the task required it). No draft → audit upstream; list risks.

**Corrections:** Specific (e.g. replace “X caused Y” with “X preceded Y in logs; causality not established”).

**Output — Verifier Report:**

```markdown
# Verifier Report

## Verdict
- Status: Pass | Pass with revisions | Fail
- Summary: ...

## Blocking Issues
...

## Major Issues
...

## Minor Issues
...

## Claim-Level Audit
...

## Checks
...

## Required Revisions
...

## Optional Improvements
...

## Corrected Final Answer
...
```

If no issues: “No material issues found.” Do not omit major categories. Corrected Final Answer only when requested or when Status is Pass with revisions / Fail and a safe rewrite is possible.

**Final answer (when shipping to the user):** Established facts, best-supported inferences, important alternatives, key assumptions, limits, next step if action was requested. Prefer a minimal template. Do not dump the full audit unless asked.

---

## Operating notes

- Role of the critic is not to be agreeable.
- Prefer deletion and weaker wording over elegant overclaim.
- Subagents are fine for isolation or parallelism *within* a lens; do not reorder the pipeline.
- This skill does not post, deploy, or edit product repos; it produces reasoning artifacts.
