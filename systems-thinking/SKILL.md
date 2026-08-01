---
name: systems-thinking
description: "Analyze complex situations as systems using first-principles reasoning: define the irreducible elements, map components and relationships, identify feedback loops and delays, find constraints and leverage points, then choose the smallest effective intervention. Includes Obsidian-friendly output."
category: decision-making
---

# systems-thinking

See the whole system before optimizing a part.

Use this skill to analyze messy problems where outcomes come from interactions, feedback loops, delays, incentives, and constraints rather than a single linear cause.

## Trigger

Use when the user says things like:
- "think about this as a system"
- "map the system"
- "find the bottleneck"
- "why is this problem persistent?"
- "what are the feedback loops?"
- "what intervention actually matters?"
- "reason from first principles"
- "help me understand the whole picture"

## Best For

- complex product or technical systems
- debugging recurring failures
- workflow and process diagnosis
- architecture tradeoffs
- market and strategy analysis
- policy or organizational dynamics
- any problem with second-order effects or repeated policy failure

## Not For

- simple factual lookup
- one-step procedural tasks
- problems that are already reducible to a direct local fix
- brainstorming with no need to identify structure or leverage

## Core Principle

Start from first principles, then build the system model.

Do not begin with industry templates, existing architecture, or received wisdom.

Ask first:
- What are the irreducible elements?
- What must be true for this system to exist?
- What is conserved, accumulated, transformed, or constrained?
- What is the smallest set of operations that satisfies the problem?
- Which parts are real versus narrative, habit, or accidental complexity?

Then ask system questions:
- What are the components and boundaries?
- What flows between them?
- What feedback loops drive behavior?
- What delays hide cause and effect?
- Where is the actual constraint?
- What intervention changes system behavior rather than symptoms?

## Required Inputs

Collect or infer these before starting:
- `problem` — what needs to be explained, improved, or designed
- `objective` — what good looks like
- `scope` — what is inside and outside the system boundary
- `constraints` — hard limits, deadlines, resources, policies
- `timescale` — immediate / short / long term
- `available evidence` — facts, logs, measurements, observations

If anything is missing, state assumptions explicitly.

## Analysis Sequence

### 1) Define the problem cleanly

Output:
- one-sentence problem statement
- one-sentence objective
- explicit scope boundary

Questions:
- What exactly is failing or underperforming?
- What outcome matters?
- What is outside scope and should be ignored for now?

### 2) Reduce to first principles

Strip the situation to irreducible truths.

Output:
- fundamental entities
- invariant constraints
- required operations
- deleted assumptions / accidental complexity

Questions:
- What must exist for this system to function at all?
- What assumptions can be removed?
- What is the minimum viable mechanism here?
- Which abstraction layers are hiding the real constraint?

### 3) Map the system

Describe the structure that produces the behavior.

Output:
- components / actors
- inputs / outputs
- stocks / accumulations
- flows / transformations
- incentives / goals
- boundaries and interfaces

Questions:
- What are the major components?
- What moves through the system: matter, money, time, energy, information, requests, errors?
- What accumulates over time?
- Who responds to what signals?

### 4) Identify dynamics

Find the loops, delays, and nonlinearities.

Output:
- reinforcing loops
- balancing loops
- delays
- nonlinear effects / tipping points
- local optimizations that damage the whole

Questions:
- What creates self-reinforcement?
- What pushes the system back toward equilibrium?
- Where are cause and effect separated in time?
- What looks harmless locally but is harmful system-wide?

### 5) Locate the constraint

Find the true limiter.

Output:
- primary bottleneck
- secondary constraints
- symptoms mistakenly treated as causes

Questions:
- If one thing were removed, what would increase throughput or stability the most?
- What part is everyone blaming that is only downstream of the real issue?

### 6) Identify leverage points

Choose interventions that change behavior, not cosmetics.

Output:
- candidate leverage points
- expected first-order effects
- expected second-order effects
- risks and failure modes

Questions:
- Where can a small change alter the whole system?
- What intervention simplifies rather than adds control overhead?
- What should be deleted instead of managed?

### 7) Recommend the smallest effective intervention

Output:
- recommended intervention
- why this is the highest-leverage move
- what to measure
- what to defer
- next review point

