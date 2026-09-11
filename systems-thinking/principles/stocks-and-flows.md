# Stocks and flows

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
