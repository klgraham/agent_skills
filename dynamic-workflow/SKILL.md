---
name: dynamic-workflow
description: Design and run script-backed multi-agent workflows with isolated Codex or Claude workers, structured outputs, barriers, verification stages, bounded loops, and resumable checkpoints. Use when the user explicitly asks for a workflow, ultracode, broad parallelism, or subagent orchestration; or when a task is too wide, long-running, repetitive, or self-grading for one context, such as codebase-wide audits, large migrations, cross-checked research, adversarial verification, per-item classification, or loop-until-clean repair. Do not use for small tasks that fit comfortably in one agent turn.
---

# Dynamic Workflow

Move orchestration state out of the conversation and into a declarative JSON workflow executed by `scripts/workflow_runner.py`. Keep the generated plan inspectable, bounded, and resumable.

## Choose the execution path

Use the current host's direct collaboration or subagent tools when the work needs only a few workers and the parent can comfortably retain every result. Use the runner when any of these apply:

- Process many independent items with the same prompt.
- Preserve intermediate results outside the parent context.
- Require producer/verifier separation.
- Repeat until a machine-checkable stop condition is reached.
- Save, inspect, rerun, or resume the orchestration.

Do not pay the workflow overhead for one-file edits, small bug fixes, or fewer than three modest subtasks.

## Plan before running

1. Read `references/spec.md` before authoring or modifying a workflow.
2. Discover enough scope to estimate worker count and cost. Do not launch workers merely to discover whether a workflow is necessary.
3. Select the smallest fitting pattern:
   - classify then map specialists;
   - discover, map, and reduce;
   - produce then adversarially verify;
   - generate then filter;
   - generate candidates then compare;
   - bounded loop until a structured condition passes.
4. Write the workflow under the current workspace, normally `.codex/workflows/<name>.json` in Codex or `.claude/workflows/<name>.json` in Claude Code. Never write generated workflows inside this skill directory.
5. Set `harness` to `codex` or `claude` for the host that should execute workers. Select a model policy and record current, available model IDs for its tiers. Do not guess model names or embed "latest" aliases without checking the selected environment or official model guidance.
6. Run `preview`, show the user the stages, resolved model per stage, worker upper bound, sandbox, and write policy, and obtain confirmation before a materially expensive or write-capable run.

Commands:

```bash
python3 <skill-dir>/scripts/workflow_runner.py validate .codex/workflows/<name>.json
python3 <skill-dir>/scripts/workflow_runner.py preview .codex/workflows/<name>.json
python3 <skill-dir>/scripts/workflow_runner.py run .codex/workflows/<name>.json --approve
```

Use `--allow-writes` in addition to `--approve` only when the workflow declares `workspace-write` and the user has authorized edits. Never generate or use `danger-full-access`.

The Claude backend defaults to read-only tools (`Read`, `Glob`, `Grep`, and web reads). A Claude `workspace-write` workflow adds `Edit` and `Write` only after `--allow-writes`. If a workflow needs a different Claude tool set, declare and preview `claude_tools`; read-only workflows cannot enable Bash or editing tools.

## Select models by policy

Use `inherit` when the user wants the normal Codex model or available model IDs cannot be verified. Otherwise choose one strategy and assign each stage an honest `model_role`:

- `economy`: favor the fast tier; use standard for verification and synthesis.
- `balanced`: use fast for discovery and bulk work, standard for repair loops, and strong for verification and synthesis.
- `quality`: use strong for every role.

Use roles `discovery`, `worker`, `verification`, `repair`, and `synthesis`. Record exact model IDs under the policy's `models` tier map so preview and reruns are reproducible. Use a stage-level `model` only for a deliberate exception. See `references/spec.md` for routing details.

## Author focused workers

- Give each worker a closed-world task, explicit scope, evidence requirements, and output contract.
- Use JSON Schema for outputs that feed later stages.
- Restate critical constraints in every relevant worker prompt; do not rely on conversation history.
- Keep producers and verifiers in separate stages.
- Mark verifier stages with `model_role: verification`; a map stage otherwise defaults to `worker`.
- Prefer five to ten substantial workers over dozens of trivial workers.
- Make reduce stages deduplicate, rank, reconcile, and identify unverified claims.
- Treat worker failure or unavailable evidence as `unverified`, not `refuted` or successful.
- Set a finite `max_rounds` for every loop and make its `until` condition objective.

## Protect the workspace

- Default to `read-only` discovery, review, research, and verification.
- For large code changes, avoid concurrent workers editing one checkout. Have workers return patches or plans, or give them explicitly isolated worktrees prepared outside the runner.
- Keep `max_concurrency` conservative. The runner caps it at 16.
- Keep secrets and large irrelevant files out of prompts and structured outputs.
- Inspect the preview and JSON file before approval. The runner interprets data; it does not execute Python or shell from the workflow.

## Resume and synthesize

The runner writes checkpoints under `.<harness>/workflow-runs/<workflow-name>/` unless `--state-dir` overrides it. Re-running the same spec with `--resume` skips completed stages. A changed spec cannot reuse an old checkpoint.

After completion:

1. Read `result.json` and any failed-worker records.
2. Fold the final result into the user-facing answer or requested artifact.
3. Verify repository changes normally; workflow success is not a substitute for tests.
4. Report important coverage gaps, unverified claims, stopped loops, and worker failures.

## Forward-test changes to this skill

After changing the runner or spec, run:

```bash
python3 <skill-dir>/scripts/test_workflow_runner.py
python3 <skill-creator-dir>/scripts/quick_validate.py <skill-dir>
```
