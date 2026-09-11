# Delays and dynamics

Search for delay between:

- cause and observable effect;
- write and replication, indexing, or cache invalidation;
- deployment and failure;
- failure and detection;
- metric movement and intervention;
- schema change and consumer migration;
- user action and downstream completion.

Explain why the delay matters. Delayed signals can cause operators or automated controllers to overcorrect, continue unsafe work, or mistake stale state for truth.

Ask whether timestamps, versions, watermarks, lag metrics, or explicit workflow state make the delay visible.

Compare the observation window with the response delay. A short-lived improvement may hide accumulated damage. Check for thresholds, overshoot, oscillation, and hysteresis: reversing an input may not immediately restore the prior state. Distinguish these hypotheses from measured dynamics. For resource saturation and growth mechanisms, load [nonlinearity and scale](nonlinearity-and-scale.md).
