# Automation and comprehension debt

Apply this lens only when automation, generated code, or agent-assisted change materially affects the review surface.

Generation and comprehension are asymmetric:

```text
generation time ≪ understanding and ownership time
```

Evaluate whether:

- generated code duplicates an existing capability;
- reviewers can reconstruct assumptions and invariants;
- tests independently establish behavior rather than mirror implementation;
- abstractions reduce conceptual load or merely add indirection;
- automation can create change faster than review and operations can absorb it;
- system discoverability and deletion keep pace with generation.

Do not object to generated code because it is generated. Comment when the resulting system behavior, evidence, ownership, or comprehensibility is inadequate.
