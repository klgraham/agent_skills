---
name: zig-memory-safety-review
description: Use when auditing Zig memory safety and ownership.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [zig, memory-safety, ownership, lifetimes, concurrency, static-analysis, code-review]
    category: software-development
    related_skills: [zig, zig-data-oriented-programming, zig-mmap-project-template]
---

# Zig Memory-Safety Review

## Overview

Zig does not statically enforce affine ownership, borrow lifetimes, temporal safety, or data-race freedom. Audit these properties by combining explicit project conventions, a mechanical risk inventory, symbol and call-path tracing, and runtime verification.

This skill is an analyzer workflow, not a theorem prover. The bundled scanner identifies locations requiring review; every reported issue must be verified against the actual ownership contract and control flow before being presented as a defect.

## When to Use

Use this skill when:

- reviewing a Zig owner type with `init` / `deinit` methods;
- investigating a leak, double free, use-after-free, stale slice, or invalidated pointer;
- reviewing allocator, arena, collection, C ABI, callback, or thread-lifecycle code;
- establishing project-wide memory-safety conventions;
- auditing a PR that changes storage, ownership, borrowing, or concurrency;
- preparing Zig code for fuzzing, production, or hostile inputs.

Do not use it as a substitute for compiling, testing, fuzzing, or understanding the source. Do not report scanner output verbatim as confirmed findings.

## Safety Model

Review five properties separately. Passing one does not imply the others.

| Property | Required evidence |
|---|---|
| Temporal safety | Every dereference occurs while the allocation/object generation is live. |
| Use-after-free prevention | Cleanup invalidates all reachable access paths, or stale paths are validated before use. |
| Single-owner enforcement | Exactly one live value has deallocation authority for each owned resource. |
| Borrow lifetime validity | Every pointer/slice/view is bounded by an owner, generation, epoch, lock, or lexical scope that outlives it. |
| Data-race freedom | Every shared mutable location has one synchronization or ownership protocol followed by all accesses. |

Also audit spatial safety, initialization, allocator pairing, and error-path cleanup because failures there often masquerade as lifetime bugs.

## Project Conventions

### 1. Classify Every Field and Return Value

Each pointer-like field, slice, container, handle, iterator, and returned view must have one role:

- **owned**: this value is responsible for cleanup;
- **borrowed**: another owner must outlive it;
- **shared immutable**: multiple readers, no mutation during the borrow;
- **shared synchronized**: all access follows a named lock/atomic protocol;
- **stable handle**: an ID is validated against owner state or a generation;
- **static**: storage has program lifetime.

Use names and doc comments that state the role: `OwnedBytes`, `BorrowedView`, `take`, `clone`, `view`, `release`, `deinit`. Avoid APIs where ownership depends on undocumented caller knowledge.

For public APIs, document:

1. who allocates;
2. who deallocates;
3. which allocator performs deallocation;
4. how long returned borrows remain valid;
5. which operations invalidate them;
6. whether the API is thread-safe.

### 2. Give Each Resource One Deallocation Authority

An owning type should normally:

- store or otherwise identify the allocator that created its allocations;
- expose `init`/`create` and `deinit`/`destroy` pairs;
- receive `*Self` in mutating and cleanup methods;
- be passed by pointer after initialization rather than casually by value;
- expose `clone` only when it performs a true deep copy;
- expose `take` or `moveFrom` only when it leaves the source in a documented empty state;
- never hide ownership transfer behind a getter or ordinary-looking assignment.

Zig structs are copyable. Treat owner copies as forbidden by convention. Search for assignments, parameter passing, returns, collection insertion, and closure/context capture involving owner types. A byte-for-byte copy duplicates deallocation authority even when only one copy was intended to survive.

Prefer an explicit empty/live state when ownership transfer is required. `take(self: *Self)` should return the previous owner and replace `self.*` with a valid empty value. `undefined` may improve diagnostics but is not an ownership proof and does not invalidate aliases.

### 3. Make Lifetimes Structural

