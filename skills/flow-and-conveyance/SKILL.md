---
name: flow-and-conveyance
description: >-
  Use when connecting services, workers, or components; when replacing
  direct calls or callback webs; or when choosing queues, channels,
  buffering, timeouts, or retries. Flow values between parts, and make
  conveyance a first-class, explicit part of the design.
---

# Flow and conveyance

A system is a machine, and its parts should be about flow, not places: transform values, move them, route them, remember them. Keep those jobs separate.

There comes a time in every good program when components must stop communicating directly with one another. Organize the program around independent processes connected by queues or channels.

Source: Rich Hickey, "The Language of the System" (Clojure/Conj, 2012), for flowing values between services; "Clojure core.async: Communicating Sequential Processes using Channels" (Strange Loop, 2013), for conveyance.

## Heuristics

- Give each component one job: transform, move or route, or record.
- Put queues or channels between producers and consumers so neither depends on the other's identity or availability.
- Send values over the wire. When a value is too big or must be remembered, pass a stable name for an immutable value, not a mutable location.
- Give every remote call a timeout, and make every operation that may be retried idempotent.
- Treat membership, capacity, and capability as dynamic; don't hard-wire who talks to whom.
- Spot the machine-like parts inside your programs too, and give them the same flow-oriented treatment.
- Choose buffering on purpose: unbuffered for rendezvous, fixed-size for asynchrony with backpressure. Never unbounded.
- Use promises or futures only for one-off handoffs; they can't model an enduring relationship.
- Let channels be many-to-many, and pass them around so the wiring is explicit, visible, and changeable at runtime.
- Keep wiring code separate from logic code, so you can see where data goes.
- Model timeouts and choice as channel operations: wait on any one of several reads, writes, or a timeout (Clojure: `alts!`, `timeout`).
- Use lightweight processes (go blocks, green threads) instead of a real thread per connection when there are many.

## Anti-patterns

- A graph of stateful services triggering effects on each other, which Hickey calls "the revenge of objects."
- Unbounded in-memory queues.
- Retries on non-idempotent operations.

When this skill shaped your work, name the principle you applied ("flow-and-conveyance") and the decision it changed. For example: "replaced the callback chain with a bounded queue between ingest and indexing".
