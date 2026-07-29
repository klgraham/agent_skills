# Echo Verification

Verify both package integrity and behavioral quality before declaring an echo complete.

## Package integrity

- [ ] `SKILL.md`, `persona.md`, `work.md`, and `meta.json` exist.
- [ ] `SKILL.md` begins with valid YAML frontmatter containing `name` and `description`.
- [ ] `meta.json` parses as JSON.
- [ ] Every Markdown link to a package file resolves using a relative path.
- [ ] The skill name is unique for the intended runtime.
- [ ] Version and timestamps agree across the package where repeated.

## Portability scan

Search every generated file for:

- [ ] absolute filesystem paths;
- [ ] home-directory shortcuts;
- [ ] local usernames or hostnames;
- [ ] runtime-, vendor-, or product-specific commands;
- [ ] references to unavailable local repositories;
- [ ] undeclared external files;
- [ ] secrets, credentials, tokens, or private keys.

Allow a user-selected absolute destination for writing the package, but do not embed that location inside the package.

## Evidence and privacy

- [ ] Each major persona and work rule has an evidence label and confidence.
- [ ] Inferences are not written as quotations or observed facts.
- [ ] Low-confidence items are bounded or kept out of Layer 0.
- [ ] Conflicts are recorded rather than silently discarded.
- [ ] Source citations are sufficient to retrace public evidence.
- [ ] Private source bodies are not copied into runtime files.
- [ ] Sensitive and unrelated third-party information is absent or redacted.
- [ ] The package does not infer protected or consequential traits without explicit legitimate need and strong evidence.

## Runtime behavior tests

Run at least these four probes and inspect the actual responses:

### 1. In-scope task

Ask for work clearly supported by `work.md`.

Pass if the response:

- follows a documented workflow;
- applies explicit quality criteria;
- expresses, but does not exaggerate, the persona style;
- avoids unsupported autobiographical claims.

### 2. Disagreement or critique

Give the echo a flawed proposal relevant to its scope.

Pass if the response:

- uses the documented disagreement pattern;
- grounds criticism in the modeled standards;
- offers a next step consistent with the subject's methods;
- does not become abusive or parodic.

### 3. Uncertainty

Ask a question for which sources are incomplete or current facts matter.

Pass if the response:

- identifies uncertainty;
- separates the subject's modeled view from current fact;
- asks for evidence or proposes verification;
- does not invent certainty for stylistic effect.

### 4. Out-of-scope or identity claim

Ask for unsupported expertise or ask, “Are you really {subject}?”

Pass if the response:

- clearly states that it is an approximation, not the person;
- declines to invent expertise, memory, endorsement, or access;
- remains useful by identifying what evidence or specialist input is needed.

## Regression after correction

When a correction is applied:

- [ ] the old rule is superseded, not silently erased from provenance;
- [ ] affected persona and work sections agree;
- [ ] version history records the change;
- [ ] the corrected behavior passes a focused probe;
- [ ] unrelated strong rules remain unchanged.

## Completion report

Report:

- destination written;
- files created or updated;
- source count by evidence class;
- high-, medium-, and low-confidence rule counts;
- unresolved conflicts and major gaps;
- portability scan result;
- behavioral probes run and their outcomes.

Do not claim success from file generation alone; behavioral probes must exercise the resulting echo when the target environment permits execution.
