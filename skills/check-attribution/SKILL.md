---
name: check-attribution
description: >-
  Use when crediting a claim, limit, requirement, dependency, or opinion to a
  library, tool, system, organization, or person, especially when summarizing
  posts, docs, examples, issues, or other agents' reports. Verify where the
  claim actually comes from before attributing it.
---

# Check attribution

Before you credit a claim, limit, or requirement to a library, system, or person, verify where it actually comes from.

A wrong attribution looks like a fact, and it spreads. It also leads to wrong decisions, like rejecting a tool for a requirement it doesn't have.

## Worked example

This is an illustrative example. A post shows how to use a library, and its example calls AWS Bedrock. A quick summary says "the library requires AWS." That's wrong. Bedrock was only the model provider the example's author chose. The library itself ran locally and supported other providers.

What went wrong: one choice made in the example was credited to the library. What would have caught it:

1. Separating what the example chose (provider, credentials, region) from what the library requires.
2. Checking the primary source: the library's docs, its install instructions, its config options, and its dependency list. A hard AWS requirement would show up there. A pluggable provider interface shows the opposite.
3. Asking whether the claim survives a swapped example. If the same post had used a local model, would anyone say "requires AWS"? If not, the claim belongs to the example, not the library.

## Heuristics

- Split every claim into its subject and its source. "X requires Y" needs evidence about X, not about a demo that uses X.
- Prefer primary sources: official docs, source code, config schemas, package manifests, changelogs, the person's own words. Summaries, blog posts, and other agents' reports are secondary.
- Check dependencies directly. A required dependency appears in the manifest; an optional one appears as an extra, a plugin, or a config choice.
- Separate defaults from requirements. A default provider, port, or region is a choice, not a constraint.
- Separate the person from the material. A quote in someone's document may be theirs, or something they were quoting. A rule in a skill may come from the skill's author, not from the user who installed it.
- Watch for version drift. A limit true in v1 may be gone in v3. Name the version you checked.
- When you can't verify, say so plainly: "the post's example uses Bedrock; I haven't confirmed whether the library requires it."
- Cite what you checked: a link, file path, or command output, so others can re-check.

## Anti-patterns

- "The library needs AWS" because its quickstart used AWS.
- Crediting a requirement to "the API" when it came from one wrapper or SDK.
- Attributing an opinion to a person because it appeared in their repo, thread, or notes.
- Repeating another agent's claim as verified fact.
- Treating a limitation in your own environment as a limitation of the tool.

When this skill shaped your work, name the principle you applied ("check-attribution") and the decision it changed. For example: "corrected 'the library requires AWS' to 'the example uses Bedrock; the library also runs locally with other providers'".
