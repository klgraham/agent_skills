# Go concurrency review notes

Read `go.mod`, toolchain directives, build tags, and deployment configuration before applying version-specific rules. The loop-variable model changed in Go 1.22, timer channels changed in Go 1.23, and `sync.WaitGroup.Go` was added in Go 1.25. Review the semantics selected by the repository, not merely those of the installed compiler.

Go makes concurrency cheap, not self-managing. Every goroutine still needs an owner, a stop condition, failure handling, and a reason it cannot block forever.

## Goroutine ownership and failure

Inspect every `go` statement, `WaitGroup.Go`, worker-pool submission, callback that starts work, server background loop, and goroutine started by a dependency wrapper.

Check:

- who waits for completion and who cancels the goroutine
- whether every send, receive, lock, condition wait, timer wait, and I/O call has an eventual unblock path
- whether a goroutine captures request data, buffers, locks, or objects that its parent later reuses or closes
- whether the parent returns while required work is still running
- whether startup failure leaves earlier goroutines live
- whether a goroutine's error reaches its owner instead of being logged or discarded
- whether a panic can cross the intended boundary, since a parent cannot recover a panic from another goroutine
- whether shutdown stops intake, signals children, waits for owned work, and only then closes shared resources

A `sync.WaitGroup` waits for completion. It does not propagate errors, cancel siblings, or recover panics. If the project needs those semantics, verify the surrounding protocol or structured group type.

For `Add` and `Done`, the positive `Add` that registers new work must occur before a zero counter can be observed by `Wait`, normally before the `go` statement. Check all early returns and panics for a matching `Done`. Do not copy a `WaitGroup` after first use or reuse it for a new batch until every prior `Wait` has returned.

For Go 1.25 and later, inspect `WaitGroup.Go` under its documented contract. The function passed to `Go` must not panic. Do not recommend this method to a module targeting an older Go language version.

## Channels and `select`

Identify the owner and closure protocol for every channel. A channel communicates values and establishes specific ordering edges. It does not own objects reachable through the values after the receive.

Check:

- a sender mutating a map, slice backing array, pointer target, or object after sending it
- multiple senders that can race to close the same channel
- sending on or closing an already closed channel
- receives that ignore the `ok` result and confuse a closed channel's zero value with real data
- nil channels that block forever, including a channel left nil on an error path
- nil channel cases used intentionally to disable a `select` branch but never re-enabled
- unbuffered ordering arguments incorrectly applied to buffered channels
- fan-in code that closes its output before every producer has stopped sending
- a consumer that exits on cancellation while producers remain blocked sending
- a producer that cannot stop because it sends before selecting on cancellation
- `default` cases that create a busy loop or bypass backpressure
- assumptions that `select` provides priority, fairness, or stable choice among ready cases

Closing a channel can broadcast completion and establish ordering for receivers that observe the close. It does not cancel arbitrary work or wait for goroutines to exit.

Inspect range loops that start goroutines or store closures. For modules using pre-1.22 loop semantics, loop variables may be shared across iterations unless captured explicitly. Newer semantics do not fix pointers to other reused variables or mutable values captured by the closure.

## Shared memory and the Go memory model

For every value accessed by several goroutines, identify the channel operation, lock, atomic operation, `Once`, condition, or other documented event that creates the needed happens-before edge.

Flag:

- ordinary concurrent reads and writes to a map
- concurrent `append`, reslicing, or element mutation through aliases to the same slice backing array
- unsynchronized lazy initialization, publication flags, and double-checked locking
- busy-wait loops on ordinary booleans or pointers
- assumptions that goroutine exit makes its writes visible without a join or synchronization event
- copying interfaces, strings, slices, maps, or structs concurrently with mutation of their multiword representation
- ownership comments that the code does not enforce

The race-free guarantee does not rescue a program that already has a data race. Use synchronization to make the program race-free instead of reasoning from outcomes seen on one architecture.

## Locks and `sync` types

Check every type containing `sync.Mutex`, `sync.RWMutex`, `sync.Once`, `sync.Cond`, `sync.Map`, `sync.Pool`, `sync.WaitGroup`, or a typed atomic value.

Verify:

