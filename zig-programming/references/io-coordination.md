# Select, queues, locks, atomics, and threads

Choose an ownership protocol before choosing a synchronization primitive.
Prefer disjoint task outputs or queue ownership transfer to shared mutation.
The APIs below are checked against the installed Zig 0.16.0 `std/Io.zig`.

## Playbook: receive completions with Select

Define a tagged union whose fields match each task's return type. Allocate
result buffer storage that outlives the select, initialize `Io.Select(U)`, and
launch with `select.async(.tag, function, args)` or the fallible `concurrent` form.
`try select.await()` returns the next completed tagged result, including a task
error when that union field contains an error union. Track how many results
are outstanding; awaiting after the last result is not an end-of-stream check.

For scalar or void results, defer `select.cancelDiscard()` so early return joins
remaining tasks. For owning results, reserve enough slots for every outstanding
task to finish, then drain `select.cancel()` until it returns null and free each
returned owner. In 0.16.0, `cancel()` waits for tasks before draining; insufficient
result capacity can deadlock. `cancelDiscard()` closes the result queue before
joining and discards values, so it is inappropriate for owning return values.

Never call await after cancellation. Receiving the first completion is not
necessarily receiving the first success; continue past errors if the operation
requires a first-success policy. The [concurrency example](../examples/concurrency.zig)
checks both a completion race and cleanup of owned results.

## Playbook: bounded producer and consumer

1. Initialize `Io.Queue(T)` with backing storage. An empty buffer is a rendezvous
   queue; a full bounded buffer blocks producers until consumers make space.
2. Establish concurrent progress for mutually dependent participants before
   entering blocking puts or gets. Handle failure to start a worker.
3. Use `putOne(io, item)` and `getOne(io)` for a simple ownership handoff.
   Define who frees an item when a put fails.
4. Close the queue when no further production is possible. Existing buffered
   items remain readable; consumers then receive `error.Closed`.
5. Cancel or finish workers before the queue or backing storage leaves scope.
   On abandonment, drain and release any queued owners after producers stop.

Queue thread safety does not extend to mutable objects referenced by an element.
A copied slice still borrows its bytes. Prefer an owned message or immutable
storage that outlives consumption.

Batch APIs require more care: `put` and `get` return progress counts and can make
partial progress around cancellation or closure. On a failed `putAll`, the count
already enqueued is unspecified. Avoid `putAll` as an all-or-nothing transfer of
owning elements; use individual transfers or a protocol that tracks ownership.

The [batch runner](../examples/batch-runner.zig) demonstrates bounded
backpressure, close/drain behavior, and disjoint output slots.

## Playbook: protect a shared invariant

Use `Io.Mutex` and `Io.Condition` in backend-neutral task code. Acquire with
`try mutex.lock(io)`, then immediately defer `mutex.unlock(io)`. The lock call
may be a cancellation point. Do not install unlock cleanup before lock succeeds.

Wait for a condition in a loop over the protected predicate. Update the predicate
under the same mutex before signaling or broadcasting. A signal is not stored
application state. `Condition.wait` releases and reacquires the mutex, including
when it returns cancellation. Keep the lock and predicate alive through shutdown.

Avoid holding a lock while spawning an async child that may run inline and
reacquire it. Also avoid a locked wait for a task that needs that lock to finish.
Uncancelable lock/wait variants are for a proved cleanup requirement, not for
silencing cancellation errors. Use `RwLock` only when measurement and access
patterns justify reader/writer coordination.

For a permit budget, use `Io.Semaphore{ .permits = n }`, acquire with
`try sem.wait(io)`, then defer `sem.post(io)`. Cancellation before acquisition
must not return a permit; cancellation after acquisition must release it.
The 0.16.0 semaphore has no `waitTimeout`; do not copy that newer guide API.
An `Io.Event` fits a persistent readiness signal. Reset it only when the protocol
proves no waiter still depends on the previous signal.

## Atomics and CPU parallelism

`std.atomic.Value(T)` coordinates memory, not task lifecycle. Use `.monotonic`
for an independent counter when no other data is published through it. Use a
release/acquire protocol for publication only with a clear happens-before
argument. An atomic index can assign disjoint work, but shared result visibility
still needs completion synchronization before the parent reads it.

Do not busy-spin on an atomic in backend-neutral task code: it can occupy the
only execution thread and prevent the producer from running. Prefer an `Io`
queue, condition, event, or futex wait. Atomics do not reclaim objects or prevent
use-after-free. `volatile` is not a synchronization replacement.

For compute-heavy work, partition data into bounded chunks and measure on a
backend that can use multiple OS threads. Include periodic cancellation checks
where appropriate. Keep per-worker scratch storage separate, and use an allocator
whose threading contract matches all allocation and free sites.

## Playbook: migrate from std.Thread

| Existing design | Migration decision |
|---|---|
| A thread per independent operation | Future, with immediate cancellation cleanup |
| Thread pool plus wait group | Bounded workers in `Io.Group`, outcomes stored explicitly |
| Channel or blocking work queue | `Io.Queue(T)` with closure and cancellation semantics |
| Thread mutex/condition in reusable task code | `Io.Mutex` and `Io.Condition` using the supplied `io` |
| Dedicated foreign thread, affinity, or thread-local runtime | Keep `std.Thread` at the adapter boundary |
| Atomic shared counter | Keep only with a documented ordering and lifetime contract |

`Thread.join` waits; it does not return the worker function's result. Store the
result in owned storage that outlives the thread, then read it after join.
Do not detach a thread borrowing stack data. Raw threads do not automatically
acquire the structured cancellation contract of an `Io` future. Explicitly
bridge stop requests and completion at that boundary.

Primary authority: `std/Io.zig`, `std/atomic.zig`, and `std/Thread.zig`.
For additional examples and compatibility notes, see [source review](io-sources.md).
