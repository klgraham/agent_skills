---
name: pure-functions
description: >-
  Use when writing or refactoring logic that mixes computation with I/O,
  clocks, randomness, globals, or mutation, or when code is hard to test.
  Prefer pure functions when useful, as they make testing straightforward.
---

# Pure functions

Prefer pure functions when useful, as they make testing straightforward.

Source: Ken's principle #12, "Pure functions are easy to test."

A pure function returns the same output for the same input and does nothing else. You can test it with a table of inputs and expected outputs, with no setup, mocks, or cleanup.

## Heuristics

- Pass in what the function depends on: the current time, a random seed, configuration, the data read from disk. Don't reach out for them.
- Return new values instead of mutating arguments.
- Test pure functions with plain values and many cases.
- When a test needs heavy mocking, treat that as a sign the logic and the effects are tangled. Extract the logic.
- "When useful" matters. Don't contort simple glue code or performance-critical loops into purity when it adds complexity and no testability.

## Anti-patterns

- Logic that could be pure but can only be tested by standing up a server, database, or CLI.
- Functions that call `now()`, `random()`, or read environment variables deep inside their logic.
- Tests that mock the filesystem, the clock, and the network to check an arithmetic rule.
- Helpers that look pure but mutate a shared cache or an argument.
- Wrapping trivial code in a functional style that hurts readability.

## Related

`values-not-places` covers state as an explicit argument (`(state, input) -> result`), which is the same move at the data layer.

## Required closing note

When this skill shaped your work, name the principle you applied ("Pure functions are easy to test, #12") and the decision it changed. For example: "moved the pricing rule out of the handler into a pure function with a table-driven test," or "passed the clock in instead of calling `Date.now()`."
