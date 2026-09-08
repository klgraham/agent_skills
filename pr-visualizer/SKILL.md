---
name: pr-visualizer
description: Create and verify source-grounded PR Lens architecture and data-flow walkthroughs for pull requests or local code changes. Use when the user asks to visualize, diagram, explain, or attach an interactive walkthrough to a PR. Do not use for review findings alone or for a general repository walkthrough with no change to compare.
---

# PR visualizer

Turn an exact code change into a PR Lens graph, deterministic SVG diagrams, and a short guided walkthrough. Use PR Lens for the graph contract and renderer. Apply the evidence, narrative, accessibility, and verification discipline from an interactive code walkthrough.

A reviewer must be able to answer three questions at every walkthrough step:

1. Where is this part in the changed system?
2. What changed in behavior or ownership?
3. Which source proves the claim?

## Keep the review boundary

Treat inspection, authoring, validation, rendering, and local preview as read-only review work. Do not post a canvas, edit a pull request, upload an asset, or publish generated files unless the user authorized that external change.

Keep generated files out of the repository by default. Use a temporary directory for read-only work. Use `.pr-lens/` only when the user wants repository-local scratch output and accepts the CLI adding it to `.gitignore`.

## Establish the exact change

For an existing pull request, read structured metadata before the diff:

```bash
gh pr view <number-or-url> --json baseRefName,baseRefOid,headRefName,headRefOid,title,body,commits,files,url
```

Use the reported base and head SHAs. Do not compare against an assumed default branch.

For a local branch, identify its tracked base branch. Fetch when current remote state matters and network access is authorized. Compare from the merge base:

```bash
PRV_MERGE_BASE="$(git merge-base <base-ref> HEAD)"
git diff --find-renames "$PRV_MERGE_BASE"...HEAD
```

Inspect the changed files, the relevant surrounding code, callers, consumers, tests, configuration, and documentation. Read the actual commits when intent or change order matters.

Record the base SHA, head SHA, and claims that support the explanation. For each claim, keep its source path, line range, symbol, and evidence class:

- `VERIFIED IN CODE` for current implementation behavior.
- `VERIFIED BY TEST` for an exercised test or check.
- `STATED IN PR` for intent recorded in PR text.
- `INFERRED` for a conclusion supported by several sources but not stated directly.
- `UNKNOWN` when the sources do not answer the question.

Do not put review findings into the graph. PR Lens explains a change. Report bugs and risks separately with precise source locations.

## Design the reviewer path

Write one internal sentence before authoring:

> For **[reviewer]**, explain **[change and scope]** so they understand **[single takeaway]**.

Choose the smallest set of views that supports that sentence:

- Use an architecture view for ownership, boundaries, dependencies, and blast radius.
- Use a data-flow view only when the change has a real ordered sequence.
- Keep unchanged direct neighbors that explain impact.
- Build lanes from runtimes, tiers, or system boundaries. Do not mirror the folder tree.
- Give the central changed connection `emphasis: "hero"` when one connection carries the change.
- Add child views only when a narrower scope answers a different reviewer question.

For any non-trivial change, add a `walkthrough` with three to seven steps. Each step must describe one behavior, API, architecture, or data-flow change. Put the headline change first. Group consecutive steps that use the same stage. Use the last step for the broad impact summary when that helps orientation.

Write step headings as concrete changes. Write step bodies as observable consequences. Use names and numbers from the source. A step must not merely describe the picture.

## Author the graph document

Read [the complete example](references/example.graph.json) before writing the first graph. Read [the graph document reference](references/graph-document.md) when the example does not answer a field or constraint question.

Use schema version `0.1.1`. Keep all IDs stable, unique, and readable. Add `files` references to the nodes and edges that make source claims. Mark added, modified, removed, and unchanged elements with the matching `delta` value.

Do not invent symbols, calls, ordering, line counts, performance claims, or test results. Label illustrative values in summaries and walkthrough text.

Write the document to a task-specific temporary directory for read-only work:

```bash
PRV_OUTPUT_DIR="$(mktemp -d)"
```

Keep that directory until the user has inspected the result. Tell the user its exact path.

## Validate and render

This skill pins `@coldtea/pr-lens-cli` to `0.4.0`, which matches the bundled `0.1.1` graph reference:

```bash
npx --yes @coldtea/pr-lens-cli@0.4.0 validate "$PRV_OUTPUT_DIR/graph.json"
npx --yes @coldtea/pr-lens-cli@0.4.0 render "$PRV_OUTPUT_DIR/graph.json" \
  --out "$PRV_OUTPUT_DIR/rendered" --theme both
```

Fix every validator error at its source. Do not delete the named element merely to make validation pass.

Read `rendered/manifest.json` to find the emitted SVG names. Read `rendered/drawn.graph.json` before describing the rendered result because repository corrections can change the graph. When a repository map is wrong, edit `.github/pr-lens.yml` only with authorization. Read [the correction reference](references/config.md) before doing so.

## Verify the real artifact

Validation is necessary but does not prove that the visual works. Complete these checks before delivery:

1. Open the exact top-level SVG in a browser and confirm that labels, routes, delta colors, and source links render.
2. Open both themes or verify both theme assets from the manifest.
3. Confirm that the graph title, base SHA, head SHA, node IDs, and walkthrough stages match the inspected change.
4. Confirm that every walkthrough focus points at the claimed nodes, edges, or messages.
5. Inspect the browser console for uncaught errors.
6. Inspect a narrow viewport for clipped labels and horizontal page overflow.
7. Re-run the relevant project tests before claiming behavior is verified.

If you publish a canvas, exercise its next, previous, reset, keyboard, theme, and deep-link behavior. Check both a desktop viewport and a narrow viewport. Motion may help orientation, but no essential claim may depend on animation alone.

Run `python3 scripts/verify_example.py` from this skill directory to verify the bundled graph against the pinned CLI. The script checks successful validation, deterministic rendering, emitted SVG safety, and rejection of a broken reference.

## Deliver or attach the result

For a local request, return the exact SVG paths and a concise verification report. Open the top view for the user when the host supports previews.

For a hosted interactive walkthrough, authorization to publish is required. Push the rendered graph, then share only the view URL:

```bash
npx --yes @coldtea/pr-lens-cli@0.4.0 canvas push "$PRV_OUTPUT_DIR/rendered/drawn.graph.json"
```

Never share the edit URL or its `#w=` token in a public place.

For a pull request, put the top architecture visual near the start of the description. Add one data-flow visual only when sequence matters. Check `gh --version` before using `--attach`. GitHub CLI added that flag in 2.99.0. If the installed CLI is older, use an authorized durable asset URL or the canvas view URL. Do not commit generated SVGs by default.

A PR body must state why the change improves the project, show the visual, and list the checks that prove the change. If the PR fixes an issue, start the body with `Fixes #<number>`.

## Maintain the bundled PR Lens contract

The graph reference, correction reference, example, and license come from PR Lens at commit `b5309c353c79e536a3f6a69713b1b7eb276515a1`. Read [the upstream record](references/upstream.md) before changing the CLI pin or the bundled files. Update the pin, the references, and the verification script together.
