# Run an actor with std.Io

Use an actor when a long-lived task must own mutable state and apply commands
one at a time. Read the [I/O principle](../principles/io.md) and the
[queue handoff and shutdown procedure](build-channel-pipeline.md#hand-off-values).

1. Define a tagged union for commands and choose a capacity for the mailbox.
   Keep mutable state inside the receiver. Give clients a way to send messages
   without giving them access to that state.
2. Start the receiver with `io.concurrent` before accepting sends. Have its
   owner register cancellation cleanup and retain the task result. Keep
   mailbox storage alive through completion.
3. Handle one command at a time. Send results through a reply channel or a
   shared response queue with request IDs. A one-slot reply queue can hold
   a reply while the client is doing other work. Keep the reply storage alive
   until the actor has finished with it, including when the client cancels.
4. Define what a successful send acknowledges. It can acknowledge admission to
   the mailbox. Use an explicit reply when the client needs confirmation
   that a command ran. Define who releases a request or reply on abandonment.
5. For graceful shutdown, stop admitting work, close the mailbox, let the actor
   drain it, and await the receiver. For abort, cancel and join, dispose of
   pending messages, and resolve any waiting clients. Use external supervision
   if the service needs restart or failure routing.

Keep the actor able to receive while clients are working. A blocking call
from an actor to a peer can deadlock if the peer needs to send back into a full
mailbox. Use buffered replies, or split a command into an outgoing request and
a later reply message when the actor must keep processing. Review the wait
dependencies before introducing calls between actors.

[actor.zig](../examples/actor.zig) stores a running peak behind a bounded
mailbox and answers a snapshot request. Its parent closes the mailbox and
joins before reading the buffered reply. Test mailbox saturation and
abandoned requests when adding clients whose lifetimes differ from the actor's.
