# Boundaries and purpose

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