- the value is not copied after first use, including through value receivers, struct returns, assignments, or container elements
- every protected field is accessed under the same lock protocol
- deferred unlocks run on all error and panic paths
- no callback, logger, channel operation, or slow I/O under a lock can block on code that needs that lock
- lock ordering is consistent across call paths
- code does not attempt to re-enter a `Mutex`
- `RWMutex` code does not upgrade a read lock to a write lock, downgrade a write lock, or recursively take read locks while a writer may be waiting
- failed `TryLock` or `TryRLock` is not treated as a synchronization event
- `Cond.Wait` occurs in a loop that rechecks the predicate

For `sync.Once`, check reentrancy and failure. Calling `Do` recursively on the same `Once` deadlocks. If the function panics, that `Once` is still considered done, so later calls do not retry initialization.

`sync.Map` is specialized. Its individual operations are safe, but `Range` is not a consistent snapshot and multi-step invariants still need coordination. `sync.Pool` holds temporary values that may disappear at any time; it is not durable storage or a bounded resource pool.

## Atomics, unsafe code, and cgo

Go atomics are sequentially consistent under the Go memory model. That does not make a multi-field invariant atomic.

Check:

- an atomic flag publishing associated non-atomic state without a clear protocol
- mixed atomic and ordinary access to the same variable
- check-then-act spread across separate atomic operations when one compare-and-swap is required
- ABA, counter wraparound, stale generations, and unsafe pointer reclamation
- copying typed atomic values after first use
- alignment and lifetime across `unsafe.Pointer`, memory-mapped data, shared memory, and cgo
- C code or callbacks accessing Go-owned memory under a different synchronization contract

Prefer locks or channels when they express the invariant more clearly. Do not approve custom lock-free code because the individual loads and stores use `sync/atomic`.

## Context, cancellation, and time

Trace `context.Context` from the operation owner to every child that must stop. Cancellation is cooperative. A goroutine that never selects on `Done`, returns from blocking I/O, or checks an API-specific signal remains live.

Check:

- every `CancelFunc` is called on all control-flow paths, even when a deadline will eventually fire
- derived contexts do not outlive the operation that owns them
- cancellation causes are preserved when callers rely on them
- `context.WithoutCancel` or `context.Background` does not accidentally detach required work
- contexts are passed explicitly rather than stored in long-lived structs or replaced with nil
- context values carry request-scoped metadata rather than synchronization or optional parameters
- timeouts stop the underlying work, not merely the caller's wait

Inspect timers and tickers under the pinned Go version. Verify `Stop` and `Reset` behavior, channel draining assumptions, and shutdown of ticker loops. Avoid copying a drain recipe written for a different timer implementation. A timer firing concurrently with cancellation must have a defined winner and cleanup path.

## Resource and server lifetimes

Trace goroutines that own sockets, response bodies, database rows, transactions, subprocess pipes, watchers, and server listeners.

Check that every terminal path closes or transfers each resource, that pooled connections are not held by leaked goroutines, and that server shutdown waits for the work the application considers owned. Inspect hijacked connections, background flushers, and dependency-managed goroutines separately because a high-level shutdown method may not own them.

Bound worker pools, queues, retries, per-key goroutines, and fan-out. A semaphore that limits only active calls still permits an unbounded number of goroutines to wait for permits.

## Verification

Use the repository's pinned toolchain and normal build tags. Prefer:

- `go test -race` for focused packages and integration paths that execute the suspect code
- a race-enabled binary under a representative workload when tests miss the path
- `go vet` checks such as copied locks and lost cancellation
- deterministic tests coordinated with channels, barriers, fake clocks, or injected hooks
- tests with both `GOMAXPROCS=1` and multiple processors when scheduling assumptions matter
- goroutine, block, and mutex profiles for leaks and liveness problems
- repeated or stress runs as supporting evidence, not proof

The race detector sees only executed paths and supports a limited set of platforms. A clean run does not prove the code race-free. Do not replace a failing concurrency test with sleeps or scheduler hints.

## Primary references

- [The Go memory model](https://go.dev/ref/mem)
- [Go data race detector](https://go.dev/doc/articles/race_detector)
- [sync package](https://pkg.go.dev/sync)
- [sync/atomic package](https://pkg.go.dev/sync/atomic)
- [context package](https://pkg.go.dev/context)
- [Go language specification, channel types](https://go.dev/ref/spec#Channel_types)
- [Go language specification, select statements](https://go.dev/ref/spec#Select_statements)


