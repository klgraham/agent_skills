# Feedback loops

Identify reinforcing loops that amplify behavior and balancing loops that constrain it.

### Retry amplification

```text
dependency degradation
→ more retries
→ greater dependency load
→ deeper degradation
```

Look for bounded attempts, exponential delay with jitter, deadlines, budgets, circuit breaking, admission control, or load shedding.

### Complexity

```text
more components
→ harder comprehension and discovery
→ more local workarounds
→ more components
```

Look for deletion, canonical capability discovery, shared invariants, or clear ownership. A new platform is not automatically the answer.

### Fragmentation

```text
poor capability discovery
→ duplicate implementation
→ more alternatives to discover
→ poorer discovery
```

Check whether the easiest path reuses the intended capability and whether legitimate variation is still possible.

### Alert fatigue

```text
noisy alerts
→ lower operator attention
→ slower response
→ more defensive alerts
```

Look for objective-linked signals, actionable ownership, deduplication, and suppression during known incidents.

Other balancing mechanisms include quotas, backpressure, reconciliation, garbage collection, rate limits, automated rollback, and capacity controls.

A causal loop must close. Mark each influence positive or negative, meaning movement in the same or opposite direction with other conditions held fixed. An even number of negative links gives a reinforcing loop; an odd number gives a balancing loop. A cycle of calls or messages alone does not establish either causal polarity.
