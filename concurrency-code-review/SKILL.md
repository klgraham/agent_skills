---
name: concurrency-code-review
description: Review code for races, missing awaits or joins, unsafe task and thread lifetimes, deadlocks, starvation, cancellation bugs, blocking async work, atomic-ordering mistakes, unbounded concurrency, and shutdown failures. Use for concurrency audits and for changes involving async code, threads, workers, processes, queues, channels, locks, atomics, parallel execution, or shared mutable state. Includes specific guidance for Python, Rust, Go, JavaScript, TypeScript, and Ruby. Do not use for style-only review.
---

# Concurrency code review

Treat concurrency as a correctness proof, not a pattern-matching exercise. A clean abstraction around a race is still wrong. A program that passed once has shown only that one schedule worked.

Review the requested diff or branch. Trace far enough into callers, callbacks, workers, cleanup paths, and shared state to judge the changed behavior. Do not modify code unless the user also asks for fixes.

## Load the relevant language notes

Identify the language, compiler, runtime, and pinned versions before applying language-specific claims.

- For Python, read [references/python.md](references/python.md).
- For Rust, read [references/rust.md](references/rust.md).
- For Go, read [references/go.md](references/go.md).
- For JavaScript or TypeScript, read [references/javascript-typescript.md](references/javascript-typescript.md).
- For Ruby, read [references/ruby.md](references/ruby.md).
- For other languages, use the core review below and verify runtime semantics from authoritative documentation when a finding depends on them.

Do not force Python, JavaScript, Rust, or any other runtime's rules onto a different execution model.

## Set the review boundary

Establish the comparison target from the user's request and repository conventions. Inspect the diff, then follow affected control flow outside the diff when needed. Include generated or vendored code only when the changed behavior depends on it.

Before judging the code, record a compact concurrency map for yourself:

- actors that can run independently, such as tasks, threads, processes, callbacks, interrupt handlers, workers, or remote consumers
- mutable state and resources each actor can reach
- the owner of each task, handle, queue, connection, lock, and allocation
- spawn, suspend, wake, handoff, cancellation, error, and shutdown boundaries
- ordering edges established by joins, awaits, locks, channels, atomics, transactions, or protocol acknowledgements
- capacity limits for tasks, queues, retries, memory, connections, and worker pools

If an important ordering exists only because one operation is "usually faster," there is no ordering guarantee.

## Review task and thread lifetimes

Inspect every changed spawn and asynchronous call site. Each unit of concurrent work needs an intentional owner and terminal path.

Determine:

- who starts it and stores its handle
- who waits for completion or deliberately detaches it
- who observes failure
- who cancels it and whether cancellation is cooperative
- which data and resources must outlive it
- what happens during normal shutdown and partial startup failure

Flag work that is created and discarded when the API returns a future, promise, coroutine, task handle, thread handle, or error-bearing join result. Detached work is acceptable only when the design names an owner, lifetime, failure policy, and shutdown policy.

Check that structured child work cannot outlive the scope whose resources it borrows. Check the inverse too: a parent must not wait forever for a child that depends on a resource still held by the parent.

## Prove shared-state safety

Inventory mutable state reachable by more than one actor. Include globals, static locals, caches, lazy initialization, flags, counters, maps, pools, files, sockets, database rows, reference counts, raw pointers, and state hidden inside third-party clients.

For each shared invariant, answer:

1. Which operations read or write it?
2. Can those operations overlap?
3. What makes a compound operation atomic when it must be?
4. What establishes visibility and ordering between actors?
5. Can an actor suspend, call external code, or be cancelled while the invariant is temporarily broken?

Look for concrete interleavings:

```text
A reads X
B reads X
A derives and writes X'
B derives and writes X''
```

```text
A checks that a resource is free
B checks that the resource is free
A claims it
B claims it
```

Check-then-act, read-modify-write, lazy publication, and "only once" logic need one atomic transition or synchronization that covers the whole invariant. A thread-safe collection does not make a multi-step algorithm using that collection atomic.

Treat every suspension, callback, blocking call, and foreign-function boundary as a point where relevant state may change unless the program proves otherwise.

## Audit synchronization protocols

For every lock, read-write lock, semaphore, condition variable, barrier, channel, queue, transaction, or custom synchronization mechanism, identify the invariant it protects. Verify that every access follows the same protocol.

Check for:

- lock acquisition on all paths and release during errors, panics, exceptions, and cancellation
- inconsistent lock ordering and cycles in the lock graph
- re-entry into non-reentrant code
- callbacks, logging hooks, destructors, allocators, or foreign code invoked while a lock is held
- blocking or slow work inside a critical section
- waits for work that needs a lock or permit held by the waiter
- condition-variable waits that do not recheck the predicate
- semaphore permit leaks, double releases, and limits applied at the wrong scope
- barriers whose participant count can change after failure or cancellation
- channels with no closure protocol, orphaned senders, or consumers that can stop while producers continue

Prefer single ownership, immutable values, message passing, and transactional state changes when they remove shared mutation. Do not recommend a lock until the review identifies the invariant and why simpler ownership cannot express it.

## Check liveness and capacity

Absence of data races does not prove progress.

Search for:

