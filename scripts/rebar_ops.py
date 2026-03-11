#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fcntl
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
OPS_ROOT = REPO_ROOT / "ops"
CONFIG_PATH = OPS_ROOT / "config" / "loop.json"
TASK_ROOT = OPS_ROOT / "tasks"
STATE_ROOT = OPS_ROOT / "state"
DEFAULT_CONTEXT_FILES = [
    REPO_ROOT / "AGENTS.md",
    REPO_ROOT / "README.md",
    OPS_ROOT / "README.md",
    STATE_ROOT / "charter.md",
    STATE_ROOT / "current_status.md",
    STATE_ROOT / "backlog.md",
    STATE_ROOT / "decision_log.md",
]
TASK_STATUSES = ("ready", "in_progress", "done", "blocked")


@dataclass(frozen=True)
class AgentSpec:
    name: str
    kind: str
    description: str
    enabled: bool
    cycle_order: int
    spec_path: Path
    prompt_path: Path
    dispatch: dict[str, Any]
    codex: dict[str, Any]


@dataclass
class RunResult:
    agent_name: str
    agent_kind: str
    run_id: str
    exit_code: int
    timed_out: bool
    run_dir: Path
    task_initial_path: Path | None
    task_final_path: Path | None
    task_final_status: str | None


def utcnow() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def read_json(path: Path, *, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_config() -> dict[str, Any]:
    config = read_json(CONFIG_PATH, default={})
    if not isinstance(config, dict):
        raise RuntimeError(f"Invalid config: {CONFIG_PATH}")
    return config


def resolve_repo_path(raw: str | Path) -> Path:
    path = Path(raw).expanduser()
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def runtime_paths(config: dict[str, Any]) -> dict[str, Path]:
    runtime_cfg = config.get("runtime", {})
    artifact_root = resolve_repo_path(runtime_cfg.get("artifact_dir", ".rebar/runtime"))
    return {
        "artifact_root": artifact_root,
        "runs_root": artifact_root / "runs",
        "loop_state": artifact_root / "loop_state.json",
        "loop_lock": artifact_root / "loop.lock",
    }


def ensure_runtime_dirs(paths: dict[str, Path]) -> None:
    paths["artifact_root"].mkdir(parents=True, exist_ok=True)
    paths["runs_root"].mkdir(parents=True, exist_ok=True)


def repo_is_git_checkout(path: Path) -> bool:
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return False
    return result.returncode == 0 and result.stdout.strip().lower() == "true"


def relpath(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def list_task_files(status: str) -> list[Path]:
    queue_dir = TASK_ROOT / status
    if not queue_dir.exists():
        return []
    return sorted(
        [path for path in queue_dir.iterdir() if path.is_file() and path.name != ".gitkeep"],
        key=lambda path: path.name,
    )


def queue_counts() -> dict[str, int]:
    return {status: len(list_task_files(status)) for status in TASK_STATUSES}


def claim_tasks(queue: str, claim_to: str, limit: int) -> list[Path]:
    claimed: list[Path] = []
    dest_dir = TASK_ROOT / claim_to
    dest_dir.mkdir(parents=True, exist_ok=True)
    for src in list_task_files(queue)[:limit]:
        dest = dest_dir / src.name
        src.rename(dest)
        claimed.append(dest)
    return claimed


def locate_task_file(task_name: str) -> tuple[str | None, Path | None]:
    matches: list[tuple[str, Path]] = []
    for status in TASK_STATUSES:
        candidate = TASK_ROOT / status / task_name
        if candidate.exists():
            matches.append((status, candidate))
    if len(matches) == 1:
        return matches[0]
    if not matches:
        return None, None
    return "multiple", None


def load_agent_specs(config: dict[str, Any]) -> list[AgentSpec]:
    agents_cfg = config.get("agents", {})
    agent_dir = resolve_repo_path(agents_cfg.get("directory", "ops/agents"))
    specs: list[AgentSpec] = []
    names: set[str] = set()

    for spec_path in sorted(agent_dir.glob("*.json")):
        raw = read_json(spec_path, default=None)
        if not isinstance(raw, dict):
            raise RuntimeError(f"Invalid agent spec: {spec_path}")
        name = str(raw.get("name", spec_path.stem))
        if name in names:
            raise RuntimeError(f"Duplicate agent name: {name}")
        names.add(name)
        prompt_path_raw = raw.get("prompt_path")
        if not isinstance(prompt_path_raw, str) or not prompt_path_raw:
            raise RuntimeError(f"Agent {name} missing prompt_path")
        prompt_path = resolve_repo_path(prompt_path_raw)
        if not prompt_path.exists():
            raise RuntimeError(f"Agent {name} prompt not found: {prompt_path}")
        specs.append(
            AgentSpec(
                name=name,
                kind=str(raw.get("kind", "worker")),
                description=str(raw.get("description", "")).strip(),
                enabled=bool(raw.get("enabled", True)),
                cycle_order=int(raw.get("cycle_order", 100)),
                spec_path=spec_path,
                prompt_path=prompt_path,
                dispatch=dict(raw.get("dispatch", {})),
                codex=dict(raw.get("codex", {})),
            )
        )

    enabled = [spec for spec in specs if spec.enabled]
    enabled_supervisors = [spec for spec in enabled if spec.kind == "supervisor"]
    if len(enabled_supervisors) != 1:
        raise RuntimeError("Exactly one enabled supervisor agent spec is required.")
    return sorted(enabled, key=lambda spec: (spec.cycle_order, spec.name))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def render_prompt(agent: AgentSpec, config: dict[str, Any], task_path: Path | None = None) -> str:
    paths = runtime_paths(config)
    agent_body = agent.prompt_path.read_text(encoding="utf-8").strip()
    lines = [
        f"# Rebar Agent Run: {agent.name}",
        "",
        f"Repository root: {REPO_ROOT}",
        f"Agent spec: {relpath(agent.spec_path)}",
        "",
        "Read these files first:",
    ]
    for path in DEFAULT_CONTEXT_FILES:
        lines.append(f"- {relpath(path)}")
    lines.extend(
        [
            "",
            "Runtime files worth checking when relevant:",
            f"- loop state: {relpath(paths['loop_state'])}",
            f"- run artifacts: {relpath(paths['runs_root'])}",
            f"- agent registry: {relpath(resolve_repo_path(config.get('agents', {}).get('directory', 'ops/agents')))}",
        ]
    )
    if task_path is not None:
        lines.extend(
            [
                "",
                "Assigned task file:",
                f"- {relpath(task_path)}",
            ]
        )
    lines.extend(
        [
            "",
            "Queue directories:",
            f"- ready: {relpath(TASK_ROOT / 'ready')}",
            f"- in_progress: {relpath(TASK_ROOT / 'in_progress')}",
            f"- done: {relpath(TASK_ROOT / 'done')}",
            f"- blocked: {relpath(TASK_ROOT / 'blocked')}",
            "",
            agent_body,
            "",
            "Leave durable state in tracked files under ops/ when it matters.",
        ]
    )
    return "\n".join(lines) + "\n"


def build_codex_command(
    *,
    config: dict[str, Any],
    agent: AgentSpec,
    output_path: Path,
    cwd: Path,
) -> list[str]:
    defaults = config.get("codex_defaults", {})
    cmd = [str(defaults.get("bin", "codex"))]

    sandbox = agent.codex.get("sandbox", defaults.get("sandbox"))
    ask_for_approval = agent.codex.get("ask_for_approval", defaults.get("ask_for_approval"))
    if sandbox:
        cmd.extend(["--sandbox", str(sandbox)])
    if ask_for_approval:
        cmd.extend(["--ask-for-approval", str(ask_for_approval)])

    model = agent.codex.get("model")
    if model:
        cmd.extend(["--model", str(model)])

    for item in defaults.get("common_config", []):
        cmd.extend(["-c", str(item)])
    for item in agent.codex.get("config", []):
        cmd.extend(["-c", str(item)])

    for item in defaults.get("extra_cli_args", []):
        cmd.append(str(item))
    for item in agent.codex.get("extra_cli_args", []):
        cmd.append(str(item))

    cmd.append("exec")
    if not repo_is_git_checkout(cwd):
        cmd.append("--skip-git-repo-check")
    cmd.extend(["--output-last-message", str(output_path), "-"])
    return cmd


def build_codex_env(config: dict[str, Any]) -> dict[str, str]:
    defaults = config.get("codex_defaults", {})
    env = os.environ.copy()
    codex_home = defaults.get("codex_home")
    if codex_home:
        env["CODEX_HOME"] = str(Path(str(codex_home)).expanduser())
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["REBAR_LOOP"] = "1"
    env.setdefault("CODEX_NO_UPDATE", "1")
    for key, value in defaults.get("extra_env", {}).items():
        env[str(key)] = str(value)
    return env


def normalize_subprocess_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def task_timeout_seconds(config: dict[str, Any], agent: AgentSpec) -> int:
    runtime_cfg = config.get("runtime", {})
    return int(agent.dispatch.get("timeout_seconds", runtime_cfg.get("default_timeout_seconds", 1800)))


class LoopLock:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.handle: Any | None = None

    def __enter__(self) -> "LoopLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = open(self.path, "a+", encoding="utf-8")
        try:
            fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError(f"Loop already running: {self.path}") from exc
        self.handle.seek(0)
        self.handle.truncate()
        self.handle.write(f"pid={os.getpid()} started_at={utcnow()}\n")
        self.handle.flush()
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        if self.handle is None:
            return
        try:
            fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
        finally:
            self.handle.close()


def run_agent(agent: AgentSpec, config: dict[str, Any], task_path: Path | None = None) -> RunResult:
    paths = runtime_paths(config)
    ensure_runtime_dirs(paths)

    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    suffix = agent.name if task_path is None else f"{agent.name}-{task_path.stem}"
    run_id = f"{stamp}-{suffix}"
    run_dir = paths["runs_root"] / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    prompt_text = render_prompt(agent, config, task_path=task_path)
    prompt_path = run_dir / "prompt.md"
    output_path = run_dir / "last_message.md"
    stdout_path = run_dir / "stdout.log"
    stderr_path = run_dir / "stderr.log"
    metadata_path = run_dir / "metadata.json"
    write_text(prompt_path, prompt_text)

    command = build_codex_command(config=config, agent=agent, output_path=output_path, cwd=REPO_ROOT)
    env = build_codex_env(config)
    timeout_seconds = task_timeout_seconds(config, agent)
    started_at = utcnow()
    timed_out = False
    try:
        proc = subprocess.run(
            command,
            input=prompt_text,
            text=True,
            capture_output=True,
            cwd=str(REPO_ROOT),
            env=env,
            check=False,
            timeout=timeout_seconds,
        )
        exit_code = proc.returncode
        stdout_text = normalize_subprocess_text(proc.stdout)
        stderr_text = normalize_subprocess_text(proc.stderr)
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        exit_code = 124
        stdout_text = normalize_subprocess_text(exc.stdout)
        stderr_text = normalize_subprocess_text(exc.stderr)
    finished_at = utcnow()

    write_text(stdout_path, stdout_text)
    write_text(stderr_path, stderr_text)
    if not output_path.exists():
        write_text(output_path, "")

    task_final_status: str | None = None
    task_final_path: Path | None = None
    if task_path is not None:
        task_final_status, task_final_path = locate_task_file(task_path.name)

    metadata = {
        "agent_name": agent.name,
        "agent_kind": agent.kind,
        "run_id": run_id,
        "task_initial_path": None if task_path is None else relpath(task_path),
        "task_final_status": task_final_status,
        "task_final_path": None if task_final_path is None else relpath(task_final_path),
        "command": command,
        "cwd": str(REPO_ROOT),
        "started_at": started_at,
        "finished_at": finished_at,
        "exit_code": exit_code,
        "timed_out": timed_out,
        "timeout_seconds": timeout_seconds,
        "prompt_path": relpath(prompt_path),
        "stdout_path": relpath(stdout_path),
        "stderr_path": relpath(stderr_path),
        "last_message_path": relpath(output_path),
    }
    write_json(metadata_path, metadata)
    return RunResult(
        agent_name=agent.name,
        agent_kind=agent.kind,
        run_id=run_id,
        exit_code=exit_code,
        timed_out=timed_out,
        run_dir=run_dir,
        task_initial_path=task_path,
        task_final_path=task_final_path,
        task_final_status=task_final_status,
    )


def agent_last_state(loop_state: dict[str, Any], agent_name: str) -> dict[str, Any]:
    agents = loop_state.get("agents")
    if not isinstance(agents, dict):
        return {}
    agent_state = agents.get(agent_name)
    return agent_state if isinstance(agent_state, dict) else {}


def agent_is_due(agent: AgentSpec, loop_state: dict[str, Any], *, force: bool = False) -> bool:
    mode = str(agent.dispatch.get("mode", "every_cycle"))
    if mode == "every_cycle":
        return True
    if mode == "interval":
        if force:
            return True
        interval_seconds = int(agent.dispatch.get("interval_seconds", 300))
        last = agent_last_state(loop_state, agent.name)
        finished_at = last.get("finished_at")
        if not isinstance(finished_at, str):
            return True
        try:
            last_dt = datetime.fromisoformat(finished_at.replace("Z", "+00:00"))
        except ValueError:
            return True
        delta = datetime.now(UTC) - last_dt.astimezone(UTC)
        return delta.total_seconds() >= interval_seconds
    if mode == "task_queue":
        queue = str(agent.dispatch.get("queue", "ready"))
        return bool(list_task_files(queue))
    raise RuntimeError(f"Unsupported dispatch mode for {agent.name}: {mode}")


def dispatch_agent(agent: AgentSpec, config: dict[str, Any], loop_state: dict[str, Any], *, force: bool = False) -> list[RunResult]:
    if not agent_is_due(agent, loop_state, force=force):
        return []

    mode = str(agent.dispatch.get("mode", "every_cycle"))
    if mode in {"every_cycle", "interval"}:
        return [run_agent(agent, config)]
    if mode == "task_queue":
        queue = str(agent.dispatch.get("queue", "ready"))
        claim_to = str(agent.dispatch.get("claim_to", "in_progress"))
        max_runs = int(agent.dispatch.get("max_runs_per_cycle", 1))
        claimed = claim_tasks(queue, claim_to, max_runs)
        return [run_agent(agent, config, task_path=task_path) for task_path in claimed]
    raise RuntimeError(f"Unsupported dispatch mode for {agent.name}: {mode}")


def build_anomalies(results: list[RunResult]) -> list[dict[str, Any]]:
    anomalies: list[dict[str, Any]] = []
    for result in results:
        if result.exit_code != 0:
            anomalies.append(
                {
                    "agent_name": result.agent_name,
                    "run_id": result.run_id,
                    "type": "nonzero_exit",
                    "exit_code": result.exit_code,
                    "timed_out": result.timed_out,
                }
            )
        if result.task_initial_path is not None and result.task_final_status not in {"done", "blocked"}:
            anomalies.append(
                {
                    "agent_name": result.agent_name,
                    "run_id": result.run_id,
                    "type": "task_not_terminated",
                    "task_initial_path": relpath(result.task_initial_path),
                    "task_final_status": result.task_final_status,
                    "task_final_path": None
                    if result.task_final_path is None
                    else relpath(result.task_final_path),
                }
            )
    return anomalies


def update_loop_state(config: dict[str, Any], agents: list[AgentSpec], results: list[RunResult]) -> None:
    paths = runtime_paths(config)
    state = read_json(paths["loop_state"], default={})
    if not isinstance(state, dict):
        state = {}

    agent_state = state.get("agents")
    if not isinstance(agent_state, dict):
        agent_state = {}

    for result in results:
        agent_state[result.agent_name] = {
            "agent_kind": result.agent_kind,
            "run_id": result.run_id,
            "exit_code": result.exit_code,
            "timed_out": result.timed_out,
            "finished_at": utcnow(),
            "task_final_status": result.task_final_status,
        }

    state.update(
        {
            "updated_at": utcnow(),
            "agents": agent_state,
            "agent_registry": [
                {
                    "name": agent.name,
                    "kind": agent.kind,
                    "cycle_order": agent.cycle_order,
                    "dispatch_mode": agent.dispatch.get("mode", "every_cycle"),
                    "spec_path": relpath(agent.spec_path),
                }
                for agent in agents
            ],
            "queue_counts": queue_counts(),
            "last_cycle_runs": [
                {
                    "agent_name": result.agent_name,
                    "agent_kind": result.agent_kind,
                    "run_id": result.run_id,
                    "exit_code": result.exit_code,
                    "timed_out": result.timed_out,
                    "task_initial_path": None
                    if result.task_initial_path is None
                    else relpath(result.task_initial_path),
                    "task_final_status": result.task_final_status,
                    "task_final_path": None
                    if result.task_final_path is None
                    else relpath(result.task_final_path),
                }
                for result in results
            ],
            "last_cycle_anomalies": build_anomalies(results),
        }
    )
    write_json(paths["loop_state"], state)


def run_cycle(config: dict[str, Any], *, force_supervisor: bool = False) -> int:
    agents = load_agent_specs(config)
    paths = runtime_paths(config)
    ensure_runtime_dirs(paths)
    loop_state = read_json(paths["loop_state"], default={})
    if not isinstance(loop_state, dict):
        loop_state = {}

    results: list[RunResult] = []
    failures = 0
    for agent in agents:
        force = force_supervisor and agent.kind == "supervisor"
        agent_results = dispatch_agent(agent, config, loop_state, force=force)
        results.extend(agent_results)
        failures += sum(int(result.exit_code != 0) for result in agent_results)

    update_loop_state(config, agents, results)
    return 0 if failures == 0 else 1


def cmd_status(config: dict[str, Any]) -> int:
    agents = load_agent_specs(config)
    paths = runtime_paths(config)
    state = read_json(paths["loop_state"], default={})
    if not isinstance(state, dict):
        state = {}
    status = {
        "repo_root": str(REPO_ROOT),
        "runtime_dir": str(paths["artifact_root"]),
        "queue_counts": queue_counts(),
        "agents": [
            {
                "name": agent.name,
                "kind": agent.kind,
                "dispatch_mode": agent.dispatch.get("mode", "every_cycle"),
                "cycle_order": agent.cycle_order,
            }
            for agent in agents
        ],
        "last_cycle_runs": state.get("last_cycle_runs", []),
        "last_cycle_anomalies": state.get("last_cycle_anomalies", []),
    }
    print(json.dumps(status, indent=2, sort_keys=True))
    return 0


def cmd_render(config: dict[str, Any], agent_name: str, task: str | None) -> int:
    agents = {agent.name: agent for agent in load_agent_specs(config)}
    agent = agents.get(agent_name)
    if agent is None:
        raise RuntimeError(f"Unknown agent: {agent_name}")
    task_path = None if task is None else resolve_repo_path(task)
    sys.stdout.write(render_prompt(agent, config, task_path=task_path))
    return 0


def cmd_cycle(config: dict[str, Any], force_supervisor: bool) -> int:
    return run_cycle(config, force_supervisor=force_supervisor)


def cmd_loop(config: dict[str, Any], *, force_supervisor: bool, max_cycles: int | None) -> int:
    runtime_cfg = config.get("runtime", {})
    sleep_seconds = int(runtime_cfg.get("sleep_seconds", 300))
    failure_backoff_seconds = int(runtime_cfg.get("failure_backoff_seconds", 30))
    paths = runtime_paths(config)
    ensure_runtime_dirs(paths)

    with LoopLock(paths["loop_lock"]):
        cycles = 0
        while True:
            exit_code = run_cycle(config, force_supervisor=(force_supervisor or cycles == 0))
            cycles += 1
            if max_cycles is not None and cycles >= max_cycles:
                return exit_code
            time.sleep(sleep_seconds if exit_code == 0 else failure_backoff_seconds)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the rebar forever harness.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status", help="Print queue, agent, and runtime status.")

    render_parser = subparsers.add_parser("render", help="Render a prompt for an agent.")
    render_parser.add_argument("agent", help="Agent name from ops/agents/*.json")
    render_parser.add_argument("--task", help="Optional task path for task-worker prompts.")

    cycle_parser = subparsers.add_parser("cycle", help="Run one full agent cycle.")
    cycle_parser.add_argument(
        "--force-supervisor",
        action="store_true",
        help="Force the supervisor to run even if its future dispatch policy becomes interval-based.",
    )

    loop_parser = subparsers.add_parser("loop", help="Run cycles forever.")
    loop_parser.add_argument(
        "--force-supervisor",
        action="store_true",
        help="Force the first cycle to run the supervisor.",
    )
    loop_parser.add_argument(
        "--max-cycles",
        type=int,
        help="Optional upper bound for local testing.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_config()
    if args.command == "status":
        return cmd_status(config)
    if args.command == "render":
        return cmd_render(config, args.agent, args.task)
    if args.command == "cycle":
        return cmd_cycle(config, args.force_supervisor)
    if args.command == "loop":
        return cmd_loop(config, force_supervisor=args.force_supervisor, max_cycles=args.max_cycles)
    raise RuntimeError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
