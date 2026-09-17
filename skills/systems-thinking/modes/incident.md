# Incident input

State the affected system, incident window, timezone, environment, and available logs, traces, deployment history, and operator observations. Distinguish event time from observation time and note clock skew or gaps.

Preserve the sequence of trigger, propagation, detection, response, and recovery. Separate initiating events from latent conditions and operator actions taken with incomplete information.

An incident analysis does not authorize remediation, production experiments, replay, or failure injection. Mark checks Proposed, Executed, or Blocked. Name ongoing unknowns and any containment or recovery claims that still need evidence.

The bundled review renderer has no incident mode. Use an incident narrative unless a formal software review is also requested; in that case choose its actual repository, architecture, pull_request, or combined review mode and record the incident window in scope.
