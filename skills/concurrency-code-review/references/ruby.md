# Ruby concurrency review notes

Identify the Ruby implementation and version before reviewing concurrency. CRuby or MRI, JRuby, and TruffleRuby do not make the same parallel-execution guarantees. Also inspect the web server, job runner, database pool, async framework, native extensions, and process model used in production.

The CRuby global VM lock does not make application state thread-safe. Threads can interleave during I/O and other scheduling points. Native extensions may release the lock. Ractors, processes, and other Ruby implementations can execute Ruby work in parallel.

## Thread ownership and failure

Inspect every `Thread.new`, `Thread.start`, `Thread.fork`, pool submission, framework worker, timer thread, and native callback.

Check:

- whether required threads are joined before the process exits or captured resources are closed
- whether `join` or `value` observes the thread's exception
- whether a timeout on `join` leaves the thread running without an owner
- whether `report_on_exception` is mistaken for failure propagation rather than logging
- whether global or per-thread `abort_on_exception` creates surprising process-wide behavior
- whether abrupt `Thread#raise`, `Thread#kill`, or asynchronous interrupts can land while an invariant is broken
- whether `Thread.handle_interrupt` protects allocation and cleanup regions when asynchronous interruption is unavoidable
- whether shutdown wakes sleepers and queue consumers before joining them

Prefer cooperative stop signals and owned queues over asynchronous exceptions. Ruby's own documentation warns that asynchronous interrupts are difficult to use.

## Shared state and synchronization

Do not infer safety from a single Hash, Array, or object method appearing atomic on one Ruby implementation. Multi-step invariants still race, and implementation details can change.

Check:

- shared class variables, class-instance variables, constants containing mutable objects, registries, caches, memoization, and lazy initialization
- check-then-act and read-modify-write sequences around Hashes, Sets, Arrays, and database records
- `Mutex#synchronize` coverage on every access to the protected invariant
- non-reentrant `Mutex` acquisition through callbacks, logging, observers, or nested helpers
- `Monitor` used intentionally when reentrancy is required, rather than mixing lock types
- `ConditionVariable#wait` guarded by a predicate loop
- `Queue#empty?`, `#size`, or similar observations used as a promise that a later pop or push will not block
- `SizedQueue` capacity, shutdown sentinels, blocked producers, and permit-like leaks
- connection or object pools shared across more threads or fibers than their configured capacity

Use `Queue` or `SizedQueue` for owned handoff when it removes shared mutation. A thread-safe queue does not make a protocol around several queues atomic.

## Fibers and schedulers

Fibers provide cooperative concurrency. With a `Fiber::Scheduler`, operations that look ordinary may invoke scheduler hooks and suspend the current fiber.

Verify:

- who owns each scheduled fiber and observes its exception
- whether a blocking operation lacks a scheduler hook and stalls every fiber on the thread
- whether state read before scheduler-mediated I/O remains valid after resumption
- whether mutexes, conditions, queues, and joins follow the pinned Ruby version's fiber-aware behavior
- whether cancellation or timeout can interrupt a resource update or leave a scheduled operation live
- whether scheduler shutdown drains all fibers and pending I/O

`Thread.current[key]` is fiber-local in modern Ruby. `thread_variable_get` and `thread_variable_set` are thread-local across fibers. Flag request IDs, transactions, security context, or connection state stored in the wrong kind of local storage.

## Timeouts and interruption

Review `Timeout.timeout` with care. Depending on the scheduler, it either delegates to the scheduler or arranges for an exception to interrupt the block. The block may be interrupted between any two operations that do not form an atomic update.

Check that timed work has an operation-level timeout where possible, cleanup runs in `ensure`, partial side effects are safe, and the underlying I/O or worker truly stops. A rescued timeout does not prove the resource is reusable.

## Ractors

For `Ractor`, verify the pinned Ruby version because the API and implementation have continued to evolve.

Check:

- whether sent objects are copied, moved, or shareable
- whether `move: true` invalidates aliases still used by the sender
- whether deep freezing via `Ractor.make_shareable` changes behavior expected elsewhere
- whether every incoming and outgoing port has a close and termination policy
- whether `take`, `select`, and child termination propagate failures to an owner
- whether C extensions and external libraries are declared and implemented as Ractor-safe
- whether threads inside a ractor still need locks for shared state within that ractor

Ractor isolation reduces some shared-memory risks. It does not prove message ordering, liveness, shutdown, or the correctness of shareable native state.

## Processes and native boundaries

For `fork`, prefork servers, process pools, and job workers, check database and socket reconnection, inherited file descriptors, buffered output, and locks copied from a multithreaded parent. A process-local mutex does not protect a database row, file, Redis key, or external API used by several workers.

For C extensions, FFI, and Java interop, establish whether calls release the CRuby GVL, invoke Ruby callbacks, require one owning thread, or expose memory to true parallel access. Do not use CRuby behavior to approve code that runs on JRuby or TruffleRuby.

## Verification

Run the repository's tests under the same Ruby implementation, version, server mode, and worker configuration used in production when practical.

Prefer queues, conditions, barriers, and injected hooks that force the unsafe interleaving. Do not use `Thread.pass` or sleep as proof because scheduling remains implementation and OS dependent. Test thread exceptions, partial startup, blocked producers, timeout during mutation, fiber scheduler shutdown, Ractor move semantics, and process-worker duplication when those paths are in scope.

## Primary references

- [Ruby 3.4 Thread](https://docs.ruby-lang.org/en/3.4/Thread.html)
- [Ruby 3.4 Fiber and scheduler](https://ruby-doc.org/3.4/fiber_md.html)
- [Ruby 3.4 Timeout](https://docs.ruby-lang.org/en/3.4/Timeout.html)
- [Ruby 3.4 Ractor](https://ruby-doc.org/3.4/ractor_md.html)
- [Ruby 3.4 extension guidance for Ractors and thread safety](https://ruby-doc.org/3.4/extension_rdoc.html)


