---
name: justify-the-change
description: >-
  Use when proposing, implementing, or describing a code, config, or
  documentation change, including commit messages and PR bodies. State why
  the change deserves to exist, what problem it solves, how it improves the
  repo or the user experience, and why the design choices were made.
---

# Justify the change

Explain why the change deserves to exist. What problem does it solve? How does it improve the repo or the user experience? Explain the design choices.

Source: Ken's principle #1, "Justify the change."

A diff shows what changed. Only the author can say why. A change that can't be justified is probably not worth the reviewer's time, or the codebase's.

## Before writing code

- State the problem in one or two sentences, in terms of a user, a failure, or a cost. "Refactor X" is an action, not a problem.
- Name who benefits: the end user, the next maintainer, the operator, or CI.
- If you can't name a concrete improvement, stop and ask whether the change should exist at all. Discovering that work doesn't need doing is a valid result.

## While designing

- For each significant choice (library, data shape, boundary, algorithm), write down the alternative you rejected and why.
- Prefer reasons tied to this repo's constraints over generic best practice. "Matches how `plugins/` already links skills" beats "symlinks are cleaner."
- Separate what you verified from what you assumed. Say which one each reason is.

## When describing the change

- Lead with the problem and the outcome, then the design choices, then the mechanics.
- Keep the justification proportional. A typo fix needs one line; a new subsystem needs a paragraph per decision.
- Point to evidence: the failing test, the issue, the measurement, the user report.
- Call out what the change deliberately does not do, so reviewers don't have to guess whether it was forgotten.

## Anti-patterns

- PR bodies that restate the diff file by file with no "why".
- "Cleanup" or "improvements" with no named problem.
- Justifying a choice by its popularity or by "best practice" alone.
- Retrofitting a reason after the code is written, then hiding the alternatives you never weighed.
- Bundling an unjustified extra into a justified change.

## Required closing note

When this skill shaped your work, name the principle you applied ("Justify the change, #1") and the decision it changed. For example: "dropped the config option because no user problem required it," or "rewrote the PR body to lead with the failing scenario."
