# First principles

Reduce the problem to the entities, operations, and constraints needed to achieve its objective. Separate required behavior from conventions and inherited implementation choices.

- What must exist for the system to function?
- What is conserved, accumulated, transformed, or constrained?
- Which invariants must hold even during partial failure?
- What is the smallest mechanism that satisfies those invariants?
- Which assumptions could be removed without breaking correctness?

Record the evidence for each hard constraint. An undocumented constraint is uncertain, not automatically disposable. Existing architecture can contain valid domain knowledge; trace its purpose before proposing deletion.

Return irreducible entities, required operations, invariants, and assumptions that can be tested. Prefer the simplest model that still explains and predicts the relevant behavior.
