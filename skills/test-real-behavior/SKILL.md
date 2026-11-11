---
name: test-real-behavior
description: >-
  Use when writing, reviewing, or keeping tests, benchmarks, or verification
  procedures, or when deciding whether a fix is done. Tests should check
  meaningful real-world scenarios, and every fix should leave behind
  committed, executable verification that catches the same problem again.
---

# Test real behavior

Tests should correspond to meaningful scenarios. Run examples and integration paths; measure representative workloads under comparable conditions.

> what real-world scenario is that test checking?

Keep verification procedures executable, current, and committed. A fix should improve the project's ability to catch the same problem again.

> Never leave an updated verify skill uncommitted

## Heuristics

- For every test, be able to answer Ken's question: what real-world scenario is it checking? If the answer is "that this function calls that function," rewrite or delete it.
- Assert what a caller, user, or operator can observe: outputs, persisted state, exit codes, messages. Avoid asserting private call order.
- Run the examples and the integration path, not just the unit under change. A passing unit suite with a broken example is a failing change.
- For performance claims, measure a representative workload, compare under the same conditions (machine, data size, warm or cold), and report both numbers.
- When fixing a bug, first write or run something that reproduces it, then show it passes after the fix.
- Turn one-off checks into something rerunnable: a test, a script, a documented command, or an updated verification skill.
- Commit the verification with the fix. An uncommitted verify step is lost the moment the session ends.
- Keep verification current. When behavior changes, update the check in the same change.

## Anti-patterns

- Tests written to raise coverage that no real scenario exercises.
- Mocks so thorough that the test only checks the mock.
- Benchmarks on toy inputs, or comparisons across different conditions.
- "Verified manually" with no recorded command or result.
- Fixing a bug without leaving anything behind that would catch it again.
- Updating a verify skill, script, or checklist and leaving it uncommitted.

When this skill shaped your work, name the principle you applied ("test-real-behavior") and the decision it changed. For example: "replaced a mock-only test with an integration test of the CLI path and committed it with the fix".
