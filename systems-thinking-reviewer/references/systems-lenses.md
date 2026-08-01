# Systems Thinking Lenses

Use this reference while generating candidate findings. Apply a lens only when the reviewed input provides evidence for it.

## Contents

1. Purpose and boundary
2. Local and global optimization
3. Stocks and flows
4. Feedback loops
5. Delays
6. Coupling and cohesion
7. Sources of truth
8. Failure propagation
9. Nonlinearity and scale
10. Observability and controllability
11. Path dependence and reversibility
12. Operational burden
13. Security and permissions
14. Incentives and organizational fit
15. Automation and AI-era comprehension debt

## 1. Purpose and boundary

Determine the real system objective, what lies inside the review boundary, and which external systems or actors shape outcomes.

Look for:

- a component optimizing a proxy rather than the user or system objective;
- overlapping or unclear responsibilities;
- dependencies hidden by the stated boundary;
- conflicting component or team objectives;
- costs exported beyond the boundary.

Ask:

- What outcome is this system meant to create?
- Who receives the benefit and who bears the cost?
- Which dependency or operator has been treated as "external" even though it controls success?

## 2. Local and global optimization

A locally reasonable choice may create globally undesirable behavior.

Trace where a local improvement moves cost:

```text
local shortcut
→ work or state transferred downstream
→ downstream queue, coordination, or failure burden
→ lower end-to-end performance
```

Check whether:

- a latency improvement increases inconsistency or load elsewhere;
- one team's convenience creates on-call or repair work for another;
- a local metric encourages behavior that harms the whole;
- per-component redundancy multiplies system-wide complexity.

## 3. Stocks and flows

Identify state that accumulates:

- databases and append-only logs;
- caches and replicas;
- queues, retry buffers, and dead-letter queues;
- sessions, connections, temporary files, and pending jobs;
- model or agent memory;
- unresolved workflows, migrations, or repair tasks.

For each important stock, ask:

- What adds to it?
- What removes from it?
- Can inflow exceed outflow, for how long, and under which conditions?
- What bounds growth?
- What signal reveals saturation?
- What recovery or disposal path exists?

An accumulation is not a defect by itself. The concern is uncontrolled growth, missing ownership, or a mismatch between inflow and outflow.

## 4. Feedback loops

Identify reinforcing loops that amplify behavior and balancing loops that constrain it.

### Retry amplification

```text
dependency degradation
→ more retries
→ greater dependency load
→ deeper degradation
```

Look for bounded attempts, exponential delay with jitter, deadlines, budgets, circuit breaking, admission control, or load shedding.

### Complexity

```text
more components
→ harder comprehension and discovery
→ more local workarounds
→ more components
```

Look for deletion, canonical capability discovery, shared invariants, or clear ownership—not automatically a new platform.

### Fragmentation

```text
poor capability discovery
→ duplicate implementation
→ more alternatives to discover
→ poorer discovery
```

Check whether the easiest path reuses the intended capability and whether legitimate variation is still possible.

### Alert fatigue

```text
noisy alerts
→ lower operator attention
→ slower response
→ more defensive alerts
```

Look for objective-linked signals, actionable ownership, deduplication, and suppression during known incidents.

Other balancing mechanisms include quotas, backpressure, reconciliation, garbage collection, rate limits, automated rollback, and capacity controls.

## 5. Delays

Search for delay between:

- cause and observable effect;
- write and replication, indexing, or cache invalidation;
- deployment and failure;
- failure and detection;
- metric movement and intervention;
- schema change and consumer migration;
- user action and downstream completion.

Explain why the delay matters. Delayed signals can cause operators or automated controllers to overcorrect, continue unsafe work, or mistake stale state for truth.

Ask whether timestamps, versions, watermarks, lag metrics, or explicit workflow state make the delay visible.

## 6. Coupling and cohesion

Evaluate:

- temporal coupling: components must be available at the same time;
- deployment coupling: components must release together;
- schema coupling: consumers depend on internal data shape;
- storage coupling: components mutate the same database or files;
- behavioral coupling: undocumented ordering or side effects are required;
- organizational coupling: changes require cross-team manual coordination.

Ask whether components can evolve, fail, test, deploy, and recover independently where independence is valuable.

Do not assume all coupling is bad. Essential domain invariants may require tight coupling. Determine whether coupling is deliberate, visible, governed, and owned.

## 7. Sources of truth

Look for duplicated state, ambiguous ownership, derived data treated as authoritative, caches without invalidation rules, and multiple definitions of the same concept or metric.

For each representation, determine:

