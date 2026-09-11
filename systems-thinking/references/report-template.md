# Systems Thinking Review Report Template

Section outline for the conversational Markdown report. Finding fields, enums, and required values live only in [findings-schema.md](findings-schema.md). Preserve those fields when adapting headings or omitting empty optional sections.

## Contents

1. Review target
2. Executive summary
3. System model
4. Key system dynamics
5. Findings summary
6. Detailed findings
7. Positive system patterns
8. Cross-cutting recommendations
9. Open questions and uncertainties
10. Suggested validation plan

## Example finding

### ST-001 — Consumer retries republish without backoff

**Confidence:** High
**Kind:** Risk
**Severity:** High
**Status or attribution:** Introduced by change
**Evidence class:** Observed
**Verification state:** Proposed

#### Relevant context

**Source:** `src/ingest/consumer.rs:112-128` — `republish_on_write_error`

```text
if let Err(e) = write(&event) {
    producer.send(topic, event)?;   // retry
}
```

#### Comment

A failed write republishes the event to the same topic with no attempt count, delay, or ceiling, so a persistently failing event circulates indefinitely and adds load exactly when the write path is already degraded.

#### Why this matters

```text
write failure republishes to source topic
→ failed events accumulate alongside new traffic
→ consumer throughput drops as retry share grows
→ recovery time extends; lag alert fires after the backlog is already large
```

#### Affected system behavior

- **Qualities:** reliability, recovery time, operability
- **Affected actors/components:** Flink consumer, `events.raw` topic
- **Blast radius:** consumer group / ingest pipeline

#### Recommendation

Attach an attempt count to the republished event and route past a ceiling to the existing dead-letter topic; add delay proportional to attempt count.

#### Tradeoffs and alternatives

Dead-lettering makes some failures visible as data loss requiring manual replay. Alternatives: in-process bounded retry, or pause partition consumption on repeated failure.

#### Verification

In a scratch environment, publish one event that fails the write and observe whether its offset recurs.

#### Assumptions

The dead-letter topic referenced in `config/kafka.yml` is consumed.