- deadlock through lock cycles, executor exhaustion, nested waits, queue dependencies, or shutdown ordering
- livelock through retries, conflict loops, repeated cancellation, or actors yielding to each other without progress
- starvation caused by unfair locks, biased selection, priority rules, hot producers, or an actor that continually reacquires capacity
- unbounded task creation, thread creation, queues, buffered results, fan-out, retries, or per-key state
- producers that can outrun consumers without backpressure
- timeouts that stop waiting but leave the underlying work running and consuming capacity

Concurrency limits must cover the actual scarce resource. Stacking unrelated pools and semaphores can reduce throughput or deadlock without providing a meaningful bound.

## Check async and event-loop behavior

For runtimes with futures, promises, or coroutines, verify that each operation is awaited, returned to an owner, grouped under structured concurrency, or deliberately detached with explicit supervision.

Check for:

- missing `await` or its runtime equivalent
- an async cleanup operation called without waiting for it
- sequential awaits that contradict the intended dependency graph
- blocking I/O, sleeps, subprocess calls, locks, or CPU-heavy work on an event-loop or cooperative executor thread
- a synchronous wait for work scheduled to the same constrained executor
- assumptions made before a suspension point that are invalid after resumption
- cancellation at a suspension point leaving partial state or leaked resources
- race-losing branches that keep running after a timeout or selection construct returns

Do not demand parallelism merely because work could overlap. It must improve the intended behavior and keep failure, ordering, and capacity understandable.

## Review atomics and lock-free code

Treat atomics, raw shared memory, and unsafe synchronization as high-risk. Do not accept "atomic" as a complete argument.

For each atomic operation, identify:

- the invariant, not just the variable
- the linearization point
- the required modification order
- which write publishes associated non-atomic data
- which read acquires that publication
- why the selected memory order is sufficient on weakly ordered hardware
- whether compare-and-swap failure ordering is legal and sufficient
- whether retry loops tolerate spurious failure and guarantee progress
- whether ABA, counter wraparound, torn composite state, or stale generation numbers matter
- how removed objects are reclaimed while other actors may still hold pointers

`volatile` is not a replacement for atomic access or synchronization. Do not approve custom lock-free code without a defensible memory-model argument and targeted verification.

## Check errors, cancellation, and shutdown

Concurrent errors cross boundaries differently from ordinary call-stack errors. Verify that the parent observes child failures and does not report success while required work failed.

Define the intended policy for sibling failure:

- fail fast or collect results
- cancel siblings or let them finish
- accept partial results or roll them back
- report one failure or aggregate several

Trace cancellation at every blocking or suspension point. Check cleanup for idempotence because cancellation, retry, and shutdown can overlap.

Walk shutdown in order. Stop intake, signal producers or children, drain or abandon queued work by policy, close channels, wait for owned work, then destroy shared resources. Flag any sequence that frees resources before all possible users have stopped.

## Include distributed races when they are in scope

Threads are not required for a race. Concurrent requests, workers, database clients, and message consumers can violate the same invariant.

Check transaction isolation, compare-and-set behavior, unique constraints, lease expiry, duplicate delivery, out-of-order messages, retry idempotence, and partial side effects. A process-local mutex does not protect state shared across processes or hosts.

## Verify findings

Use the strongest practical evidence available:

- source-level happens-before or interleaving argument
- focused test that coordinates the risky schedule instead of relying on sleeps
- existing stress, race-detector, model-checking, sanitizer, or interpreter support
- compiler and static-analysis diagnostics
- authoritative runtime or library documentation for semantic claims

Do not make a finding from a suspicious token alone. Trace whether the path is reachable and whether another guarantee already prevents the failure. State when a concern remains unverified because the necessary runtime, target, or workload is unavailable.

Do not "fix" a flaky concurrency test by adding sleeps, large timeouts, or retries. Use barriers, latches, injected schedulers, fake clocks, hooks, or repeated schedule exploration when the codebase supports them.

## Report findings first

Report only actionable concurrency findings. Order them by severity:

- P0: immediate catastrophic impact, such as exploitable memory corruption or certain broad data loss
- P1: likely production race, deadlock, lost work, use-after-free, silent failure, or unbounded exhaustion
- P2: real bug under a narrower schedule, workload, shutdown path, or failure condition
- P3: low-impact correctness issue or a test and observability gap that materially hides concurrency risk

Each finding must include:

1. a short title with severity
2. the narrowest useful file and line location
3. the violated invariant
4. a concrete failing interleaving, missing ordering edge, or lifetime sequence
5. user-visible or operational impact
6. the smallest sound remedy, preferring simpler ownership over more synchronization
7. verification performed or still needed

Avoid style comments, generic warnings, and speculative lists. Do not inflate severity because concurrency is involved.

If there are no findings, say so directly. Then name any material coverage gaps or residual risks, such as an unavailable target, missing stress tests, unsafe code not reached by the diff, or a runtime behavior you could not verify.

## Approval bar

Approve only when all changed concurrent work has an owner and terminal path, shared invariants have defensible ordering, failure and cancellation cannot silently lose required work, liveness has no reachable cycle, capacity is bounded where inputs are unbounded, shutdown respects lifetimes, and any unsafe or atomic code has a memory-model argument.
