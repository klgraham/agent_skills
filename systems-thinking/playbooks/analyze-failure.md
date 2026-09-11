# Analyze a failure

Reconstruct how a trigger became a system failure and how recovery did or did not work.

## Load

Read [failure propagation](../principles/failure-propagation.md), [feedback loops](../principles/feedback-loops.md), [stocks and flows](../principles/stocks-and-flows.md), [observability and controllability](../principles/observability-and-controllability.md), and [coupling and cohesion](../principles/coupling-and-cohesion.md). Add [incident mode](../modes/incident.md) for an incident record. Use the [causal reasoning boundary](../references/causal-reasoning.md) for causal attribution.

## Procedure

1. Establish the failure definition, affected actors, operating conditions, and evidence window. Build a timeline with explicit evidence gaps.
2. Trace trigger, state transition, propagation, amplifying loops, containment failure, observable symptoms, and recovery. Distinguish the initiating event from enabling conditions.
3. Identify which boundary should have contained the failure and the mechanism that crossed it. Examine partial writes, retries, shared resources, backlog growth, stale state, and recovery work only when supported.
4. Compare detection time, intervention time, and recovery time. Ask whether recovery itself added load or state divergence.
5. Consider alternative explanations and counterfactuals. Use [verify a system model](verify-system-model.md) to seek evidence that contradicts the proposed sequence. Do not infer causation from deployment timing alone.
6. If corrective action is requested, use [choose an intervention](choose-intervention.md) to compare containment, prevention, and recovery improvements.

## Deliver

Return the evidence-backed timeline, propagation model, initiating and contributing conditions, containment and detection gaps, recovery behavior, confidence, and unresolved questions. Mark checks Proposed, Executed, or Blocked. Include corrective actions only at the requested scope.
