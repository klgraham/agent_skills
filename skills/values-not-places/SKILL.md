---
name: values-not-places
description: >-
  Use when choosing how state, records, or history are represented in
  memory, across threads, at API boundaries, or in storage; when shared
  mutable state is guarded by a lock; or when code reads from a database,
  cache, or stateful service. Build on immutable values, change state only
  through managed references, and pass state in as an argument.
---

# Values, not places

A place is a slot you overwrite, and a value never changes. Build on values, and reach for places only when you can justify it.

Source: Ken's principles #14 "Values not places," #18 "Managed references," and #20 "State as an argument." #18 is from Rich Hickey, "Persistent Data Structures and Managed References" (QCon London, 2009). #20 is from Hickey, "The Functional Database" (QCon New York, 2013), "The Database as a Value" (GOTO Night Chicago, 2012), and "Deconstructing the Database" (QCon San Francisco, 2012).

## Values (#14)

- Default to immutable data, and keep mutation explicit and contained.
- Pass values across threads and services, never references to mutable state.
- Model information as facts that were true at a point in time. Record new facts instead of overwriting old ones, and keep history when it's cheap.
- Separate identity (the thing over time) from state (its value at one moment).
- If something can't be compared, cached, logged, and replayed without coordination, ask why.

## Managed references (#18)

The only thing that mutates is a reference, and only in a controlled way: it swaps from one immutable value to the next. The new value is a pure function of the old one.

- Hold state as an immutable value behind a single reference, not as a mutable object with fields.
- Change state with `update(ref, f, args)`, never by reading, modifying, and writing back by hand.
- Choose the reference's semantics on purpose: shared or isolated, synchronous or asynchronous, coordinated or autonomous.
- Coordinate several references only where an invariant spans them, and do it in one transaction.
- Keep side effects out of anything that may be retried. Do I/O after the swap.
- Treat locks in application code as a design smell.

## State as an argument (#20)

Compute with values, passed in explicitly, not with a live connection.

- Get a value of the state once (a snapshot or version), then pass it to functions. Don't thread connections or rely on ambient connection pools.
- Record the basis (transaction id, version, timestamp) with every result, so the same query on the same basis gives the same answer.
- Write domain logic as `(state, input) -> result` or `(state, change) -> new-state`, with no I/O inside.
- Test with fabricated or generated state values, not mocked connections or a shared test database.

## Anti-patterns

- Shared mutable objects passed between threads, guarded by ad hoc locks.
- Read-modify-write without compare-and-set or a transaction.
- `UPDATE` in place that throws away the history you'll later need.
- Domain functions that open their own database connections.

## Required closing note

When this skill shaped your work, name the principle you applied ("Values not places, #14," "Managed references, #18," or "State as an argument, #20") and the decision it changed. For example: "replaced the locked cache object with an atom of an immutable map," or "passed a snapshot into the report function instead of a connection."
