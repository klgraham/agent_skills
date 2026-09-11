---
name: systems-thinking
description: Understand, diagnose, design, visualize, and review systems whose behavior depends on interactions, state, feedback, delays, constraints, or incentives. Use for recurring problems, architecture tradeoffs, intervention choices, and evidence-grounded repository, PR, or architecture reviews. Exclude factual lookup, style review, and isolated local fixes.
---

# Systems thinking

Model the structure that produces the behavior. Keep facts, hypotheses, and verified results distinct.

## Route the task

Choose one primary playbook by the user's intent. Read that playbook, its required principles, and only the conditional resources that apply. Do not preload the library.

| Intent | Playbook |
|---|---|
| Understand the whole system | [Understand a system](playbooks/understand-system.md) |
| Explain a persistent behavior or bottleneck | [Diagnose a problem](playbooks/diagnose-problem.md) |
| Review software, a repository, PR, or architecture | [Review a software system](playbooks/review-software-system.md) |
| Design a system or compare architectures | [Design a system](playbooks/design-system.md) |
| Decide what to change | [Choose an intervention](playbooks/choose-intervention.md) |
| Explain a failure and recovery | [Analyze a failure](playbooks/analyze-failure.md) |
| Draw or explore a system model | [Visualize a system](playbooks/visualize-system.md) |
| Challenge a model or causal claim | [Verify a system model](playbooks/verify-system-model.md) |

For a compound request, start with the missing prerequisite and pass its compact output to the next requested playbook. Understanding alone does not require intervention. A diagram does not require a formal review. Reuse an existing model after checking its scope and evidence.

## Establish the scope

Collect or infer the problem, objective, boundary, hard constraints, timescale, and available evidence. State material assumptions. Ask only when missing information prevents useful progress or would change the decision materially.

Preserve the requested action boundary. Review and analysis do not authorize implementation, external publication, or state-changing experiments. Verification actions remain proposals until executed within the authorized scope.

## Choose an input mode when needed

Modes adapt evidence and scope; they do not repeat the playbook.

- For every software review, load [review](modes/review.md).
- For repository input, load [repository](modes/repository.md).
- For a PR or diff, load [pull request](modes/pull-request.md).
- For an architecture document or proposal, load [architecture](modes/architecture.md).
- For an incident record, load [incident](modes/incident.md).

Combine input modes only when the target spans them. A general workflow, product, or organizational question needs no software input mode.

## Select principles by mechanism

The selected playbook declares its required principles. Add a conditional principle when the observed mechanism or question warrants it. Do not turn this index into a checklist of findings.

| Mechanism or question | Principle |
|---|---|
| Required entities, operations, and invariants | [First principles](principles/first-principles.md) |
| Objective, boundary, or exported local costs | [Boundaries and purpose](principles/boundaries-and-purpose.md) |
| Queues, state, and accumulation | [Stocks and flows](principles/stocks-and-flows.md) |
| Reinforcing or balancing behavior | [Feedback loops](principles/feedback-loops.md) |
| Lag, overshoot, thresholds, or hysteresis | [Delays and dynamics](principles/delays-and-dynamics.md) |
| Throughput, saturation, or displaced bottlenecks | [Constraints and bottlenecks](principles/constraints-and-bottlenecks.md) |
| Coordinated evolution, deployment, or failure | [Coupling and cohesion](principles/coupling-and-cohesion.md) |
| Authority, divergence, or reconciliation | [Sources of truth](principles/sources-of-truth.md) |
| Partial failure, recovery, or blast radius | [Failure propagation](principles/failure-propagation.md) |
| Fan-out, contention, or growth mechanisms | [Nonlinearity and scale](principles/nonlinearity-and-scale.md) |
| Detection, diagnosis, or safe control | [Observability and controllability](principles/observability-and-controllability.md) |
| Durable commitments or rollback | [Path dependence and reversibility](principles/path-dependence-and-reversibility.md) |
| On-call, repair, and ongoing ownership cost | [Operational burden](principles/operational-burden.md) |
| Trust, identity, authorization, or revocation | [Security and permissions](principles/security-and-permissions.md) |
| Incentives, handoffs, or human dependencies | [Incentives and organization](principles/incentives-and-organization.md) |
| Generated complexity or review capacity | [Automation and comprehension debt](principles/automation-and-comprehension-debt.md) |

## Load output references only when needed

- Formal software review: [findings schema](references/findings-schema.md) for the field contract and [report template](references/report-template.md) for the section outline.
- Requested review files: [findings schema](references/findings-schema.md), then run `scripts/build_report.py` with `--strict` to render matching HTML and Obsidian Markdown.
- Diagram or interactive exploration: [visualization conventions](references/visualization-conventions.md).
- Causal claims or quantitative causal questions: [causal reasoning boundary](references/causal-reasoning.md).
- Requested general Obsidian note: [system analysis note template](references/obsidian-template.md). Review artifacts use the review schema instead.

Resolve all resource and script paths relative to this skill directory. The bundled report renderer works offline with Python's standard library. Do not require a separate visualization or causal-inference skill; use one only when it is available and appropriate.

## Deliver the selected result

Follow the playbook's output contract and the user's requested format. Keep the answer proportionate to the decision, not to the size of this library.

Show the current model, decisive evidence, assumptions, and coverage limits. For causal claims, explain the mechanism and what would falsify it. Mark verification Proposed, Executed, or Blocked, and report what an executed check actually established.

A plausible story is not a verified result. If the evidence cannot resolve the question, return the uncertainty and next discriminating observation. Do not manufacture findings or recommendations to fill a template.
