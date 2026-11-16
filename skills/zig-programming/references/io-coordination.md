# Select, queues, locks, atomics, and threads

For procedures, see [Coordinate tasks](../playbooks/coordinate-io-tasks.md) and
[Build a channel pipeline](../playbooks/build-channel-pipeline.md).

## Select

`Io.Select(U)` owns the tasks it starts. Each task publishes its return value
in the associated field of the tagged union. `await()` receives one tagged
result, including any task error carried by that field. `await()` has no
end-of-stream result. `awaitMany` can receive multiple results.

`cancel()` waits for tasks before draining. The result buffer needs room for
every result that has yet to be received or cleanup can deadlock.
`cancelDiscard()` closes the result queue before joining and discards results.
Discarded owning results get no automatic resource cleanup. Calling
`await()` or `awaitMany()` after cancellation is illegal.

## Queues

`Io.Queue(T)` is a thread-safe queue with caller-provided storage. A backing
slice of length zero creates a rendezvous. Closing rejects new puts.
Buffered items remain readable before consumers receive `error.Closed`.

The batch methods `put` and `get` report progress counts. They can return
fewer elements than requested around closure or cancellation. If a batch
call reports an error directly, it transferred zero items. A failed
`putAll` can leave an unspecified prefix enqueued. The single-item methods
`putOne` and `getOne` transfer exactly one item on success.

## Locks and signals

`Io.Mutex.lock` can return `error.Canceled` before acquisition.
`Io.Condition.wait` releases and reacquires its mutex, including on
cancellation. A condition signal carries no stored application state.

`Io.Semaphore.waitTimeout` leaves its permit unconsumed on `error.Timeout`
or `error.Canceled`. An `Io.Event` retains its set state until reset.
Reset requires a protocol in which no waiter still needs the old signal.

## Atomics and threads

`std.atomic.Value(T)` provides memory synchronization. A `.monotonic`
counter can allocate disjoint work indices without publishing other data.
Publication using release and acquire needs a happens-before argument.
Object reclamation and task completion require their own protocols.
Busy-spinning can occupy a backend's only execution thread.

`std.Thread.join` waits for the thread and returns no worker result. A
detached thread can outlive the launching scope. Raw threads have their own
lifecycle, outside the structured cancellation of `Io.Future` and `Io.Group`.

Primary authority: `std/Io.zig`, `std/Io/Semaphore.zig`, `std/Io/RwLock.zig`,
`std/atomic.zig`, and `std/Thread.zig` in the pinned SDK.
