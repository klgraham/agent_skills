# Review boundary

Treat a review request as read-only. Do not edit code, post review comments, change a pull request, or mutate external state unless the user explicitly asks for those actions.

Verification items in the report are proposals unless explicitly marked as executed. Execute only safe local or read-only checks, or explicitly authorized experiments in an isolated environment. Do not perform load tests, failure injection, migrations, rollback exercises, or other state-changing actions against production or shared external state without explicit authorization.

State:

- review mode: repository, pull request/diff, architecture, or a combination;
- exact target and baseline;
- included and excluded scope;
- review depth and coverage limits;
- unavailable evidence;
- inferred purpose and important assumptions.

For a pull request, identify the base and head revisions whenever possible. Do not confuse the working tree with the review diff.

Default to a contextual Markdown report in the conversation. Create report files only when requested or explicitly authorized by the host workflow. Analysis and verification do not authorize implementation or publication.
