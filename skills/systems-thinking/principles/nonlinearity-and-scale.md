# Nonlinearity and scale

Do not assume cost grows linearly with traffic, data, tenants, components, or development velocity.

Look for:

- quadratic or all-to-all interaction;
- fan-out and fan-in;
- lock contention and serialized coordination;
- hot keys or partitions;
- shared queues and connection pools;
- synchronized refresh or cache stampedes;
- unbounded cardinality in telemetry or state;
- thresholds where graceful behavior becomes collapse.

Use `10×` as a probing question, not a forecast:

- What happens at 10× traffic, data, tenants, components, or change rate?
- Which resource saturates first?
- Does saturation apply backpressure, shed load, or amplify failure?
