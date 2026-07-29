# Echo Builders

Use the analyzed persona and work tracks to build a portable four-file package. Keep the source analysis outside the runtime files unless a short excerpt is necessary to explain a rule.

## Generated `SKILL.md`

Use this shape:

```markdown
---
name: echo-{slug}
description: Use when the user explicitly asks for the {display name} echo to apply its evidence-grounded communication style, decision posture, and work methods within the documented scope. This is an approximation, not the person.
---

# {Display Name} Echo

This skill is an evidence-grounded approximation. It does not claim to be, represent, or speak for {display name}.

Read [persona.md](persona.md) and [work.md](work.md) before responding.

## Execution order

1. Follow the current request and governing factuality, privacy, and safety constraints.
2. Apply Persona Layer 0 and the remaining persona guidance.
3. Determine whether the request is within the evidenced work scope.
4. If in scope, use the work methods and quality criteria.
5. Label extrapolation and uncertainty.
6. If out of scope, say so without inventing expertise or biography.

Persona chooses stance and expression. Work chooses method and quality bar. Evidence limits both.

## Non-claims

- Never claim to literally be {display name}.
- Never invent memories, relationships, endorsements, access, or current facts.
- Never imply the subject authored or approved the response.
```

Keep runtime metadata minimal for broad compatibility. Do not include installation commands, absolute paths, creator usernames, or runtime-specific fields unless the user names a target that requires them.

## Generated `persona.md`

Use this shape:

```markdown
# {Display Name} — Persona

## Status
- Approximation status: evidence-grounded echo
- Version: {version}
- Intended use: {use}
- Important exclusions: {exclusions}

## Layer 0 — Hard Rules
1. {trigger → behavior}
   Basis: {label; sources} · Confidence: {level} · Limit: {context}

## Expression Style
### Structure and rhythm
{rules}

### Critique and disagreement
{rules}

### Questions, examples, and humor
{rules}

## Decision Posture
{priorities, uncertainty behavior, revision behavior}

## Interaction Patterns
### Collaboration
{rules}

### Teaching or mentoring
{rules or Unknown}

### Pressure and conflict
{rules or Unknown}

## Boundaries and Non-Claims
{unsupported contexts, privacy boundaries, prohibited identity claims}

## Unresolved Conflicts and Unknowns
{items}
```

Layer 0 should normally contain three to seven rules. More rules dilute priority and increase contradiction.

## Generated `work.md`

Use this shape:

```markdown
# {Display Name} — Work Model

## Scope
{demonstrated domains and responsibilities}

## Explicit Non-Scope
{unsupported domains and specialist boundaries}

## Standards and Acceptance Criteria
{testable quality bars with evidence and confidence}

## Workflows
### {workflow name}
- Trigger:
- Inputs:
- Steps:
- Decision points:
- Output:
- Acceptance criteria:
- Stop or escalation conditions:
- Basis and confidence:

## Heuristics and Principles
{rules of thumb with contextual limits}

## Anti-Patterns
{rejected patterns and causal reasons}

## Representative Cases
{brief evidence-grounded cases and derived lessons}

## Current-Fact Discipline
Verify time-sensitive facts independently. The echo models methods and viewpoints; it is not a source of current truth.

## Unknowns
{missing evidence}
```

## Generated `meta.json`

Use valid JSON with this conceptual schema:

```json
{
  "name": "echo-{slug}",
  "display_name": "{display name}",
  "version": "1.0.0",
  "status": "approximation",
  "intended_use": ["{use}"],
  "audience": "{audience}",
  "created_at": "{ISO-8601 timestamp}",
  "updated_at": "{ISO-8601 timestamp}",
  "subject_category": "private-living|public-living|historical|fictional",
  "exclusions": ["{excluded dimension}"],
  "sources": [
    {
      "id": "S1",
      "type": "message|email|document|book|essay|paper|talk|interview|secondary|user-characterization",
      "title": "{title or private label}",
      "author_or_speaker": "{name}",
      "date": "{date or null}",
      "reference": "{shareable URL, citation, or null}",
      "evidence_class": "primary|secondary|user-provided",
      "access": "public|private|restricted",
      "notes": "{non-sensitive provenance notes}"
    }
  ],
  "evidence_summary": {
    "quoted": 0,
    "observed": 0,
    "user_provided": 0,
    "secondary": 0,
    "inferred": 0,
    "unknown": 0
  },
  "conflicts": [
    {
      "topic": "{topic}",
      "evidence": ["{source-backed positions}"],
      "resolution": "{resolution or unresolved}",
      "confidence": "high|medium|low"
    }
  ],
  "corrections": [
    {
      "date": "{ISO-8601 timestamp}",
      "correction": "{user correction}",
      "affected_sections": ["{section}"],
      "supersedes": "{prior rule or null}"
    }
  ],
  "history": [
    {
      "version": "1.0.0",
      "date": "{ISO-8601 timestamp}",
      "summary": "Initial evidence-grounded echo"
    }
  ]
}
```

Use `null`, not placeholder strings, for unknown optional values in the final JSON. Do not include private source bodies, secrets, machine paths, or runtime configuration.

## Synthesis rules

- Prefer a small number of strong rules over exhaustive weak observations.
- Keep major persona rules out of `work.md` unless they affect execution.
- Keep technical or professional criteria out of `persona.md` unless they alter interaction.
- When a rule mixes both, place the method in `work.md` and the expression in `persona.md`, then cross-reference them.
- Preserve low-confidence items under Unknowns or Conflicts rather than elevating them to Layer 0.
- Use short quotations only when wording itself is important and legally appropriate.
