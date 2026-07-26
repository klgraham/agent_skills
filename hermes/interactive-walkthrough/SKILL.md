---
name: interactive-walkthrough
description: Use when the user wants a self-contained, interactive HTML walkthrough of a pull request, a whole Git repository, a subsystem, or a technical/scientific/industrial process such as a chemical reaction or petroleum refining. Build an evidence-grounded, reader-driven explainer with one strong interactive centerpiece, paced steps, source citations, honest caveats, and verified browser behavior. Do not use for a chat-paced PR review; use pr-walkthrough for that.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [interactive, walkthrough, html, repository, process, science, engineering, visualization]
    related_skills: [claude-design, architecture-diagram, pr-walkthrough, technical-documentation]
---

# Interactive Walkthrough

## Overview

Create a polished, self-contained HTML artifact that lets the reader **walk through a subject by driving it**. The subject may be:

- a pull request or migration,
- an entire Git repository,
- a subsystem or request lifecycle,
- a protocol or algorithm,
- a scientific mechanism,
- or an industrial process such as catalytic cracking, polymerization, distillation, or petroleum refining.

The artifact is not a wall of prose with decorative arrows. It has a clear sequence, one interactive centerpiece, visible state, and evidence for every load-bearing claim. The reader should be able to answer three questions at any point:

1. **Where am I in the overall flow?**
2. **What changed or transformed at this step?**
3. **What evidence supports this explanation?**

Default deliverable: one complete local `.html` file with inline CSS and JavaScript, openable directly in a modern browser and delivered with its exact path. If a publishing tool is available, publish the same file after local verification; do not make publishing a prerequisite for completion.

## When to Use

Use for requests such as:

- “Make an interactive walkthrough of this repo.”
- “Show me how this codebase hangs together.”
- “Turn this PR into a visual walkthrough.”
- “Explain the request lifecycle as a clickable artifact.”
- “Walk through the stages of this chemical reaction.”
- “Show how crude oil becomes gasoline, diesel, and other products.”
- “Build a visual, shareable explainer of this protocol/process.”

Do **not** use when:

- The user wants a paced PR discussion in chat with review comments → use `pr-walkthrough`.
- The user wants a static architecture picture only → use `architecture-diagram`.
- The user wants a generic landing page or UI prototype rather than a technical explainer → use `claude-design`.
- The user wants prose documentation with no interactive artifact → use `technical-documentation`.

## Core Contract

Every walkthrough must have:

1. **A one-line subject statement** — what is being explained, to whom, and the single takeaway.
2. **A trustworthy evidence model** appropriate to the subject.
3. **A real sequence** — architecture entry path, lifecycle, transformation chain, or causal mechanism.
4. **Exactly one primary interactive centerpiece.** Secondary controls may support it, but do not create multiple unrelated demos.
5. **Reader-driven progression.** No auto-play and no timers that advance essential content.
6. **Persistent orientation.** The reader can always see the current step and the whole map.
7. **Honest boundaries.** Distinguish observed facts, simplified teaching models, assumptions, variants, and unknowns.
8. **A verified artifact.** Open it, exercise the controls, inspect the browser console, and fix failures before delivery.

## 1. Pin the Subject Before Building

Write one internal sentence in this form:

> For **[audience]**, explain **[subject and scope]** so they understand **[single takeaway]**.

Examples:

- For a new maintainer, explain how requests enter this repository, pass through orchestration, and reach storage so they know where to make changes safely.
- For a reviewer, explain how this PR changes cancellation semantics so they can focus on races and cleanup.
- For an engineering student, explain how atmospheric and vacuum distillation separate crude fractions before conversion units change molecular structure.
- For a chemist outside the specialty, explain how the catalyst lowers the activation barrier and how intermediates evolve across the reaction coordinate.

Everything in the artifact must serve that sentence. If the scope is “whole repository,” choose a representative path through the system; do not turn the file tree into the walkthrough.

## 2. Build the Evidence Map First

Never write the walkthrough from memory when inspectable sources exist. Build a small claim-to-source map before writing HTML.

### A. Pull request or code change

Inspect:

