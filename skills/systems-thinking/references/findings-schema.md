# Findings Payload Schema

The renderer consumes one JSON file and produces both deliverables from it. Write the analysis here, not directly into HTML or Markdown, so the two documents cannot disagree and the system model is declared once.

`scripts/build_report.py` validates this payload and reports problems on stderr. Fix the payload rather than the outputs.

## Top level

```json
{
  "meta": { ... },
  "system_model": { ... },
  "headline": ["..."],
  "findings": [ ... ],
  "open_questions": [ ... ],
  "validation_plan": [ ... ]
}
```

`meta`, `system_model`, and `findings` are required. `findings` may be an empty array — that is a legitimate result, and the renderer produces a report stating so.

## meta

```json
{
  "slug": "af-reactor-pr-4820",
  "title": "Ingest retry path — PR 4820",
  "review_mode": "pull_request",
  "target": "appfolio/af_reactor PR #4820 (head 9f2c1ab)",
  "baseline": "master @ 4de77c0",
  "date": "2026-08-05",
  "reviewer_note": "Static review only; no runtime access.",
  "inferred_purpose": "Reduce duplicate ingest events after broker restarts.",
  "scope_included": ["src/ingest/**", "config/kafka.yml"],
  "scope_excluded": ["generated protobuf", "vendored deps"],
  "depth": "Changed path plus one upstream producer and the consumer retry branch.",
  "sampled_paths": ["produce → topic → consumer → RDS write", "consumer failure → retry → DLQ"],
  "coverage_limits": ["No load or failure-injection testing performed."],
  "unavailable_evidence": ["Production retry metrics", "Consumer group lag history"],
  "assumptions": ["Single consumer group; at-least-once delivery is acceptable downstream."],
  "obsidian_tags": ["review/systems", "af-reactor"]
}
```

`review_mode` is one of `repository`, `pull_request`, `architecture`, or `combined`. `slug` drives output filenames. Everything else is optional but omitting scope, depth, or coverage limits weakens the report — those fields are what let a reader calibrate how much to trust it.

## system_model

Declare nodes and edges once. The script derives the HTML SVG diagram and the Markdown Mermaid block from this, so they always match.

```json
{
  "summary": "One or two sentences on the shape of the system as reviewed.",
  "nodes": [
    {"id": "producer", "label": "Ingest producer", "kind": "service", "note": "Owned by data platform"},
    {"id": "topic", "label": "events.raw", "kind": "queue"},
    {"id": "consumer", "label": "Flink consumer", "kind": "service"},
    {"id": "rds", "label": "events table", "kind": "store"},
    {"id": "operator", "label": "On-call engineer", "kind": "actor"},
    {"id": "vendor", "label": "Vendor webhook", "kind": "external"}
  ],
  "edges": [
    {"from": "producer", "to": "topic", "label": "publish", "kind": "async"},
    {"from": "topic", "to": "consumer", "kind": "async"},
    {"from": "consumer", "to": "rds", "label": "upsert", "kind": "data"},
    {"from": "consumer", "to": "topic", "label": "retry", "kind": "async", "note": "no backoff"}
  ],
  "trust_boundaries": [
    {"label": "AppFolio VPC", "nodes": ["producer", "topic", "consumer", "rds"]}
  ],
  "sources_of_truth": ["events table is authoritative; topic is a transport only"]
}
```

Node `kind`: `actor`, `service`, `store`, `queue`, `external`, or `process`. Edge `kind`: `sync`, `async`, `data`, or `control`.

An edge that points backward in the flow is rendered as a distinct feedback edge, which is usually the most informative thing on the diagram — declare real loops rather than flattening them.

Keep the model to roughly 5–15 nodes. Above 24 the script warns; the fix is narrower scope, not a bigger picture.

## findings

