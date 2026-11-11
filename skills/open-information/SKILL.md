---
name: open-information
description: >-
  Use when modeling domain data, records, DTOs, or API payloads; when
  defining schemas, types, or validators; or when marking fields optional or
  required. Represent information as open, namespaced attributes, and define
  each attribute's shape apart from which attributes a given context selects.
---

# Open information

Information is sparse, open, accumulative, and carried by names. Classes and fixed product types are poor fits: they bury names, make the aggregate decide meaning, and turn information into rigid concretions.

Optionality isn't a property of data; it depends on context. Define what attributes mean (shape) separately from which ones a given function, endpoint, or message requires or provides (selection).

Source: Rich Hickey, "Effective Programs: 10 Years of Clojure" (Clojure/Conj, 2017) and "Maybe Not" (Clojure/Conj, 2018) for open information; "Maybe Not" for schema apart from selection.

## Open information

- Represent information as associative data (maps of attributes), not bespoke classes per shape.
- Give attributes globally unique, namespace-qualified names (`org.myorg/email`), and attach meaning to the attribute, not the record that holds it.
- Don't let a container own a fact: an email means the same thing in every aggregate it appears in.
- Avoid positional semantics (tuple fields, long positional parameter lists).
- Keep systems open: accept attributes you don't know about, pass them along, and take only what you need.
- When something is absent, leave the key out. Don't fill slots with null or "Maybe" placeholders.
- Use the same plain data model inside the program as on the wire and in storage.
- Reach for a generic library of data functions before writing per-type accessors.

## Schema apart from selection

- Define each attribute's shape once and reuse it everywhere.
- Don't bake optional or required into the aggregate type. The record has no usage context.
- State requirements at the point of use: this function requires `name` and `addr/zip`; that response also provides `id`.
- Make selections deep, so nested requirements don't need a new type per context.
- Avoid context-driven type proliferation (`UserForCreate`, `UserForUpdate`). One schema, many selections.
- Support pipelines that accept partially filled data and return it more filled in.
- Evolve compatibly: requiring less or providing more must not break existing callers. If making an argument optional (wrapping it in Maybe/Option) breaks callers, blame the encoding, not the change.
- Prefer real unions (nullable, `A | B`) over Maybe/Either wrappers when you must model alternatives.

## Anti-patterns

- A new DTO class for every endpoint that differs by one field.
- `Optional<String>` fields that mean "required here, absent there."
- Dropping unknown fields at every hop, so adding a field means redeploying everything.

When this skill shaped your work, name the principle you applied ("open-information") and the decision it changed. For example: "kept one `user` schema and declared per-endpoint required keys instead of three DTOs".
