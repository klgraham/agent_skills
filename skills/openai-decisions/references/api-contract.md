# Decisions contract notes

Checked on 2026-10-06 against the official [guide](https://developers.openai.com/api/docs/guides/decisions), [API reference](https://developers.openai.com/api/reference/resources/decisions/methods/create), and [Python SDK resource](https://github.com/openai/openai-python/blob/main/src/openai/resources/decisions.py). Refresh these sources before relying on beta behavior. These notes cover common integration traps rather than the full schema.

## Request shapes

Send JSON to `POST https://api.openai.com/v1/decisions` with bearer authentication. Required fields are `model`, `input`, and `questions`. The checked model is `gpt-6-luna`.

`input` accepts a string or an array of user messages. Message content can be a string or `input_text` and `input_image` parts. Non-user roles, tools, audio, files, and item references are unsupported. A request permits at most 128 images, supplied as base64 data URLs.

An image message has this shape; replace the placeholder with real encoded bytes:

```json
{
  "role": "user",
  "content": [
    {"type": "input_text", "text": "Inspect the device's screen."},
    {"type": "input_image", "image_url": "data:image/png;base64,<encoded-bytes>"}
  ]
}
```

Question shapes:

```json
[
  {
    "type": "predicate",
    "name": "screen_cracked",
    "instructions": "Is there a visible crack in the screen? Ignore reflections."
  },
  {
    "type": "choice",
    "name": "device",
    "instructions": "Which device is shown?",
    "choices": [
      {"value": "phone", "description": "A handheld phone."},
      {"value": "tablet", "description": "A tablet computer."},
      {"value": "other", "description": "Neither device or insufficient evidence."}
    ]
  },
  {
    "type": "score",
    "name": "screen_damage",
    "instructions": "Rate visible physical damage to the screen.",
    "levels": [
      {"label": "None", "description": "No visible physical damage."},
      {"label": "Minor", "description": "Scratches, with no visible crack."},
      {"label": "Major", "description": "Visible cracks or shattered glass."}
    ]
  }
]
```

`instructions` is a string. Choice values can be strings or booleans, with optional descriptions. Numeric choice values are not part of the checked schema. Score levels require labels and may include descriptions. Names are optional in the schema; this skill recommends unique names to simplify application handling.

## Answers

The response includes `model`, `answers`, and `usage`. Answers arrive in question order and echo names, or use null for an unnamed question. Branch on each answer's type:

| Type | Result fields |
| --- | --- |
| `predicate` | `probability` from 0 to 1 |
| `choice` | `choice`, `probabilities` entries with `value` and `probability`, `confidence` |
| `score` | `score`, `probabilities` entries with numeric `value`, `label`, and `probability`, `confidence` |
| `refusal` | `name` and `type`; no scored answer to consume |

For a score with probabilities `[0.1, 0.7, 0.2]`, the result is `0 * 0.1 + 1 * 0.7 + 2 * 0.2 = 1.1`. Keeping that value preserves information lost by rounding to a label. Rubric index spacing is an application design choice, not a physical measurement.

Do not invent Responses parameters such as `tools`, `response_format`, or conversation IDs for this endpoint. Check the current reference for any requested parameter. A Python SDK response wrapper called `with_streaming_response` does not itself establish support for model token streaming.

## Runnable example

The standard-library example prints a request by default. It does not send customer data or spend API tokens unless `--live` is set. Run from the installed skill directory:

```bash
python3 examples/route_ticket.py --text "My receipt has two charges."
python3 -m unittest discover -s examples -p 'test_*.py'
python3 examples/route_ticket.py --response /path/to/recorded-response.json
python3 examples/route_ticket.py --live --text "My receipt has two charges."
```

Live mode requires `OPENAI_API_KEY`. It makes one request with a timeout, reports HTTP or transport errors, and has no automatic retry. It prints the suggested queue, not an executed action. `--min-probability` defaults to an illustrative 0.8 and compares the selected choice's probability, not `confidence`. Response replay should use data recorded for this example's request contract.

The checked Python SDK offers `OpenAI().decisions.create(model=..., input=..., questions=...)` and an async equivalent. Verify the installed package's version and types before adapting that spelling. Raw HTTP is sufficient when that SDK version lacks the endpoint.

For production costs or regulated data, consult current [pricing](https://developers.openai.com/api/docs/pricing) and [data controls](https://developers.openai.com/api/docs/guides/your-data). Do not infer organization eligibility from endpoint support.
