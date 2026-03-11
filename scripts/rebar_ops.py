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


@dataclass
class RunResult:
    role: str
    run_id: str
    exit_code: int
    run_dir: Path
    task_path: Path | None


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
        "home_dir": resolve_repo_path(runtime_cfg.get("home_dir", ".rebar/home")),
    }


def ensure_runtime_dirs(paths: dict[str, Path]) -> None:
    paths["artifact_root"].mkdir(parents=True, exist_ok=True)
    paths["runs_root"].mkdir(parents=True, exist_ok=True)
    paths["home_dir"].mkdir(parents=True, exist_ok=True)
    (paths["home_dir"] / ".cache").mkdir(parents=True, exist_ok=True)


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


def claim_ready_tasks(limit: int) -> list[Path]:
    claimed: list[Path] = []
    for src in list_task_files("ready")[:limit]:
        dest = TASK_ROOT / "in_progress" / src.name
        src.rename(dest)
        claimed.append(dest)
    return claimed


def render_prompt(role: str, config: dict[str, Any], task_path: Path | None = None) -> str:
    role_cfg = config["roles"][role]
    prompt_path = resolve_repo_path(role_cfg["prompt_path"])
    role_body = prompt_path.read_text(encoding="utf-8").strip()

    lines = [
        f"# Rebar {role.title()} Run",
        "",
        f"Repository root: {REPO_ROOT}",
        "",
        "Read these files first:",
    ]
    for path in DEFAULT_CONTEXT_FILES:
        lines.append(f"- {relpath(path)}")
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
            role_body,
            "",
            "Leave durable state in tracked files under ops/ when it matters.",
        ]
    )
    return "\n".join(lines) + "\n"


def build_codex_command(
    *,
    config: dict[str, Any],
    role: str,
    output_path: Path,
    cwd: Path,
) -> list[str]:
    codex_cfg = config.get("codex", {})
    role_cfg = config["roles"][role]
    cmd = [str(codex_cfg.get("bin", "codex"))]

    sandbox = role_cfg.get("sandbox", codex_cfg.get("sandbox"))
    ask_for_approval = role_cfg.get("ask_for_approval", codex_cfg.get("ask_for_approval"))
    if sandbox:
        cmd.extend(["--sandbox", str(sandbox)])
    if ask_for_approval:
        cmd.extend(["--ask-for-approval", str(ask_for_approval)])

    model = role_cfg.get("model")
    if model:
        cmd.extend(["--model", str(model)])

    for item in codex_cfg.get("common_config", []):
        cmd.extend(["-c", str(item)])
    for item in role_cfg.get("config", []):
        cmd.extend(["-c", str(item)])

    for item in codex_cfg.get("extra_cli_args", []):
        cmd.append(str(item))
    for item in role_cfg.get("extra_cli_args", []):
        cmd.append(str(item))

    cmd.append("exec")
    if not repo_is_git_checkout(cwd):
        cmd.append("--skip-git-repo-check")
    cmd.extend(["--output-last-message", str(output_path), "-"])
    return cmd


def build_codex_env(config: dict[str, Any], paths: dict[str, Path]) -> dict[str, str]:
    codex_cfg = config.get("codex", {})
    actual_home = Path.home()
    env = os.environ.copy()
    env["HOME"] = str(paths["home_dir"])
    env["CODEX_HOME"] = str(Path(codex_cfg.get("codex_home", "~/.codex")).expanduser())
    env["GIT_CONFIG_GLOBAL"] = str(actual_home / ".gitconfig")
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["REBAR_LOOP"] = "1"
    for key, value in codex_cfg.get("extra_env", {}).items():
        env[str(key)] = str(value)
    return env


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


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_role(role: str, config: dict[str, Any], task_path: Path | None = None) -> RunResult:
    paths = runtime_paths(config)
    ensure_runtime_dirs(paths)

    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    suffix = role if task_path is None else f"{role}-{task_path.stem}"
    run_id = f"{stamp}-{suffix}"
    run_dir = paths["runs_root"] / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    prompt_text = render_prompt(role, config, task_path=task_path)
    prompt_path = run_dir / "prompt.md"
    output_path = run_dir / "last_message.md"
    stdout_path = run_dir / "stdout.log"
    stderr_path = run_dir / "stderr.log"
    metadata_path = run_dir / "metadata.json"
    write_text(prompt_path, prompt_text)

    command = build_codex_command(config=config, role=role, output_path=output_path, cwd=REPO_ROOT)
    env = build_codex_env(config, paths)
    started_at = utcnow()
    proc = subprocess.run(
        command,
        input=prompt_text,
        text=True,
        capture_output=True,
        cwd=str(REPO_ROOT),
        env=env,
        check=False,
    )
    finished_at = utcnow()

    write_text(stdout_path, proc.stdout)
    write_text(stderr_path, proc.stderr)
    if not output_path.exists():
        write_text(output_path, "")

    metadata = {
        "role": role,
        "run_id": run_id,
        "task_path": None if task_path is None else relpath(task_path),
        "command": command,
        "cwd": str(REPO_ROOT),
        "started_at": started_at,
        "finished_at": finished_at,
        "exit_code": proc.returncode,
        "prompt_path": relpath(prompt_path),
        "stdout_path": relpath(stdout_path),
        "stderr_path": relpath(stderr_path),
        "last_message_path": relpath(output_path),
    }
    write_json(metadata_path, metadata)
    return RunResult(role=role, run_id=run_id, exit_code=proc.returncode, run_dir=run_dir, task_path=task_path)


