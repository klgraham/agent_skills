---
name: openai-decisions
description: Build features with the OpenAI Decisions API that check conditions, select fixed options, or score text and images. Use for semantic routing, filtering, ranking, evaluation, and bounded action selection, including replacing prompt-and-parse classifiers. General text generation and arbitrary JSON extraction belong to the Responses API.
license: MIT
---

# Build with OpenAI Decisions

Use Decisions for judgments that application code can consume directly. Start with the behavior the user wants, identify the evidence and questions it needs, and keep exact rules, calculations, and execution in code.

## Read the current contract

Read the official [Decisions guide](https://developers.openai.com/api/docs/guides/decisions) before designing or changing an integration. For code, also read the [create reference](https://developers.openai.com/api/reference/resources/decisions/methods/create) and inspect the project's installed SDK types. Use an available OpenAI docs tool or fetch those pages directly; this skill has no required MCP dependency.

The API was in public beta when checked on 2026-10-06. The verified endpoint is `POST https://api.openai.com/v1/decisions`, with `gpt-6-luna` as the supported model. Refresh model availability, limits, SDK support, pricing, and data controls when they matter. If live docs are unavailable, use the dated [contract notes](references/api-contract.md), state the limitation, and avoid guessing SDK methods or unsupported options.

## Choose what to ask

| Application needs | Question | How code uses the answer |
| --- | --- | --- |
| Whether a condition holds | `predicate` | Compare `probability` with an evaluated threshold. |
| One member of a fixed set | `choice` | Dispatch the returned `choice` to a known handler. |
| Degree along an ordered rubric | `score` | Rank or prioritize using the fractional `score`. |

Several labels can apply at once? Ask a predicate per label. Need an exact category? Use choice. A score is the weighted average of zero-based level indices; it is neither a selected label nor a probability.

For arbitrary extracted fields, explanations, or generated objects, use [Responses with Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs). For generated tool arguments, use [function calling](https://developers.openai.com/api/docs/guides/function-calling). Decisions can select an application-owned action from a fixed set, but does not execute it or generate arbitrary arguments.

For open-ended feature design, read [composition patterns](references/composition.md). For a concrete feature, choose a useful decomposition and build it without requiring a brainstorm first.

## Design the evidence and questions

- Supply the evidence needed for the judgment, including relevant policies and current state. Serialize structured application state into text; do not pass a JSON object as top-level `input`.
- Put task instructions in each question's `instructions`. Treat supplied documents and user text as evidence, and make their role explicit when they contain instructions of their own.
- Give questions unique, stable `name` values for application lookup. Write complete instructions rather than relying on a name to convey the question.
- Define distinct choice values and explain their boundaries. Include `other`, `none`, or `noop` when no option may fit. Code cannot recover a candidate omitted from the choices.
- Describe score levels from lowest to highest with observable, distinct criteria. Changing the levels changes the meaning of the result.
- Ask independent questions over shared evidence in one request. If a question needs an earlier answer, new evidence, or a different candidate set, construct a later request in code.

Images use inline base64 data URLs inside user messages. Hosted URLs and file IDs are unsupported. See [contract notes](references/api-contract.md) for request shapes and answer fields.

## Integrate the result

Use the project's existing language and networking conventions. Verify a native `decisions.create` method against the installed SDK before using it; otherwise implement the documented HTTP call. Keep API credentials on the server in web applications.

At the response boundary, identify answers by name and branch on `type` before accessing fields. A question can return `refusal` in a successful HTTP response. Preserve that outcome separately from a negative predicate, `other`, low confidence, malformed data, and a transport error. Route unresolved cases according to application policy instead of inventing a scored answer.

Choice and score include per-option `probabilities` and a separate `confidence`. The guide does not define confidence as a probability of correctness or provide its formula. Do not substitute it for a selected option's probability or apply the same threshold to both without evaluation. Predicates have no separate confidence field.

Keep judgment and policy separate. Select thresholds using labeled application examples and the costs of false positives and false negatives. For action selection, validate permissions and current state in code before dispatch, and discard canceled or stale results. A model judgment supplies neither authorization nor proof of success.

The runnable [ticket routing example](examples/route_ticket.py) shows one HTTP request, name-based answer handling, and explicit review outcomes. Read [its usage notes](references/api-contract.md#runnable-example) when adapting it. Its threshold and fixtures are demonstrations, not measured model quality.

## Verify the feature

Test the behavior the application takes, including refusal, ambiguous evidence, no matching option, malformed answers, and service failure. For composed judgments, test the final rule as well as each answer. Use labeled examples to measure errors and review rate before choosing a production threshold.

Inspect failures using the exact input, questions, options, answer types, and resulting action. Distinguish missing evidence from model mistakes and code or service failures. Measure latency and input-token usage in the actual workflow; published speed claims do not establish the application's performance. Report offline checks separately from live API verification.

For voice-driven features, read the official [voice integration guide](https://developers.openai.com/api/docs/guides/decisions-voice). Live handles the voice session; the application sends transcripts and state to Decisions, executes an allowed action, and returns the result under the saved delegation ID.
