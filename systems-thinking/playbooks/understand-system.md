# Understand a system

Use to explain how a system produces its behavior, without requiring a recommendation.

## Load

Read [first principles](../principles/first-principles.md), [boundaries and purpose](../principles/boundaries-and-purpose.md), [stocks and flows](../principles/stocks-and-flows.md), [feedback loops](../principles/feedback-loops.md), [delays and dynamics](../principles/delays-and-dynamics.md), and [constraints and bottlenecks](../principles/constraints-and-bottlenecks.md).

Load an input mode only for repository, diff, architecture, or incident evidence. Add another principle only when the model exposes a relevant mechanism.

## Procedure

1. Define purpose, success criteria, boundary, and timescale. Include external actors that materially control the outcome.
2. Identify irreducible entities, required operations, invariants, and inherited assumptions.
3. Map components, actors, inputs, outputs, stocks, transformations, interfaces, and ownership. Trace one representative end-to-end path.
4. Identify supported loops, delays, and nonlinear behavior. Separate causal influences from simple data or control dependencies.
5. Locate the likely constraint and distinguish it from downstream symptoms. State uncertainty when there are no measurements.
6. Check whether the model explains the observed behavior and predicts something observable. Remove detail that changes neither explanation nor prediction.

## Deliver

Return the purpose and boundary, first-principles core, compact model, key dynamics, likely constraint, evidence, and open questions. A small table or diagram can carry the model. Do not force absent loops or stocks into the answer.

Stop after explaining the system. If the user also asks what to change, pass the model to [choose an intervention](choose-intervention.md). For a requested drawing, use [visualize a system](visualize-system.md); for an Obsidian note, use the [note template](../references/obsidian-template.md).