- PR metadata, base/head SHAs, and commit list,
- the real diff and affected tests,
- surrounding code, not only changed lines,
- build or CI evidence for claims about behavior,
- docs or issues that explain intent.

Use real function/type/field names and `path:line` citations. Illustrative values are allowed only when marked as examples.

### B. Whole Git repository or subsystem

Inspect the repository itself:

- README and architecture docs,
- package/build manifests,
- entry points,
- central data types and public APIs,
- configuration and wiring,
- tests that prove behavior,
- one or two representative execution paths,
- recent Git history only when it explains current structure.

A repository walkthrough should explain **how to think about the repo**, not enumerate every directory. Separate:

- entry points,
- control flow,
- data flow,
- extension points,
- boundaries/external dependencies,
- tests and operational surfaces.

Cite exact paths and line ranges. When line numbers may drift, also name the symbol or section.

### C. Technical, scientific, or industrial process

Prefer authoritative sources:

1. standards, government or laboratory references,
2. textbooks, peer-reviewed papers, or review articles,
3. official engineering/vendor process descriptions,
4. reputable secondary explainers for pedagogy only.

Capture the variables that make the process technically meaningful:

- inputs and outputs,
- phases and physical state,
- chemical species or material fractions,
- balanced equations or reaction families when known,
- temperature, pressure, catalyst, residence time, and energy transfer,
- separation versus chemical-conversion steps,
- side streams, recycle loops, by-products, losses, and waste handling,
- safety and environmental constraints,
- plant- or feedstock-specific variation.

Do not collapse an industrial system into one universal sequence when real facilities vary. Label the depicted configuration, for example: **“representative complex refinery; exact unit order and yields vary by crude slate and product targets.”**

For chemistry, distinguish:

- a balanced net reaction from a proposed elementary mechanism,
- a catalyst from a reactant,
- thermodynamic favorability from reaction rate,
- conceptual electron flow from experimentally established intermediates.

For industrial processes, distinguish:

- **separation** (molecules are sorted by physical properties),
- **conversion** (molecular structures are changed),
- **treatment** (impurities are removed or properties adjusted),
- **blending/finishing** (streams are combined to meet specifications).

Attach source links or footnotes to the relevant step, not only to a bibliography at the end.

## 3. Choose the Walkthrough Model

Pick one model that matches the subject.

### Model A — Drive the flow

Best for request lifecycles, state machines, protocols, reaction mechanisms, and industrial process trains.

The reader clicks **Next step** or a specific event. The artifact updates:

- active stage/node,
- current inputs,
- transformation or operation,
- outputs,
- conditions,
- accumulated trace or material ledger,
- source/caveat panel.

For a chemical or industrial process, track one named thing through the flow: a molecule, atom, feed stream, hydrocarbon fraction, packet, request, or state object. This continuity makes the sequence understandable.

### Model B — Explore the repository path

Best for whole repositories and large subsystems.

Use a map with clickable nodes and one recommended **golden path**. Selecting a node updates a detail pane with:

- responsibility,
- inputs/outputs,
- important symbols,
- upstream/downstream relationships,
- extension points,
- tests,
- `file:line` sources.

Provide a **Take the guided path** control so the reader does not have to infer an order from the map.

### Model C — Before/after diptych

Best for PRs, migrations, redesigns, and API changes.

Show synchronized before/after panes grounded in real code or behavior. Advance by capability or scenario, not by file order. For each step show:

- old model,
- new model,
- what got simpler,
- what complexity remains,
- verification evidence,
- caveats or deferred work.

### Model D — Mapping table

Best for analogies, API comparisons, or concept translation. The table must include:

- source concept,
- target concept,
- what maps cleanly,
- what does not map,
- evidence/examples.

Use this only when comparison is the primary learning mechanism; do not use it as an excuse to avoid showing sequence.

## 4. Pick the Container

### Format A — Slide deck (default)

Use when the walkthrough will be presented or paged through.

Requirements:

- fixed viewport; the body does not scroll,
- one idea per slide,
- an early whole-flow map,
- numbered acts or stages,
- visible current-step strip,
- keyboard navigation: arrows, Space, J/K, Home/End,
- previous/next buttons,
- progress bar and slide counter,
- table-of-contents overlay,
- hash deep links,
- per-slide source footer,
- print CSS that stacks slides as pages.

