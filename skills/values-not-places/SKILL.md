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

Source: Rich Hickey, "Persistent Data Structures and Managed References" (QCon London, 2009), for managed references; "The Functional Database" (QCon New York, 2013), "The Database as a Value" (GOTO Night Chicago, 2012), and "Deconstructing the Database" (QCon San Francisco, 2012), for state as an argument.

## Values

- Default to immutable data, and keep mutation explicit and contained.
- Pass values across threads and services, never references to mutable state.
- Model information as facts that were true at a point in time. Record new facts instead of overwriting old ones, and keep history when it's cheap.
- Separate identity (the thing over time) from state (its value at one moment).
- If something can't be compared, cached, logged, and replayed without coordination, ask why.

## Managed references

The only thing that mutates is a reference, and only in a controlled way: it swaps from one immutable value to the next. The new value is a pure function of the old one.

- Hold state as an immutable value behind a single reference, not as a mutable object with fields.
- Change state with `update(ref, f, args)`, never by reading, modifying, and writing back by hand.
- Choose the reference's semantics on purpose: shared or isolated, synchronous or asynchronous, coordinated or autonomous.
- Coordinate several references only where an invariant spans them, and do it in one transaction.
- Keep side effects out of anything that may be retried. Do I/O after the swap.
- Let readers dereference a consistent snapshot without locks; readers never block writers, and writers never block readers.
- Use persistent data structures with structural sharing so "copying" on every change stays cheap; avoid copy-on-write of whole collections.
- Treat locks in application code as a design smell.

## State as an argument

Compute with values, passed in explicitly, not with a live connection.

- Get a value of the state once (a snapshot or version), then pass it to functions. Don't thread connections or rely on ambient connection pools.
- Record the basis (transaction id, version, timestamp) with every result, so the same query on the same basis gives the same answer and can be shared as a permalink.
- Write domain logic as `(state, input) -> result` or `(state, change) -> new-state`, with no I/O inside.
- Answer what-if questions by applying a change to a value speculatively (Datomic `with`) and dropping it to backtrack, instead of writing and rolling back.
- Keep history in the value so you can query as-of, since, or across time without a separate audit system.
- Test with fabricated or generated state values, not mocked connections or a shared test database.
- Use one value with many access paths (queries, index scans, navigation) instead of a different service per question.

## Anti-patterns

- Shared mutable objects passed between threads, guarded by ad hoc locks.
- Read-modify-write without compare-and-set or a transaction.
- `UPDATE` in place that throws away the history you'll later need.
- Domain functions that open their own database connections.

When this skill shaped your work, name the principle you applied ("values-not-places") and the decision it changed. For example: "passed a database snapshot into the report function instead of a live connection".
