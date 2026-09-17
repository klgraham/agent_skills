# Security and permissions

Treat security as an end-to-end property.

Review:

- trust boundaries and identity propagation;
- authorization at the authoritative resource boundary;
- privilege delegation and confused-deputy risks;
- tenant isolation;
- secret handling;
- auditability and provenance;
- behavior when identity or policy services are stale or unavailable;
- revocation during long-running or asynchronous work.

Do not conclude that upstream validation secures downstream resources unless the trust and enforcement chain is explicit.