Prefer designs where invalid lifetimes are difficult to express:

- Stack borrows remain within the lexical scope of the owner.
- Request/query temporaries come from an arena destroyed after all consumers finish.
- Long-lived data uses database- or subsystem-scoped storage.
- Thread work items own their payload or borrow only until a mandatory `join`.
- Iterators and views document mutation invalidation.
- C callbacks receive a context whose owner remains alive until unregister/close completes.

Avoid storing a borrowed pointer in a longer-lived struct unless the owner relationship is structurally visible and enforced by the API.

### 4. Prefer Handles Over Long-Lived Interior Pointers

Pointers and slices into movable storage are invalidated by operations such as collection growth, compaction, replacement, arena reset, owner move, and deinitialization. Prefer:

- dense indices for stable, append-only arrays;
- byte offsets for serialized or memory-mapped data;
- opaque IDs at public boundaries;
- generational handles for reusable slots;
- immutable snapshots for concurrent readers.

A generational handle contains at least `{ index, generation }`. Dereference checks that the slot is occupied and its current generation matches. Increment the generation before a freed slot is reused. Define overflow behavior rather than silently wrapping into an old generation.

Indices alone are insufficient when deletion and reuse are possible.

### 5. Establish Pointer-Invalidation Barriers

For every pointer, slice, iterator, or `.items` view derived from a container, identify all operations that can reallocate or rearrange that container. Common invalidators include:

- `append`, `appendSlice`, `insert`, `resize`;
- capacity changes and `realloc`;
- hash-map insertion, removal, and rehash;
- sort, compaction, swap-remove, and replacement;
- arena reset/deinit;
- freeing or moving the owner.

Conventions:

- Never hold an interior pointer across a possible invalidating operation.
- Reacquire the pointer after mutation.
- Use indices if mutation must occur between lookup and use.
- Reserve sufficient capacity only as a local proof with an explicit bound; do not treat capacity reservation as an undocumented lifetime guarantee.
- Do not build self-referential structs whose fields point into other fields unless the containing object has stable storage and cannot be copied or moved by convention.

### 6. Make Cleanup a State Transition

`deinit` should have a clear contract:

- **exactly once**: double deinit is a caller bug and should fail loudly in development; or
- **idempotent**: the object tracks an empty/dead state and repeated cleanup is harmless.

Do not accidentally mix the two models. Cleanup order must be the reverse of dependency order. Parent storage must outlive child cleanup that reads it.

Every fallible partial initializer needs `errdefer` for resources not yet transferred into the final owner. After transfer into a container or result, remove or scope the temporary cleanup so there is still exactly one cleanup path.

### 7. Use Allocators as Lifetime Domains

Assign allocator roles explicitly:

- persistent allocator for long-lived owner state;
- arena or fixed-buffer allocator for bounded-phase temporaries;
- debug/testing allocator for diagnostics;
- C allocator only at a documented ABI boundary.

Never free with a different allocator instance than the one used to allocate. Do not route library allocations through `page_allocator` or `c_allocator` when the caller supplied an allocator unless the boundary requires it and documents the rule.

Arena allocation prevents individual double frees, but does not validate borrows after reset/deinit. Arena reset is a lifetime boundary and must be reviewed like a bulk free.

### 8. Define a Concurrency Ownership Protocol

Every mutable object reachable from multiple threads must use exactly one documented protocol:

- **thread confined**: only the owning thread accesses it;
- **message transferred**: ownership moves through a channel/queue and the sender stops accessing it;
- **mutex protected**: every access, including cleanup and callbacks, holds the same lock;
- **atomic**: each field has a documented memory-ordering and reclamation argument;
- **immutable snapshot**: writers publish a new version; readers retain a version that cannot be reclaimed early.

Lifecycle synchronization matters as much as field synchronization:

- signal cancellation before cleanup;
- join workers before freeing captured/context data;
- unregister callbacks and wait for in-flight callbacks before destruction;
- ensure the allocator is safe for every thread that uses or frees its allocations;
- never rely on `volatile` for synchronization;
- treat a mutable global as shared state unless proven thread-local or startup-only.

