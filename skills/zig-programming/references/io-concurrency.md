# Task and backend contracts in Zig 0.17.1

`std.Io` provides scheduling, cancellation, and OS operations through a
runtime interface. The capability is passed explicitly. Globals, foreign
calls, and raw threads can still perform work without an `Io` argument.

For implementation steps, see [Coordinate tasks](../playbooks/coordinate-io-tasks.md)
or [Choose an Io implementation](../playbooks/use-io.md#choose-an-io-implementation).

## Execution contracts

| Mechanism | Contract | Use |
|---|---|---|
| Direct call | Completes before the caller continues | Sequential work |
| `io.async(function, args)` | Returns a future; may execute inline before returning | Independent work that remains correct sequentially |
| `try io.concurrent(function, args)` | Reserves concurrent progress or returns `error.ConcurrencyUnavailable` | Tasks whose correctness depends on another task making progress |
| `Io.Group` | Await or cancel an unordered set together | Many tasks with externally stored outcomes |
| `Io.Select(U)` | Receive tagged task completions | Races, deadlines, completion-order processing |
| `Io.Batch` | Coordinates supported low-level `Io.Operation` values | Measured operation-level overhead; not arbitrary functions |
| `std.Thread.spawn` | Creates an OS thread with explicit join/detach ownership | Thread affinity, foreign runtimes, dedicated CPU workers |

## Futures and groups

`io.async` can complete before returning. `io.concurrent` either reserves
concurrent progress or returns `error.ConcurrencyUnavailable`. It makes no
guarantee about which hardware threads execute the tasks.

`Future.await` and `Future.cancel` return the same stored result on repeated
calls to the same future. A successful owning result has one owner, including
when it is returned by `cancel`. These methods are unsafe to call
simultaneously on the same future. The same restriction applies to
`Group.await` and `Group.cancel` on the same group.

A group worker's result must coerce to `Io.Cancelable!void`. A member's
`error.Canceled` stops at the group boundary. `Group.await` propagates
cancellation of the waiter to members and returns that cancellation after they
finish. Application results and domain errors need their own storage. Group
membership alone imposes no limit on how many workers can be launched.

## Cancellation

A cancellation request is observed at a cancellation point. `io.checkCancel()`
is an explicit point. An observed request is consumed. `io.recancel()` re-arms
a request after observing `error.Canceled`. `io.swapCancelProtection(.blocked)`
suppresses cancellation points until protection is restored.

A task that already finished can return its normal result from
`Future.cancel`. A task that never reaches a cancellation point can keep its
owner waiting until it finishes.

## Backends

| Implementation | Contract |
|---|---|
| `Io.Threaded` | Thread-backed implementation with separate limits for optional and required concurrency |
| `Io.Threaded.init_single_threaded` | Inline async, unavailable concurrent launch, and no task-level cancellation |
| `Io.Evented` | Experimental alias selected by target and fiber support |
| `Io.failing` | Failure-path stub |

The 0.17.1 startup code supplies `Io.Threaded` to `main(std.process.Init)`.
The SDK contains Uring, Kqueue, and Dispatch implementations. Backend
availability and operation coverage depend on the target.

Primary authority: `std/Io.zig`, `std/Io/Threaded.zig`, `std/start.zig`, and
`std/testing.zig` in the SDK located with `zig env`.
