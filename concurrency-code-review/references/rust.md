# Rust concurrency review notes

Apply these notes only after identifying the Rust version, async runtime, enabled features, and target platforms in the repository.

Rust's type system prevents many memory-safety failures and data races in safe code. It does not prevent logical races, deadlocks, starvation, lost wakeups caused by a flawed protocol, blocking an async executor, cancellation bugs, or leaks caused by detached work. `unsafe` code and incorrect `unsafe impl Send` or `unsafe impl Sync` can invalidate the compiler's guarantees.

## Threads and ownership

Inspect every `std::thread::spawn`, scoped thread, thread pool submission, Rayon operation, and foreign thread callback.

Check:

- whether every required thread is joined and its panic result is handled
- whether dropping a join handle detaches work that the caller assumes has finished
- whether scoped threads truly end before borrowed data leaves scope
- whether `Arc` is mistaken for synchronization rather than shared ownership
- whether `Rc`, `RefCell`, raw pointers, interior mutability, or foreign handles cross threads through unsafe code
- whether thread-local state is incorrectly treated as process-global or vice versa

Audit all manual `Send` and `Sync` implementations and types containing `UnsafeCell`, raw pointers, FFI handles, custom allocators, or non-thread-safe foreign objects. The proof belongs in the implementation, not in the marker trait alone.

## Futures and runtimes

Calling an `async fn` creates a future. It does not run to completion until an executor polls it. Trace every changed future to an `.await`, return value, stream consumer, join set, task group, or intentional spawn.

For Tokio, async-std, smol, embassy, custom executors, and runtime bridges, verify the actual library version. Check:

- dropped or ignored `Future` values and `JoinHandle`s
- spawned task errors that no owner awaits or records
- select or race branches whose losing futures are cancelled, detached, or not cancellation-safe
- values borrowed or locks held across `.await`
- `std::sync` blocking locks held while awaiting or contended on an executor thread
- blocking file, network, FFI, subprocess, or CPU work on executor workers
- `spawn_blocking` or equivalent work whose cancellation semantics differ from async tasks
- nested runtimes and synchronous `block_on` calls inside a runtime
- local tasks that depend on a particular thread but are moved through an unsafe boundary
- streams or channels that never close because a sender remains alive

An async-aware mutex permits holding its guard across `.await`; that does not make a large critical section wise. Verify that the awaited operation belongs inside the invariant and cannot wait on code that needs the same lock.

## Locks, poisoning, and RAII

RAII usually releases guards during ordinary unwinding. Still check:

- guard lifetimes that extend farther than the source layout suggests
- explicit `mem::forget`, leaked guards, or cycles that prevent drop
- panic behavior and whether poisoned state is recovered, rejected, or silently ignored
- `parking_lot` or other lock semantics that differ from `std::sync`
- lock ordering across methods and trait callbacks
- destructors or logging invoked while a guard is live

Do not rely on mutex poisoning for memory safety or invariant repair. It is advisory and runtime-specific.

## Atomics and unsafe memory

Review each `Ordering` as part of a publication protocol. A common shape is a release operation that publishes prior writes and an acquire operation that observes them, but do not prescribe that shape when the algorithm requires something else.

Flag:

- `Relaxed` used for a flag that also publishes non-atomic data
- mismatched compare-exchange success and failure orderings
- atomic fields that protect only themselves while a larger invariant is non-atomic
- mixed atomic and non-atomic access to the same location
- pointer reclamation without a sound epoch, hazard-pointer, ownership, or quiescence scheme
- ABA-sensitive pointer or generation updates
- references that outlive storage after unsafe lifetime extension, pinning mistakes, or detached work

Inspect FFI contracts for which side owns memory, which threads may call back, and whether foreign synchronization establishes the ordering Rust code assumes.

## Verification

Use the repository's existing checks first. When available and appropriate, consider:

- Loom or another model checker for a small synchronization protocol
- Miri for unsafe-code and data-race diagnostics within its supported model
- ThreadSanitizer on supported nightly toolchains and targets
- deterministic tests using barriers, channels, or injected schedulers
- stress tests as supporting evidence, not proof

Do not introduce a new tool dependency merely to complete a review unless the user asks or the repository already accepts it.

## Primary references

- [The Rust Programming Language, concurrency](https://doc.rust-lang.org/book/ch16-00-concurrency.html)
- [The Rust Programming Language, async and await](https://doc.rust-lang.org/book/ch17-00-async-await.html)
- [Rust standard library Mutex](https://doc.rust-lang.org/std/sync/struct.Mutex.html)
- [Rust reference, await expressions](https://doc.rust-lang.org/reference/expressions/await-expr.html)