```json
{
  "id": "F1",
  "title": "Consumer retries republish without backoff or attempt ceiling",
  "kind": "risk",
  "severity": "high",
  "status": "introduced_by_change",
  "evidence_class": "observed",
  "confidence": "high",
  "node_ids": ["consumer", "topic"],
  "lenses": ["Reinforcing loops", "Unbounded accumulation"],
  "sources": [
    {
      "location": "src/ingest/consumer.rs:112-128",
      "lang": "rust",
      "excerpt": "if let Err(e) = write(&event) {\n    producer.send(topic, event)?;   // retry\n}",
      "note": "No attempt counter is attached to the republished event."
    }
  ],
  "comment": "A failed write republishes the event to the same topic with no attempt count, delay, or ceiling, so a persistently failing event circulates indefinitely and adds load exactly when the write path is already degraded.",
  "causal_chain": [
    "write failure republishes to source topic",
    "failed events accumulate alongside new traffic",
    "consumer throughput drops as retry share grows",
    "recovery time extends; lag alert fires after the backlog is already large"
  ],
  "affected": ["reliability", "recovery time", "operability"],
  "recommendation": "Attach an attempt count to the republished event and route past a ceiling to the existing dead-letter topic; add delay proportional to attempt count.",
  "tradeoffs": "Dead-lettering makes some failures visible as data loss requiring manual replay, which is a real operator cost, but it is bounded and observable rather than silent and unbounded.",
  "alternatives": ["In-process bounded retry with the event held out of the topic", "Pause partition consumption on repeated failure"],
  "acceptance": "Acceptable as-is only if write failures are known to be transient within seconds and the topic has retention short enough to drop stuck events.",
  "assumptions": ["The dead-letter topic referenced in config/kafka.yml is consumed."],
  "verification": {
    "method": "In a scratch environment, publish one event that fails the write and observe whether its offset recurs.",
    "state": "proposed",
    "result": null
  }
}
```

Field notes:

- `kind`: `risk` or `positive`. Positive patterns belong in the report only when consequential — they tell the reader what to protect during a refactor.
- `severity` applies to risks only; use `null` for positive patterns.
  - **critical** — credible data loss, security compromise, cross-tenant exposure, widespread outage, unrecoverable inconsistency, or a severe one-way commitment.
  - **high** — major reliability, correctness, operability, or architectural degradation with broad effects.
  - **medium** — meaningful maintainability, observability, scalability, coordination, or recovery risk.
  - **low** — limited improvement, small blast radius, or low likelihood.
- `status` for a pull request or diff: `introduced_by_change`, `made_more_severe_by_change`, `pre_existing_exposed_by_change`, or `unrelated_pre_existing`. For repository or architecture review: `architectural`. For any positive pattern: `positive_pattern`. Do not hold a pull request responsible for unrelated architecture — include pre-existing context only when the change depends on it, worsens it, or the reader needs it.
- `evidence_class`: `observed` or `inferred`. There is no `unknown`; unresolved uncertainty goes to `open_questions`.
- `confidence`: `high` (clear source evidence), `medium` (evidence plus stated reasonable assumptions), `low` (plausible and decision-relevant but needs missing runtime, organizational, or domain evidence).
- `node_ids` link the finding to the diagram. These drive the interaction — omitting them costs the report its most useful feature.
- `sources` may hold several entries when a finding depends on multiple locations; explain the relationship in each `note`. Excerpts should be the smallest span that still makes sense on its own. Redact secrets, keep structure: `api_key = "<redacted>"`.
- `causal_chain` is an ordered list of steps rendered as a trace. Each step should be something a reader could dispute on its own.
- `verification.state`: `proposed`, `executed`, or `blocked`. Anything not actually run is `proposed`. If `executed`, put what happened in `result`.

## open_questions

```json
[{"question": "Is the dead-letter topic consumed by anything today?",
  "affects": ["F1"],
  "why_it_matters": "If nothing consumes it, dead-lettering converts an unbounded loop into silent loss and F1's recommendation changes.",
  "how_to_resolve": "Check consumer groups on the dlq topic."}]
```

## validation_plan

Ordered, each item tied to findings, each with an honest state.

```json
[{"order": 1,
  "action": "Reproduce the retry loop with one poison event in a scratch environment.",
  "affects": ["F1"],
  "state": "proposed",
  "notes": "Read-only against shared infrastructure; do not run in production."}]
```

## Minimal valid payload

A review that found nothing substantive is still a complete review:

```json
{
  "meta": {"slug": "tiny-cli", "title": "tiny-cli repository review",
           "review_mode": "repository", "target": "tiny-cli @ 3f1a2b0",
           "date": "2026-08-05",
           "coverage_limits": ["Single pass over 400 lines; no runtime observation."]},
  "system_model": {"summary": "Single-process CLI reading stdin and writing stdout.",
                   "nodes": [{"id": "cli", "label": "tiny-cli", "kind": "process"}],
                   "edges": []},
  "headline": ["No system-level findings passed the evidence gate at this scope."],
  "findings": [],
  "open_questions": [],
  "validation_plan": []
}
```
