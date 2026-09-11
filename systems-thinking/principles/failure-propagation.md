# Failure propagation

Trace failure through synchronous chains, fan-out, shared infrastructure, bulk operations, retries, poison messages, partial writes, timeouts, and global configuration.

Ask:

- Can one tenant, request, key, job, or region exhaust a shared resource?
- Does a small failure trigger more work?
- Can degraded operation continue safely?
- Is failure isolated by tenant, user, region, request, or workload?
- Is a partial operation detectable and recoverable?
- Is the recovery path practiced?

Name the blast-radius boundary and the mechanism that crosses or contains it.