A slide’s content region may scroll vertically if necessary. Wide code, tables, equations, and diagrams must scroll inside their own containers.

### Format B — Scrolling act page

Use for long-form reference or exploratory repository maps.

Requirements:

- compact header and thesis,
- numbered sections,
- sticky stage rail or map,
- current-section highlighting,
- keyboard or explicit next/previous controls,
- inline sources and a final reference section,
- no horizontal body scrolling.

Do not choose scrolling merely because the content is long. First cut or restructure. Choose it when async reference value is genuinely higher than presentation pacing.

## 5. Interaction Rules

The reader drives the explanation.

- Essential progression must never use `setTimeout`, intervals, autoplay, or automatic carousels.
- A **Next step** control advances exactly one meaningful transition.
- A **Run remaining** control may apply all remaining steps synchronously, without timers.
- A **Reset** control restores the initial state.
- A **Happy path** control may jump through the common route instantly and fill the trace.
- Branches must be explicit. Label alternatives by condition: feedstock, operating mode, error path, catalyst, product target, or implementation choice.
- Every control needs a keyboard path, visible focus state, and clear disabled state.
- Preserve the reader’s place with the URL hash or local state when useful.

The visual should update multiple coordinated views from one canonical state object. Avoid separate click handlers that can drift out of sync.

## 6. Narrative Structure

A strong walkthrough usually follows this sequence:

1. **Orientation** — subject, audience, scope, status, and takeaway.
2. **Whole map** — the entire path on one screen.
3. **Vocabulary** — only terms needed to follow the mechanism.
4. **Guided sequence** — the numbered steps.
5. **Interactive centerpiece** — introduced early, then reused rather than replaced.
6. **Edge cases or variants** — alternate branches, failure modes, feedstock differences, or open questions.
7. **Verification and caveats** — what proves the story and where it is simplified.
8. **Reference guide** — sources and where to inspect next.

For repositories, end with **“Where to make common changes”** and **“How to verify them.”**

For scientific/industrial processes, end with **“What this model omits”**, safety/environmental considerations, and configuration variability.

## 7. Visual Language

Load `claude-design` for design process and artifact quality. This skill defines the walkthrough-specific information architecture.

Default family identity, adaptable to the subject:

- cool slate neutral ground,
- restrained semantic color,
- system sans for prose and headings,
- monospace for paths, labels, equations, values, and trace logs,
- one accent per semantic role rather than decorative color.

Suggested roles:

| Role | Meaning |
|---|---|
| signal | current input, attention, energy added |
| structural | data, vessels, interfaces, intermediate state |
| resolved | completed state, product, verified result |
| critical | failure, hazard, rejected path, contaminant |

For chemistry and industrial systems, color by **role or material family**, not arbitrary stage. Always pair color with text, shape, or pattern; color alone cannot carry meaning.

Support light and dark themes unless the artifact deliberately commits to one presentation theme. If single-theme, state that choice in the design brief.

## 8. Honesty and Safety Devices

Use visible labels such as:

- `SHIPPED`, `PROPOSED`, `SPIKE`, `OPEN`,
- `VERIFIED IN CODE`, `SUPPORTED BY SOURCE`,
- `REPRESENTATIVE CONFIGURATION`,
- `SIMPLIFIED MODEL`, `PLANT-SPECIFIC`,
- `MECHANISM PROPOSED`, `INTERMEDIATE OBSERVED`,
- `SAFETY-CRITICAL — NOT OPERATING INSTRUCTIONS`.

A walkthrough may teach a hazardous process, but it must not silently become an operational recipe. For industrial chemistry, high pressure, high temperature, toxic materials, explosives, or controlled substances:

- keep the artifact explanatory rather than procedural,
- avoid actionable quantities or control settings unless the user explicitly needs legitimate professional documentation and authoritative sources support them,
- name major hazards and safeguards at a conceptual level,
- state that real operation requires qualified personnel, process-specific procedures, and regulatory controls.

Always show **the clean core and the tax**: what the model clarifies, what complexity remains, and what was deliberately omitted.

## 9. Build Workflow

