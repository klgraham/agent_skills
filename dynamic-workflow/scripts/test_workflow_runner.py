#!/usr/bin/env python3
"""Self-contained tests for workflow_runner.py using fake Codex and Claude executables."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


RUNNER = Path(__file__).with_name("workflow_runner.py")


def run(*args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run([sys.executable, str(RUNNER), *args], text=True, capture_output=True)
    if result.returncode != expected:
        raise AssertionError(
            f"expected exit {expected}, got {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="dynamic-workflow-test-") as temporary:
        root = Path(temporary)
        fake = root / "fake-codex"
        fake.write_text(
            """#!/usr/bin/env python3
import json, pathlib, sys
args = sys.argv[1:]
out = pathlib.Path(args[args.index('--output-last-message') + 1])
model = args[args.index('--model') + 1] if '--model' in args else 'inherit'
prompt = sys.stdin.read()
if 'List values' in prompt:
    value = {'values': ['alpha', 'beta']}
elif 'Inspect' in prompt:
    item = prompt.split('Inspect ', 1)[1].split('.', 1)[0]
    value = {'item': item, 'ok': True}
elif 'Summarize' in prompt:
    value = {'summary': 'two inspected'}
elif 'Loop round' in prompt:
    round_number = int(prompt.split('Loop round ', 1)[1].split('.', 1)[0])
    value = {'done': round_number >= 2}
else:
    value = {'ok': True}
value['_model'] = model
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(value))
print(json.dumps({'type': 'fake.complete'}))
""",
            encoding="utf-8",
        )
        fake.chmod(0o755)
        fake_claude = root / "fake-claude"
        fake_claude.write_text(
            """#!/usr/bin/env python3
import json, sys
args = sys.argv[1:]
model = args[args.index('--model') + 1] if '--model' in args else 'inherit'
prompt = sys.stdin.read()
value = {'harness': 'claude', 'prompt': prompt, '_model': model,
         '_tools': args[args.index('--tools') + 1]}
envelope = {'type': 'result', 'result': json.dumps(value)}
if '--json-schema' in args:
    envelope['structured_output'] = value
