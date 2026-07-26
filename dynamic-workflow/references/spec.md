# Workflow specification

## Contents

- Top-level fields
- Model policies
- Templates
- Stage types
- Safety and checkpoints
- Complete example

## Top-level fields

The workflow file is JSON. Required fields are `version`, `name`, `workdir`, and `stages`.

```json
{
  "version": 1,
  "name": "audit-routes",
  "description": "Audit and verify route authentication",
  "workdir": "/absolute/path/to/repository",
  "sandbox": "read-only",
  "max_concurrency": 4,
  "timeout_seconds": 900,
  "retries": 1,
  "model_policy": {
    "strategy": "balanced",
    "models": {
      "fast": "CURRENT_FAST_MODEL_ID",
      "standard": "CURRENT_STANDARD_MODEL_ID",
      "strong": "CURRENT_STRONG_MODEL_ID"
    }
  },
  "args": {},
  "stages": []
}
```

- `name` must contain only lowercase letters, digits, and hyphens.
- `workdir` must be an existing absolute directory.
- `sandbox` is `read-only` or `workspace-write`. The latter also requires the runner's `--allow-writes` flag.
- `max_concurrency` is 1 through 16 and applies to map workers.
- `timeout_seconds` is per worker. `retries` is 0 through 3.
- `model` is an optional single-model override for every stage. Do not combine it with `model_policy`.
- `model_policy` selects models by semantic stage role. See the next section.
- `args` contains invocation data available to templates.

Stages execute in listed order. Each stage is a barrier: the next begins only after the current stage finishes and its checkpoint is written.

## Model policies

Use a policy to keep quality/cost intent separate from model IDs:

```json
{
  "model_policy": {
    "strategy": "balanced",
    "models": {
      "fast": "CURRENT_FAST_MODEL_ID",
      "standard": "CURRENT_STANDARD_MODEL_ID",
      "strong": "CURRENT_STRONG_MODEL_ID"
    },
    "roles": {
      "verification": "strong"
    }
  }
}
```

The supported strategies are:

| Strategy | Discovery | Worker | Verification | Repair | Synthesis |
|---|---|---|---|---|---|
| `inherit` | inherited | inherited | inherited | inherited | inherited |
| `economy` | fast | fast | standard | fast | standard |
| `balanced` | fast | fast | strong | standard | strong |
| `quality` | strong | strong | strong | strong | strong |

For any non-`inherit` strategy, `models` must provide every tier used by that strategy. Codex must choose exact model IDs that are currently available in the user's Codex environment. The runner intentionally contains no hard-coded model catalog.

Stages default to these roles: `agent` and `map` use `worker`, `reduce` uses `synthesis`, and `loop` uses `repair`. Set `model_role` when semantics differ:

```json
{
  "id": "verify",
  "type": "map",
  "model_role": "verification",
  "source": "results.audit.findings",
  "prompt": "Try to refute {{item_json}}.",
  "output_schema": {"type": "object"}
}
```

Optional `model_policy.roles` entries override the chosen strategy's tier for a role. An optional stage-level `model` overrides policy resolution for only that stage. Do not set both `model` and `model_role` on the same stage.

## Templates

Prompts support these data substitutions:

- `{{args}}` or `{{args.key}}`
- `{{results.stage-id}}` or a nested path such as `{{results.discover.files}}`
- `{{results_json}}` for the full prior-results object
- Map only: `{{item}}`, `{{item_json}}`, and `{{index}}`
- Loop only: `{{round}}`, `{{previous}}`, and `{{previous_json}}`

Values ending in `_json` are JSON encoded. Other objects are also encoded rather than evaluated. Missing paths are an error. Templates are string substitution only: they cannot invoke Python, shell, or filesystem operations.

## Stage types

### Agent

Run one isolated Codex worker.

```json
{
  "id": "discover",
  "type": "agent",
  "prompt": "List route files. Return JSON only.",
  "output_schema": {
    "type": "object",
    "required": ["files"],
    "properties": {"files": {"type": "array", "items": {"type": "string"}}},
    "additionalProperties": false
  }
}
```

### Map

Run one worker per item concurrently. Set `items` to a literal array or `source` to a prior result path.

```json
{
  "id": "audit",
  "type": "map",
  "source": "results.discover.files",
  "prompt": "Audit {{item}}. Return JSON only.",
  "output_schema": {"type": "object"}
}
```

Map output is an array preserving input order. Every element records `id`, `status`, and either `result` or `error`. Later stages must not silently discard failures.

### Reduce

Run one synthesis worker. `inputs` optionally limits the prior stage results exposed through `{{results_json}}`.

```json
{
  "id": "report",
  "type": "reduce",
  "inputs": ["audit", "verify"],
  "prompt": "Deduplicate and rank these results:\n{{results_json}}",
  "output_schema": {"type": "object"}
}
```

### Loop

Run one worker repeatedly. The first round receives `previous` as null. Later rounds receive the preceding result. Stop when `until.path` equals `until.equals`, or after `max_rounds`.

```json
{
  "id": "fix-until-clean",
  "type": "loop",
  "max_rounds": 5,
  "prompt": "Round {{round}}. Previous result: {{previous_json}}. Run checks and fix failures.",
  "output_schema": {
    "type": "object",
    "required": ["clean"],
    "properties": {"clean": {"type": "boolean"}}
  },
  "until": {"path": "clean", "equals": true}
}
```

Loop output records all rounds and whether the stop condition was satisfied. Reaching the cap is not success.

## Safety and checkpoints

The runner invokes `codex exec` directly without a shell. Workers are ephemeral and receive the workflow's sandbox and working directory. The workflow itself has no command-execution primitive.

Checkpoints include a SHA-256 hash of the complete spec. `--resume` refuses a checkpoint created from a different spec. `--restart` discards checkpoint progress for the run directory while leaving the workflow file untouched.

## Complete example

```json
{
  "version": 1,
  "name": "verified-route-audit",
  "workdir": "/absolute/path/to/repository",
  "sandbox": "read-only",
  "max_concurrency": 4,
  "model_policy": {
    "strategy": "balanced",
    "models": {
      "fast": "CURRENT_FAST_MODEL_ID",
      "standard": "CURRENT_STANDARD_MODEL_ID",
      "strong": "CURRENT_STRONG_MODEL_ID"
    }
  },
  "stages": [
    {
      "id": "discover",
      "type": "agent",
      "model_role": "discovery",
      "prompt": "Find route handler files under src/routes. Return JSON only.",
      "output_schema": {
        "type": "object",
        "required": ["files"],
        "properties": {"files": {"type": "array", "items": {"type": "string"}}}
      }
    },
    {
      "id": "audit",
      "type": "map",
      "source": "results.discover.files",
      "prompt": "Inspect {{item}} for missing authentication. Return findings as JSON.",
      "output_schema": {"type": "object"}
    },
    {
      "id": "report",
      "type": "reduce",
      "model_role": "synthesis",
      "inputs": ["audit"],
      "prompt": "Return a ranked report. Mark failed workers as coverage gaps.\n{{results_json}}",
      "output_schema": {"type": "object"}
    }
  ]
}
```
