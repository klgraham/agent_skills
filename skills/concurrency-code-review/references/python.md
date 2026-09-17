# Python concurrency review notes

Identify the supported Python versions, event-loop implementation, async framework, worker model, and deployment topology before applying these notes. `asyncio.TaskGroup` requires Python 3.11 or later, queue shutdown APIs require Python 3.13 or later, and free-threaded CPython changes assumptions that accidentally depended on the global interpreter lock. Review the repository's actual runtime contract.

Python has several concurrency models with different synchronization rules. Do not use an `asyncio` primitive to coordinate operating-system threads, a `threading` primitive to block an event-loop thread, or a process-local lock to protect state shared by processes or hosts.

## Coroutines, tasks, and ownership

Calling an `async def` function creates a coroutine object. It does not run the body to completion. Trace each changed coroutine to one of these terminal paths:

- awaited directly
- returned to a caller that owns awaiting it
- scheduled in a structured group such as `asyncio.TaskGroup`
- passed to a combinator whose result is awaited
- deliberately supervised as background work

Flag coroutine objects created and discarded, async cleanup called without `await`, and synchronous callback APIs given an async callable that they do not await.

Inspect every `asyncio.create_task`, `loop.create_task`, `ensure_future`, callback-created task, and framework-specific spawn. For each task, identify:

- the strong reference that keeps it alive
- the owner that observes its result or exception
- the scope that cancels and awaits it during shutdown
- the resources and context variables that must outlive it

The event loop keeps weak references to tasks. A bare fire-and-forget call has neither reliable lifetime ownership nor failure supervision. A background-task set needs a done callback that retrieves the result or otherwise reports failure, removes the task, and preserves the application's intended failure policy.

Check the exact combinator semantics:

- `TaskGroup` waits for all children and normally cancels siblings after the first non-cancellation failure. Verify the project's Python version and nested cancellation behavior.
- `gather` does not provide the same sibling-failure policy as `TaskGroup`. Verify `return_exceptions`, caller cancellation, child cancellation, and whether unfinished work continues after one child fails.
- `wait` and `as_completed` return or yield task handles. A timeout does not automatically give every pending task a terminal path. Cancel and await pending work when the policy requires it.
- `shield` separates cancellation of the waiter from cancellation of the underlying task. The underlying task still needs a strong reference, owner, and later observation.

Do not replace a sequential dependency with concurrency merely because `gather` or `TaskGroup` is available. Match the code to the real dependency graph and capacity limit.

## Races across `await`

A single-threaded event loop does not make a multi-step state transition atomic. Another task can run whenever the current task awaits or calls code that awaits.

Look for this sequence:

```text
Task A reads shared state
Task A awaits
Task B changes the shared state
Task A resumes and writes a value derived from its stale read
```

Audit check-then-act, read-modify-write, lazy initialization, cache fills, connection-state changes, and state machines that cross an `await`. Keep the whole invariant under one ownership protocol or revalidate after suspension. Do not hold a lock across unrelated network or user code merely to avoid revalidation.

Callbacks and signal handlers can also interleave with tasks. Treat a synchronous callback as atomic with respect to other event-loop callbacks only until it returns. It is not atomic with respect to operating-system threads, signal delivery rules, or foreign code.

## Blocking and CPU-bound work

Within `async def`, flag synchronous operations that can block an event-loop worker:

- `time.sleep`
- `requests` and other synchronous network clients
- synchronous database, filesystem, subprocess, or logging calls with material latency
- `threading.Lock.acquire`, `Thread.join`, `Future.result`, or queue operations that wait
- CPU-heavy loops, parsing, compression, cryptography, or image processing

Use an async-native API when one fits. `asyncio.to_thread` or a thread executor can isolate blocking I/O, but the submitted work keeps running if its awaiting coroutine is cancelled. The thread still needs thread-safe inputs, a bounded executor, failure observation, and a shutdown policy. Use a process or interpreter executor for CPU work only when serialization, startup cost, cancellation, and process lifecycle are acceptable.

Check executor deadlocks. A worker must not synchronously wait for work submitted to the same exhausted pool. A coroutine must not call `.result()` on a future whose completion needs the blocked event-loop thread.

## Cancellation, timeouts, and cleanup

`Task.cancel()` requests cooperative cancellation. It does not prove the task has stopped. After cancelling owned work, await it and handle the terminal outcome according to policy.

`asyncio.CancelledError` normally needs to propagate after cleanup. Flag broad exception handling or explicit cancellation handling that swallows it and lets the task report success. `TaskGroup` and `asyncio.timeout` use cancellation internally, so swallowing cancellation can break their guarantees.

At every suspension point, ask whether cancellation can leave:

- a lock or semaphore permit held
- a database transaction open
- partial state published
- an item removed from a queue but not marked done
- a child task or thread running without an owner
- an async generator or context manager unclosed

