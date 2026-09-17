# Diagnose a problem

Explain a recurring behavior through competing mechanisms and evidence.

## Load

Read [stocks and flows](../principles/stocks-and-flows.md), [feedback loops](../principles/feedback-loops.md), [delays and dynamics](../principles/delays-and-dynamics.md), and [constraints and bottlenecks](../principles/constraints-and-bottlenecks.md). Read the [causal reasoning boundary](../references/causal-reasoning.md) before making causal claims.

If the boundary or objective is unclear, add [boundaries and purpose](../principles/boundaries-and-purpose.md). Load failure propagation, incentives, or sources of truth only when those mechanisms are candidates.

## Procedure

1. State the observed behavior, expected behavior, onset, frequency, timescale, and affected population. Separate measurements from interpretations.
2. Build or reuse the smallest model that includes the symptom and its upstream influences.
3. Generate competing explanations, including accumulation, feedback, delay, and constraint mechanisms where relevant. Distinguish an initiating event from the structure that reproduces it.
4. For each explanation, state its assumptions, predicted observations, and evidence that would contradict it. Seek comparisons across time, workloads, components, or operating conditions.
5. Use [verify a system model](verify-system-model.md) to challenge the consequential claims. An executed check does not automatically confirm a hypothesis.
6. Rank explanations by the evidence they survive. Record unresolved alternatives rather than forcing one root cause.

## Deliver

Return the observed pattern, candidate mechanisms, supporting and contradicting evidence, current best explanation, likely constraint, and the next observation that distinguishes alternatives. Mark proposed and executed checks honestly.

If a change is requested, pass the diagnosis and remaining uncertainty to [choose an intervention](choose-intervention.md). Diagnosis alone does not authorize remediation.
