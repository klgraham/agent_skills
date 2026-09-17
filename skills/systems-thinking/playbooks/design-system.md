# Design a system

Choose a structure that satisfies the objective and its failure conditions.

## Load

Read [first principles](../principles/first-principles.md), [boundaries and purpose](../principles/boundaries-and-purpose.md), [constraints and bottlenecks](../principles/constraints-and-bottlenecks.md), [sources of truth](../principles/sources-of-truth.md), [failure propagation](../principles/failure-propagation.md), and [path dependence and reversibility](../principles/path-dependence-and-reversibility.md).

For a supplied architecture proposal, add [architecture mode](../modes/architecture.md). Add security for trust boundaries, observability for operational controls, and coupling or organizational principles when deployment or ownership choices matter.

## Procedure

1. Define objectives, non-goals, hard constraints, timescale, and success measures. Separate required domain behavior from preferred technologies.
2. Derive entities, required operations, and invariants. Name the authoritative owner of each state and who may change it.
3. Trace inputs through state transitions to outputs. Include concurrency, disagreement, partial success, and recovery where applicable.
4. Define failure containment, detection, safe intervention, and ongoing ownership. A diagram of the happy path is not a failure model.
5. Compare materially different candidate structures against the same workload and constraints. Include a simpler alternative or the existing design when it is viable. Do not invent alternatives solely to fill a quota.
6. Explain tradeoffs in useful throughput, correctness, operator work, coordination, and future migration. Mark estimates and unresolved requirements.
7. Select the structure with the best supported fit and define a bounded prototype or measurement that could overturn that choice.

## Deliver

Return requirements and assumptions, state ownership and flow model, failure and control model, alternatives with tradeoffs, recommended structure, irreversible commitments, and validation plan. Clearly label proposed behavior. A design request alone does not authorize implementing or deploying it.
