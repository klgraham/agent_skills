# I/O capabilities and task lifetimes

`std.Io` carries the implementation for OS operations, scheduling, and
synchronization. An allocator carries a separate policy. Applications choose
these dependencies at their boundary. Reusable functions accept the ones they
use. A byte transform can often accept a reader and writer interface alone.

## Progress comes from the dependency graph

A task is safe to run inline if it can finish before the caller takes its
next step. A task that waits for a peer needs both participants to make
progress. Work out who wakes each waiter before choosing a launch operation,
and account for the same dependencies during shutdown.

Concurrent progress lets tasks continue independently. Parallel execution
requires hardware overlap. The backend, its worker limits, and the workload
determine whether concurrent tasks execute in parallel.

## Ownership follows the task or message

Give each task a completion owner. Keep the backend, argument pointees,
buffers, and allocator state alive until their last task completes. Give each
result and message one owner at a time. Copying a slice copies a view of its
bytes. The view still depends on the lifetime and stability of those bytes.

Choose a state owner before choosing synchronization. Independent workers
can each own disjoint results. A queue can transfer a message to one receiver.
A single service task can own and update an entire mutable state. A lock
protects shared state when multiple tasks need direct access to the same invariant.

## Cancellation and capacity are part of the interface

Cancellation is cooperative. Requests stop tasks at cancellation points, and
completion establishes when their borrowed state can be reclaimed. A service
that accepts work also needs a policy for pending work on graceful shutdown
and on abort.

Size the number of live tasks and the capacity of each queue independently.
State what happens at capacity and who can still make progress when a producer
blocks. Bounds on task count and message count need a separate byte budget
when messages can own variable-size payloads.

Select a procedure in [Use std.Io](../playbooks/use-io.md).