Atomics do not by themselves solve memory reclamation. Lock-free pointers require a reclamation scheme such as epochs, hazard pointers, reference counting, or database-lifetime append-only storage.

## Analyzer Workflow

### Phase 0: Establish Scope and Baseline

1. Read `build.zig`, `build.zig.zon`, repository instructions, and the relevant owner/storage modules.
2. Run `git status` and identify whether the review covers the whole tree or a diff.
3. Determine the Zig version from project configuration or `zig version`.
4. Run the existing Debug tests before drawing conclusions.
5. Record which tests actually execute; a vacuous build step is not evidence.

### Phase 1: Mechanical Risk Inventory

Set `ZMS_SKILL_DIR` to this skill's installed directory, then run the bundled scanner with prioritized output first. This keeps the workflow independent of any particular agent or skill installation path:

```bash
export ZMS_SKILL_DIR=/path/to/zig-memory-safety-review
python3 "$ZMS_SKILL_DIR/scripts/zig_memory_safety_scan.py" . --min-severity medium
```

For the full machine-readable inventory:

```bash
python3 "$ZMS_SKILL_DIR/scripts/zig_memory_safety_scan.py" . --format json
```

Lower `--min-severity` to `low` or `inventory` when building the ownership ledger. The summary always counts all candidates even when detailed output is filtered.

The scanner inventories:

- unsafe pointer conversions and casts;
- many-item/C pointers and `allowzero`;
- pointer/slice fields and borrowed-return surfaces;
- allocations, frees, destroys, and deinitializers;
- container operations that may invalidate pointers;
- arena reset/deinit boundaries;
- mutable globals, thread creation, locks, and atomics;
- by-value `deinit` receivers and explicit `undefined` use.

Scanner results are candidates. A cast at a carefully checked FFI boundary may be correct; an innocent-looking owner copy may be dangerous and remain invisible to regex analysis.

### Phase 2: Build an Ownership Ledger

For each owning type, create a compact ledger:

| Type/resource | Created by | Owner | Borrow surfaces | Invalidators | Cleanup | Thread protocol |
|---|---|---|---|---|---|---|

Trace definitions and all usages. Do not infer a type’s semantics from its name alone. Locate:

- constructors and clone/take functions;
- every return, assignment, collection insertion, and parameter crossing;
- all `deinit`, `destroy`, `free`, reset, replacement, and close paths;
- all functions returning pointers/slices into the object;
- all mutations that may reallocate or reorder storage;
- all thread/callback boundaries that capture the object.

### Phase 3: Check Invariants by Property

#### Temporal safety and use-after-free

For every dereference, identify the live owner and the event that ends validity. Check cleanup, arena reset, slot reuse, callback unregister, worker shutdown, and collection mutation. Look for stale aliases surviving any of these events.

#### Single ownership

For each cleanup authority, search for copies and transfers. Confirm that success and every error path leave exactly one owner. Pay special attention to `try container.append(owner)`, because a pre-insertion temporary and post-insertion element have different cleanup responsibilities.

#### Borrow validity

Trace each returned or stored pointer/slice back to storage. List invalidating operations and confirm no caller can retain the borrow across them. Do not accept “normally called immediately” as an invariant unless the API makes it unavoidable.

#### Data-race freedom

Identify thread entry functions, queues, callbacks, mutable globals, shared allocators, locks, and atomics. For each shared field, prove that all reads, writes, and destruction follow the same protocol. Review lock ordering and early returns for unlock correctness.

### Phase 4: Exercise Failure and Invalidation Paths

At minimum:

1. Run tests with a debug/testing allocator.
2. Inject allocation failures into multi-allocation constructors and mutation paths.
3. Test double cleanup according to the type’s contract.
4. Test stale handles after delete/reuse.
5. Test a borrow across every documented invalidator; safe APIs should prevent it structurally or detect it.
6. Stress collection growth so reallocations actually occur.
7. Stress shutdown while work/callbacks are active.
8. Run fuzzing or sanitizer/race tooling where supported by the selected Zig compiler/backend and platform.

