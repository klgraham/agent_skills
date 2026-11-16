# Coordinate tasks with std.Io

Read the [I/O principle](../principles/io.md) and check the
[launch and cancellation contracts](../references/io-concurrency.md).

## Launch and collect typed results

1. Use a direct call for sequential work. Use `io.async` when overlap is
   optional. Use `io.concurrent` when the caller or a peer has to make progress
   before the task can finish. Propagate or handle `error.ConcurrencyUnavailable`
   before entering a dependent wait.
2. Arrange cancellation cleanup immediately after each launch. For a future
   returning `Io.Cancelable!void`, use `defer task.cancel(io) catch {};` and
   report the normal outcome with `try task.await(io)`.
3. Choose whether a failed task cancels its siblings or whether the caller
   collects every result before propagating an error. Keep one owner for
   each future and finish each task before its borrowed data leaves scope.
4. For a future returning an owned value, dispose of any successful value
   returned by cancellation when abandoning the task. Disarm that disposal
   after taking ownership of the awaited value.

## Run coroutine-style work

Write an ordinary function that makes the necessary `Io` calls as it goes.
Launch it as a scoped task, then await it or cancel and join it. The backend
determines how waiting and resumption work. For a pair of routines that
have to exchange values while both are live, give each exchange a
[queue and progress contract](build-channel-pipeline.md).

If the caller drives one step at a time, model a pull generator with a state
struct and `next` method. Keep its cursor and pending data in the struct.
Use a scheduled task with a queue when the producer needs to progress between
pulls.

## Receive completions or race a deadline

1. Model the results with a tagged union. Initialize `Io.Select(U)` with
   buffer storage. Use one slot per outstanding task if cleanup needs to
   recover owned results. The same sizing lets inline tasks publish results
   before the caller starts waiting.
2. Register the cleanup from step 4 before launching. Launch the operations
   with tags matching their return types. For a deadline, race the operation
   against `io.sleep` using `select.concurrent` for both. Handle refusal at
   either launch.
3. Count outstanding results when collecting more than one. For a first
   success policy, inspect each completion for errors before choosing it.
4. On exit, join the remaining tasks. Use `cancelDiscard()` for disposable
   results. For owning results, call `cancel()` until it returns `null`, then
   release each value you recovered during that drain.
5. Add cancellation points to CPU loops that must stop promptly. A deadline
   limits the race. Cleanup still waits for every task to return.

Check the [Select contract](../references/io-coordination.md#select) for buffer
and lifecycle rules. For competing channel operations, use the
[channel selection guidance](build-channel-pipeline.md#route-events-from-several-inputs).

## Protect a shared invariant

1. Acquire `Io.Mutex` with `try mutex.lock(io)`, then immediately defer
   `mutex.unlock(io)`. Keep the predicate and every access to it under the lock.
2. For a condition wait, check the predicate in a loop. Update it under the
   same mutex before signaling or broadcasting.
3. Release the lock before launching work that could run inline and reacquire
   it, or before joining work that needs it to finish.
4. For a permit budget, initialize `Io.Semaphore{ .permits = n }`. After
   `try sem.wait(io)` succeeds, defer `sem.post(io)`. Use `waitTimeout` for
   a deadline on acquiring a permit.

Start with a mutex for shared state. Consider `Io.RwLock` if profiling shows
that reads contend and the workload can benefit from concurrent readers.

See [coordination](../references/io-coordination.md) for events, locks,
semaphores, atomics, and memory publication.

## Migrate from std.Thread

| Existing design | Migration decision |
|---|---|
| A thread per independent operation | Future with immediate cancellation cleanup |
| Thread pool and wait group | [Bounded workers](parallelize-work.md#run-a-bounded-worker-pool) with explicit outcomes |
| Channel or blocking work queue | [Queue](build-channel-pipeline.md) with explicit close and drain |
| Thread mutex or condition in reusable task code | `Io.Mutex` or `Io.Condition` using the supplied `io` |
| Dedicated foreign thread, affinity, or thread-local runtime | Keep `std.Thread` at the adapter boundary and bridge stop and join explicitly |
| Shared atomic counter | Keep it with a documented ordering and lifetime contract |

## Verify

Run [concurrency.zig](../examples/concurrency.zig) for inline launch, sibling
cleanup, owned results, deadlines, and locks. Use readiness handshakes for
shutdown tests and a subprocess timeout to catch deadlocks. Exercise failure
after each fallible launch in a sequence when earlier work can already be live.
