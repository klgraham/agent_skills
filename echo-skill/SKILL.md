---
name: echo-skill
description: Create evidence-grounded, English-language persona-and-work skills from source material about a colleague, mentor, collaborator, or public figure. Use when the user wants a reusable “echo” that captures a person's communication style, decision patterns, principles, standards, and workflows without claiming to be the person. Guides intake, source collection, separate persona and work analysis, conflict handling, portable skill generation, provenance, corrections, and verification.
---

# Echo Skill

Create a portable, evidence-grounded approximation of how a person communicates and approaches work. Call the result an **echo**: a useful model derived from sources, not the person and not a claim of identity.

## Preserve these invariants

1. **Evidence before confidence.** Distinguish direct quotations, observed patterns, user-provided characterizations, and inference.
2. **Behavior over biography.** Capture reproducible decisions, standards, workflows, and expression patterns. Do not turn the output into a résumé or fan page.
3. **Persona and work remain separate.** Persona controls stance, tone, interaction, and decision posture. Work controls domain methods, quality bars, and execution.
4. **Task truth outranks imitation.** Never invent facts, sources, memories, access, relationships, or first-person experiences to sound more authentic.
5. **Corrections outrank earlier analysis.** Record explicit user corrections and regenerate affected rules.
6. **Portable output.** Use relative paths and plain Markdown/JSON. Do not embed machine-specific paths, product-specific commands, or assumptions about a particular agent runtime.

## Use this skill when

- The user wants to preserve a colleague's, mentor's, collaborator's, or public figure's working style as a reusable skill.
- Source material includes messages, emails, documents, reviews, talks, essays, books, papers, transcripts, or interviews.
- The desired result must combine communication behavior with concrete work methods.
- The user wants to improve or correct an existing echo with more evidence.

Do not use it to:

- impersonate someone deceptively or communicate as them without disclosure;
- fabricate private beliefs, protected traits, credentials, relationships, or memories;
- infer consequential personal attributes from weak evidence;
- reproduce confidential source material unnecessarily;
- create a generic fictional character with no real source subject.

For a fictional character, use a normal persona-writing workflow instead.

## Produce this package

Write each echo to a user-selected destination. If none is supplied, use the workspace-relative path `echoes/{slug}/`.

```text
echoes/{slug}/
├── SKILL.md      # compact runtime entry point and execution contract
├── persona.md    # interaction style and behavioral model
├── work.md       # domain methods, standards, workflows, and knowledge
└── meta.json     # provenance, confidence, conflicts, versions, corrections
```

The generated skill name should normally be `echo-{slug}`. Keep the directory movable: every internal link must be relative.

## Follow the creation workflow

### 1. Establish scope and permission

Before collecting material, establish:

- the subject and intended use;
- whether the subject is private, public, historical, or fictional;
- who may use the echo and in what contexts;
- whether source material contains secrets, personal data, or restricted content;
- the desired output location.

Ask the user not to provide credentials, authentication tokens, private keys, medical data, financial account data, or unrelated third-party personal information. If supplied sources contain sensitive values, exclude or redact them before analysis.

An echo of a living private person should be used as a disclosed approximation for drafting, rehearsal, analysis, or internal assistance—not as undisclosed identity substitution.

### 2. Run the compact intake

Read [references/intake.md](references/intake.md). Collect the minimum identity and style framing needed to begin. Treat intake tags as user assertions, not objective facts.

Confirm the normalized profile before analyzing sources. Record any intended exclusions such as “do not imitate accent,” “work behavior only,” or “exclude personal messages.”

### 3. Build a source manifest

Collect only sources relevant to the intended echo. For each source, record:

- a stable label;
- source type and title;
- author or speaker;
- date, if known;
- location or bibliographic reference, if shareable;
- whether it is primary, secondary, or user characterization;
- permission or access notes;
- what dimensions it can support;
- extraction or transcription method, if applicable.

Prefer primary sources for voice and explicit principles. Use secondary sources for context and triangulation, not as substitutes for the subject's own words.

Do not paste large copyrighted works into the generated package. Store bibliographic references, short necessary quotations, and derived rules.

For published works, also read [references/public-figure-extraction.md](references/public-figure-extraction.md).

### 4. Analyze persona and work separately

Run two conceptual tracks over the same source manifest:

- [references/persona-analyzer.md](references/persona-analyzer.md) for expression, interaction, decision posture, boundaries, and hard behavioral rules;
- [references/work-analyzer.md](references/work-analyzer.md) for scope, standards, workflows, evaluation criteria, knowledge, and anti-patterns.

Parallel analysis is useful when the environment supports it, but it is not required. The two tracks must return independently inspectable evidence tables before synthesis.

Use these evidence labels consistently:

- **Quoted** — directly stated in a primary source.
- **Observed** — repeated behavior visible in primary sources.
- **User-provided** — asserted during intake or correction.
- **Secondary** — described by another source.
- **Inferred** — a cautious synthesis from the above.
- **Unknown** — insufficient evidence.

Never silently convert a stereotype, job title, personality label, or single anecdote into a behavioral rule.

### 5. Resolve conflicts explicitly

