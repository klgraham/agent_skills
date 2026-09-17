# Sources of truth

Look for duplicated state, ambiguous ownership, derived data treated as authoritative, caches without invalidation rules, and multiple definitions of the same concept or metric.

For each representation, determine:

- which source is authoritative;
- whether consumers agree on that authority;
- how divergence is detected;
- how conflicts are resolved;
- what behavior occurs during disagreement;
- whether reconciliation is automatic, manual, or absent.

Typical causal mechanism:

```text
two writable representations
→ independent updates
→ divergence
→ behavior depends on read path
→ inconsistent decisions and difficult repair
```
