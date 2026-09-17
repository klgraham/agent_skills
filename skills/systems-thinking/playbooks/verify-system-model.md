# Verify a system model

Try to refute the consequential claims before increasing confidence.

## Load

Read the [causal reasoning boundary](../references/causal-reasoning.md). Load principles only for the mechanism under challenge. Do not read every principle or require a formal review schema for a general model.

## Procedure

1. Extract testable claims from the supplied model, finding, diagnosis, or intervention. Assign stable claim IDs, or retain existing finding IDs. Separate observations, inferred mechanisms, and predictions.
2. Identify assumptions and derive observable predictions with a timescale and boundary. State what would falsify each claim.
3. Seek contradictory evidence and plausible alternative mechanisms. Inspect relevant source, traces, tests, measurements, and owner statements; source code can establish a path without establishing its frequency in production.
4. Choose checks that distinguish alternatives rather than merely repeat the original evidence. Run safe local or read-only checks within authorization. Record unavailable or unauthorized checks as Blocked or Proposed; do not perform shared-state experiments merely to complete verification.
5. When an independent verifier is available and delegation is authorized, give it the claims, scope, and raw evidence and ask it to challenge them. Do not feed it the desired verdict. Otherwise perform a separate falsification pass and disclose that it was not independent.
6. Record the actual result of each executed check, its limits, and whether it supports, contradicts, or leaves the claim unresolved. Revise or reject the model when warranted.

## Deliver

Return a claim ledger with claim ID, evidence, assumptions, prediction, falsifier, check, verification state, result, and revised confidence or verdict. Use Proposed, Executed, or Blocked for the check state. Use supported, contradicted, or unresolved for the outcome; Executed does not mean confirmed.

Retain material unresolved alternatives and identify the next discriminating observation. Return to the calling playbook without recursively restarting verification. A surviving static check is not proof of a causal effect or of production behavior.