Create a conflict table whenever sources disagree:

| Topic | Evidence A | Evidence B | Resolution | Confidence |
|---|---|---|---|---|
| review style | user says “blunt” | messages show diplomatic phrasing | model as direct on substance, diplomatic in wording | medium |

Resolution order:

1. explicit user correction about the desired model;
2. repeated direct evidence from the subject;
3. explicit statement from the subject;
4. intake characterization;
5. reliable secondary evidence;
6. cautious inference.

This order determines the generated model, not historical truth. Preserve unresolved conflicts in `meta.json` rather than flattening them.

### 6. Build the four output files

Read [references/builders.md](references/builders.md) and generate the package.

The generated `SKILL.md` must:

- identify itself as an approximation;
- link to `persona.md` and `work.md` using relative paths;
- state the persona-then-work execution order;
- preserve higher-priority user, factuality, privacy, and safety constraints;
- define behavior for requests outside the subject's evidenced scope;
- avoid references to the creation environment.

The generated `persona.md` must contain:

- Layer 0 hard rules;
- expression and interaction style;
- decision posture;
- behavior under disagreement and uncertainty;
- boundaries and non-claims;
- confidence and evidence labels for major rules.

The generated `work.md` must contain:

- scope and explicit non-scope;
- standards and evaluation criteria;
- repeatable workflows;
- domain heuristics and anti-patterns;
- evidence-grounded examples;
- unknowns and conditions requiring clarification.

The generated `meta.json` must remain valid JSON and include provenance, confidence, conflicts, corrections, and version history. Do not place sensitive source text in it.

### 7. Review with the user

Present two concise summaries before finalizing:

1. **Persona summary** — the strongest tone, interaction, and decision rules.
2. **Work summary** — the strongest standards, workflows, and domain principles.

Also present:

- low-confidence or inferred rules;
- source gaps;
- unresolved conflicts;
- material deliberately excluded for privacy or relevance.

Ask for targeted corrections. Do not ask the user to approve a large opaque bundle without showing the rules that will govern it.

### 8. Verify portability and behavior

Complete all checks in [references/verification.md](references/verification.md).

At minimum:

- parse the generated frontmatter and JSON;
- verify all relative links resolve;
- scan the package for absolute paths, home-directory shortcuts, machine usernames, secrets, and product-specific runtime commands;
- confirm every major rule has an evidence label and confidence;
- test at least one in-scope task, one disagreement or uncertainty case, and one out-of-scope request;
- confirm the output never claims to literally be the subject.

If the target agent supports skill packages, install or register the generated directory according to that agent's documentation. Keep installation instructions outside the generated echo unless they are fully runtime-neutral.

## Runtime order for generated echoes

Generated echoes must use this order on every task:

1. Apply the current user's request and all governing factuality, privacy, and safety constraints.
2. Load Persona Layer 0, then the rest of `persona.md`.
3. Determine whether the request is within the evidenced scope in `work.md`.
4. If in scope, execute using the work methods while expressing the persona style.
5. If partly supported, separate evidenced guidance from extrapolation.
6. If out of scope, say so in the modeled voice without inventing expertise.
7. Never claim personal memory, identity, endorsement, or access not present in the current context.

A concise rule is:

```text
Persona chooses the stance and expression.
Work chooses the method and quality bar.
Evidence limits both.
```

## Evolve an existing echo

When the user adds sources or makes a correction:

1. append the new source or correction to `meta.json`;
2. identify the exact persona or work rules affected;
3. re-run only the relevant analysis dimensions;
4. update the four output files coherently;
5. increment the version and add a short change summary;
6. rerun behavioral and portability checks.

Do not overwrite correction history. A correction may supersede a prior rule, but the provenance record should retain both.

## Common pitfalls

1. **Style-only imitation.** Catchphrases without decision and work models produce a caricature. Require concrete standards and workflows.
2. **Biography-as-skill.** Facts about a person's life rarely tell an agent what to do. Convert only supported behavior into executable guidance.
3. **Overfitting one source.** A single message or anecdote may reflect context, not a stable trait. Require repetition or label the rule as low-confidence.
4. **Stereotype translation.** Personality types, employers, nationalities, gender, and job titles are not behavioral evidence.
5. **Hidden contradiction.** Do not silently choose between conflicting sources. Record the conflict and resolution.
6. **False first person.** The echo may use a recognizable style, but it must not invent autobiographical claims or imply the subject authored the response.
7. **Sensitive-source leakage.** Derived rules rarely need full private messages. Quote minimally and redact.
8. **Environment coupling.** Absolute paths, runtime commands, tool names, and installation layouts make the package brittle.
9. **Blended echoes.** Loading multiple high-context personas can produce accidental mixtures. Keep each echo self-contained and combine them only when explicitly requested.
10. **Duplicate names.** A generated skill name must be unique within its target runtime.

## Acknowledgment

This workflow is an English-language adaptation of the general colleague-skill pattern published at <https://github.com/titanwings/colleague-skill>, extended for evidence provenance, public figures, portable output, privacy boundaries, corrections, and runtime-neutral verification.
