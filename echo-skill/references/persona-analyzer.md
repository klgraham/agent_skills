# Persona Analyzer

Extract a behavioral model from the confirmed intake and source manifest. Analyze the subject's own material first. Keep user characterization, secondary reporting, and inference visibly separate.

## Output contract

Return:

1. an evidence table;
2. candidate Layer 0 rules;
3. expression and interaction patterns;
4. decision posture;
5. boundaries and non-claims;
6. conflicts and unknowns.

For every major pattern include:

- evidence label: Quoted, Observed, User-provided, Secondary, Inferred, or Unknown;
- source labels;
- short supporting excerpt or description;
- recurrence count or breadth when available;
- confidence: high, medium, or low;
- contextual limits.

## 1. Expression style

Analyze only material authored or spoken by the subject when making voice claims.

Look for:

- sentence length and rhythm;
- typical openings and closings;
- directness and degree of qualification;
- question, example, analogy, and story use;
- formatting habits such as headings, lists, fragments, or long paragraphs;
- humor mode;
- formality and technical density;
- repeated phrases or rhetorical moves;
- how recommendations and criticism are phrased.

Do not reproduce quirks so aggressively that output becomes parody. Do not imitate accents, speech impediments, or identity-linked dialect unless the user has a legitimate, disclosed use and the source supports it; prefer semantic and rhetorical traits.

## 2. Decision posture

Extract how the subject appears to:

- frame the actual goal;
- weigh quality, speed, cost, risk, reversibility, and user impact;
- seek evidence;
- respond to uncertainty;
- choose between experimentation and planning;
- delegate or intervene;
- revise a position;
- treat consensus, authority, and dissent.

A decision rule must describe a trigger and action. Prefer:

```text
When a proposal creates an irreversible interface, ask for alternatives and migration cost before approving it.
```

over:

```text
Cares about architecture.
```

## 3. Interaction patterns

Separate contexts instead of treating behavior as universal:

- teaching or mentoring;
- peer collaboration;
- review or critique;
- disagreement;
- high-pressure or incident response;
- public presentation versus private discussion;
- response to incomplete requests.

Capture one or two evidence-grounded scenarios for each supported context.

## 4. Boundaries and red lines

Identify:

- explicit refusals;
- recurring pushback conditions;
- topics outside demonstrated expertise;
- claims the echo must never make;
- privacy or attribution constraints;
- behaviors seen only in one context and unsafe to generalize.

## 5. Layer 0 rule construction

Layer 0 contains the smallest set of high-priority rules that noticeably changes responses. Each rule must be concrete, observable, and bounded.

Template:

```text
Rule: {trigger → behavior}
Basis: {evidence label and source labels}
Confidence: {high|medium|low}
Limit: {where the rule may not apply}
```

Good examples:

- “Lead critiques with the central problem, then supply evidence and a repair path.”
- “Challenge the stated solution by first restating the underlying goal.”
- “When evidence is insufficient, ask for a small discriminating test rather than pretending certainty.”

Reject rules that:

- depend only on a personality type, employer stereotype, demographic trait, or job title;
- assert motives not visible in the sources;
- encode abusive, discriminatory, deceptive, or unsafe behavior;
- claim personal memories or relationships;
- duplicate a work standard better placed in `work.md`.

## 6. Conflict handling

When intake and observed material disagree, preserve both. Propose a bounded synthesis only if evidence supports it, such as:

```text
Direct about technical conclusions, but usually frames interpersonal criticism as questions.
```

If no synthesis is justified, mark the topic unresolved and keep it out of Layer 0.

## Confidence guide

- **High:** explicit repeated statements, or a pattern repeated across several independent primary sources.
- **Medium:** multiple examples in limited contexts, or one explicit statement consistent with observed behavior.
- **Low:** one example, secondary reporting, or a reasonable but untested inference.
- **Unknown:** the sources do not support a conclusion.

Do not increase confidence merely because a description feels coherent.
