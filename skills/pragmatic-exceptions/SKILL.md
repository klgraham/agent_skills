---
name: pragmatic-exceptions
description: >-
  Use when a programming principle, repo convention, or workflow rule seems
  to conflict with the task at hand, or before enforcing a rule on someone
  else's change. Understand and justify the tradeoff rather than enforce a
  rule regardless of context.
---

# Pragmatic exceptions

Be pragmatic. It is sometimes okay to accept breaking changes for fresh installations, justified unsafe code for performance, and exceptions to normal branch and CI workflows. Understand and justify tradeoffs rather than enforce rules regardless of context.

These exceptions depend on context. The current task, repository, users, and data determine which tradeoff is appropriate.

## Heuristics

- Before applying or enforcing a principle, ask what it protects in this context. If that thing isn't at stake, the rule may not apply.
- Weigh the concrete cost of following the rule against the concrete risk of breaking it. Name both.
- Breaking changes are acceptable when there are no existing installs or data to break. Check who is actually affected.
- Unsafe code is acceptable when it's justified for performance. Useful review questions: is the need measured, is the unsafe code contained, and is the reason written down?
- Branch and CI exceptions are acceptable when the repo's owner has set up that workflow or approved the exception for this task.
- An exception is a decision, not a loophole. Write down the tradeoff where reviewers will see it.
- Exceptions don't widen your authority. An approved exception covers this task only, and merge permission remains task-specific.

## Anti-patterns

- Blocking a change on a rule whose purpose doesn't apply here.
- Taking an exception silently, with no stated tradeoff.
- Treating one approved exception as standing permission.
- Using "pragmatism" to skip verification or review with no stated tradeoff. A justified, recorded branch or CI exception is still allowed.

When this skill shaped your work, name the principle you applied ("pragmatic-exceptions") and the decision it changed. For example: "accepted a breaking config rename because there are no existing installs, and recorded the tradeoff in the PR".