def update_loop_state(
    config: dict[str, Any],
    *,
    supervisor_run: RunResult | None,
    worker_runs: list[RunResult],
) -> None:
    paths = runtime_paths(config)
    state = read_json(paths["loop_state"], default={})
    if not isinstance(state, dict):
        state = {}
    state.update(
        {
            "updated_at": utcnow(),
            "queue_counts": queue_counts(),
            "last_cycle_worker_runs": [
                {
                    "run_id": result.run_id,
                    "exit_code": result.exit_code,
                    "task_path": None if result.task_path is None else relpath(result.task_path),
                }
                for result in worker_runs
            ],
        }
    )
    if supervisor_run is not None:
        state["last_supervisor_run"] = {
            "run_id": supervisor_run.run_id,
            "exit_code": supervisor_run.exit_code,
            "finished_at": utcnow(),
        }
    write_json(paths["loop_state"], state)


def supervisor_is_due(config: dict[str, Any]) -> bool:
    paths = runtime_paths(config)
    state = read_json(paths["loop_state"], default={})
    if not isinstance(state, dict):
        return True
    supervisor_cfg = config["roles"]["supervisor"]
    interval_seconds = int(supervisor_cfg.get("interval_seconds", 300))
    last = state.get("last_supervisor_run")
    if not isinstance(last, dict):
        return True
    finished_at = last.get("finished_at")
    if not isinstance(finished_at, str):
        return True
    try:
        last_dt = datetime.fromisoformat(finished_at.replace("Z", "+00:00"))
    except ValueError:
        return True
    delta = datetime.now(UTC) - last_dt.astimezone(UTC)
    return delta.total_seconds() >= interval_seconds


def run_cycle(config: dict[str, Any], *, force_supervisor: bool = False) -> int:
    supervisor_cfg = config["roles"]["supervisor"]
    implementation_cfg = config["roles"]["implementation"]
    supervisor_run: RunResult | None = None
    worker_runs: list[RunResult] = []
    failures = 0

    if supervisor_cfg.get("enabled", True) and (force_supervisor or supervisor_is_due(config)):
        supervisor_run = run_role("supervisor", config)
        failures += int(supervisor_run.exit_code != 0)

    if implementation_cfg.get("enabled", True):
        max_runs = int(implementation_cfg.get("max_runs_per_cycle", 1))
        for task_path in claim_ready_tasks(max_runs):
            result = run_role("implementation", config, task_path=task_path)
            worker_runs.append(result)
            failures += int(result.exit_code != 0)

    update_loop_state(config, supervisor_run=supervisor_run, worker_runs=worker_runs)
    return 0 if failures == 0 else 1


def cmd_status(config: dict[str, Any]) -> int:
    paths = runtime_paths(config)
    state = read_json(paths["loop_state"], default={})
    status = {
        "repo_root": str(REPO_ROOT),
        "queue_counts": queue_counts(),
        "runtime_dir": str(paths["artifact_root"]),
        "supervisor_due": supervisor_is_due(config),
        "last_supervisor_run": state.get("last_supervisor_run"),
        "last_cycle_worker_runs": state.get("last_cycle_worker_runs", []),
    }
    print(json.dumps(status, indent=2, sort_keys=True))
    return 0


def cmd_render(config: dict[str, Any], role: str, task: str | None) -> int:
    task_path = None if task is None else resolve_repo_path(task)
    sys.stdout.write(render_prompt(role, config, task_path=task_path))
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
    parser = argparse.ArgumentParser(description="Run the rebar supervisor/implementation loop.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status", help="Print queue and runtime status.")

    render_parser = subparsers.add_parser("render", help="Render a prompt for a role.")
    render_parser.add_argument("role", choices=("supervisor", "implementation"))
    render_parser.add_argument("--task", help="Optional task path for implementation prompts.")

    cycle_parser = subparsers.add_parser("cycle", help="Run one supervisor/implementation cycle.")
    cycle_parser.add_argument(
        "--force-supervisor",
        action="store_true",
        help="Run the supervisor even if the configured interval has not elapsed.",
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
        return cmd_render(config, args.role, args.task)
    if args.command == "cycle":
        return cmd_cycle(config, args.force_supervisor)
    if args.command == "loop":
        return cmd_loop(
            config,
            force_supervisor=args.force_supervisor,
            max_cycles=args.max_cycles,
        )
    raise RuntimeError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