print(json.dumps(envelope))
""",
            encoding="utf-8",
        )
        fake_claude.chmod(0o755)
        schema = {"type": "object"}
        spec = {
            "version": 1,
            "name": "runner-self-test",
            "workdir": str(root),
            "sandbox": "read-only",
            "max_concurrency": 2,
            "model_policy": {
                "strategy": "balanced",
                "models": {
                    "fast": "test-fast",
                    "standard": "test-standard",
                    "strong": "test-strong"
                }
            },
            "stages": [
                {
                    "id": "discover",
                    "type": "agent",
                    "model_role": "discovery",
                    "prompt": "List values.",
                    "output_schema": schema
                },
                {
                    "id": "inspect",
                    "type": "map",
                    "model_role": "verification",
                    "source": "results.discover.values",
                    "prompt": "Inspect {{item}}.",
                    "output_schema": schema,
                },
                {
                    "id": "loop-check",
                    "type": "loop",
                    "max_rounds": 3,
                    "prompt": "Loop round {{round}}. Previous: {{previous_json}}",
                    "output_schema": schema,
                    "until": {"path": "done", "equals": True},
                },
                {
                    "id": "report",
                    "type": "reduce",
                    "inputs": ["inspect", "loop-check"],
                    "prompt": "Summarize {{results_json}}",
                    "output_schema": schema,
                },
            ],
        }
        workflow = root / "workflow.json"
        workflow.write_text(json.dumps(spec), encoding="utf-8")
        state = root / "state"

        run("validate", str(workflow))
        preview = run("preview", str(workflow))
        assert "Worker upper bound: 5 plus dynamically discovered map items" in preview.stdout
        assert "Model policy: balanced" in preview.stdout
        assert "Harness: codex" in preview.stdout
        assert "discover: agent; role=discovery; model=test-fast" in preview.stdout
        assert "inspect: map; role=verification; model=test-strong" in preview.stdout
        run("run", str(workflow), "--state-dir", str(state), "--codex-bin", str(fake), expected=2)
        run(
            "run",
            str(workflow),
            "--approve",
            "--state-dir",
            str(state),
            "--codex-bin",
            str(fake),
        )
        result = json.loads((state / "result.json").read_text(encoding="utf-8"))
        assert result["completed"] == ["discover", "inspect", "loop-check", "report"]
        assert len(result["results"]["inspect"]) == 2
        assert result["results"]["discover"]["_model"] == "test-fast"
        assert result["results"]["inspect"][0]["result"]["_model"] == "test-strong"
        assert result["results"]["loop-check"]["result"]["_model"] == "test-standard"
        assert result["results"]["report"]["_model"] == "test-strong"
        assert result["results"]["loop-check"]["satisfied"] is True
        assert len(result["results"]["loop-check"]["rounds"]) == 2
        resumed = run(
            "run",
            str(workflow),
            "--approve",
            "--resume",
            "--state-dir",
            str(state),
            "--codex-bin",
            str(fake),
        )
        assert "checkpoint found; skipping" in resumed.stdout

        write_spec = dict(spec, name="write-test", sandbox="workspace-write")
        write_workflow = root / "write.json"
        write_workflow.write_text(json.dumps(write_spec), encoding="utf-8")
        denied = run(
            "run",
            str(write_workflow),
            "--approve",
            "--state-dir",
            str(root / "write-state"),
            "--codex-bin",
            str(fake),
            expected=2,
        )
        assert "requires --allow-writes" in denied.stderr

        invalid_policy = dict(spec)
        invalid_policy["name"] = "invalid-policy"
        invalid_policy["model_policy"] = {
            "strategy": "balanced",
            "models": {"fast": "test-fast", "standard": "test-standard"},
        }
        invalid_workflow = root / "invalid-policy.json"
        invalid_workflow.write_text(json.dumps(invalid_policy), encoding="utf-8")
        invalid = run("validate", str(invalid_workflow), expected=2)
        assert "missing tiers: strong" in invalid.stderr

        claude_spec = {
            "version": 1,
            "name": "claude-self-test",
            "harness": "claude",
            "workdir": str(root),
            "sandbox": "read-only",
            "stages": [
                {
                    "id": "inspect",
                    "type": "agent",
                    "prompt": "Inspect with Claude.",
                    "output_schema": schema,
                }
            ],
        }
        claude_workflow = root / "claude.json"
        claude_workflow.write_text(json.dumps(claude_spec), encoding="utf-8")
        claude_preview = run("preview", str(claude_workflow))
        assert "Harness: claude" in claude_preview.stdout
        assert "Claude tools: Read, Glob, Grep, WebFetch, WebSearch" in claude_preview.stdout
        claude_state = root / "claude-state"
        run(
            "run",
            str(claude_workflow),
            "--approve",
            "--state-dir",
            str(claude_state),
            "--agent-bin",
            str(fake_claude),
        )
        claude_result = json.loads((claude_state / "result.json").read_text(encoding="utf-8"))
        assert claude_result["result"]["harness"] == "claude"
        assert claude_result["result"]["prompt"] == "Inspect with Claude."
        assert "Read" in claude_result["result"]["_tools"]
        assert "Edit" not in claude_result["result"]["_tools"]

        unsafe_claude = dict(claude_spec, name="unsafe-claude", claude_tools=["Read", "Bash"])
        unsafe_workflow = root / "unsafe-claude.json"
        unsafe_workflow.write_text(json.dumps(unsafe_claude), encoding="utf-8")
        unsafe = run("validate", str(unsafe_workflow), expected=2)
        assert "read-only Claude workflows cannot enable: Bash" in unsafe.stderr

    print("all workflow runner tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
