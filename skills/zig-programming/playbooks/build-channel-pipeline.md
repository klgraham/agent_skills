# Build a channel pipeline

Use a channel for communicating sequential processes (CSP), where tasks
coordinate by exchanging values. `Io.Queue(T)` supports buffered handoff and
rendezvous. Read the [I/O principle](../principles/io.md) and the
[queue contract](../references/io-coordination.md#queues).

## Hand off values

1. Set the capacity at each handoff. Pass a zero-length backing buffer when
   the sender must rendezvous with a receiver. Use a bounded buffer when a
   stage should absorb short bursts before slowing the producer.
2. Start participants with `concurrent` when progress depends on a peer.
   Register cancellation cleanup before the next launch. Include the sink in
   the progress plan when the last stage can block on output.
3. Send with `putOne(io, item)` and receive with `getOne(io)`. Transfer
   ownership on a successful send. The sender retains the item on error.
   Keep borrowed payload storage alive through consumption. For batch sends,
   track progress with `put` or send one item at a time. A failed `putAll`
   leaves the sender without a count of the items already enqueued.
4. Give each queue a close owner. Close when the last sender has finished.
   Drain until `error.Closed`. Treat `error.Canceled` as an abort.
5. On abort, stop and join the participants before releasing backing storage.
   Close and drain any abandoned queues of owning messages and free those
   messages. Use `getOneUncancelable` on the closed queue if cleanup must
   drain it after cancellation. Handle stage failures separately from normal
   end of stream.

## Compose stages

For a Go-style channel handoff or a Clojure `core.async`-style pipeline, give
each stage an ordinary task function. Read one item, transform it, then write
to the next queue. A stage that is the sole sender can defer closing its
output. Observe stage results even when the sink reached end of stream. If a
stage or sink exits before draining its input, stop its upstream producers
before joining them. A producer may still be blocked on that input queue.

For fan-in, wait for every producer before closing their shared output. For
fan-out, workers sharing a queue divide the work. To broadcast, give each
subscriber its own queue and define how to copy or share each payload and what
to do when a subscriber falls behind. When multiple workers can reorder items,
carry sequence numbers and bound any reordering buffer.

## Route events from several inputs

When you control the senders, use one queue of tagged events so a dispatcher
can block on one inbox. When bridging existing queues, use bounded forwarding
tasks and account for messages the forwarders already hold during shutdown.

Use `Io.Select` for task completions. Separate queue operations in
`Io.Select` can consume or publish several values before cancellation reaches
them. Define how to handle every value that may already have been consumed.
If the protocol needs a single choice like Go's `select` or Clojure's
`alts!`, have a coordinator commit at most one channel operation.
[Go language specification](https://go.dev/ref/spec#Select_statements).
[Clojure core.async API](https://clojure.github.io/core.async/clojure.core.async.html#var-alts.21).

## Verify

[channel-pipeline.zig](../examples/channel-pipeline.zig) chains a rendezvous
input to a buffered output. It tests close and drain, empty input, and
refusal to start the source after the transform is live. It also demonstrates
two receives completing in a single `Io.Select`. For owning messages, test
a failed send and cleanup of queued items on abort.
