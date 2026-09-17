# Constraints and bottlenecks

Find the resource or rule that limits the end-to-end objective. A busy component or visible queue alone does not establish the constraint.

Trace demand through admission, processing, coordination, and completion. Include human approvals and repair capacity when they limit throughput.

- Measure arrival rate, service rate, queue size, and waiting time in compatible units and over a stated interval.
- Identify the constrained resource and distinguish useful work from retries, rework, and discarded output.
- Check sustained demand as well as bursts. Near saturation, small changes in demand can produce large changes in waiting time.
- Ask what would happen if capacity at the suspected constraint increased. Would completed useful work increase, or would another limit immediately take over?
- Predict where the bottleneck moves after intervention, including downstream storage, operators, and recovery work.

For a stock, change over an interval equals inflow minus outflow over that interval. Use this accounting to test a backlog explanation before adding capacity.

Report the primary limiter, evidence, secondary constraints, and a measurement that distinguishes the limiter from its downstream symptoms. Do not claim throughput gains from optimizing work outside the constraint without tracing the end-to-end effect.
