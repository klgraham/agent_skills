# JavaScript and TypeScript concurrency review notes

Identify the host before reviewing the code. Browser JavaScript, Node.js, Deno, Bun, edge runtimes, Electron, service workers, and embedded engines have different event loops, APIs, worker models, and shutdown rules. For TypeScript, also inspect the compiler version, target, module mode, runtime, transpiler, and lint configuration.

TypeScript uses JavaScript's runtime concurrency model. Its types do not create synchronization, cancellation, runtime immutability, or ownership. Review the emitted behavior, not only the declared types.

## Promise ownership and error propagation

An `async` function returns a promise immediately. Trace each promise to an `await`, `return`, combinator, queue, supervisor, or explicit detached-work policy.

Check:

- missing `await` or `return` that lets the caller finish before required work
- a promise created in a callback whose return value the caller ignores
- an async callback passed to `forEach`, an event listener, timer, constructor callback, or API typed to return `void`
- `map` or another collection operation producing `Promise[]` that no code joins
- `await array.forEach(...)`, which does not wait for the callback promises
- rejection handlers attached too late or only on some branches
- `try` and `catch` that surround a promise creation but not its awaited rejection
- a `new Promise` executor declared `async`, since the constructor ignores the executor's returned promise
- promise constructors that never settle on an error, cancellation, or early-return path
- async iterators and generators that are abandoned without the cleanup their `return` or `finally` path performs
- async resource disposal or `finally` logic that races with an unawaited returned promise

`Promise.all`, `Promise.race`, `Promise.any`, and timeout wrappers settle their result according to their contract. They do not cancel the underlying operations. Trace losing or failed branches and verify that they stop, finish harmlessly, or remain owned.

A leading `void` can document that a promise is intentionally ignored and can silence lint rules. It does not observe rejection or provide cancellation, cleanup, or shutdown ownership.

## Event-loop ordering and reentrancy

Single-threaded JavaScript still has logical races. State read before `await` may be stale when execution resumes. A later request can finish first and overwrite newer state.

Build the actual ordering from the host's queues and callbacks. Distinguish promise jobs or microtasks, timers, I/O callbacks, rendering steps, `process.nextTick`, `setImmediate`, and framework schedulers when the distinction affects correctness.

Check:

- assumptions that `setTimeout(fn, 0)` runs before or after a promise continuation
- recursive microtasks or `process.nextTick` callbacks that starve timers and I/O
- event emitters or user callbacks that run synchronously and re-enter partially updated state
- multiple listeners that mutate shared state while depending on registration order
- stale closures, captured mutable variables, and component or request state used after its owner is gone
- fake-timer tests that advance timers without flushing the relevant microtask or I/O queues

Do not turn a queue-order detail into a finding unless it matters on the pinned host and version.

## Cancellation, timeouts, and cleanup

JavaScript promises have no universal cancellation operation. `AbortController` works only when the callee accepts the signal and responds to it.

Verify:

- the signal reaches every operation that must stop
- already-aborted signals are handled before work starts
- abort listeners are removed or registered with one-shot behavior
- cancellation rejects or resolves with the contract callers expect
- partial side effects and buffers are safe if abort arrives between steps
- a timeout does not merely stop waiting while work continues to consume sockets, workers, or permits
- cleanup itself is awaited when it is asynchronous
- shutdown stops intake, aborts or drains owned work, and waits before destroying resources

In browser and UI code, check response ordering, navigation, component disposal, event-listener removal, and work that updates state after its view or request has been replaced.

## Node.js and server runtimes

Inspect synchronous and CPU-heavy work on the event-loop thread. Include synchronous filesystem, child-process, compression, crypto, large JSON, regular expressions with unbounded worst cases, and native add-ons. Async syntax does not move computation off the event loop.

Also check:

- saturation of the host worker pool by slow file, DNS, crypto, compression, or native tasks
- request-scoped state stored in module globals
- `AsyncLocalStorage` used as if it serialized access rather than propagated context
- context loss across callback APIs, custom thenables, event emitters, or native boundaries
- streams whose producers ignore backpressure or whose error and close paths disagree
- server close logic that stops accepting connections but fails to drain owned requests, workers, or sockets
- process-level concurrency such as cluster workers and job consumers that bypasses in-process locks

## Workers and shared memory

For Web Workers, Node worker threads, worklets, and embedded workers, trace worker construction, startup failure, message ports, errors, termination, and resource ownership.

Verify:

- whether data is cloned, transferred, or shared
- whether transferring an `ArrayBuffer` detaches a buffer still used by the sender
- whether every `MessagePort` is closed and every required response has an owner
- whether termination can cut off a required write or leave a promise pending
- whether `SharedArrayBuffer`, `Atomics`, native memory, or WebAssembly memory has a defensible synchronization protocol
- whether a worker pool is bounded and reuses workers rather than spawning one per unbounded input

Ordinary module state is not automatically shared between workers or processes. Conversely, native add-ons and explicit shared buffers may introduce real parallel memory access even when most application code is event-loop based.

## TypeScript-specific checks

Inspect the real `tsconfig`, runtime types, and lint rules. Do not assume strict mode or promise-aware linting is enabled.

Check:

- `Promise<void>` or `() => void` contracts that let callers discard meaningful completion or failure
- async functions assigned to callbacks whose declared return type is `void`
- union types such as `T | Promise<T>` that leave ownership unclear
- `any`, unsafe assertions, or inaccurate declaration files hiding promises, abort signals, thread affinity, or resource lifetime
- `readonly`, `private`, and branded state treated as runtime synchronization
- thenables accepted as `PromiseLike` whose scheduling or cancellation differs from native promises
- explicit resource management with `using` or `await using`, especially return paths that start another promise while disposal is awaiting

When the project uses typescript-eslint, inspect rules such as `no-floating-promises` and `no-misused-promises`. Their absence can explain a missed bug, but it is not itself a correctness finding. Their presence also does not prove every promise is owned.

## Verification

Use the repository's existing tests and host version. Prefer controlled deferred promises, barriers over message channels, abortable test operations, and assertions on settlement and cleanup. Avoid sleep-based ordering tests.

When useful, run the configured type checker and promise-aware linter. Test unhandled rejections, worker startup failure, abort-before-start, abort-during-work, stream backpressure, shutdown with live work, and out-of-order responses. Stress tests support an interleaving argument but do not replace one.

## Primary references

- [ECMAScript specification, Promise objects](https://tc39.es/ecma262/multipage/control-abstraction-objects.html#sec-promise-objects)
- [Node.js, do not block the event loop or worker pool](https://nodejs.org/learn/asynchronous-work/dont-block-the-event-loop)
- [Node.js worker threads](https://nodejs.org/api/worker_threads.html)
- [Node.js AbortController](https://nodejs.org/api/globals.html#class-abortcontroller)
- [TypeScript, await using declarations](https://www.typescriptlang.org/docs/handbook/variable-declarations.html#await-using-declarations)
- [typescript-eslint, no-floating-promises](https://typescript-eslint.io/rules/no-floating-promises/)