Use `try/finally`, `async with`, and idempotent cleanup. Apply `shield` only to the smallest cleanup action that must finish and keep ownership of the shielded work. A timeout that stops waiting while the underlying operation continues can consume capacity or mutate state after the caller has reported failure.

## Locks, semaphores, conditions, and queues

`asyncio` synchronization objects coordinate tasks on an event loop. They are not thread-safe. `threading` synchronization objects coordinate threads and can block the event loop when used directly by a coroutine.

For each `asyncio.Lock`, identify the invariant and every access that must follow its protocol. Check for re-entry, lock-order cycles, cancellation during acquisition or protected work, callbacks under the lock, and waits for code that needs the same lock. An async lock may be held across `await`, but the awaited operation must belong inside the invariant.

Use `async with` for locks and semaphores so exceptions and cancellation release them. Check manual `acquire` and `release` pairs for leaks and double release. Consider `BoundedSemaphore` when over-release must be detected. Confirm that the semaphore bounds the scarce resource, not merely one call site while other paths bypass it.

For conditions, wait in a loop that rechecks the predicate. Notifications are not durable state. For events, check whether a stale set flag incorrectly satisfies a later generation of work.

For `asyncio.Queue` and `queue.Queue`:

- pair every successful `get` with exactly one `task_done`, normally in `finally`
- do not call `task_done` for a failed `get`
- verify that `join` cannot return before the work's real side effects finish
- bound the queue or prove why producers cannot outrun consumers
- define how producers, consumers, and blocked operations stop during shutdown
- apply `shutdown` only when the supported Python version provides it and understand that immediate shutdown can violate the normal `join` invariant

## Threads, the GIL, and event-loop boundaries

The global interpreter lock is not an application synchronization protocol. Compound operations, check-then-act sequences, and invariants across several objects still need a lock, queue, immutable handoff, or another explicit ordering mechanism. C extensions can release the GIL, and free-threaded CPython builds permit more true parallel execution.

Audit shared dictionaries, lists, caches, counters, singleton initialization, and mutable objects passed to executors. Do not infer that an operation is safe because a current CPython implementation happens to execute one bytecode sequence without switching.

Most `asyncio` objects are not thread-safe. From another thread, use `loop.call_soon_threadsafe` for callbacks and `asyncio.run_coroutine_threadsafe` for coroutines. The returned `concurrent.futures.Future` still needs result, exception, timeout, and cancellation handling. Check loop lifetime so a thread cannot submit after shutdown or wait on the event-loop thread in a cycle.

`asyncio.run` is the top-level event-loop owner and cannot be called while another event loop is already running in the same thread. Libraries should expose awaitables instead of starting a private top-level loop. If code manually owns a loop, verify finalization of pending tasks, asynchronous generators, and the default executor before closing it.

Processes do not share ordinary locks or memory unless the program explicitly uses multiprocessing synchronization, shared memory, a manager, a database, or another interprocess protocol. Check pickling boundaries, duplicated connections after `fork`, worker initialization, child failure propagation, executor shutdown, and platform-specific start methods.

## Async iterators and context managers

Check every asynchronous resource for its protocol:

- use `async with`, not `with`, for asynchronous context managers
- use `async for`, not `for`, for asynchronous iterators
- await `__aenter__`, `__aexit__`, `aclose`, and other async cleanup through their public syntax or API
- close partially consumed async generators when their scope ends early
- ensure cancellation during entry or exit cannot leak a resource or suppress the original failure

Framework helpers may own this cleanup. Trace the actual owner before reporting a leak.

## Verification

Use the repository's current tools before adding dependencies. Useful checks include:

- asyncio debug mode for slow callbacks, wrong-thread API use, never-awaited coroutines, and never-retrieved exceptions
- warnings configured as errors in focused tests where practical
- deterministic tests using events, barriers, queues, fake clocks, or injected hooks to force the risky ordering
- thread stress tests and supported race tooling as supporting evidence, not proof
- process tests under every supported start method when behavior differs

Do not use sleeps as the primary way to force a schedule. State the exact interleaving, missing owner, or absent ordering edge that the test exercises.

## Primary references

- [Python documentation: Coroutines and tasks](https://docs.python.org/3/library/asyncio-task.html)
- [Python documentation: Developing with asyncio](https://docs.python.org/3/library/asyncio-dev.html)
- [Python documentation: Synchronization primitives](https://docs.python.org/3/library/asyncio-sync.html)
- [Python documentation: Queues](https://docs.python.org/3/library/asyncio-queue.html)
- [Python documentation: Event loop](https://docs.python.org/3/library/asyncio-eventloop.html)
- [Python documentation: Threading](https://docs.python.org/3/library/threading.html)
- [Python documentation: Multiprocessing](https://docs.python.org/3/library/multiprocessing.html)
- [Python documentation: Concurrent futures](https://docs.python.org/3/library/concurrent.futures.html)
