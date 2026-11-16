# Use std.Io

Read the [I/O principle](../principles/io.md). Choose the procedure that matches
the work and its progress requirements.

| Need | Playbook |
|---|---|
| Format, transform, or bound byte streams | [Read, write, and format streams](process-streams.md) |
| Collect typed results, run coroutine-style tasks, race a deadline, or synchronize shared state | [Coordinate tasks](coordinate-io-tasks.md) |
| Split CPU work, reduce results, or run a bounded worker pool | [Parallelize independent work](parallelize-work.md) |
| Hand off work, apply backpressure, or compose Go-style or core.async-style stages | [Build a channel pipeline](build-channel-pipeline.md) |
| Serialize commands against private state or ask a service for a reply | [Run an actor](run-actor.md) |

## Choose an Io implementation

1. At application startup, take `init.io` from `main(init: std.process.Init)`.
   Pass it through APIs that perform I/O or schedule work. Pass an allocator
   separately if the operation allocates.
2. For tests, start with `std.testing.io`. Use `Io.Threaded.init_single_threaded`
   for inline execution and launch refusal. Use `Io.failing` to exercise
   supported failure paths.
3. If the application needs configurable limits, construct
   `Io.Threaded.init(gpa, options)` with a thread-safe allocator. Set
   `async_limit` and `concurrent_limit` according to the workload. Account for
   all tasks using that backend when budgeting slots for dependent peers.
4. Keep the backend at a stable address after taking its `io()` handle.
   Finish or cancel and join all tasks before calling `deinit`. Destroy the
   backing allocator after backend teardown.
5. If you are considering `Io.Evented`, check the alias and operation coverage
   in the pinned SDK for the deployment target. Run workload and shutdown
   tests on that backend before adopting it.

Check [backend contracts](../references/io-concurrency.md#backends) before
choosing a policy. Test the work that depends on each contract on the backend
that will run it.
