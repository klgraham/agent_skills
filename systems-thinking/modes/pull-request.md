# Pull request or diff input

Identify base and head revisions and the actual review diff. Use the merge base for a branch or PR comparison unless the supplied diff or user specifies a different baseline. Record that choice. Do not substitute the current working tree for the reviewed head.

Inspect the complete diff, surrounding unchanged code, and at least one relevant upstream or downstream path plus a failure or recovery branch. Trace callers, consumers, tests, schemas, configuration, deployment, migrations, compatibility, and rollback as relevant.

Pay attention to persistent state, public interfaces, async work, retries, caching, fan-out, shared resources, authorization, and commitments that are hard to reverse.

Attribute each risk as Introduced by change, Made more severe by change, Pre-existing, exposed by change, or Unrelated pre-existing architecture. Do not require the PR to fix unrelated architecture. Include pre-existing context only when the change depends on it, worsens it, or the reader needs it to understand the risk.
