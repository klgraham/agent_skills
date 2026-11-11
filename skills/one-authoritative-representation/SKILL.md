---
name: one-authoritative-representation
description: >-
  Use when adding or changing a schema, type, config key, constant, parser,
  validator, or data store, or when the same concept appears in more than one
  place. Give each concept one authoritative representation and derive the
  rest from it.
---

# One authoritative representation

Avoid duplicate schema definitions, competing canonical stores, and repeated parsing or validation. Use meaningful types and small abstractions that clarify the domain and improve maintainability.

When a concept has two definitions, they drift, and a reader can't tell which one wins.

## Heuristics

- Before adding a definition, search for an existing one: the same field names, the same enum values, the same regex, the same table.
- Pick one canonical source and derive the rest from it: generate types from the schema, or the schema from the types, but don't hand-maintain both.
- Have one canonical store per kind of data; avoid competing canonical stores.
- Parse and validate at the boundary once, then pass the parsed, typed value inward. Inner code shouldn't re-parse strings or re-check what the boundary guaranteed.
- Name domain concepts with meaningful types (`ZigVersion`, `SkillName`) rather than passing raw strings everywhere, when the type removes real ambiguity.
- Keep abstractions small. An abstraction earns its place by making the domain clearer, not by hiding the duplication behind another layer.
- When you find duplicates, consolidate in the same change if it's small. Otherwise, file the follow-up and say which copy is authoritative for now.

## Anti-patterns

- The same constant pinned in a schema, a test, a README, and a UI string, edited by hand.
- Two stores that both claim to be the source of truth.
- A validator at the API edge, another in the service, and a third in the database, each with slightly different rules.
- Copy-pasting a type into a second package "to avoid a dependency".
- Wrapper types that add a name but no meaning.

When this skill shaped your work, name the principle you applied ("one-authoritative-representation") and the decision it changed. For example: "imported the version constant from the schema instead of redefining it in the store".