- which source is authoritative;
- whether consumers agree on that authority;
- how divergence is detected;
- how conflicts are resolved;
- what behavior occurs during disagreement;
- whether reconciliation is automatic, manual, or absent.

Typical causal mechanism:

```text
two writable representations
→ independent updates
→ divergence
→ behavior depends on read path
→ inconsistent decisions and difficult repair
```

## 8. Failure propagation

Trace failure through synchronous chains, fan-out, shared infrastructure, bulk operations, retries, poison messages, partial writes, timeouts, and global configuration.

Ask:

- Can one tenant, request, key, job, or region exhaust a shared resource?
- Does a small failure trigger more work?
- Can degraded operation continue safely?
- Is failure isolated by tenant, user, region, request, or workload?
- Is a partial operation detectable and recoverable?
- Is the recovery path practiced?

Name the blast-radius boundary and the mechanism that crosses or contains it.

## 9. Nonlinearity and scale

Do not assume cost grows linearly with traffic, data, tenants, components, or development velocity.

Look for:

- quadratic or all-to-all interaction;
- fan-out and fan-in;
- lock contention and serialized coordination;
- hot keys or partitions;
- shared queues and connection pools;
- synchronized refresh or cache stampedes;
- unbounded cardinality in telemetry or state;
- thresholds where graceful behavior becomes collapse.

Use `10×` as a probing question, not a forecast:

- What happens at 10× traffic, data, tenants, components, or change rate?
- Which resource saturates first?
- Does saturation apply backpressure, shed load, or amplify failure?

## 10. Observability and controllability

A system cannot be effectively controlled when important internal state is invisible.

Determine whether operators can answer:

- What is happening?
- Why is it happening?
- Who or what is affected?
- Is the system recovering?
- Which intervention is safe?
- Did the intervention work?

Review logs, metrics, traces, correlation identifiers, audit records, provenance, health signals, and operational dashboards. Prefer signals connected to system objectives and known failure modes over undifferentiated telemetry volume.

Also inspect control surfaces: rollback, pause, drain, replay, reconcile, isolate, rate-limit, or disable. Observation without safe intervention may still leave the system uncontrollable.

## 11. Path dependence and reversibility

Identify changes that create durable commitments:

- schemas and persistent formats;
- public APIs and user-visible contracts;
- external integrations;
- cross-team dependencies;
- stored identifiers or semantics;
- migrations that delete or transform information.

Ask:

- Is this a one-way or two-way decision?
- What must be migrated, coordinated, or deleted later?
- Can old and new versions coexist safely?
- Does a prototype become an accidental permanent interface?
- Is rollback possible after new data has been written?

A small generation cost can conceal a large future migration cost.

## 12. Operational burden

Estimate ongoing ownership cost:

- deployment and release coordination;
- on-call response and incident diagnosis;
- data repair and reconciliation;
- support and access management;
- dependency upgrades;
- capacity planning;
- manual workflows and runbooks.

Use the conceptual model:

```text
net engineering value
= capability created
− complexity introduced
− operational cost
− future coordination cost
```

Identify which actor bears each cost. A design whose builders gain speed while another team inherits permanent work is a system-level tradeoff.

## 13. Security and permissions

Treat security as an end-to-end property.

Review:

- trust boundaries and identity propagation;
- authorization at the authoritative resource boundary;
- privilege delegation and confused-deputy risks;
- tenant isolation;
- secret handling;
- auditability and provenance;
- behavior when identity or policy services are stale or unavailable;
- revocation during long-running or asynchronous work.

Do not conclude that upstream validation secures downstream resources unless the trust and enforcement chain is explicit.

## 14. Incentives and organizational fit

Ask:

- Does the easiest local action produce the desired global behavior?
- Does the design encourage bypassing the shared path?
- Who benefits, and who maintains or operates it?
- Is ownership aligned with blast radius?
- Does the system require tribal knowledge or repeated manual coordination?
- Can the responsible team observe and control the behavior it owns?

Treat undocumented human procedure as a dependency. It may be acceptable, but its capacity, reliability, and ownership should be visible.

## 15. Automation and AI-era comprehension debt

Apply this lens only when automation, generated code, or agent-assisted change materially affects the review surface.

Generation and comprehension are asymmetric:

```text
generation time ≪ understanding and ownership time
```

Evaluate whether:

- generated code duplicates an existing capability;
- reviewers can reconstruct assumptions and invariants;
- tests independently establish behavior rather than mirror implementation;
- abstractions reduce conceptual load or merely add indirection;
- automation can create change faster than review and operations can absorb it;
- system discoverability and deletion keep pace with generation.

Do not object to generated code because it is generated. Comment when the resulting system behavior, evidence, ownership, or comprehensibility is inadequate.