Never claim sanitizer coverage without showing the executed command and result.

### Phase 5: Report Source-Grounded Findings

Order findings by severity. Each confirmed finding must include:

- `path:line`;
- the owner and borrowed/aliased value involved;
- the invalidating event or competing access;
- the reachable execution path;
- the consequence: UAF, double free, stale read, leak, race, or contract ambiguity;
- a minimal repair that strengthens the invariant;
- a regression test that would fail before the repair.

Use this format:

```markdown
## Critical / High
- [ZMS-001] `src/foo.zig:42` — concise title
  - Ownership path: ...
  - Invalidator/race: ...
  - Why reachable: ...
  - Fix: ...
  - Test: ...

## Medium / Low
...

## Verified non-findings
- Candidate at `path:line` is safe because ...

## Unproven contracts
- Information needed to complete the proof ...
```

Explicitly refute important scanner false positives. This prevents heuristic output from becoming folklore.

## Severity Guide

- **Critical**: attacker-controllable memory corruption, concurrent reclamation, or reliably exploitable UAF.
- **High**: reachable UAF, double free, invalid free, unsynchronized shared mutation, or stale pointer write.
- **Medium**: plausible lifetime/ownership defect requiring a specific failure or mutation sequence; ambiguous public ownership contract with dangerous callers.
- **Low**: localized resource leak, missing diagnostic invalidation, or convention violation without demonstrated corruption.
- **Inventory**: risky mechanism requiring review but not itself a defect.

## What Mechanical Analysis Can and Cannot Prove

A scanner can reliably locate syntax and suspicious combinations. It cannot generally prove:

- that two pointers alias;
- that an owner value was semantically copied;
- that a callback outlives its context;
- that a reserve operation covers every future mutation;
- that every call site respects an undocumented lifetime;
- that a mutex consistently protects a field across modules;
- that an atomic reclamation protocol is sound.

Therefore use the scanner to reduce search cost, then use agent reasoning to trace symbols and callers. If a finding cannot be tied to a reachable path, label it as a risk or unproven contract rather than a bug.

## Common Pitfalls

1. **Treating a clean leak check as temporal-safety proof.** Leak detection does not prove absence of UAF, aliasing, or races.
2. **Assuming assignment moves an owner.** Zig assignment copies; the source remains usable.
3. **Using `self.* = undefined` as invalidation proof.** Existing aliases and copies remain valid-looking.
4. **Assuming an arena makes borrows safe.** It only groups deallocation; reset/deinit invalidates everything at once.
5. **Treating `const` as Rust shared borrowing.** Another alias may still mutate the same storage.
6. **Keeping `.items` pointers across append.** Reallocation may invalidate them.
7. **Using indices without generations after deletion.** Reused slots can make stale indices point at new objects.
8. **Calling an atomic pointer lock-free without reclamation.** Publication and reclamation are separate problems.
9. **Reporting every cast as a vulnerability.** Verify boundary checks and reachability first.
10. **Auditing only the happy path.** Allocation failure, append failure, callback shutdown, and partial initialization contain many real defects.

## Verification Checklist

- [ ] Existing Debug tests were run and the number/scope of executed tests was checked.
- [ ] Mechanical scan completed and important candidates were source-verified.
- [ ] Owning types have an ownership ledger.
- [ ] Owner copies and transfers were traced.
- [ ] Every borrow has an owner, validity interval, and invalidator list.
- [ ] Interior pointers were checked against collection mutation.
- [ ] Cleanup and partial-initialization paths were checked.
- [ ] Arena reset/deinit was treated as a bulk-free boundary.
- [ ] Thread and callback shutdown precedes captured-data cleanup.
- [ ] Every confirmed finding has a reachable path and regression test.
- [ ] Important false positives are documented as verified non-findings.
- [ ] Final report distinguishes proof, evidence, risk, and unknowns.
