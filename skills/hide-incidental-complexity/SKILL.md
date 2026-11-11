---
name: hide-incidental-complexity
description: >-
  Use when designing a CLI, API, or workflow, when users or agents must
  stitch together commands, IDs, or shell plumbing to do a routine task, or
  when deciding whether to add a dependency, feature, rewrite, or abstraction.
  Make the normal workflow first-class, reuse what exists, and remove what
  doesn't earn its complexity.
---

# Hide incidental complexity

Users shouldn't need to manufacture UUIDs or reconstruct missing commands with shell plumbing.

> Also if we have to use `jq` to get info out of the database, then we did not build the right commands.

Prefer established libraries and standard-library facilities. Avoid speculative features, unnecessary rewrites, and edits to someone else's vendored code. Discovering work needn't be done is valuable.

## Make the normal workflow first-class

- Make each routine task one obvious command or call.
- If a routine task needs a pipe into `jq`, `grep`, or `awk`, or a hand-built ID, the tool is missing a command. Add it.
- Let users refer to things by names they already know. Generate IDs for them.
- Test the workflow end to end the way a user would type it, not only the functions underneath.

## Reuse and remove

- Before writing a helper, check the standard library, then the project's existing dependencies, then established libraries.
- Don't build for hypothetical users. A feature with no current caller is a cost with no benefit.
- Prefer a targeted fix to a rewrite. A rewrite has to justify everything it touches.
- Don't edit vendored or third-party code in place. Wrap it, configure it, or upstream the fix.
- Delete code, flags, and options that no longer earn their keep.
- Report "this doesn't need doing" as a result, with the reason.

## Anti-patterns

- Docs that teach users a shell pipeline to answer a routine question.
- Requiring users to copy UUIDs between commands.
- A hand-rolled parser, retry loop, or date library when a standard one exists.
- Speculative configuration, plugin systems, or abstraction layers.
- Patching `node_modules/`, `vendor/`, or a copied upstream file.

When this skill shaped your work, name the principle you applied ("hide-incidental-complexity") and the decision it changed. For example: "added a `show --by-name` command instead of documenting a `jq` query".
