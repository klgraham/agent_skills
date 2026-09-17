# Visualize a system

Represent a model so the reader can inspect the property they care about.

## Load

Read [visualization conventions](../references/visualization-conventions.md). Load only the principle that governs the view, such as feedback loops for a causal-loop diagram or stocks and flows for accumulation. No other principle is required by default.

## Procedure

1. Reuse the supplied model after checking scope and evidence. If missing, build only the relevant portion using [understand a system](understand-system.md).
2. Identify the question the visual should answer. Choose an architecture, causal, causal-loop, stock-flow, sequence, dependency, or state-transition view accordingly.
3. Define nodes, edges, boundaries, and a legend before styling. Preserve stable identifiers, source evidence, uncertainty, polarity, and delay where applicable.
4. Choose a renderer already available in the environment. Mermaid fits compact text diagrams; D2 can produce static diagrams; React Flow supports custom interactive views; Cytoscape supports graph exploration and analysis. These are options, not dependencies. Honor the user's chosen format.
5. For requested interactive software review reports, use the existing [review schema](../references/findings-schema.md) and `scripts/build_report.py --strict`. It renders SVG and Mermaid from one model. Do not fabricate review findings to get a general diagram.
6. Inspect the rendered result when rendering is available. Check edge direction, labels, loops, boundary membership, readability, and legend consistency. Check selection and evidence navigation for interactive views. State any rendering check that could not be performed.

## Deliver

Provide the visual in the requested form with a legend, scope, source or evidence references, and unresolved relationships. A graph's appearance is not evidence for its causal claims. Keep the model and its views consistent; change the model before regenerating its views.
