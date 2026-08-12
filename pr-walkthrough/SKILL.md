---
name: pr-walkthrough
description: Walk a user through a GitHub pull request interactively in architectural chunks, pausing after each chunk, citing exact file and line locations, answering follow-up questions from surrounding code, and ending with copy-paste-ready review comments. Use when the user asks to walk through, explain, or review a PR interactively. Do not use for a one-shot review or a visual HTML walkthrough.
---

# PR Walkthrough

Guide a paced pull-request review in which the user navigates the code while the explanation advances in deliberate chunks.

## Preserve the review boundary

Treat the walkthrough as read-only. Do not edit code, submit a review, post comments, or change the pull request unless the user explicitly asks.

## Establish the exact change

1. Read the PR metadata and capture its base branch, base SHA, head branch, head SHA, title, body, commits, and changed files. Prefer structured output such as:

   ```bash
   gh pr view <number> --json baseRefName,baseRefOid,headRefName,headRefOid,title,body,commits,files,url
   ```

2. Inspect the PR diff and each actual PR commit. Do not assume the default branch is `master`, and do not use a broad local branch diff when the checked-out branch may be behind or ahead of the PR.
3. Read surrounding unchanged code, callers, consumers, tests, configuration, migrations, and documentation where they explain the change.
4. Record the head SHA. If the user later says the PR changed, fetch current metadata and compare the old and new head SHAs. State which earlier concerns were resolved, remain, or are newly introduced.

Use the connected GitHub source when it provides the required metadata and patch context; use `gh` when exact diff, commit, or line-level inspection is needed.

## Plan the walkthrough

Create four to six chunks grouped by architectural responsibility, not file order. A useful sequence is:

1. vocabulary and data types;
2. request or input shape;
3. core control and data flow;
4. integrations and leaf behavior;
5. tests, compatibility, rollout, and documentation.

Adjust the sequence to match the PR. Skip mechanical changes unless they materially affect behavior.

## Present one chunk at a time

For each chunk:

- open with one sentence explaining what the chunk covers and why it matters;
- provide two to four precise `path/to/file.ext:line` or `path/to/file.ext:start-end` citations;
- explain intent, coupling, tradeoffs, and consequences rather than paraphrasing visible code;
- call out a non-obvious risk, invariant, or positive pattern when evidence supports it;
- end with `Say "next" when ready.` and wait.

Do not continue until the user asks to proceed.

## Handle follow-up questions

- Read the surrounding implementation before answering a specific code question.
- Trace concrete scenarios with realistic inputs instead of describing only abstract risk.
- Correct earlier claims explicitly when new evidence changes them.
- For design comparisons, give two or three viable options with tradeoffs, then recommend one and state why.
- After answering, offer to continue the current chunk sequence or investigate further.

## Synthesize the review

When all chunks are complete, or the user asks for a summary, provide copy-paste-ready review comments grouped by file. For each comment include:

- a precise file and line anchor;
- a quote-formatted comment body;
- the concrete scenario in which the issue matters;
- a proportionate suggested change;
- one sentence explaining why it matters.

Order comments by severity within each file. Include an architectural follow-up only when it is consequential and genuinely outside the PR's scope. Offer to turn the comments into `gh pr review` commands, but do not post them without explicit authorization.

If no actionable comments survive inspection, say so and summarize the reviewed coverage and remaining uncertainties.

## Avoid common failures

- Do not list every changed file.
- Do not make concerns that lack a source location.
- Do not continue past a chunk without waiting.
- Do not hide risks inside generic praise.
- Do not compare against an assumed `master` branch.
- Do not infer behavior from the diff without reading relevant surrounding code.
- Do not confuse the interactive chat walkthrough with a self-contained HTML walkthrough.
