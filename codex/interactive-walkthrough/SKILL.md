---
name: interactive-walkthrough
description: Create evidence-grounded, self-contained interactive HTML walkthroughs of pull requests, Git repositories, subsystems, request lifecycles, protocols, algorithms, and technical, scientific, or industrial processes. Use when the user asks to explore or explain a subject through a clickable visual artifact, guided sequence, repository map, before-and-after comparison, or reader-driven simulation. Do not use for a chat-paced PR review, a static diagram alone, a generic landing page, or prose-only documentation.
---

# Interactive Walkthrough

Create a polished interactive artifact that lets the reader drive an explanation. Default to one complete local `.html` file with inline CSS and JavaScript, openable without a build step. Publish only when the user requests it or the project is already configured for hosting.

The reader must always be able to answer:

1. Where am I in the overall flow?
2. What changed or transformed at this step?
3. What evidence supports this explanation?

## Satisfy the core contract

Every walkthrough must include:

1. A one-line subject statement naming the audience, scope, and single takeaway.
2. A trustworthy claim-to-source model appropriate to the subject.
3. A real causal, execution, data, or transformation sequence.
4. Exactly one primary interactive centerpiece.
5. Reader-driven progression without autoplay or timed essential content.
6. Persistent orientation showing the current step and whole map.
7. Visible distinctions between observed facts, simplifications, assumptions, variants, and unknowns.
8. A verified artifact whose controls, console, keyboard path, and responsive behavior were exercised.

## Pin the subject

Write one internal sentence before building:

> For **[audience]**, explain **[subject and scope]** so they understand **[single takeaway]**.

Keep every stage, visual, and control in service of that sentence. For a whole repository, choose a representative path through the system instead of turning the file tree into the walkthrough.

## Build the evidence map first

Never write from memory when inspectable sources exist. Record each load-bearing claim and the source that supports it before writing HTML.

### Pull request or code change

Inspect:

- PR metadata, base and head revisions, and commits;
- the real diff and affected tests;
- surrounding code, not only changed lines;
- CI or local verification evidence;
- issues or documentation that explain intent.

Use real symbols and `path:line` citations. Mark illustrative values as examples.

### Git repository or subsystem

Inspect:

- README and architecture documentation;
- package and build manifests;
- entry points and configuration;
- central data types and public APIs;
- wiring, extension points, and external boundaries;
- tests that establish behavior;
- one or two representative execution paths;
- recent history only when it explains current structure.

Explain how to think about the repository. Separate entry points, control flow, data flow, extension points, dependencies, tests, and operational surfaces. Cite exact paths and line ranges, and name the relevant symbol or section when line numbers may drift.

### Technical, scientific, or industrial process

Prefer:

1. standards, government, and laboratory references;
2. textbooks, peer-reviewed papers, and review articles;
3. official engineering or vendor descriptions;
4. reputable secondary explainers for pedagogy only.

Capture technically meaningful inputs, outputs, phases, conditions, transformations, energy transfer, side streams, recycle loops, by-products, losses, safety constraints, and configuration variability. Do not present one facility or mechanism as universal.

For chemistry, distinguish:

- a net reaction from an elementary mechanism;
- a catalyst from a reactant;
- thermodynamic favorability from reaction rate;
- conceptual electron flow from observed intermediates.

For industrial processes, distinguish:

- **separation**: sorting by physical properties;
- **conversion**: changing molecular structure;
- **treatment**: removing impurities or adjusting properties;
- **blending or finishing**: combining streams to meet specifications.

Place citations beside the step they support, then provide a consolidated reference section.

## Choose one walkthrough model

Pick one primary model and derive every view from one canonical state object.

### Drive the flow

Use for lifecycles, state machines, protocols, reaction mechanisms, and process trains. A step action updates the active stage, inputs, operation, outputs, conditions, accumulated trace or ledger, sources, and caveats.

Track one named thing through the sequence: a request, packet, state object, molecule, atom, feed stream, or material fraction.

### Explore the repository path

Use for repositories and large subsystems. Provide a map, a recommended golden path, and a guided-path control. Selecting a node updates responsibility, inputs and outputs, important symbols, upstream and downstream relationships, extension points, tests, and source locations.

### Before-and-after diptych

Use for pull requests, migrations, redesigns, and API changes. Advance by capability or scenario rather than file order. For each step show the old model, new model, simplification, remaining complexity, verification evidence, and deferred work.

### Mapping table

Use only when comparison is the main learning mechanism. Include the source concept, target concept, clean mappings, broken mappings, and evidence or examples.

## Choose the delivery surface

### Standalone HTML

Use by default:

- one complete HTML document;
- inline CSS and JavaScript;
- no external runtime dependency;
- direct local use or a small local server for verification;
- exact file path in the final response.

### Sites deployment

If `.openai/hosting.json` exists, use the Sites building and hosting skills and preserve its project ID. Also use Sites when the user asks to publish, deploy, or host the walkthrough. Finish deployable work with a production deployment unless the user asks for local-only output.

Do not make deployment a prerequisite when the user only asked for a local artifact.

## Choose the container

### Slide deck

Use for presentation-paced walkthroughs:

- fixed viewport with no body scrolling;
- one idea per slide;
- early whole-flow map;
- numbered stages and visible current-step strip;
- arrow, Space, J/K, Home, and End navigation;
- previous and next buttons;
- progress bar and slide counter;
- table-of-contents overlay and hash deep links;
- per-slide sources;
- print CSS that stacks slides as pages.

