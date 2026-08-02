# Zig standard for machine-written code

Rules for Zig that minimize the working memory needed to understand, review, and
change a region of code. Make symbols greppable, keep ownership visible, and
give each behavior one home. Follow the hard rules mechanically. When a public
ABI, generated file, wire format, performance constraint, or repository rule
requires a deviation, explain it at the deviation site.

This standard targets Zig 0.16+ as used by this skill collection. Verify
version-sensitive APIs against the repository's compiler and load
`zig-0.16-stdlib-patterns` when the code touches the standard library.

## Contents

1. [Rule levels](#1-rule-levels)
2. [File layout](#2-file-layout)
3. [Constants and vocabulary](#3-constants-and-vocabulary)
4. [Naming and lifecycle pairs](#4-naming-and-lifecycle-pairs)
5. [Functions](#5-functions)
6. [Control flow](#6-control-flow)
7. [Errors](#7-errors)
8. [Ownership and lifetimes](#8-ownership-and-lifetimes)
9. [Types, slices, and data](#9-types-slices-and-data)
10. [Generics and comptime](#10-generics-and-comptime)
11. [Collections and invalidation](#11-collections-and-invalidation)
12. [Concurrency](#12-concurrency)
13. [Comments and repository guidance](#13-comments-and-repository-guidance)
14. [Formatting and build hygiene](#14-formatting-and-build-hygiene)
15. [Pre-delivery checklist](#15-pre-delivery-checklist)
16. [Module skeleton](#16-module-skeleton)
17. [Worked near miss](#17-worked-near-miss)
18. [Adaptation note](#18-adaptation-note)

## 1. Rule levels

Classify a rule before applying it:

- **Hard:** never violate silently. Add a site comment when a higher-priority
  constraint forces an exception.
- **Default:** follow unless the local code shape or measured requirement gives
  a reason not to. Record the reason in the review or change notes.
- **Preference:** follow the repository's established dialect when it is
  coherent. Do not reformat unrelated code to enforce a personal preference.

Hard rules include checked fallible operations, explicit ownership transfer,
valid borrows, correct cleanup, and a passing project verification loop. A
function-length target is a legibility signal, not permission to split a module
into meaningless one-line wrappers.

## 2. File layout

Give each module one clear responsibility. Use this reader-first order:

1. A one- or two-line module comment stating what the file owns and does.
2. Imports, with standard-library imports before project imports.
3. Compile-time constants and derived configuration values.
4. Error sets, enums, tagged unions, and public type aliases.
5. Public structs and their field invariants.
6. Private types and implementation-only tables.
7. Public functions, in the order a caller learns the lifecycle: `init`, the
   primary operations, then `deinit` or `close`.
8. Private helpers in approximate call order.
9. Tests, unless the repository keeps tests in a separate file.

Zig does not require prototypes and permits declarations to be referenced
before their textual definition. Keep the order above anyway: the first screen
should teach the module's vocabulary before the reader meets its logic.

Do not mix CLI argument parsing, storage ownership, wire-format encoding, and
domain decisions in one module merely because Zig makes imports cheap. Give
each concept a home and make adapters obvious at the boundary.

## 3. Constants and vocabulary

- Name every nontrivial literal. Bare `0` and `1` are acceptable only when
  their meaning is obvious; name sizes, limits, protocol values, timeouts, and
  scores.
- Put units in names: `timeout_ms`, `max_payload_bytes`, `retry_count`.
- Compute derived values from named sources instead of repeating the result.
- Define a constant once. A second spelling of the same domain fact is a future
  divergence point.
- Use enums for closed sets and tagged unions for states carrying different
  data. Do not encode a state machine as unrelated booleans when a named state
  would make invalid combinations impossible.
- Keep configuration near the module top. Do not bury a limit in the branch
  that happens to use it.
- Prefer a named domain type over a naked integer when mixing two values with
  different meanings. At minimum, use a descriptive alias or wrapper at a
  public boundary and convert once.

Example:

```zig
const max_entries: usize = 4_096;
const header_bytes: usize = 16;
const max_payload_bytes = max_entries * header_bytes;

const EntryIndex = struct {
    value: u32,
};
```

Do not introduce a wrapper solely to hide a trivially obvious local value. The
name test still applies: a declaration earns its existence by making a domain
concept or invariant easier to find.

## 4. Naming and lifecycle pairs

Use the repository's established Zig dialect consistently. In this collection,
functions use lower camel case and types use title case; fields, locals, and
constants follow the repository's existing naming style. Prefer precise names
over long descriptions.

- Name functions with a verb and object: `parseHeader`, `flushQueue`,
  `recordSample`.
- Start predicates with `is`, `has`, or `can`; avoid negated predicate names
  such as `isNotReady`.
- Use exact lifecycle pairs. `init` pairs with `deinit`; `create` pairs with
  `destroy`; `open` pairs with `close`; `clone` creates an independent owner;
  `take` transfers ownership and leaves a documented empty source.
- Let receiver shape communicate mutation: `*Self` mutates, `*const Self`
  reads, and a by-value receiver is reserved for small copy-safe values.
- Name ownership and borrow roles in APIs and docs: `owned`, `clone`, `take`,
  `view`, `borrowed`, `snapshot`, and `release` should not be interchangeable.
- Keep short names such as `buf`, `len`, `idx`, and `ctx` local to a small
  scope. Use a domain name when a value crosses a helper boundary.
- Do not use `tmp`, `data2`, `thing`, or `doStuff` when the value has a real
  concept.
- Avoid unexplained abbreviations and inconsistent spellings of the same
  symbol. A grep for a concept should find its producers and consumers.

Document public lifecycle contracts with ownership, allocator, borrow duration,
invalidation, failure, and thread-safety behavior. A method name alone cannot
carry those facts.

## 5. Functions

- Give each function one job. If its contract needs several independent
  sentences joined by “and”, look for a decomposition.
- Target roughly 20 lines of logic and treat 60 lines as a hard review trigger.
  Split at a named concept, ownership transition, external call, or error
  boundary—not at arbitrary line counts.
- Keep nesting at depth two or less. Validate preconditions first; let the
  success path stay near the left margin.
- Keep ordinary functions to four meaningful parameters or fewer. Use a
  configuration or request struct when the parameters form a concept. Count
  `comptime` parameters when they materially affect the contract.
- Put the receiver first, then the allocator or context required by the
  operation, then inputs. Return values instead of adding output pointers
  unless an ABI, streaming interface, or measured hot path requires one.
- Classify every function as one of these:
  - **Orchestrator:** sequences named operations and propagates their errors;
    it contains no hidden domain algorithm.
  - **Leaf:** performs one local calculation, predicate, state mutation, or
    accessor operation.
  - **Adapter:** wraps one foreign API and translates its types, errors, or
    ownership convention into the module's vocabulary.
- Do not mix orchestration with a second algorithm in the same function. Move
  the algorithm into a leaf or move the foreign call into an adapter.
- Apply the name test: if the most honest helper name merely paraphrases its
  two-line body and adds no ownership, error, or side-effect boundary, inline
  it. Avoid both giant functions and pointer-chasing ravioli code.
- Prefer explicit concrete types at public boundaries. Use `anytype` only when
  the generic contract is obvious at the call site, normally for a writer,
  allocator-compatible adapter, or small compile-time abstraction.

## 6. Control flow

- Use guard clauses and early returns for invalid input, unsupported states,
  and errors. Keep the normal path unindented.
- Use `try` for transparent error propagation. Use `catch` only to classify an
  error, provide a documented fallback, perform local cleanup, or translate at
  a boundary.
- Do not use `catch unreachable` for input, I/O, allocation, or other external
  failure. Use it only after a local invariant proves the error impossible and
  state that proof next to the expression.
- Keep `switch` exhaustive for closed enums and tagged unions. Do not hide a
  newly added variant behind `else` unless the type is intentionally open and
  the fallback behavior is documented.
- Make loop progress and termination visible. Every loop over external or
  mutable data needs an evident bound, a termination condition, or a comment
  identifying an intentional event pump.
- Extract a loop body once it contains a second conceptual phase or roughly
  ten lines of logic. The call site should say what each iteration means.
- Avoid recursion for unbounded or attacker-controlled input. Use a bounded
  explicit worklist when it makes stack use and termination easier to prove.
- Keep side effects out of conditions and complex expressions. Zig's loop
  continuation clause may update a simple index, but do not hide resource
  acquisition, mutation, or error handling inside it.
- Use `inline for`, `comptime` branching, and metaprogrammed dispatch only
  when they express a compile-time fact. Do not use them to make runtime
  control flow harder to read.

## 7. Errors

- Make fallible public operations return an error union. Use a named error set
  when the failure vocabulary is part of the API; avoid widening a public
  contract to `anyerror` without a reason.
- Keep normal absence distinct from failure: use `?T` for “not present”, an
  error for “could not determine or perform”, and a tagged result when both
  carry meaningful information.
- Let lower layers return evidence; let the boundary decide whether to log,
  retry, translate, or present the error. Do not log and discard an error in a
  reusable library helper.
- Keep error translations at adapters. Do not make every inner helper know the
  vocabulary of an unrelated subsystem.
- Check every fallible call. A `catch {}` that discards an error is a hard
  violation unless the ignored failure is explicitly the intended behavior.
- Place `errdefer` immediately after an allocation or partial initialization
  that must be rolled back. Remove or narrow it when ownership transfers.
- Keep error paths short enough to inspect locally. If a partial initializer
  needs several independent rollback obligations, give each owner a clear
  cleanup responsibility rather than relying on a distant shared label.
- Use `unreachable` only for a proved internal invariant, never as a substitute
  for validating external data.

## 8. Ownership and lifetimes

Zig structs are copyable, so ownership is a convention enforced by API shape,
review, and tests. Make that convention visible.

- Give every allocation one deallocation authority. Record the allocator in
  the owner or pass the same allocator explicitly to its `deinit` method.
- Pair `init`/`deinit` and `create`/`destroy` with matching ownership semantics.
  State whether cleanup is exactly-once or idempotent; do not accidentally mix
  the two models.
- Prefer `*Self` for mutating owner methods. Do not copy an owning struct into a
  parameter, return value, container, closure, or thread context unless the
  operation is explicitly a move, clone, or ownership transfer.
- Use `clone` for a deep independent copy and `take` for a move that leaves a
  valid empty source. Do not hide a transfer behind a getter or ordinary
  assignment.
- Schedule `defer` immediately after successful acquisition:

  ```zig
  const file = try directory.openFile(path, .{});
  defer file.close();
  ```

- Use `errdefer` for resources acquired during a fallible initializer until the
  final owner takes responsibility:

  ```zig
  const name = try allocator.dupe(u8, input_name);
  errdefer allocator.free(name);

  const body = try allocator.dupe(u8, input_body);
  errdefer allocator.free(body);
  ```

- Treat arena reset and deinit as lifetime boundaries. Do not return a slice,
  pointer, iterator, or view backed by storage that is about to be reset.
- Document borrowed values with their owner and invalidating operations. Prefer
  indices, offsets, handles, or owned copies over long-lived interior pointers.
- Never use a different allocator instance to free an allocation. Do not route
  library allocations through `page_allocator` or `c_allocator` when the
  caller supplied an allocator unless the boundary requires it and says so.
- Avoid `@constCast` as a convenience. If a legacy API requires it for a
  method that only needs mutable allocator access, prove the method does not
  mutate logical state and comment at the cast site.

## 9. Types, slices, and data

- Use `[]const T` for read-only borrows and `[]T` only when the callee writes.
  Do not accept mutable slices merely because a downstream helper happens to
  accept them.
- Group struct fields by ownership, identity, mutable state, and derived data.
  Comment invariants that connect fields, such as `len <= items.len` or an
  offset/length pair staying inside a backing buffer.
- Initialize every local at its declaration when a meaningful initial value is
  available. Declare it at the smallest scope and immediately before first
  use; do not place an uninitialized placeholder above guards.
- Keep pointer depth shallow. Bind intermediate owners or views to named locals
  instead of writing a chain that hides several lifetime questions.
- Use tagged unions when variants have different payloads. Handle each variant
  at one decision site and keep mutation outside the variant mapping when
  possible.
- Keep `extern`, `packed`, alignment, and sentinel representations at explicit
  ABI or wire-format boundaries. Do not spread representation constraints into
  ordinary domain code.
- Make state transitions named. A method such as `start`, `finish`, or
  `close` should make the legal before and after states clear, preferably with
  an enum or a small owner type rather than a collection of flags.
- Expose only the fields callers must construct or inspect. Keep invariants and
  storage layout private when a public method can preserve them more reliably.

## 10. Generics and comptime

- Prefer a concrete implementation until a second real use demonstrates the
  abstraction. Generality is not legibility when it hides the data shape.
- Put generic constraints near the generic declaration. A caller should be
  able to learn what `T` must provide without following several `@hasDecl`
  branches.
- Use `comptime` to express facts known before runtime: type selection, fixed
  dimensions, generated tables, and compile-time validation. Keep runtime
  policy in ordinary functions.
- Give generated types and tables stable names. Add `comptime` assertions for
  size, alignment, field count, or protocol constants when the representation
  matters.
- Keep `@Type`, `@field`, `@hasDecl`, `@call`, and reflection-heavy code behind
  a named adapter or generator. Explain the invariant that the metaprogram
  enforces.
- Do not use `anytype` or reflection to avoid choosing an ownership or error
  contract. Generic syntax cannot replace documentation.

## 11. Collections and invalidation

Treat every view into a collection as borrowed until proven otherwise.

- Do not hold an item pointer, slice, iterator, or `.items` view across an
  operation that may reallocate, rehash, sort, compact, swap-remove, replace,
  reset, or deinitialize the collection.
- Reacquire the view after mutation. Use an index or stable handle when a
  mutation must happen between lookup and use.
- Treat `append`, `insert`, `resize`, map insertion/removal, sorting, and arena
  reset as invalidation barriers. A prior `reserve` is a local capacity proof,
  not a general lifetime guarantee.
- Centralize nontrivial indexing and offset arithmetic in accessors. A question
  such as “what mutates this storage?” should have a small, greppable set of
  answers.
- Keep nested owner cleanup explicit. Deinitialize inner collections before the
  outer collection, and use `errdefer` while construction is partial.
- Do not assume map iteration order. Sort or otherwise stabilize output when
  tests, snapshots, logs, or wire formats require deterministic order.
- Use the collection initializer and deinitializer required by the pinned Zig
  version. For this repository's Zig 0.16 guidance, confirm the `.empty`,
  allocator, and `deinit` forms in `zig-0.16-stdlib-patterns` rather than
  copying an older version's pattern.

## 12. Concurrency

Give each shared mutable object exactly one named protocol:

| Protocol | Required proof |
|---|---|
| Thread-confined | Only the owning thread reads, mutates, and destroys it. |
| Message-transferred | Ownership moves through the queue; the sender stops using it. |
| Mutex-protected | Every access, cleanup, and callback follows the same lock. |
| Atomic | Field-level ordering and a reclamation scheme are documented. |
| Immutable snapshot | Readers retain a version that cannot be reclaimed early. |

- Synchronize lifecycle, not just fields: cancel, unregister callbacks, join
  workers, and only then free captured state.
- Treat a mutable global as shared state unless its thread-local or startup-only
  lifetime is proven.
- Do not use `volatile` as a synchronization protocol.
- Do not claim that atomics solve reclamation. Lock-free pointers still need
  epochs, hazard pointers, reference counting, or an append-only lifetime.
- Keep channel or queue ownership transfers visible at the send and receive
  sites. Avoid passing a borrowed pointer to work that can outlive the borrow.

## 13. Comments and repository guidance

- Document public declarations with behavior, ownership, allocator, borrow
  duration, invalidation, errors, and thread safety as applicable. Do not merely
  restate the signature.
- Comment why, not what. The expression tells the reader what it does; the
  comment should explain an invariant, compatibility constraint, algorithmic
  choice, or non-obvious lifetime.
- Put invariant assertions beside the mutation they protect. An assertion is a
  machine-checked comment in debug builds.
- Do not leave commented-out code. Version control retains it.
- Keep repository-level agent guidance short and evidence-based. Include build,
  test, lint, boundaries, and intentional decisions that a stranger could not
  infer; do not invent a path map that the tree already reveals.
- Do not change `AGENTS.md`, test policy, or unrelated conventions as part of a
  scoped code edit unless the task authorizes repository-level changes.

## 14. Formatting and build hygiene

- Run `zig fmt` on touched Zig files and review the resulting diff. Let the
  formatter settle whitespace instead of inventing a competing style.
- Keep one statement and one declaration per line when the formatter permits;
  use multiline literals for meaningful structure rather than dense expressions.
- Prefer compiler errors over clever suppression. Fix unused locals, incorrect
  mutability, narrowing casts, and unreachable error paths at their source.
- Run the project's normal build and test step in Debug or its diagnostic mode.
  Use `std.testing.allocator` for tests that own allocations and inspect leak
  failures rather than switching to an allocator that hides them.
- Run focused tests directly with `zig test path/to/touched_test.zig` when the
  build graph may skip a module or produce a false-green result.
- Test error paths, empty inputs, boundary values, ownership cleanup, and
  invalidation behavior—not only the happy path.
- Stabilize serialized or snapshot output before comparing it in tests.
- Finish with `git diff --check` and a review of only the intended paths.

## 15. Pre-delivery checklist

Before presenting Zig code, verify:

1. Does every module and public type have one clear responsibility?
2. Does the file-top vocabulary expose constants, errors, states, and owners?
3. Is every nontrivial literal named with units where needed?
4. Are names precise, consistent, and ownership-aware?
5. Does every function have one altitude and one job?
6. Are nesting, parameter count, and helper boundaries still legible?
7. Does every fallible call propagate, classify, or intentionally handle its
   error?
8. Are `?T`, error unions, and tagged results used for distinct meanings?
9. Does every allocation have one allocator and one cleanup authority?
10. Are `defer` and `errdefer` placed immediately at acquisition boundaries?
11. Does any borrow cross append, rehash, sort, reset, move, or deinit?
12. Are owner copies, `clone`, `take`, and empty states explicit?
13. Are `anytype`, reflection, `comptime`, casts, and `unreachable` justified?
14. Are state-mutating leaves asserting or preserving their invariants?
15. Are public errors, ownership, lifetimes, invalidation, and thread rules
    documented?
16. Are loops bounded or explicitly marked as intentional event pumps?
17. Are runtime branches separated from compile-time generation?
18. Did `zig fmt`, focused tests, the required build/test step, and
    `git diff --check` run successfully?
19. Did any required check remain unchecked or any rule require a documented
    deviation?
20. Does the final diff give the next change a single obvious place to land?

## 16. Module skeleton

This small owner demonstrates the intended altitude split. The public API names
the lifecycle and keeps allocation visible; the initializer owns every partial
allocation until the returned value takes responsibility.

```zig
// document.zig: owns a named document and its two allocator-backed buffers.
const std = @import("std");

const DocumentError = error{ EmptyName, OutOfMemory };

pub const Document = struct {
    allocator: std.mem.Allocator,
    name: []u8,
    body: []u8,

    /// Owns copies of `name` and `body` allocated with `allocator`.
    /// The caller must call `deinit` exactly once on success.
    pub fn init(
        allocator: std.mem.Allocator,
        name: []const u8,
        body: []const u8,
    ) DocumentError!Document {
        if (name.len == 0) return error.EmptyName;

        const owned_name = try allocator.dupe(u8, name);
        errdefer allocator.free(owned_name);

        const owned_body = try allocator.dupe(u8, body);
        errdefer allocator.free(owned_body);

        return .{
            .allocator = allocator,
            .name = owned_name,
            .body = owned_body,
        };
    }

    /// Releases both owned buffers. Invalidates the document's slices.
    pub fn deinit(self: *Document) void {
        self.allocator.free(self.body);
        self.allocator.free(self.name);
    }

    /// Replaces the body only after the replacement is fully owned.
    pub fn replaceBody(self: *Document, body: []const u8) DocumentError!void {
        const replacement = try self.allocator.dupe(u8, body);
        const previous = self.body;
        self.body = replacement;
        self.allocator.free(previous);
    }
};

test "document owns and releases its buffers" {
    var document = try Document.init(std.testing.allocator, "title", "body");
    defer document.deinit();

    try std.testing.expectEqualStrings("title", document.name);
    try document.replaceBody("new body");
    try std.testing.expectEqualStrings("new body", document.body);
}
```

The named error set earns its place by exposing the domain's `EmptyName` rule
and the allocator's `OutOfMemory` failure at the public boundary. The important
structure is the allocation/rollback/transfer sequence and the single `deinit`
authority.

## 17. Worked near miss

Machine-written Zig often looks short while placing several concepts in one
function. This version duplicates mutation and turns a mapping into branches:

```zig
const Cell = enum { empty, coin, gem };

pub fn consume(board: *Board, position: Position) u32 {
    var cell: Cell = undefined;
    if (!board.contains(position)) return 0;

    cell = board.cells[board.index(position)];
    if (cell == .coin) {
        board.cells[board.index(position)] = .empty;
        board.score += 1;
        return 1;
    }
    if (cell == .gem) {
        board.cells[board.index(position)] = .empty;
        board.score += 10;
        return 10;
    }
    return 0;
}
```

The tells are:

1. The cell-clearing mutation is pasted twice. A future side effect can land in
   one branch and not the other.
2. Cell-to-score is data encoded as control flow. The mapping should have one
   leaf, so adding a new collectible changes one place.
3. Validation, lookup, eligibility, scoring, and mutation are interleaved.
4. `cell` is declared before the guard and initialized with `undefined` even
   though its first valid value is known later.
5. The index calculation is repeated, making the storage convention harder to
   change safely.

A clearer decomposition preserves the simple return contract:

```zig
fn cellScore(cell: Cell) u32 {
    return switch (cell) {
        .coin => 1,
        .gem => 10,
        .empty => 0,
    };
}

fn consumeCell(board: *Board, position: Position, score: u32) void {
    board.setCell(position, .empty);
    board.score += score;
}

pub fn consume(board: *Board, position: Position) u32 {
    if (!board.contains(position)) return 0;

    const cell = board.cellAt(position);
    const score = cellScore(cell);
    if (score == 0) return 0;

    consumeCell(board, position, score);
    return score;
}
```

If the public signature must distinguish an invalid position from an empty
cell, change it to a named error union and validate at the boundary. If the
signature is frozen, keep the compatibility behavior and document the
deviation above the declaration; do not let the frozen boundary excuse
duplicated mutation or unclear ownership inside the module.

## 18. Adaptation note

This standard follows the same machine-legibility premise as the linked
`write-legible-c` skill: teach the module vocabulary early, give each concept a
single grep-able home, separate orchestration from leaves and adapters, and
finish with a mechanical checklist. It deliberately replaces C-specific
rules—headers and prototypes, status enums, macros, pointer nullability, and
`goto` cleanup—with Zig-native rules for error unions, slices, allocator
ownership, `defer`/`errdefer`, comptime, and invalidation barriers.

Source inspiration: <https://github.com/7etsuo/write-legible-c/tree/main/plugins/write-legible-c/skills/write-legible-c>
