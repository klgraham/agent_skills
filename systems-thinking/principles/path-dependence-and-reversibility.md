# Path dependence and reversibility

Identify changes that create durable commitments:

- schemas and persistent formats;
- public APIs and user-visible contracts;
- external integrations;
- cross-team dependencies;
- stored identifiers or semantics;
- migrations that delete or transform information.

Ask:

- Is this a one-way or two-way decision?
- What must be migrated, coordinated, or deleted later?
- Can old and new versions coexist safely?
- Does a prototype become an accidental permanent interface?
- Is rollback possible after new data has been written?

A small generation cost can conceal a large future migration cost.