Allow scrolling inside a slide only for wide code, tables, equations, diagrams, or dense content.

### Scrolling act page

Use for long-form reference or exploratory repository maps:

- compact header and thesis;
- numbered sections;
- sticky stage rail or map;
- current-section highlighting;
- explicit next and previous controls;
- inline sources and final references;
- no horizontal body scrolling.

Choose scrolling because reference value matters, not merely because the draft is long.

## Enforce interaction rules

- Let the reader cause every meaningful transition.
- Make **Next step** advance exactly one transition.
- Permit **Run remaining** only as an immediate synchronous action.
- Make **Reset** restore the complete initial state.
- Permit a **Happy path** control to jump instantly and populate the trace.
- Label branches by their real condition, such as error path, mode, feedstock, catalyst, or product target.
- Provide keyboard access, visible focus, and clear disabled states for every control.
- Preserve position with a hash or local state when useful.
- Update coordinated views from one canonical data model; avoid independent handlers that can drift.

## Structure the narrative

Use this progression:

1. Orientation: audience, subject, scope, status, and takeaway.
2. Whole map: the entire route visible early.
3. Vocabulary: only the terms required to follow the mechanism.
4. Guided sequence: numbered causal or execution steps.
5. Interactive centerpiece: introduced early and reused.
6. Variants: branches, edge cases, failures, or open questions.
7. Verification and caveats: evidence and simplifications.
8. Reference guide: sources and where to inspect next.

For repositories, end with **Where to make common changes** and **How to verify them**.

For scientific or industrial processes, end with **What this model omits**, safety and environmental considerations, and configuration variability.

## Apply a restrained visual system

- Use a cool neutral ground and restrained semantic color.
- Use system sans-serif for prose and headings.
- Use monospace for paths, labels, equations, values, and traces.
- Assign one accent per semantic role: signal, structure, resolved, or critical.
- Pair color with text, shape, pattern, or iconography.
- Support light and dark themes unless the design deliberately commits to one theme.
- Prefer legible diagrams and state changes over decoration.

## Mark certainty and hazards

Use visible labels such as:

- `SHIPPED`, `PROPOSED`, `SPIKE`, `OPEN`;
- `VERIFIED IN CODE`, `SUPPORTED BY SOURCE`;
- `REPRESENTATIVE CONFIGURATION`, `SIMPLIFIED MODEL`;
- `MECHANISM PROPOSED`, `INTERMEDIATE OBSERVED`;
- `SAFETY-CRITICAL — NOT OPERATING INSTRUCTIONS`.

For hazardous industrial or chemical subjects:

- keep the artifact explanatory rather than procedural;
- omit actionable quantities or control settings unless legitimate professional documentation and authoritative evidence require them;
- identify major hazards and safeguards conceptually;
- state that operation requires qualified personnel, process-specific procedures, and regulatory controls.

Always show the clean core and the tax: what the model clarifies, what remains complex, and what was deliberately omitted.

## Build and verify

1. Pin the audience, scope, and takeaway.
2. Inspect sources and create the claim-to-source map.
3. Choose one walkthrough model and one container.
4. Sketch stages and the canonical state shape.
5. Build the interaction before polishing the visual design.
6. Add citations, caveats, accessibility, responsive behavior, and print behavior.
7. Validate the HTML structure and inspect the generated source.
8. Load the browser-control skill before using Codex browser automation.
9. Open the exact local artifact. If direct local-file navigation is unavailable, serve its directory through a temporary local HTTP server.
10. Exercise every primary control and at least one alternate branch.
11. Check keyboard navigation, focus states, disabled states, reset behavior, and hash links.
12. Inspect the browser console and fix uncaught errors.
13. Inspect screenshots at the primary viewport and a narrow viewport.
14. Re-run relevant repository tests when the walkthrough describes code behavior.
15. Deliver the exact path or production URL with a concise verification report.

Do not claim browser verification from file existence or static source inspection alone.

## Meet technical requirements

- Include `<!doctype html>`, `<html>`, `<head>`, and `<body>`.
- Keep CSS and JavaScript inline for standalone output.
- Use semantic headings, landmarks, labels, and real `<button>` elements.
- Give primary controls at least 44px pointer targets and visible focus states.
- Support `prefers-reduced-motion`.
- Prevent horizontal body scrolling.
- Contain wide code, equations, tables, and diagrams within responsive wrappers.
- Include a stable favicon and descriptive `<title>`.
- Open external source links safely and visibly.
- Include print styles when the artifact should work as a handout.
- Derive all transitions from one canonical state model.
- Do not invent code, equations, yields, performance numbers, or process conditions.

## Avoid common failures

- Do not turn a repository walkthrough into a file-tree tour.
- Do not explain a whole repository as though it were only a pull-request diff.
- Do not conflate physical separation with chemical conversion.
- Do not present one process configuration or reaction mechanism as universal.
- Do not invent quantitative detail to make the interface look complete.
- Do not autoplay the primary interaction.
- Do not create multiple competing demos.
- Do not isolate all citations in a bibliography.
- Do not oversell certainty.
- Do not polish before the state model works.
- Do not claim verification without exercising the artifact.
- Do not turn hazardous-process education into operating instructions.

## Deliver concisely

Use this pattern:

```text
Created: /absolute/path/to/<subject>-walkthrough.html

Covers: <guided sequence and interactive centerpiece>.
Evidence: <repository, code, or authoritative-source basis>.
Verified: <controls, console, keyboard, and viewport checks>.
Caveat: <most important simplification or open issue, if any>.
```
