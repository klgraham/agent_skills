# Compose judgments into features

These are application design patterns, not additional API capabilities. Choose the pattern that serves the requested behavior and verify the current [Decisions contract](https://developers.openai.com/api/docs/guides/decisions).

## Routing and bounded actions

Build choices from known handlers and current application state. Add a fallback when none applies. After selection, code validates the result against current availability and permissions, then runs the handler. If an action needs arbitrary extracted arguments, use a separate extraction step with an appropriate API.

For a hierarchy, choose a coarse category first and construct that category's candidates for a second request. Evaluate the hierarchy end to end: an early routing mistake can exclude the right downstream answer.

## Filtering and several labels

Use separate predicates for independently applicable labels, such as relevance and duplicate status. A probability near 0.5 expresses uncertainty about truth, not medium relevance or intensity. Ask for a score when intensity is the desired result.

Let code combine predicates according to the actual rule. A requirement that any serious violation triggers review should not become an average that lets one dimension cancel another.

## Ranking and composite preferences

Retrieve candidates with code or an existing search system, then judge their relevance or quality against shared criteria. A choice selects one available candidate; a score rates an item along an ordered dimension.

For ranking with scores, use consistent level meanings and evidence across items. Keep dimensions separate when users may change their weights. Code can recompute weighted rankings without inference if the evidence and rubrics are unchanged. Evaluate comparability across separate calls rather than assuming it.

## Evidence checks and escalation

Supply a claim and the supporting passage or image, then ask a narrow predicate about support. Decide separately what to do with missing evidence, uncertain support, or refusal. A model judgment does not prove a citation exists; code checks source identifiers and retrieves the actual evidence.

Use Decisions to route a complex task to a reasoning or generation workflow when appropriate. Pass that workflow the original request and evidence, not just the category selected by Decisions.

## Changing state and voice

For interactive features, record which state a request evaluated. Before applying the result, check whether the state still permits it and whether the user canceled. Bound loops by the application's goal, cancellation, and resource budget.

For voice, use the official [Live and Decisions guide](https://developers.openai.com/api/docs/guides/decisions-voice). Decisions accepts text and images; it does not accept raw audio. The application owns transcripts, delegation IDs, action execution, and continuation.

## Evaluate the composed behavior

Maintain labeled examples that include ambiguous inputs, no match, missing evidence, and boundary cases. Measure false positives, false negatives, and review rate for threshold decisions. For actions or routing, measure the final handler outcome. Keep a held-out set so tuning and assessment do not use the same examples.

Record input-token usage and end-to-end latency for the full workflow, including subsequent requests. More questions and sequential branches can change the cost and latency even when an individual judgment is fast.
