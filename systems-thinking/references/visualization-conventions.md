# Visualization conventions

Choose the representation by the question, then declare its semantics in a visible legend.

| Question | Representation |
|---|---|
| Components and interfaces | Architecture graph |
| Hypothesized cause and effect | Causal graph |
| Reinforcing or balancing behavior | Causal-loop diagram |
| Accumulation and rates | Stock-flow diagram |
| Request or data movement | Flow diagram |
| Ordering and delays over time | Sequence diagram |
| Dependency or blast radius | Dependency graph |
| Legal transitions and recovery | State machine |
| Large model with selectable evidence | Interactive graph explorer |

For custom diagrams, use these defaults unless the user's notation overrides them:

- Solid edges for observed relationships and dashed edges for inferred relationships, with text labels so uncertainty does not depend on appearance alone.
- Label causal influences with `+` for same-direction influence and `-` for opposing influence, holding other conditions fixed. These signs do not mean good and bad.
- Label closed causal loops R or B after checking the product of edge signs. A directed cycle in a dependency graph is not necessarily a reinforcing loop.
- Annotate delay with a duration or a delay label. Do not invent a measured duration.
- Use a cylinder or an explicit stock label for stored state; label flow rates and units where known.
- Enclose system or trust boundaries in labeled groups. Identify which boundary each group means.
- Annotate failure propagation in words; color may reinforce the label but must not carry meaning alone.
- Keep source references or evidence IDs next to the relevant relationships or in selectable details.

Prefer a focused view over shrinking a large graph until labels are unreadable. Split views by question while retaining shared model IDs. Label uncertain relationships and proposed architecture as such.

## Bundled report renderer

The existing report renderer has its own transport notation: `sync`, `async`, `data`, and `control` edges. Its dashed async edges do not encode uncertainty, and a backward edge marks a graph cycle, not proven causal polarity. Preserve its legend; use explicit edge labels and adjacent explanation for inference, delay, or causal signs. Edge notes are payload metadata and should not be the only place a material caveat appears.

The [findings schema](findings-schema.md) defines the supported model. `scripts/build_report.py` already derives inline SVG and Mermaid from that model, so a second rendering script is unnecessary. For a general causal-loop or stock-flow view, use a suitable custom diagram without inventing a review payload.
