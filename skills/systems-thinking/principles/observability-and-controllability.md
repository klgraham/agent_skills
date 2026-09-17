# Observability and controllability

A system cannot be effectively controlled when important internal state is invisible.

Determine whether operators can answer:

- What is happening?
- Why is it happening?
- Who or what is affected?
- Is the system recovering?
- Which intervention is safe?
- Did the intervention work?

Review logs, metrics, traces, correlation identifiers, audit records, provenance, health signals, and operational dashboards. Prefer signals connected to system objectives and known failure modes over undifferentiated telemetry volume.

Also inspect control surfaces: rollback, pause, drain, replay, reconcile, isolate, rate-limit, or disable. Observation without safe intervention may still leave the system uncontrollable.
