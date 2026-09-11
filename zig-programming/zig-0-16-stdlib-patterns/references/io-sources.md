# std.Io source review for Zig 0.16.0

Reviewed on 2026-09-11. The examples in this collection are checked with the
installed compiler reporting `0.16.0`. Tutorials supply use cases; the pinned
library declarations and executed examples decide which APIs this skill teaches.

## Primary contracts

- [Zig 0.16.0 release notes](https://ziglang.org/download/0.16.0/release-notes.html):
  I/O interface, futures, groups, cancellation, synchronization, and backend status.
- [Andrew Kelley's introduction](https://andrewkelley.me/post/zig-new-async-io-text-version.html):
  task lifetime and cancellation motivation. This is an earlier design preview;
  constructor signatures must be checked against the release.
- Installed `std/Io.zig`: Future, Group, Select, Queue, Mutex, Condition, Event,
  cancellation, and async/concurrent contracts.
- Installed `std/Io/Threaded.zig`: limits, inline fallback, and backend lifetime.
- Installed `std/Io/Semaphore.zig`, `std/Io/RwLock.zig`, `std/atomic.zig`, and
  `std/Thread.zig`: synchronization and OS-thread boundaries.
- Installed `std/Io/Reader.zig`, `std/Io/Writer.zig`, and `std/Io/File.zig`:
  stream buffers, formatting, EOF, and flush behavior.

Locate installed sources using `zig env`; do not depend on a maintainer's path.

## Supplied examples reviewed

| Reading | How to use it for this skill |
|---|---|
| [Streams and formatting](https://jkingston.github.io/zig_guide/06-io-streams.html) | Formatting and buffer use cases; replace mixed old filesystem recipes with 0.16.0 Io.File/Dir signatures |
| [Async, concurrency, and performance](https://jkingston.github.io/zig_guide/08-async-concurrency.html) | Topic map; verify queue methods, backend names, and concurrency guarantees |
| [The Io interface](https://www.ziglang.in/learn/standard-library/io-interface/) | Capability injection; absence of an Io parameter is not an enforced ban on side effects |
| [Concurrency overview](https://www.ziglang.in/learn/concurrency/) | Separate task lifecycle from parallel execution |
| [Async, Future, and Group](https://www.ziglang.in/learn/concurrency/async-future-group/) | Inline fallback, progress requirements, and explicit task completion |
| [Cancellation](https://www.ziglang.in/learn/concurrency/cancellation/) | Cooperative points and workers that must not start inline |
| [Select](https://www.ziglang.in/learn/concurrency/select/) | Tagged completions, deadline races, and cleanup of losing tasks |
| [Queues](https://www.ziglang.in/learn/concurrency/queues/) | Bounded capacity, backpressure, and close/drain behavior |
| [Locks](https://www.ziglang.in/learn/concurrency/locks/) | Predicate waits and permits; check release-specific methods |
| [Atomics](https://www.ziglang.in/learn/concurrency/atomics/) | Counters and publication; verify namespace changes before migration |
| [Threads](https://www.ziglang.in/learn/concurrency/threads/) | Raw thread lifetime and when structured task APIs fit |
| [Coming from std.Thread](https://www.ziglang.in/learn/concurrency/coming-from-std-thread/) | Migration choices; task groups are not a textual replacement for counters |
| [Choosing an Io](https://www.ziglang.in/learn/concurrency/choosing-an-io/) | Application-level backend ownership and limits |
| [Batch runner](https://www.ziglang.in/learn/concurrency/batch-runner/) | Bounded workers and scheduling-independent reports; distinguish finite atomic-index batches from streaming queues |
| [daily.dev overview](https://daily.dev/blog/zig-async-io-io-uring-zig-0-16-rethinks-concurrent-programming/) | Context only; do not infer backend readiness or speed from its examples |
| [LearningZig async I/O](https://learningzig.org/lessons/11-async-io) | Future/group introduction; supply cleanup for every early-return path |

The recovered ziglang.in concurrency pages identify their verification compiler
as `0.17.0-dev.2085+5e36170b5`. Their examples are not automatically 0.16.0 recipes.
The [mickeyzzc article](https://blog.mickeyzzc.tech/en/posts/programming/zig-stdlib-io-concurrency/)
returned HTTP 403 and was not reviewed. No API claim here relies on it.

## Corrections retained in the playbooks

- `io.concurrent` requires concurrent progress, not simultaneous execution on
  separate cores. `io.async` can run inline and must remain correct that way.
- Use `Queue.putOne/getOne/close` with `io`, not unverified push/pop recipes.
- Use `Io.Threaded.init_single_threaded` for inline tests. `Io.Blocking` is not
  an exported backend in the pinned installation.
- `Semaphore.waitTimeout` from the newer guide is absent in this 0.16.0 SDK.
- `Select.cancel` must have room for outstanding results before joining.
  `cancelDiscard` instead closes the result queue before joining; only use it
  when discarded result values do not own resources.
- Await/cancel are explicit obligations. Lexical scope alone does not finish
  tasks, and an early `try` can abandon siblings without registered cleanup.
- Readers and writers over memory do not need `Io`. Both regular file streams
  and standard streams use `Io` when creating their 0.16.0 file adapters.
- Evented implementations remain experimental in this release. Their names
  and operation coverage must be checked on the intended target.
