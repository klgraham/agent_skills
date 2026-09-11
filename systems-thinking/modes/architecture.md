# Architecture input

Record the document version, proposal status, and implementation evidence available. Normalize prose or diagrams into actors, components, flows, state, queues, boundaries, controls, and ownership.

Inspect every stated dependency and trust boundary. Ask what happens during slowdown, duplication, reordering, partial success, restart, authorization change, overload, and divergence. Who detects, controls, and repairs each condition?

Treat omitted behavior as uncertainty, not automatically as a defect. Do not treat a proposed safeguard as implemented. In a formal review, use Architectural status for risks and record omitted behavior as a coverage limit or open question.
