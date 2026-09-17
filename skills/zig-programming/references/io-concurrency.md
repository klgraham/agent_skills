# Task concurrency and parallelism through std.Io

`std.Io` abstracts task scheduling, waiting, cancellation, and synchronization
as well as filesystem and network operations. This is an API design contract,
not an effect system: globals, foreign calls, or raw threads can still perform
work without an `Io` parameter. Ordinary functions can participate;
there is no required language-level async function annotation. Pass the same
`io` through the task's operations and use it to await or cancel its resources.

## Choose the execution contract

| Mechanism | Contract | Use |
|---|---|---|
| Direct call | Completes before the caller continues | Sequential work |
| `io.async(function, args)` | Returns a future; may execute inline before returning | Independent work that remains correct sequentially |
| `try io.concurrent(function, args)` | Reserves concurrent progress or returns `error.ConcurrencyUnavailable` | Tasks whose correctness depends on another task making progress |
| `Io.Group` | Await or cancel an unordered set together | Many tasks with externally stored outcomes |
| `Io.Select(U)` | Receive tagged task completions | Races, deadlines, completion-order processing |
| `Io.Batch` | Coordinates supported low-level `Io.Operation` values | Measured operation-level overhead; not arbitrary functions |
| `std.Thread.spawn` | Creates an OS thread with explicit join/detach ownership | Thread affinity, foreign runtimes, dedicated CPU workers |

Concurrency means tasks can make progress independently. Parallelism means
execution overlaps on hardware. `concurrent` does not promise a dedicated OS
thread, simultaneous execution on separate cores, or a speedup. A backend and
its configuration determine the execution mechanism.

Never substitute `async` after `ConcurrencyUnavailable` when inline execution
could deadlock. A rendezvous producer waiting for a consumer that the caller
has not started yet is such a case. Sequential fallback is appropriate only
when the algorithm can actually finish sequentially.

## Playbook: fan out and collect futures

1. Identify whether tasks are independent or wait on each other.
2. Keep argument storage, allocator state, and `Io` implementation alive until
   all tasks finish. An argument tuple copies pointers, not their pointees.
3. Register cancellation cleanup immediately after each launch, before another
   launch or `try` can fail.
4. Await the required results. Decide whether one failure cancels siblings or
   whether all outcomes must be collected before propagating an error.
5. Release returned resources exactly once. Await/cancel are idempotent on the
   same future, but copying a future is not an ownership transfer. Await/cancel
on a Future or Group are not safe to call simultaneously from multiple owners.

For a task returning `Cancelable!void`, `defer task.cancel(io) catch {};` is a
cleanup boundary. It ensures the task finishes on early return. Report the
normal result through `try task.await(io)`. Do not discard errors inside the
worker's operation loop.

For a future returning owned memory, cancellation may return a successful
allocation if the task already finished. Free that result if abandoning it.
After consuming an awaited owned result, disarm any cleanup that would fetch
and free the same stored result again. Idempotent waiting does not make double
free safe. [concurrency.zig](../examples/concurrency.zig) tests abandoned
owned results as well as void-task cleanup.

## Playbook: bound a batch with Group

`Group` does not collect arbitrary return values or application errors. A group
worker returns a value coercible to `Io.Cancelable!void`. Store success and domain
errors explicitly in disjoint result slots, or send owned outcomes through a queue.
`Group.await` reports cancellation of the waiting task and propagates it to
members. A member returning `error.Canceled` stops at the group boundary; it
does not itself make await fail. Await is not an aggregate domain-error result.

For a finite independent batch, preallocate result slots and assign one writer
per slot. For a stream, start a bounded number of workers with `Group.concurrent`
and feed a bounded queue. Declare the queue and result storage before the group,
and defer `group.cancel(io)` before the first fallible launch. Close the queue
on producer completion, await the group, then inspect outcomes.

The [batch runner](../examples/batch-runner.zig) uses three workers,
a two-item queue, per-job errors, and ordered results. It tests empty input,
a failed job, and launch refusal with concurrency disabled. A group alone does
not bound active work; do not spawn one task per unbounded input item.

## Playbook: cancellation and deadlines

Cancellation is cooperative. `Future.cancel` requests cancellation and waits
for completion; it does not kill a thread. A task can finish successfully before
observing the request. A long CPU loop needs periodic `try io.checkCancel()` if
shutdown must interrupt it. I/O calls with `error.Canceled` are cancellation
points, subject to cancel protection.

An observed cancellation request is not automatically raised at every later
point. Propagate `error.Canceled`. If a narrow recovery boundary must defer it,
use `io.recancel()` or restore a scoped `swapCancelProtection` state according
to `Io.zig`. Keep uncancelable cleanup short and bounded. It can block shutdown.

For a task-level deadline, race the work against `io.sleep` using `Select`.
Start both with `concurrent` when a sequential implementation would invalidate
the deadline. Handle `ConcurrencyUnavailable`. A timeout result still requires
canceling and joining the loser; an uncooperative task can delay return beyond
the deadline. Test winner cleanup using handshakes, not fragile timing assertions.

## Choose an Io implementation

Start with `init.io` in applications and `std.testing.io` in tests. A library
accepts an `Io`; it should not silently create its own scheduler. If the
application needs limits, construct `Io.Threaded.init(gpa, options)`, retain
its address, await/cancel tasks, then `deinit` it before destroying its allocator.

| Implementation | 0.16.0 decision |
|---|---|
| `Io.Threaded` | Thread-backed implementation; inspect `async_limit` and `concurrent_limit` |
| `Io.Threaded.init_single_threaded` | Exercise inline async and unavailable concurrency; no task-level cancellation |
| `Io.Evented` | Experimental, platform-dependent alias; verify supported operations and target before opting in |
| `Io.failing` | Failure-path stub, not a working scheduler |

The release notes describe `Threaded` as the startup default. Evented backends
include Uring, Kqueue, and Dispatch; their existence does not establish feature
parity or production readiness. Do not copy an example using `Io.Blocking`
without checking the installed declarations. Benchmark the actual backend,
CPU count, worker limit, task size, and memory usage before claiming parallel gain.

## Verification

Run the example tests in Debug and ReleaseSafe. Include inline execution,
launch failure, task failure, cancellation, resource cleanup, and queue shutdown.
Use a subprocess timeout to catch deadlocks. Tests validate lifecycle contracts,
not fairness or multicore throughput. See [coordination](io-coordination.md)
and [source review](io-sources.md) for related contracts and source status.

Primary authority: `std/Io.zig`, `std/Io/Threaded.zig`, and `std/testing.zig`
from `zig env`; [0.16.0 release notes](https://ziglang.org/download/0.16.0/release-notes.html).
