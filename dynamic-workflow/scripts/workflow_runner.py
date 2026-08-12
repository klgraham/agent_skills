#!/usr/bin/env python3
"""Run declarative, checkpointed workflows with isolated Codex or Claude workers."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any


class WorkflowError(Exception):
    pass


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TEMPLATE_RE = re.compile(r"\{\{\s*([^{}]+?)\s*\}\}")
STAGE_TYPES = {"agent", "map", "reduce", "loop"}
SANDBOXES = {"read-only", "workspace-write"}
MODEL_STRATEGIES = {"inherit", "economy", "balanced", "quality"}
MODEL_TIERS = {"fast", "standard", "strong"}
MODEL_ROLES = {"discovery", "worker", "verification", "repair", "synthesis"}
HARNESSES = {"codex", "claude"}
CLAUDE_READ_TOOLS = ["Read", "Glob", "Grep", "WebFetch", "WebSearch"]
CLAUDE_WRITE_TOOLS = CLAUDE_READ_TOOLS + ["Edit", "Write"]
CLAUDE_READ_ONLY_FORBIDDEN = {"Bash", "Edit", "Write", "NotebookEdit"}
DEFAULT_ROLES = {"agent": "worker", "map": "worker", "reduce": "synthesis", "loop": "repair"}
POLICY_ROUTES = {
    "economy": {
        "discovery": "fast",
        "worker": "fast",
        "verification": "standard",
        "repair": "fast",
        "synthesis": "standard",
    },
    "balanced": {
        "discovery": "fast",
        "worker": "fast",
        "verification": "strong",
        "repair": "standard",
        "synthesis": "strong",
    },
    "quality": {role: "strong" for role in MODEL_ROLES},
}


def load_spec(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WorkflowError(f"cannot read workflow {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise WorkflowError("workflow root must be a JSON object")
    return value


def spec_hash(spec: dict[str, Any]) -> str:
    raw = json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def require_int(value: Any, label: str, low: int, high: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise WorkflowError(f"{label} must be an integer from {low} through {high}")
    return value


def validate_spec(spec: dict[str, Any]) -> None:
    if spec.get("version") != 1:
        raise WorkflowError("version must be 1")
    name = spec.get("name")
    if not isinstance(name, str) or not NAME_RE.fullmatch(name):
        raise WorkflowError("name must use lowercase letters, digits, and hyphens")
    workdir = spec.get("workdir")
    if not isinstance(workdir, str) or not Path(workdir).is_absolute():
        raise WorkflowError("workdir must be an absolute path")
    if not Path(workdir).is_dir():
        raise WorkflowError(f"workdir is not an existing directory: {workdir}")
    sandbox = spec.get("sandbox", "read-only")
    if sandbox not in SANDBOXES:
        raise WorkflowError("sandbox must be read-only or workspace-write")
    harness = spec.get("harness", "codex")
    if harness not in HARNESSES:
        raise WorkflowError(f"harness must be one of {sorted(HARNESSES)}")
    claude_tools = spec.get("claude_tools")
    if claude_tools is not None:
        if not isinstance(claude_tools, list) or not claude_tools or not all(
            isinstance(tool, str) and tool.strip() for tool in claude_tools
        ):
            raise WorkflowError("claude_tools must be a non-empty array of tool names")
        if sandbox == "read-only":
            forbidden = {
                tool
                for tool in claude_tools
                if any(
                    tool == blocked or tool.startswith(f"{blocked}(")
                    for blocked in CLAUDE_READ_ONLY_FORBIDDEN
                )
            }
            if forbidden:
                raise WorkflowError(
                    "read-only Claude workflows cannot enable: " + ", ".join(sorted(forbidden))
                )
    require_int(spec.get("max_concurrency", 4), "max_concurrency", 1, 16)
    require_int(spec.get("timeout_seconds", 900), "timeout_seconds", 1, 86400)
    require_int(spec.get("retries", 0), "retries", 0, 3)
    model = spec.get("model")
    if model is not None and (not isinstance(model, str) or not model.strip()):
        raise WorkflowError("model must be a non-empty string")
    policy = spec.get("model_policy")
    if model is not None and policy is not None:
        raise WorkflowError("choose either model or model_policy, not both")
    if policy is not None:
        if not isinstance(policy, dict):
            raise WorkflowError("model_policy must be an object")
        strategy = policy.get("strategy")
        if strategy not in MODEL_STRATEGIES:
            raise WorkflowError(f"model_policy.strategy must be one of {sorted(MODEL_STRATEGIES)}")
        models = policy.get("models", {})
        if not isinstance(models, dict):
            raise WorkflowError("model_policy.models must be an object")
        for tier, selected_model in models.items():
            if tier not in MODEL_TIERS or not isinstance(selected_model, str) or not selected_model.strip():
                raise WorkflowError("model_policy.models must map fast, standard, or strong to model names")
        roles = policy.get("roles", {})
        if not isinstance(roles, dict):
            raise WorkflowError("model_policy.roles must be an object")
        for role, tier in roles.items():
            if role not in MODEL_ROLES or tier not in MODEL_TIERS:
                raise WorkflowError("model_policy.roles must map known roles to fast, standard, or strong")
        if strategy != "inherit":
            required_tiers = set(POLICY_ROUTES[strategy].values()) | set(roles.values())
            missing = required_tiers - set(models)
            if missing:
                raise WorkflowError(f"model_policy.models is missing tiers: {', '.join(sorted(missing))}")
    if "args" in spec and not isinstance(spec["args"], dict):
        raise WorkflowError("args must be an object")
    stages = spec.get("stages")
    if not isinstance(stages, list) or not stages:
        raise WorkflowError("stages must be a non-empty array")
    seen: set[str] = set()
    for index, stage in enumerate(stages):
        label = f"stages[{index}]"
        if not isinstance(stage, dict):
            raise WorkflowError(f"{label} must be an object")
        stage_id = stage.get("id")
        if not isinstance(stage_id, str) or not ID_RE.fullmatch(stage_id):
            raise WorkflowError(f"{label}.id must use lowercase letters, digits, and hyphens")
        if stage_id in seen:
            raise WorkflowError(f"duplicate stage id: {stage_id}")
        seen.add(stage_id)
        stage_type = stage.get("type")
        if stage_type not in STAGE_TYPES:
            raise WorkflowError(f"{label}.type must be one of {sorted(STAGE_TYPES)}")
        if not isinstance(stage.get("prompt"), str) or not stage["prompt"].strip():
            raise WorkflowError(f"{label}.prompt must be a non-empty string")
        schema = stage.get("output_schema")
        if schema is not None and not isinstance(schema, dict):
            raise WorkflowError(f"{label}.output_schema must be an object")
        stage_model = stage.get("model")
        if stage_model is not None and (not isinstance(stage_model, str) or not stage_model.strip()):
            raise WorkflowError(f"{label}.model must be a non-empty string")
        model_role = stage.get("model_role")
        if model_role is not None and model_role not in MODEL_ROLES:
            raise WorkflowError(f"{label}.model_role must be one of {sorted(MODEL_ROLES)}")
        if stage_model is not None and model_role is not None:
            raise WorkflowError(f"{label} cannot set both model and model_role")
        if stage_type == "map":
            has_items = "items" in stage
            has_source = "source" in stage
            if has_items == has_source:
                raise WorkflowError(f"{label} must have exactly one of items or source")
            if has_items and not isinstance(stage["items"], list):
                raise WorkflowError(f"{label}.items must be an array")
            if has_source and not isinstance(stage["source"], str):
                raise WorkflowError(f"{label}.source must be a dotted path")
        if stage_type == "reduce":
            inputs = stage.get("inputs")
            if inputs is not None and (
                not isinstance(inputs, list) or not all(isinstance(x, str) for x in inputs)
            ):
                raise WorkflowError(f"{label}.inputs must be an array of stage ids")
            for item in inputs or []:
                if item not in seen - {stage_id}:
                    raise WorkflowError(f"{label}.inputs references a later or unknown stage: {item}")
        if stage_type == "loop":
            require_int(stage.get("max_rounds"), f"{label}.max_rounds", 1, 100)
            until = stage.get("until")
            if not isinstance(until, dict) or not isinstance(until.get("path"), str) or "equals" not in until:
                raise WorkflowError(f"{label}.until requires path and equals")


def resolve_path(root: Any, path: str) -> Any:
    current = root
    if not path:
        return current
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list) and part.isdigit() and int(part) < len(current):
            current = current[int(part)]
        else:
            raise WorkflowError(f"template/source path not found: {path}")
    return current


def render(template: str, context: dict[str, Any]) -> str:
    def replace(match: re.Match[str]) -> str:
        expression = match.group(1).strip()
        value = resolve_path(context, expression)
        if expression.endswith("_json") or isinstance(value, (dict, list)) or value is None:
            return json.dumps(value, ensure_ascii=False)
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)

    return TEMPLATE_RE.sub(replace, template)


def source_items(stage: dict[str, Any], context: dict[str, Any]) -> list[Any]:
    value = stage.get("items") if "items" in stage else resolve_path(context, stage["source"])
    if not isinstance(value, list):
        raise WorkflowError(f"map stage {stage['id']} source did not resolve to an array")
    return value


class Runner:
    def __init__(
        self,
        spec: dict[str, Any],
        state_dir: Path,
        harness: str,
        agent_bin: str,
        allow_writes: bool,
        resume: bool,
        restart: bool,
    ) -> None:
        self.spec = spec
        self.state_dir = state_dir
        self.harness = harness
        self.agent_bin = agent_bin
        self.allow_writes = allow_writes
        self.resume = resume
        self.restart = restart
        self.state_path = state_dir / "state.json"
        self.result_path = state_dir / "result.json"
        self.logs_dir = state_dir / "logs"
        self.schemas_dir = state_dir / "schemas"
        self.hash = spec_hash(spec)
        self.state: dict[str, Any] = {"spec_hash": self.hash, "completed": [], "results": {}}
        self.semaphore = asyncio.Semaphore(spec.get("max_concurrency", 4))

    def prepare(self) -> None:
        sandbox = self.spec.get("sandbox", "read-only")
        if sandbox == "workspace-write" and not self.allow_writes:
            raise WorkflowError("workspace-write requires --allow-writes")
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.schemas_dir.mkdir(parents=True, exist_ok=True)
        if self.resume:
            if not self.state_path.exists():
                raise WorkflowError(f"no checkpoint to resume: {self.state_path}")
            loaded = json.loads(self.state_path.read_text(encoding="utf-8"))
            if loaded.get("spec_hash") != self.hash:
                raise WorkflowError("checkpoint belongs to a different workflow specification")
            self.state = loaded
        elif self.state_path.exists() and not self.restart:
            raise WorkflowError("checkpoint already exists; use --resume or --restart")

    def save_state(self) -> None:
        temporary = self.state_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(self.state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        temporary.replace(self.state_path)

    def model_for(self, stage: dict[str, Any]) -> str | None:
        if stage.get("model"):
            return stage["model"]
        if self.spec.get("model"):
            return self.spec["model"]
        policy = self.spec.get("model_policy")
        if not policy or policy["strategy"] == "inherit":
            return None
        role = stage.get("model_role", DEFAULT_ROLES[stage["type"]])
        tier = policy.get("roles", {}).get(role, POLICY_ROUTES[policy["strategy"]][role])
        return policy["models"][tier]

    async def worker(
        self, label: str, prompt: str, schema: dict[str, Any] | None, model: str | None
    ) -> Any:
        async with self.semaphore:
            safe_label = re.sub(r"[^a-zA-Z0-9_.-]", "_", label)
            output_path = self.logs_dir / f"{safe_label}.result.txt"
            event_path = self.logs_dir / f"{safe_label}.events.jsonl"
            schema_path = self.schemas_dir / f"{safe_label}.schema.json"
            if self.harness == "codex":
                command = [
                    self.agent_bin,
                    "exec",
                    "--ephemeral",
                    "--skip-git-repo-check",
                    "--color",
                    "never",
                    "--json",
                    "--sandbox",
                    self.spec.get("sandbox", "read-only"),
                    "--cd",
                    self.spec["workdir"],
                    "--output-last-message",
                    str(output_path),
                ]
                if model:
                    command.extend(["--model", model])
                if schema is not None:
                    schema_path.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
                    command.extend(["--output-schema", str(schema_path)])
                command.append("-")
            else:
                sandbox = self.spec.get("sandbox", "read-only")
                tools = self.spec.get("claude_tools") or (
                    CLAUDE_READ_TOOLS if sandbox == "read-only" else CLAUDE_WRITE_TOOLS
                )
                command = [
                    self.agent_bin,
                    "--print",
                    "--output-format",
                    "json",
                    "--no-session-persistence",
                    "--permission-mode",
                    "dontAsk" if sandbox == "read-only" else "acceptEdits",
                    "--tools",
                    ",".join(tools),
                ]
                if model:
                    command.extend(["--model", model])
                if schema is not None:
                    command.extend(
                        ["--json-schema", json.dumps(schema, separators=(",", ":"))]
                    )
            attempts = self.spec.get("retries", 0) + 1
            last_error = "unknown worker failure"
            for attempt in range(1, attempts + 1):
                print(f"[{label}] starting attempt {attempt}/{attempts}", flush=True)
                try:
                    process = await asyncio.create_subprocess_exec(
                        *command,
                        cwd=self.spec["workdir"],
                        stdin=asyncio.subprocess.PIPE,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(prompt.encode()), timeout=self.spec.get("timeout_seconds", 900)
                    )
                except asyncio.TimeoutError:
                    process.kill()
                    await process.wait()
                    last_error = f"timed out after {self.spec.get('timeout_seconds', 900)} seconds"
                    continue
                event_path.write_bytes(stdout)
                if process.returncode != 0:
                    last_error = (
                        stderr.decode(errors="replace").strip()
                        or f"{self.harness} exited {process.returncode}"
                    )
                    continue
                if self.harness == "codex":
                    if not output_path.exists():
                        last_error = "codex did not write a final result"
                        continue
                    raw = output_path.read_text(encoding="utf-8")
                else:
                    try:
                        envelope = json.loads(stdout.decode(encoding="utf-8"))
                    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                        last_error = f"Claude output is not a valid JSON envelope: {exc}"
                        continue
                    value = envelope.get("structured_output") if schema is not None else None
                    if value is None:
                        value = envelope.get("result")
                    if value is None:
                        last_error = "Claude JSON envelope contains no result"
                        continue
                    if schema is not None and isinstance(value, str):
                        try:
                            value = json.loads(value)
                        except json.JSONDecodeError as exc:
                            last_error = f"Claude structured result is not valid JSON: {exc}"
                            continue
                    raw = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
                    output_path.write_text(raw, encoding="utf-8")
                if schema is None:
                    print(f"[{label}] completed", flush=True)
                    return raw
                try:
                    result = json.loads(raw)
                except json.JSONDecodeError as exc:
                    last_error = f"final result is not valid JSON: {exc}"
                    continue
                print(f"[{label}] completed", flush=True)
                return result
            raise WorkflowError(f"{label}: {last_error}")

    def context(self, extra: dict[str, Any] | None = None, results: dict[str, Any] | None = None) -> dict[str, Any]:
        selected = self.state["results"] if results is None else results
        value: dict[str, Any] = {
            "args": self.spec.get("args", {}),
            "results": selected,
            "results_json": selected,
        }
        if extra:
            value.update(extra)
        return value

    async def execute_stage(self, stage: dict[str, Any]) -> Any:
        stage_id = stage["id"]
        stage_type = stage["type"]
        model = self.model_for(stage)
        if stage_type == "agent":
            prompt = render(stage["prompt"], self.context())
            return await self.worker(stage_id, prompt, stage.get("output_schema"), model)
        if stage_type == "map":
            items = source_items(stage, self.context())

            async def run_item(index: int, item: Any) -> dict[str, Any]:
                context = self.context({"item": item, "item_json": item, "index": index})
                prompt = render(stage["prompt"], context)
                label = f"{stage_id}.{index}"
                try:
                    result = await self.worker(label, prompt, stage.get("output_schema"), model)
                    return {"id": label, "status": "ok", "result": result}
                except WorkflowError as exc:
                    return {"id": label, "status": "failed", "error": str(exc)}

            return await asyncio.gather(*(run_item(i, item) for i, item in enumerate(items)))
        if stage_type == "reduce":
            inputs = stage.get("inputs")
            selected = self.state["results"] if inputs is None else {key: self.state["results"][key] for key in inputs}
            prompt = render(stage["prompt"], self.context(results=selected))
            return await self.worker(stage_id, prompt, stage.get("output_schema"), model)
        previous: Any = None
        rounds: list[dict[str, Any]] = []
        until = stage["until"]
        for round_number in range(1, stage["max_rounds"] + 1):
            context = self.context(
                {"round": round_number, "previous": previous, "previous_json": previous}
            )
            prompt = render(stage["prompt"], context)
            result = await self.worker(
                f"{stage_id}.{round_number}", prompt, stage.get("output_schema"), model
            )
            rounds.append({"round": round_number, "result": result})
            previous = result
            try:
                actual = resolve_path(result, until["path"])
            except WorkflowError:
                actual = object()
            if actual == until["equals"]:
                return {"satisfied": True, "rounds": rounds, "result": result}
        return {"satisfied": False, "rounds": rounds, "result": previous}

    async def run(self) -> dict[str, Any]:
        self.prepare()
        for stage in self.spec["stages"]:
            stage_id = stage["id"]
            if stage_id in self.state["completed"]:
                print(f"[{stage_id}] checkpoint found; skipping", flush=True)
                continue
            print(f"[{stage_id}] stage {stage['type']}", flush=True)
            result = await self.execute_stage(stage)
            self.state["results"][stage_id] = result
            self.state["completed"].append(stage_id)
            self.save_state()
        final_stage = self.spec["stages"][-1]["id"]
        final = {
            "workflow": self.spec["name"],
            "spec_hash": self.hash,
            "completed": self.state["completed"],
            "final_stage": final_stage,
            "result": self.state["results"][final_stage],
            "results": self.state["results"],
        }
        self.result_path.write_text(json.dumps(final, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return final


def upper_bound(spec: dict[str, Any]) -> tuple[int, bool]:
    total = 0
    dynamic = False
    for stage in spec["stages"]:
        if stage["type"] in {"agent", "reduce"}:
            total += 1
        elif stage["type"] == "loop":
            total += stage["max_rounds"]
        elif "items" in stage:
            total += len(stage["items"])
        else:
            dynamic = True
    return total, dynamic


def default_state_dir(spec: dict[str, Any], harness: str) -> Path:
    return Path(spec["workdir"]) / f".{harness}" / "workflow-runs" / spec["name"]


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    subparsers = value.add_subparsers(dest="command", required=True)
    for name in ("validate", "preview"):
        command = subparsers.add_parser(name)
        command.add_argument("workflow", type=Path)
    run = subparsers.add_parser("run")
    run.add_argument("workflow", type=Path)
    run.add_argument("--approve", action="store_true", help="confirm the previewed workflow")
    run.add_argument("--allow-writes", action="store_true", help="allow a workspace-write workflow")
    run.add_argument("--resume", action="store_true")
    run.add_argument("--restart", action="store_true")
    run.add_argument("--state-dir", type=Path)
    run.add_argument("--harness", choices=sorted(HARNESSES), help="override workflow harness")
    run.add_argument("--agent-bin", help="override the selected harness executable")
    run.add_argument("--codex-bin", help="deprecated alias for --agent-bin with the Codex harness")
    return value


def main() -> int:
    args = parser().parse_args()
    try:
        spec = load_spec(args.workflow.resolve())
        validate_spec(spec)
        if args.command == "validate":
            print("workflow is valid")
            return 0
        bound, dynamic = upper_bound(spec)
        harness = getattr(args, "harness", None) or spec.get("harness", "codex")
        print(f"Workflow: {spec['name']}")
        print(f"Description: {spec.get('description', '(none)')}")
        print(f"Harness: {harness}")
        print(f"Workdir: {spec['workdir']}")
        print(f"Sandbox: {spec.get('sandbox', 'read-only')}")
        if harness == "claude":
            sandbox = spec.get("sandbox", "read-only")
            tools = spec.get("claude_tools") or (
                CLAUDE_READ_TOOLS if sandbox == "read-only" else CLAUDE_WRITE_TOOLS
            )
            print(f"Claude tools: {', '.join(tools)}")
        print(f"Max concurrency: {spec.get('max_concurrency', 4)}")
        suffix = " plus dynamically discovered map items" if dynamic else ""
        print(f"Worker upper bound: {bound}{suffix}")
        preview_runner = Runner(spec, Path("."), harness, harness, False, False, False)
        policy = spec.get("model_policy")
        if policy:
            print(f"Model policy: {policy['strategy']}")
        elif spec.get("model"):
            print(f"Model: {spec['model']}")
        else:
            print("Model policy: inherit")
        for stage in spec["stages"]:
            detail = f" ({len(stage['items'])} items)" if stage["type"] == "map" and "items" in stage else ""
            selected_model = preview_runner.model_for(stage) or "inherit"
            role = stage.get("model_role", DEFAULT_ROLES[stage["type"]])
            print(f"- {stage['id']}: {stage['type']}{detail}; role={role}; model={selected_model}")
        if args.command == "preview":
            return 0
        if not args.approve:
            raise WorkflowError("run requires --approve after reviewing preview")
        if args.codex_bin and harness != "codex":
            raise WorkflowError("--codex-bin cannot be combined with the Claude harness; use --agent-bin")
        agent_bin = args.agent_bin or args.codex_bin or harness
        if shutil.which(agent_bin) is None and not Path(agent_bin).is_file():
            raise WorkflowError(f"{harness} executable not found: {agent_bin}")
        if args.resume and args.restart:
            raise WorkflowError("choose either --resume or --restart")
        state_dir = (args.state_dir or default_state_dir(spec, harness)).resolve()
        runner = Runner(
            spec,
            state_dir,
            harness,
            agent_bin,
            args.allow_writes,
            args.resume,
            args.restart,
        )
        asyncio.run(runner.run())
        print(f"Result: {runner.result_path}")
        return 0
    except (WorkflowError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
