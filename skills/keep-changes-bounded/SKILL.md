---
name: keep-changes-bounded
description: >-
  Use when planning, committing, branching, or opening a PR, or when a task
  starts to grow beyond its original scope. Keep changes coherent, bounded,
  and reviewable, keep generated output and machine-specific clutter out of
  history, and defer unrelated extensions to follow-up issues.
---

# Keep changes bounded

Use coherent issues, acceptance criteria, sensible commits, and appropriate branches. Keep generated output and machine-specific clutter out of history. Defer unrelated extensions to follow-up issues.

Source: Ken's principle #9, "Keep changes bounded and reviewable."

A reviewer can only judge what they can hold in their head. Bound the change so the review is real.

## Heuristics

- Start from an issue or a written goal with acceptance criteria. If there isn't one, write the criteria down before coding.
- One change, one purpose. If the PR description needs "and also", split it.
- Work on an appropriately named branch, not directly on the default branch, unless the repo's workflow says otherwise.
- Make each commit coherent: it builds, it says what and why, and it doesn't mix refactors with behavior changes.
- Before committing, read `git status` and `git diff --stat`. Every path should be one you meant to change.
- Keep build outputs, caches, lockfile churn you didn't intend, editor files, local paths, and machine-specific config out of history. Use `.gitignore` when appropriate.
- When you notice an unrelated improvement, write it down as a follow-up issue or note and leave it out of this change.
- Prefer several small PRs that each stand alone over one large one, and say how they stack.

## Anti-patterns

- Drive-by reformatting of files the change doesn't otherwise touch.
- Committing `dist/`, `.DS_Store`, generated bindings, or absolute paths from one machine.
- "While I was in there" features added to a bug fix.
- A single commit titled "wip" or "updates" covering several unrelated changes.
- Expanding a scoped ticket because the extension seemed easy.

## Required closing note

When this skill shaped your work, name the principle you applied ("Keep changes bounded and reviewable, #9") and the decision it changed. For example: "moved the logging refactor to a follow-up issue," or "dropped generated files from the commit and added them to `.gitignore`."
