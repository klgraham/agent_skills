# Parallelize independent work

Read the [I/O principle](../principles/io.md). Establish a sequential baseline
and check which inputs and outputs can be separated before arranging workers.

## Split a finite CPU batch

1. Partition immutable input into a bounded number of chunks. Give each task
   disjoint output or its own partial result and scratch storage. Make allocator
   sharing consistent with its threading contract.
2. Use `io.async` for a few typed results when the same algorithm can execute
   inline. Use `Io.Group.async` with disjoint result slots for many chunks.
   Arrange cancellation cleanup before the next fallible operation.
3. If the caller needs to reject a backend with insufficient concurrent
   capacity, use the fallible `concurrent` form. Measure hardware overlap on
   the target backend. Check long CPU loops for cooperative cancellation.
4. Await before reading shared output slots. Reduce the results in a fixed
   order where the API promises deterministic results. For floating-point
   reductions, define how chunking affects rounding.

[parallel-reduction.zig](../examples/parallel-reduction.zig) counts matches
in two chunks. One chunk runs as a task and the caller computes the other.
The tests compare threaded and inline results and cover empty input.

## Run a bounded worker pool

1. Set a worker budget. For finite work, distribute disjoint ranges or allocate
   indices from a shared counter with a documented ordering. For streaming
   work, choose a bounded [queue](build-channel-pipeline.md).
2. Keep job storage and results outside the group. Defer `group.cancel(io)`
   before launching workers. Use `Group.concurrent` when workers wait on a
   producer or another worker.
3. Store each job's result or domain error explicitly. `Group.await` waits
   for the group and can report cancellation of the waiter. Inspect the
   result slots separately.
4. For a queue-fed pool, close input after the last producer finishes. Await
   the group before inspecting results. Preserve input order with job indices
   if the API promises it.

[batch-runner.zig](../examples/batch-runner.zig) uses three workers, a two-item
queue, and ordered outcomes. It tests refused launches before any worker starts
and after one worker has started.

## Verify

Compare with a sequential result and test uneven chunks, failure, and
shutdown. Measure across representative input sizes and worker counts before
claiming a speedup. Record the backend, CPU count, throughput, and peak memory.