1. Load `claude-design`; also load the domain skill if one exists.
2. Pin audience, scope, and takeaway in one sentence.
3. Inspect sources and build the claim-to-source map.
4. Choose one walkthrough model and one container format.
5. Sketch the stages and canonical state shape before styling.
6. Build a complete self-contained HTML document with inline CSS/JS.
7. Implement the primary interaction first; styling comes after it works.
8. Add citations, caveats, accessibility, responsive behavior, and print behavior.
9. Open the local file in a browser.
10. Exercise every primary control and at least one alternate branch.
11. Inspect the browser console and fix errors.
12. Inspect a screenshot at the primary viewport and one narrow viewport when responsive behavior matters.
13. Deliver the exact path and a concise verification report.

If updating an existing walkthrough, edit the same file unless the user asks for a preserved version. Keep stable IDs, hashes, and favicon so existing links remain useful.

## 10. Technical Requirements

- Complete standalone HTML document, including `<!doctype html>`, `<html>`, `<head>`, and `<body>`.
- Inline CSS and JavaScript.
- No external runtime dependency by default; embed required small assets as data URIs.
- Semantic controls: real `<button>` elements, labels, headings, landmarks.
- Visible focus states and minimum 44px pointer targets for primary controls.
- `prefers-reduced-motion` support; no essential information available only through motion.
- No horizontal body scrolling.
- Responsive handling for wide diagrams, code, equations, and tables.
- Stable favicon and descriptive `<title>`.
- Source links open safely and visibly.
- Print stylesheet when the artifact should double as a handout.
- All state transitions derive from one canonical data model.
- No invented code, equations, yields, performance numbers, or process conditions.

## Common Pitfalls

1. **Treating a repo walkthrough as a file-tree tour.** Follow a real execution or data path and explain boundaries.
2. **Using PR assumptions for a whole repository.** Repositories need entry points, extension points, tests, and operational surfaces—not only diffs.
3. **Conflating separation with chemical conversion.** In refining and similar processes, name which steps sort molecules and which alter them.
4. **Presenting one refinery or reaction path as universal.** Label configuration, feedstock, catalyst, and mechanism variability.
5. **Inventing quantitative detail to make the UI feel complete.** Unknown values stay unknown; simplified values are labeled illustrative.
6. **Auto-playing the centerpiece.** The reader must cause each meaningful transition.
7. **Multiple competing demos.** Use one centerpiece and coordinated supporting panes.
8. **Source dump at the end.** Put evidence at the step where the claim appears, then provide a consolidated reference section.
9. **Overselling certainty.** Separate verified behavior, proposed models, simplifications, and open questions.
10. **Polishing before validating the state model.** First make step, back, reset, branch, and deep-link behavior correct.
11. **Claiming verification without opening the artifact.** File existence is not interaction verification.
12. **Unsafe process detail.** Educational explanation is not a plant procedure; label boundaries and hazards.

## Verification Checklist

### Subject and evidence

- [ ] Audience, scope, and single takeaway are explicit.
- [ ] Every load-bearing claim maps to a code citation or authoritative source.
- [ ] Repo paths, symbols, equations, conditions, and process stages are real.
- [ ] Simplifications, variants, and unknowns are visibly labeled.

### Walkthrough quality

- [ ] The whole flow is visible early.
- [ ] The stages form a real causal or execution sequence.
- [ ] Exactly one primary interactive centerpiece carries the explanation.
- [ ] The reader can step, go back, reset, and understand branching.
- [ ] The current state and current position are always visible.

### Artifact quality

- [ ] HTML opens locally without external setup.
- [ ] Primary controls and one alternate path were exercised.
- [ ] Browser console has no uncaught errors.
- [ ] Keyboard navigation and focus states work.
- [ ] Reduced motion and narrow viewport behavior were checked.
- [ ] Sources, caveats, title, and favicon are present.
- [ ] The delivered response includes the exact file path and what was verified.

## Final Response Pattern

Keep the handoff concise:

```text
Created: /absolute/path/to/<subject>-walkthrough.html

Covers: <the guided sequence and the centerpiece>.
Evidence: <repo/code/source basis>.
Verified: <browser interactions, console, viewport checks>.
Caveat: <most important simplification or open issue, if any>.
```
