---
name: transcript-skill-miner
description: Analyze a current or recent Codex or Claude Code session transcript to find repeated, generalizable tool-use patterns that should become reusable skills, scripts, or references, especially patterns that cause repeated shell, Python, or approval prompts. Use when the user asks to mine a transcript, find skill opportunities, reduce approval prompts, identify recurring automation, or asks what skills they should create. Also use when the user explicitly says they repeatedly perform or approve the same workflow.
---

# Transcript Skill Miner

Mine an agent-session transcript for reusable abstractions. Favor opportunities that replace repeated ad hoc execution with reviewed scripts and narrow, trustworthy skill instructions.

## Locate the relevant transcript

Prefer a transcript the user names or attaches. Otherwise inspect the current host's likely session storage, in this order:

1. `/mnt/transcripts/` when the host exposes session transcripts there;
2. `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects/` for Claude Code JSONL sessions;
3. `${CODEX_HOME:-$HOME/.codex}/sessions/` for Codex `rollout-*.jsonl` sessions.

Choose the most recent transcript associated with the current workspace when paths or metadata make that relationship visible. Do not silently analyze an unrelated recent session. If several transcripts are plausible, show the candidates and ask the user which one to use.

If no transcript can be read, explain which locations were checked and ask the user to provide or export one.

Treat transcripts as potentially sensitive. Do not reproduce secrets, tokens, personal data, or large private excerpts in the report.

## Extract tool-use episodes

Identify each shell, code-execution, file-creation, file-conversion, browser, connector, or repeated manual sequence. For each episode record:

- the user's intended outcome;
- tools or commands used;
- number and type of approvals or interruptions;
- whether similar code or command structure appeared elsewhere;
- inputs, outputs, and environment assumptions;
- failure, retry, or correction patterns;
- which judgment was domain-specific and which mechanics were reusable.

Normalize host-specific event names into conceptual operations. A Codex `exec_command`, a Claude Bash tool call, and a pasted Python script may represent the same abstraction.

## Score abstraction opportunities

Give priority to patterns with several of these signals:

- repeated in the transcript or across user-identified sessions;
- required multiple approval prompts;
- used boilerplate shell or Python;
- transformed files or structured data predictably;
- had a stable input/output contract;
- required deterministic validation;
- was generalizable beyond the immediate dataset or repository;
- caused visible user frustration or repeated correction.

Do not propose a skill for:

- one-off exploratory code tied tightly to one dataset;
- a simple command that needs no procedural guidance;
- business rules that should remain explicit user decisions;
- a workflow already handled well by an installed skill or purpose-built tool;
- unsafe automation whose only benefit is bypassing meaningful approval.

## Choose the smallest reusable form

For each surviving opportunity, recommend one of:

- **script only** for a deterministic transformation with a stable CLI;
- **skill with script** when judgment selects or configures a deterministic operation;
- **skill with references** when the repeated cost is rediscovering a schema, contract, or policy;
- **workflow** when several isolated workers, barriers, or verification passes are genuinely required;
- **no new artifact** when documentation, an alias, or an existing capability is sufficient.

Prefer narrow composable skills over a broad catch-all.

## Report the result

Return a ranked table with:

| Rank | Opportunity | Transcript evidence | Reusable contract | Recommended form | Approval reduction | Risks or limits |
|---|---|---|---|---|---|---|

Then provide a short specification for the top one to three opportunities:

- proposed skill name and trigger description;
- two or three concrete example requests;
- reusable scripts, references, or assets;
- required inputs and produced outputs;
- validation and safety boundaries;
- host-specific adapters, if any.

Quote only the smallest redacted transcript fragments needed to support a recommendation. Distinguish observed repetition from an inferred future opportunity.

Do not create or install the proposed skills unless the user explicitly asks.