Questions:
- What is the smallest change that tests the model?
- What measurement confirms or falsifies the recommendation?
- What should not be changed yet?

## Output Contract

Unless the user asks otherwise, return these sections:
- Problem
- Objective
- First principles
- System boundary
- Components
- Stocks and flows
- Feedback loops
- Delays / nonlinearities
- Constraint
- Leverage points
- Recommended intervention
- Risks / second-order effects
- What to measure next

## Obsidian-Friendly Output Template

```md
---
tags:
  - systems-thinking
  - first-principles
status: active
problem: <one line>
objective: <one line>
---

# <Title>

## Problem
- <what needs to be explained or improved>

## Objective
- <desired outcome>

## First Principles
- Irreducible elements:
- Invariants / constraints:
- Minimum viable mechanism:
- Deleted assumptions / accidental complexity:

## System Boundary
- In scope:
- Out of scope:
- Interfaces:

## Components
- Actors / modules:
- Inputs:
- Outputs:
- Incentives / goals:

## Stocks and Flows
- Stocks / accumulations:
- Flows / transformations:

## Feedback Loops
- Reinforcing loops:
- Balancing loops:

## Delays and Nonlinearities
- Delays:
- Tipping points / nonlinear behavior:

## Constraint
- Primary bottleneck:
- Secondary constraints:
- Commonly mistaken cause:

## Leverage Points
- Candidate interventions:
- Highest-leverage point:

## Recommendation
- Smallest effective intervention:
- Why this move:
- What to defer:

## Risks and Second-Order Effects
- Risks:
- Side effects across the system:

## Measurements
- What to track:
- What would falsify this model:
- Next review time:

## Related
- [[systems thinking]]
- [[What is systems thinking?]]
- [[OODA Loop Skill]]
```

## Minimal Terminal Output

If speed matters more than completeness, compress to:
- Problem
- First-principles core
- Constraint
- Key loops
- Leverage point
- Smallest intervention
- Measurement

## Anti-Patterns

Do not:
- confuse a symptom with the constraint
- assume linear cause-and-effect in a feedback system
- optimize one part while harming the whole
- treat delayed effects as unrelated effects
- keep abstractions that hide the real mechanism
- propose large programs before testing a smaller intervention
- add management layers when deletion would solve it

## Heuristics

- Simplify the model until predictive power breaks
- Prefer structure over narrative
- Prefer measured flows over opinions
- Prefer removing steps over coordinating more steps
- Prefer changing incentives or interfaces over adding policy text
- If behavior persists, look for the loop that reproduces it

## Relationship to Other Decision Frameworks

These three related skills form a layered stack — use them together or independently:

### First Principles Reasoning (`first-principles-reasoner`)
Use to reduce the problem to bedrock truths before mapping structure.

Key questions:
- What are the irreducible elements?
- What must be true for this system to exist?
- What is the minimum viable mechanism?
- What can be deleted without breaking correctness?

### OODA Loop (`ooda-loop`)
Use to decide and execute the next bounded move inside the mapped structure.

Key questions:
- What is the smallest move with the highest information gain?
- What is the predicted result?
- What triggers a re-loop vs. stop?

### Systems-Thinking + OODA Combined (`systems-thinking-ooda`)
Use when the problem is both structurally messy and operationally urgent.
This meta-skill composes all three: first-principles → systems-map → OODA move.

## Relationship to OODA

Use `systems-thinking` to understand structure.
Use `ooda-loop` to decide and execute the next move inside that structure.

Common pairing:
1. systems-thinking → map system, loops, constraint, leverage point
2. ooda-loop → choose probe, predict outcome, act, re-loop

## Quick Reference

| Situation | Skill to Use |
|---|---|
| Need to strip assumptions and find bedrock truths | `first-principles-reasoner` |
| Need to map components, flows, loops, constraints | `systems-thinking` |
| Need to choose and execute the next bounded action | `ooda-loop` |
| Problem is both messy AND urgent | `systems-thinking-ooda` |

## Final Deliverable

End with:
1. best current model of the system
2. real constraint
3. highest-leverage intervention
4. measurement that validates or falsifies the model.
