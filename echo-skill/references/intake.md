# Echo Intake

Ask these questions in one compact round. Only the name or slug and intended use are required; derive or leave the rest unknown rather than forcing answers.

## Questions

1. **Name and intended use**
   - “What should this echo be called, and what should it help with?”
   - Normalize the name to a short lowercase hyphenated slug.

2. **Subject and scope**
   - “Who is the subject, what is their relevant role or context, and which parts of their behavior should the echo capture or exclude?”
   - Record whether the subject is a living private person, living public person, historical person, or fictional character.

3. **Style and decision profile**
   - “How would you describe their communication style, working style, and decision habits?”
   - Treat the answer as a user-provided characterization, not as verified fact.

4. **Sources and permission**
   - “What source material can be used, and are there privacy, confidentiality, copyright, or sharing restrictions?”
   - Ask the user to remove secrets and unrelated third-party personal data.

5. **Destination and audience**
   - “Where should the package be written, and who will use it?”
   - If no destination is provided, use `echoes/{slug}/` relative to the current workspace.

## Optional tag vocabulary

Tags are prompts for investigation, not evidence. Use only tags the user supplies or directly confirms.

### Work style

- high standards
- pragmatic
- detail-oriented
- fast iteration
- process-heavy
- experimental
- risk-averse
- high risk tolerance
- hands-on
- delegating

### Communication style

- direct
- diplomatic
- concise
- expansive
- formal
- conversational
- question-led
- example-led
- low-context
- high-context

### Decision style

- data-driven
- first-principles
- consensus-seeking
- fast-deciding
- deliberative
- reversible-bet oriented
- principle-led
- user-impact led

Avoid pejorative personality labels when a concrete behavior can be stated instead. For example, replace “difficult” with “often rejects proposals that lack measurable acceptance criteria,” if evidence supports that statement.

## Confirmation block

Before source analysis, show:

```text
Echo name: {slug}
Subject/context: {profile}
Intended use: {use}
Capture: {included dimensions}
Exclude: {excluded dimensions}
User-provided style: {characterization}
Sources: {source types}
Destination: {relative or user-selected path}
Audience/access: {audience}

Proceed or change a field?
```

Record the confirmation and exclusions in `meta.json`.
