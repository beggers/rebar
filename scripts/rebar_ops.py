#!/usr/bin/env python3
from __future__ import annotations

import argparse
import atexit
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
OPS_ROOT = REPO_ROOT / "ops"
CONFIG_PATH = OPS_ROOT / "config" / "loop.json"
TASK_ROOT = OPS_ROOT / "tasks"
USER_ASK_ROOT = OPS_ROOT / "user_asks"
STATE_ROOT = OPS_ROOT / "state"
README_REPORTING_CONFIG_PATH = OPS_ROOT / "reporting" / "readme.json"
README_STATUS_START = "<!-- REBAR:STATUS_START -->"
README_STATUS_END = "<!-- REBAR:STATUS_END -->"
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
USER_ASK_STATUSES = ("inbox", "done")
TRAILER = "Co-authored-by: Codex <noreply@openai.com>"
PYTHON_SOURCE_ROOT = REPO_ROOT / "python"
DIRTY_STATUS_SAMPLE_LIMIT = 20


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
    requested_sandbox: str | None = None
    observed_sandbox: str | None = None
    environment_issue: str | None = None
    recovery_actions: list[dict[str, Any]] = field(default_factory=list)


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


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def ensure_python_source_on_syspath() -> None:
    python_source = str(PYTHON_SOURCE_ROOT)
    if python_source not in sys.path:
        sys.path.insert(0, python_source)


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


def relpath(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def runtime_paths(config: dict[str, Any]) -> dict[str, Path]:
    runtime_cfg = config.get("runtime", {})
    reporting_cfg = config.get("reporting", {})
    recovery_cfg = config.get("task_recovery", {})
    artifact_root = resolve_repo_path(runtime_cfg.get("artifact_dir", ".rebar/runtime"))
    return {
        "artifact_root": artifact_root,
        "runs_root": artifact_root / "runs",
        "cycle_lock": artifact_root / "cycle.lock.d",
        "loop_state": artifact_root / "loop_state.json",
        "task_state": resolve_repo_path(
            recovery_cfg.get("state_path", ".rebar/runtime/task_state.json")
        ),
        "dashboard_json": resolve_repo_path(
            reporting_cfg.get("status_json_path", ".rebar/runtime/dashboard.json")
        ),
        "dashboard_markdown": resolve_repo_path(
            reporting_cfg.get("status_markdown_path", ".rebar/runtime/dashboard.md")
        ),
        "loop_log": artifact_root / "loop.log",
    }


def ensure_runtime_dirs(paths: dict[str, Path]) -> None:
    paths["artifact_root"].mkdir(parents=True, exist_ok=True)
    paths["runs_root"].mkdir(parents=True, exist_ok=True)
    paths["task_state"].parent.mkdir(parents=True, exist_ok=True)
    paths["dashboard_json"].parent.mkdir(parents=True, exist_ok=True)
    paths["dashboard_markdown"].parent.mkdir(parents=True, exist_ok=True)


def pid_is_running(pid_text: str) -> bool:
    try:
        pid = int(pid_text)
    except (TypeError, ValueError):
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def acquire_cycle_lock(paths: dict[str, Path]) -> tuple[bool, str | None]:
    lock_dir = paths["cycle_lock"]
    pid_path = lock_dir / "pid"
    owner_path = lock_dir / "owner"
    owner_label = f"pid={os.getpid()} cmd={' '.join(sys.argv)}"

    try:
        lock_dir.mkdir()
    except FileExistsError:
        holder_pid = ""
        if pid_path.exists():
            try:
                holder_pid = pid_path.read_text(encoding="utf-8").strip()
            except OSError:
                holder_pid = ""
        if holder_pid and pid_is_running(holder_pid):
            return False, holder_pid
        shutil.rmtree(lock_dir, ignore_errors=True)
        lock_dir.mkdir()

    try:
        pid_path.write_text(f"{os.getpid()}\n", encoding="utf-8")
        owner_path.write_text(owner_label + "\n", encoding="utf-8")
    except OSError:
        shutil.rmtree(lock_dir, ignore_errors=True)
        raise
    return True, None


def release_cycle_lock(paths: dict[str, Path]) -> None:
    shutil.rmtree(paths["cycle_lock"], ignore_errors=True)


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


def git_run(
    *args: str,
    capture_output: bool = True,
    check: bool = False,
    input_text: str | None = None,
    timeout_seconds: int | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        input=input_text,
        text=True,
        capture_output=capture_output,
        check=check,
        timeout=timeout_seconds,
    )


def git_stdout(*args: str) -> str:
    result = git_run(*args)
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def git_status_lines(*, untracked_all: bool = False) -> list[str]:
    args = ["status", "--porcelain"]
    if untracked_all:
        args.append("--untracked-files=all")
    result = git_run(*args)
    if result.returncode != 0:
        return []
    output = result.stdout
    return [line for line in output.splitlines() if line]


def git_worktree_dirty() -> bool:
    return bool(git_status_lines())


def git_status_paths(line: str) -> list[str]:
    if len(line) <= 3:
        return []
    payload = line[3:]
    if " -> " in payload and ("R" in line[:2] or "C" in line[:2]):
        before_path, after_path = payload.split(" -> ", 1)
        return [before_path, after_path]
    return [payload]


def git_dirty_paths(*, untracked_all: bool = False) -> set[str]:
    paths: set[str] = set()
    for line in git_status_lines(untracked_all=untracked_all):
        for path in git_status_paths(line):
            if path:
                paths.add(path)
    return paths


def worktree_path_fingerprint(path_text: str) -> tuple[str, int | None, str | None]:
    path = REPO_ROOT / path_text
    try:
        stat_result = path.lstat()
    except FileNotFoundError:
        return ("missing", None, None)
    except OSError:
        return ("error", None, None)

    if path.is_symlink():
        try:
            return ("symlink", stat_result.st_mode, os.readlink(path))
        except OSError:
            return ("symlink-error", stat_result.st_mode, None)

    if path.is_file():
        try:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError:
            return ("file-error", stat_result.st_mode, None)
        return ("file", stat_result.st_mode, digest)

    return ("other", stat_result.st_mode, str(stat_result.st_size))


def snapshot_worktree_paths(paths: set[str]) -> dict[str, tuple[str, int | None, str | None]]:
    return {path: worktree_path_fingerprint(path) for path in sorted(paths)}


def changed_snapshot_paths(
    snapshot: dict[str, tuple[str, int | None, str | None]],
) -> list[str]:
    changed: list[str] = []
    for path, fingerprint in snapshot.items():
        if worktree_path_fingerprint(path) != fingerprint:
            changed.append(path)
    return changed


def git_dirty_summary(*, limit: int = DIRTY_STATUS_SAMPLE_LIMIT) -> dict[str, Any]:
    status_lines = git_status_lines()
    return {
        "count": len(status_lines),
        "sample": status_lines[:limit],
        "truncated": len(status_lines) > limit,
    }


def git_branch() -> str:
    return git_stdout("branch", "--show-current")


def git_head() -> str:
    return git_stdout("rev-parse", "HEAD")


def git_upstream_ref(config: dict[str, Any]) -> str:
    policy = config.get("git_policy", {})
    remote = str(policy.get("push_remote", "origin"))
    branch = str(policy.get("push_branch") or git_branch() or "main")
    return f"{remote}/{branch}"


def git_ahead_count(config: dict[str, Any]) -> int | None:
    ahead, _ = git_ahead_behind_counts(config)
    return ahead


def git_behind_count(config: dict[str, Any]) -> int | None:
    _, behind = git_ahead_behind_counts(config)
    return behind


def git_ahead_behind_counts(config: dict[str, Any]) -> tuple[int | None, int | None]:
    upstream = git_upstream_ref(config)
    result = git_run("rev-list", "--left-right", "--count", f"HEAD...{upstream}")
    if result.returncode != 0:
        return None, None
    parts = result.stdout.strip().split()
    if len(parts) != 2:
        return None, None
    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        return None, None


def tracked_json_blob_paths() -> list[str]:
    output = git_stdout("ls-files", "*.json")
    return [line for line in output.splitlines() if line]


def tracked_json_blob_count() -> int:
    return len(tracked_json_blob_paths())


def recent_git_commits(limit: int) -> list[dict[str, str]]:
    if limit <= 0:
        return []
    output = git_stdout(
        "log",
        f"-n{limit}",
        "--date=short",
        "--format=%h%x09%ad%x09%s",
    )
    commits: list[dict[str, str]] = []
    for line in output.splitlines():
        parts = line.split("\t", 2)
        if len(parts) != 3:
            continue
        commits.append({"sha": parts[0], "date": parts[1], "subject": parts[2]})
    return commits


def list_task_files(status: str) -> list[Path]:
    queue_dir = TASK_ROOT / status
    if not queue_dir.exists():
        return []
    return sorted(
        [path for path in queue_dir.iterdir() if path.is_file() and path.name != ".gitkeep"],
        key=lambda path: path.name,
    )


def recent_tasks(status: str, limit: int) -> list[dict[str, str]]:
    tasks = [path for path in list_task_files(status)]
    tasks.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    rows: list[dict[str, str]] = []
    for path in tasks[:limit]:
        rows.append(
            {
                "name": path.name,
                "path": relpath(path),
                "updated_at": datetime.fromtimestamp(path.stat().st_mtime, UTC)
                .replace(microsecond=0)
                .isoformat(),
            }
        )
    return rows


def queue_counts() -> dict[str, int]:
    return {status: len(list_task_files(status)) for status in TASK_STATUSES}


def agent_may_dispatch_on_dirty_worktree(agent: AgentSpec) -> bool:
    if agent.kind == "supervisor":
        return True
    return bool(agent.dispatch.get("allow_dirty_worktree", False))


def list_user_ask_files(status: str) -> list[Path]:
    queue_dir = USER_ASK_ROOT / status
    if not queue_dir.exists():
        return []
    return sorted(
        [
            path
            for path in queue_dir.iterdir()
            if path.is_file() and path.name not in {".gitkeep", "README.md"}
        ],
        key=lambda path: path.name,
    )


def user_ask_counts() -> dict[str, int]:
    return {status: len(list_user_ask_files(status)) for status in USER_ASK_STATUSES}


def is_user_ask_name(name: str) -> bool:
    return name.startswith("USER-ASK")


def reroute_misplaced_user_asks() -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    for status in TASK_STATUSES:
        queue_dir = TASK_ROOT / status
        if not queue_dir.exists():
            continue
        for path in sorted(
            [
                candidate
                for candidate in queue_dir.iterdir()
                if candidate.is_file() and is_user_ask_name(candidate.name)
            ],
            key=lambda candidate: candidate.name,
        ):
            dest_status = "done" if status in {"done", "blocked"} else "inbox"
            dest_dir = USER_ASK_ROOT / dest_status
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / path.name
            if dest.exists():
                suffix = f".from-{status}"
                deduped = dest_dir / f"{path.name}{suffix}"
                counter = 2
                while deduped.exists():
                    deduped = dest_dir / f"{path.name}{suffix}-{counter}"
                    counter += 1
                dest = deduped
            path.replace(dest)
            actions.append(
                {
                    "task_name": path.name,
                    "action": "rerouted_misplaced_user_ask",
                    "severity": "warning",
                    "final_status": dest_status,
                    "path": relpath(dest),
                }
            )
    return actions


def task_metadata_value(path: Path, key: str) -> str | None:
    prefix = f"{key}:"
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    for line in lines:
        if line.startswith(prefix):
            value = line.partition(":")[2].strip()
            return value or None
        if line.startswith("## "):
            break
    return None


def claimable_task_files(queue: str, accepted_owners: set[str] | None = None) -> list[Path]:
    owners = None if accepted_owners is None else {owner.strip() for owner in accepted_owners}
    claimable: list[Path] = []
    for path in list_task_files(queue):
        if owners is not None:
            owner = task_metadata_value(path, "Owner") or ""
            if owner not in owners:
                continue
        claimable.append(path)
    return claimable


def claim_tasks(
    queue: str,
    claim_to: str,
    limit: int,
    accepted_owners: set[str] | None = None,
) -> list[Path]:
    claimed: list[Path] = []
    dest_dir = TASK_ROOT / claim_to
    dest_dir.mkdir(parents=True, exist_ok=True)
    for src in claimable_task_files(queue, accepted_owners)[:limit]:
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


def set_task_status_line(text: str, status: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.startswith("Status: "):
            lines[index] = f"Status: {status}"
            break
    else:
        insert_at = 1 if lines else 0
        lines.insert(insert_at, f"Status: {status}")
    return "\n".join(lines).rstrip("\n") + "\n"


def append_task_note(path: Path, note: str, *, status: str | None = None) -> None:
    text = path.read_text(encoding="utf-8")
    if status is not None:
        text = set_task_status_line(text, status)
    bullet = f"- {note}"
    if "## Notes" not in text:
        text = text.rstrip("\n") + "\n\n## Notes\n" + bullet + "\n"
        write_text(path, text)
        return

    lines = text.splitlines()
    notes_index = lines.index("## Notes")
    insert_at = len(lines)
    for index in range(notes_index + 1, len(lines)):
        if lines[index].startswith("## "):
            insert_at = index
            while insert_at > notes_index + 1 and lines[insert_at - 1] == "":
                insert_at -= 1
            break
    lines.insert(insert_at, bullet)
    write_text(path, "\n".join(lines).rstrip("\n") + "\n")


def move_task_with_note(path: Path, dest_status: str, note: str) -> Path:
    dest = TASK_ROOT / dest_status / path.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    if path != dest:
        path.replace(dest)
    append_task_note(dest, note, status=dest_status)
    return dest


def move_task(path: Path, dest_status: str) -> Path:
    dest = TASK_ROOT / dest_status / path.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    if path != dest:
        path.replace(dest)
    return dest


def load_task_state(paths: dict[str, Path]) -> dict[str, Any]:
    payload = read_json(paths["task_state"], default={})
    return payload if isinstance(payload, dict) else {}


def task_state_entry(task_state: dict[str, Any], task_name: str) -> dict[str, Any]:
    entry = task_state.get(task_name)
    if not isinstance(entry, dict):
        entry = {}
    task_state[task_name] = entry
    return entry


def load_readme_reporting_config(config: dict[str, Any]) -> dict[str, Any]:
    reporting_cfg = config.get("reporting", {})
    path = resolve_repo_path(
        reporting_cfg.get("readme_config_path", str(README_REPORTING_CONFIG_PATH))
    )
    payload = read_json(path, default={})
    if not isinstance(payload, dict):
        return {"readme_path": "README.md", "capability_tracks": [], "benchmark_scorecard": {}}
    payload.setdefault("readme_path", "README.md")
    payload.setdefault("capability_tracks", [])
    payload.setdefault("benchmark_scorecard", {})
    payload.setdefault("status_sections", {})
    payload.setdefault("readme_limits", {})
    return payload


def markdown_sections(path: Path) -> dict[str, list[str]]:
    if not path.exists():
        return {}
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
            continue
        if current is not None:
            sections[current].append(line)
    return sections


def first_nonempty_line(lines: list[str]) -> str:
    for line in lines:
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def bullet_lines(lines: list[str]) -> list[str]:
    bullets: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- "):
            bullets.append(stripped[2:].strip())
    return bullets


def configured_section_lines(
    sections: dict[str, list[str]],
    reporting_cfg: dict[str, Any],
    key: str,
    default_name: str,
) -> list[str]:
    configured_name = ""
    raw_sections = reporting_cfg.get("status_sections", {})
    if isinstance(raw_sections, dict):
        raw_name = raw_sections.get(key)
        if isinstance(raw_name, str):
            configured_name = raw_name.strip()

    names = [name for name in (configured_name, default_name) if name]
    for name in names:
        lines = sections.get(name, [])
        if first_nonempty_line(lines):
            return lines
    return []


def limited_items(items: list[str], raw_limit: Any) -> list[str]:
    if not isinstance(raw_limit, (int, float)):
        return items
    limit = int(raw_limit)
    if limit <= 0:
        return []
    return items[:limit]


def task_queue_index() -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for status in TASK_STATUSES:
        for path in list_task_files(status):
            index[path.name] = {"status": status, "path": path}
    return index


def matching_repo_paths(entry: dict[str, Any]) -> list[Path]:
    matches: list[Path] = []
    seen: set[str] = set()
    for raw in entry.get("paths_any", []):
        if not isinstance(raw, str) or not raw:
            continue
        path = resolve_repo_path(raw)
        if path.exists():
            key = str(path)
            if key not in seen:
                matches.append(path)
                seen.add(key)
    for raw in entry.get("globs_any", []):
        if not isinstance(raw, str) or not raw:
            continue
        for path in sorted(REPO_ROOT.glob(raw)):
            if not path.is_file():
                continue
            key = str(path)
            if key not in seen:
                matches.append(path)
                seen.add(key)
    return matches


def markdown_link(path: Path | str) -> str:
    raw = str(path)
    return f"[`{raw}`]({raw})"


def capability_track_rows(config: dict[str, Any]) -> list[dict[str, Any]]:
    reporting_cfg = load_readme_reporting_config(config)
    queue_index = task_queue_index()
    rows: list[dict[str, Any]] = []
    status_score = {
        "complete": 1.0,
        "in progress": 0.6,
        "planned": 0.25,
        "blocked": 0.1,
        "not started": 0.0,
    }

    for raw_entry in reporting_cfg.get("capability_tracks", []):
        if not isinstance(raw_entry, dict):
            continue
        entry = dict(raw_entry)
        label = str(entry.get("label", "Unnamed capability")).strip() or "Unnamed capability"
        description = str(entry.get("description", "")).strip()
        matches = matching_repo_paths(entry)
        task_name = entry.get("task")
        task_info = queue_index.get(str(task_name)) if task_name else None

        if matches:
            status = "complete"
            evidence = markdown_link(relpath(matches[0]))
        elif task_info is not None:
            status = {
                "ready": "planned",
                "in_progress": "in progress",
                "blocked": "blocked",
                "done": "complete",
            }.get(str(task_info["status"]), "planned")
            evidence = markdown_link(relpath(task_info["path"]))
        else:
            status = "not started"
            evidence = "`not yet queued`"

        rows.append(
            {
                "label": label,
                "description": description,
                "status": status,
                "score": status_score.get(status, 0.0),
                "evidence": evidence,
            }
        )
    return rows


def first_present(*values: Any) -> Any:
    for value in values:
        if value is not None:
            return value
    return None


def numeric_ratio(numerator: Any, denominator: Any) -> float | None:
    if isinstance(numerator, bool) or isinstance(denominator, bool):
        return None
    if not isinstance(numerator, (int, float)) or not isinstance(denominator, (int, float)):
        return None
    if denominator == 0:
        return None
    return round(float(numerator) / float(denominator), 4)


def scorecard_from_config(config: dict[str, Any], key: str, default_title: str, default_path: str) -> dict[str, Any]:
    reporting_cfg = load_readme_reporting_config(config)
    raw = reporting_cfg.get(key, {})
    if not isinstance(raw, dict):
        raw = {}
    rel = str(raw.get("path", default_path))
    path = resolve_repo_path(rel)
    scorecard: dict[str, Any] = {
        "title": str(raw.get("title", default_title)),
        "path": relpath(path),
        "available": False,
    }
    if not path.exists():
        return scorecard

    payload = read_json(path, default=None)
    if not isinstance(payload, dict):
        scorecard["error"] = "invalid_json"
        return scorecard

    summary = payload.get("summary")
    if not isinstance(summary, dict):
        summary = {}

    workloads = payload.get("workloads")
    if not isinstance(workloads, list):
        workloads = []
    cases = payload.get("cases")
    if not isinstance(cases, list):
        cases = []

    baseline = payload.get("baseline")
    if not isinstance(baseline, dict):
        baseline = {}
    implementation = payload.get("implementation")
    if not isinstance(implementation, dict):
        implementation = {}

    cases_total = first_present(summary.get("cases_total"), summary.get("total_cases"))
    cases_passed = first_present(
        summary.get("cases_passed"),
        summary.get("passed_cases"),
        summary.get("passed"),
    )
    cases_failed = first_present(summary.get("failed_cases"), summary.get("failed"))
    cases_skipped = first_present(summary.get("skipped_cases"), summary.get("skipped"), 0)
    cases_unimplemented = first_present(
        summary.get("unimplemented_cases"),
        summary.get("known_gap_count"),
        0,
    )
    case_manifest_ids = sorted(
        {
            str(case.get("manifest_id")).strip()
            for case in cases
            if str(case.get("manifest_id") or "").strip()
        }
    )
    implemented_cases = None
    if isinstance(cases_total, (int, float)):
        implemented_cases = cases_total
        if isinstance(cases_skipped, (int, float)):
            implemented_cases -= cases_skipped
        if isinstance(cases_unimplemented, (int, float)):
            implemented_cases -= cases_unimplemented
        if implemented_cases < 0:
            implemented_cases = None
    pass_rate = first_present(summary.get("pass_rate"), numeric_ratio(cases_passed, cases_total))
    parity_rate = first_present(
        summary.get("parity_rate"),
        numeric_ratio(cases_passed, implemented_cases),
        pass_rate,
    )
    candidate = first_present(
        payload.get("candidate"),
        summary.get("candidate"),
        implementation.get("module_name"),
        baseline.get("target_module"),
        "rebar",
    )

    scorecard.update(
        {
            "available": True,
            "generated_at": payload.get("generated_at") or summary.get("generated_at"),
            "baseline": first_present(payload.get("baseline"), summary.get("baseline")),
            "candidate": candidate,
            "workload_count": first_present(summary.get("total_workloads"), len(workloads)),
            "measured_workloads": summary.get("measured_workloads"),
            "known_gap_count": summary.get("known_gap_count"),
            "geomean_speedup": summary.get("geomean_speedup_vs_baseline"),
            "median_speedup": summary.get("median_speedup_vs_baseline"),
            "cases_total": cases_total,
            "cases_passed": cases_passed,
            "cases_failed": cases_failed,
            "cases_unimplemented": cases_unimplemented,
            "case_manifest_count": len(case_manifest_ids),
            "case_manifest_ids": case_manifest_ids,
            "pass_rate": pass_rate,
            "parity_rate": parity_rate,
            "timing_path": first_present(
                implementation.get("timing_path"),
                implementation.get("adapter_mode_resolved"),
                implementation.get("build_mode"),
            ),
            "native_module_loaded": implementation.get("native_module_loaded"),
        }
    )
    return scorecard


def tracked_project_snapshot(config: dict[str, Any]) -> dict[str, Any]:
    status_sections = markdown_sections(STATE_ROOT / "current_status.md")
    backlog_sections = markdown_sections(STATE_ROOT / "backlog.md")
    reporting_cfg = load_readme_reporting_config(config)
    readme_limits = reporting_cfg.get("readme_limits", {})
    if not isinstance(readme_limits, dict):
        readme_limits = {}
    tracks = capability_track_rows(config)
    total_tracks = len(tracks)
    total_score = sum(float(item.get("score", 0.0)) for item in tracks)
    completion_ratio = 0.0 if total_tracks == 0 else total_score / total_tracks

    phase = first_nonempty_line(
        configured_section_lines(status_sections, reporting_cfg, "phase", "Phase")
    )
    delivery_estimate = first_nonempty_line(
        configured_section_lines(
            status_sections,
            reporting_cfg,
            "delivery_estimate",
            "Compatibility Heuristic",
        )
    )
    next_steps = bullet_lines(
        configured_section_lines(status_sections, reporting_cfg, "next_steps", "Immediate Next Steps")
    )
    risks = bullet_lines(
        configured_section_lines(status_sections, reporting_cfg, "risks", "Risks")
    )

    return {
        "phase": phase,
        "delivery_estimate": delivery_estimate,
        "compatibility_heuristic": first_nonempty_line(
            status_sections.get("Compatibility Heuristic", [])
        ),
        "milestone": first_nonempty_line(backlog_sections.get("Current Milestone", [])),
        "next_steps": limited_items(next_steps, readme_limits.get("next_steps")),
        "risks": limited_items(risks, readme_limits.get("risks")),
        "queue_counts": queue_counts(),
        "capability_tracks": tracks,
        "completion_ratio": completion_ratio,
        "complete_tracks": sum(1 for item in tracks if item.get("status") == "complete"),
        "correctness_scorecard": scorecard_from_config(
            config,
            "correctness_scorecard",
            "Correctness Snapshot",
            "reports/correctness/latest.json",
        ),
        "benchmark_scorecard": scorecard_from_config(
            config,
            "benchmark_scorecard",
            "Benchmark Snapshot",
            "reports/benchmarks/latest.json",
        ),
    }


def ascii_progress_bar(ratio: float, width: int = 18) -> str:
    bounded = max(0.0, min(1.0, ratio))
    filled = int(round(bounded * width))
    return "[" + "#" * filled + "." * (width - filled) + "]"


def summarize_benchmark_baseline(raw_baseline: Any) -> str:
    if not isinstance(raw_baseline, dict):
        return str(raw_baseline) if raw_baseline else "Unknown"

    implementation = str(raw_baseline.get("python_implementation") or "").strip()
    version = str(
        raw_baseline.get("python_version") or raw_baseline.get("python_version_family") or ""
    ).strip()
    executable = str(raw_baseline.get("executable") or "").strip()
    re_module = str(raw_baseline.get("re_module") or "").strip()

    headline = " ".join(part for part in (implementation, version) if part)
    details: list[str] = []
    if re_module:
        details.append(f"module `{re_module}`")
    if executable:
        details.append(f"exe `{executable}`")

    if headline and details:
        return f"{headline} ({', '.join(details)})"
    if headline:
        return headline
    if details:
        return ", ".join(details)
    return "Unknown"


def replace_markdown_block(text: str, start_marker: str, end_marker: str, block: str) -> str:
    normalized = block.rstrip("\n")
    if start_marker in text and end_marker in text:
        prefix, remainder = text.split(start_marker, 1)
        _, suffix = remainder.split(end_marker, 1)
        return prefix + start_marker + "\n" + normalized + "\n" + end_marker + suffix
    base = text.rstrip("\n")
    return base + "\n\n" + start_marker + "\n" + normalized + "\n" + end_marker + "\n"


def render_readme_status(config: dict[str, Any]) -> str:
    snapshot = tracked_project_snapshot(config)
    queue = snapshot["queue_counts"]
    tracks = snapshot["capability_tracks"]
    correctness = snapshot["correctness_scorecard"]
    benchmark = snapshot["benchmark_scorecard"]
    total_tracks = len(tracks)
    completion_ratio = float(snapshot["completion_ratio"])
    delivery_estimate = snapshot.get("delivery_estimate") or "Unknown"
    lines = [
        "## Current State",
        "",
        "_This block reports the implemented slice and measurement coverage, not estimated end-state parity._",
        "",
        "| Signal | Value |",
        "| --- | --- |",
        f"| Phase | {snapshot['phase'] or 'Unknown'} |",
        f"| Delivery estimate | {delivery_estimate} |",
        f"| Current milestone | {snapshot['milestone'] or 'Unknown'} |",
        f"| Work queue | `{queue['ready']}` ready, `{queue['in_progress']}` in progress, `{queue['done']}` done, `{queue['blocked']}` blocked |",
        f"| Foundation tracks | `{snapshot['complete_tracks']}/{total_tracks}` landed (`{ascii_progress_bar(completion_ratio)} {int(round(completion_ratio * 100))}%`) |",
    ]

    lines.extend(["", f"### {correctness['title']}", ""])
    if not correctness.get("available"):
        lines.append(
            f"No published correctness scorecard yet. Expected tracked source: {markdown_link(correctness['path'])}."
        )
    else:
        lines.extend(
            [
                "| Metric | Value |",
                "| --- | --- |",
                f"| Published cases | `{correctness.get('cases_total')}` |",
                f"| Passing in published slice | `{correctness.get('cases_passed')}` |",
                f"| Explicit failures | `{correctness.get('cases_failed')}` |",
                f"| Honest gaps (`unimplemented`) | `{correctness.get('cases_unimplemented')}` |",
                f"| Covered manifests | `{correctness.get('case_manifest_count')}` |",
                f"| Source | {markdown_link(correctness['path'])} |",
            ]
        )
        lines.extend(
            [
                "",
                f"_These correctness counts cover only the published slice. Overall delivery estimate: {delivery_estimate}_",
            ]
        )

    lines.extend(["", f"### {benchmark['title']}", ""])
    if not benchmark.get("available"):
        lines.append(
            f"No published benchmark scorecard yet. Expected tracked source: {markdown_link(benchmark['path'])}."
        )
    else:
        lines.extend(
            [
                "| Metric | Value |",
                "| --- | --- |",
                f"| Baseline | {summarize_benchmark_baseline(benchmark.get('baseline'))} |",
                f"| Published workloads | `{benchmark.get('workload_count', 0)}` |",
                f"| Workloads with real `rebar` timings | `{benchmark.get('measured_workloads')}` |",
                f"| Known-gap workloads | `{benchmark.get('known_gap_count')}` |",
                f"| Timing path | `{benchmark.get('timing_path') or 'unknown'}` |",
                f"| Source | {markdown_link(benchmark['path'])} |",
            ]
        )
        if benchmark.get("timing_path") == "source-tree-shim":
            native_full_exists = resolve_repo_path("reports/benchmarks/native_full.json").exists()
            lines.extend(
                [
                    "",
                    (
                        "_Full-suite benchmark publication still runs through the source-tree shim; strict built-native sidecars are checked in separately at "
                        + markdown_link("reports/benchmarks/native_full.json")
                        + " for the latest built-native full-suite run and "
                        + markdown_link("reports/benchmarks/native_smoke.json")
                        + " for the smoke slice._"
                        if native_full_exists
                        else "_Full-suite benchmark publication still runs through the source-tree shim; built-native timing remains limited to "
                        + markdown_link("reports/benchmarks/native_smoke.json")
                        + "._"
                    ),
                ]
            )
        measured_workloads = benchmark.get("measured_workloads")
        workload_count = benchmark.get("workload_count")
        if (
            isinstance(measured_workloads, (int, float))
            and isinstance(workload_count, (int, float))
            and measured_workloads < workload_count
        ):
            lines.extend(
                [
                    "",
                    f"_README speedup rollups stay omitted while only `{int(measured_workloads)}` of `{int(workload_count)}` published workloads have real `rebar` timings._",
                ]
            )

    next_steps = snapshot.get("next_steps", [])
    if next_steps:
        lines.extend(["", "### Immediate Next Steps", ""])
        for item in next_steps:
            lines.append(f"- {item}")

    risks = snapshot.get("risks", [])
    if risks:
        lines.extend(["", "### Current Risks", ""])
        for item in risks:
            lines.append(f"- {item}")

    return "\n".join(lines) + "\n"


def sync_readme_status(config: dict[str, Any]) -> None:
    reporting_cfg = load_readme_reporting_config(config)
    readme_path = resolve_repo_path(str(reporting_cfg.get("readme_path", "README.md")))
    current = readme_path.read_text(encoding="utf-8")
    updated = replace_markdown_block(
        current,
        README_STATUS_START,
        README_STATUS_END,
        render_readme_status(config),
    )
    if updated != current:
        write_text(readme_path, updated)


def load_agent_specs(config: dict[str, Any]) -> list[AgentSpec]:
    agents_cfg = config.get("agents", {})
    agent_dir = resolve_repo_path(agents_cfg.get("directory", "ops/agents"))
    specs: list[AgentSpec] = []
    seen: set[str] = set()

    for spec_path in sorted(agent_dir.glob("*.json")):
        raw = read_json(spec_path, default=None)
        if not isinstance(raw, dict):
            raise RuntimeError(f"Invalid agent spec: {spec_path}")
        name = str(raw.get("name", spec_path.stem))
        if name in seen:
            raise RuntimeError(f"Duplicate agent name: {name}")
        seen.add(name)
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


def render_prompt(agent: AgentSpec, config: dict[str, Any], task_path: Path | None = None) -> str:
    paths = runtime_paths(config)
    body = agent.prompt_path.read_text(encoding="utf-8").strip()
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
            f"- task state: {relpath(paths['task_state'])}",
            f"- dashboard: {relpath(paths['dashboard_markdown'])}",
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
            "USER-ASK directories:",
            f"- inbox: {relpath(USER_ASK_ROOT / 'inbox')}",
            f"- done: {relpath(USER_ASK_ROOT / 'done')}",
            "",
            body,
            "",
            "Commit policy:",
            "- End your run with a concise final summary of what changed and what you verified.",
            "- If tracked files changed, the harness will commit them immediately after your run.",
            "- Generated commit subjects use the format `<agent-name>: <brief description>` and the body is derived from your final message plus the changed-file list.",
            "",
            "Leave durable state in tracked files under ops/ when it matters.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_write_probe_prompt(probe_relpath: str, token: str) -> str:
    return (
        "# Rebar Worker Write Probe\n\n"
        "Create exactly one file at the path below with the exact token shown below, then stop.\n"
        "This is an environment probe, not project work. Do not edit tracked files.\n\n"
        f"Probe path: `{probe_relpath}`\n"
        f"Required contents: `{token}`\n"
    )


def build_codex_command(
    *,
    config: dict[str, Any],
    agent: AgentSpec,
    output_path: Path,
    cwd: Path,
) -> list[str]:
    defaults = config.get("codex_defaults", {})
    cmd = [str(defaults.get("bin", "codex"))]

    bypass_all = bool(
        agent.codex.get(
            "dangerously_bypass_approvals_and_sandbox",
            defaults.get("dangerously_bypass_approvals_and_sandbox", False),
        )
    )
    sandbox = agent.codex.get("sandbox", defaults.get("sandbox"))
    ask_for_approval = agent.codex.get("ask_for_approval", defaults.get("ask_for_approval"))
    if bypass_all:
        cmd.append("--dangerously-bypass-approvals-and-sandbox")
    else:
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


def requested_sandbox(config: dict[str, Any], agent: AgentSpec) -> str | None:
    defaults = config.get("codex_defaults", {})
    sandbox = agent.codex.get("sandbox", defaults.get("sandbox"))
    if sandbox is None:
        return None
    return str(sandbox)


def observed_sandbox(*texts: str) -> str | None:
    for text in texts:
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if line.startswith("sandbox:"):
                value = line.split(":", 1)[1].strip()
                return value or None
    return None


def detect_environment_issue(
    *,
    requested: str | None,
    observed: str | None,
    stdout_text: str,
    stderr_text: str,
    last_message_text: str,
) -> str | None:
    requested_writable = requested not in {None, "", "read-only"}
    if requested_writable and observed == "read-only":
        return "sandbox_clamped_to_read_only"
    # Codex stdout/stderr can both contain the echoed prompt and tool transcript, so
    # only the explicit sandbox banner and the agent-authored last message are stable
    # enough to classify environment failures.
    combined = last_message_text.lower()
    if requested_writable and (
        "this codex session is read-only" in combined
        or "sandboxed `read-only`" in combined
        or "sandbox: read-only" in combined
        or "read-only filesystem" in combined
        or "writing outside of the project; rejected by user approval settings" in combined
        or "rerun this task in a writable checkout" in combined
    ):
        return "sandbox_clamped_to_read_only"
    if "permissionerror" in combined and "/.cache/codex/meta.json" in combined:
        return "codex_cache_not_writable"
    return None


def read_text_if_exists(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def run_artifact_path(run_dir: Path, raw_path: Any, fallback_name: str) -> Path:
    if isinstance(raw_path, str) and raw_path:
        return resolve_repo_path(raw_path)
    return run_dir / fallback_name


def normalize_report_run(paths: dict[str, Path], raw_run: dict[str, Any]) -> dict[str, Any]:
    record = dict(raw_run)
    run_id = str(record.get("run_id", "")).strip()
    if not run_id:
        return record

    run_dir = paths["runs_root"] / run_id
    metadata = read_json(run_dir / "metadata.json", default={})
    if not isinstance(metadata, dict):
        metadata = {}

    stdout_path = run_artifact_path(run_dir, metadata.get("stdout_path"), "stdout.log")
    stderr_path = run_artifact_path(run_dir, metadata.get("stderr_path"), "stderr.log")
    last_message_path = run_artifact_path(
        run_dir, metadata.get("last_message_path"), "last_message.md"
    )
    stdout_text = read_text_if_exists(stdout_path)
    stderr_text = read_text_if_exists(stderr_path)
    last_message_text = read_text_if_exists(last_message_path)
    requested = metadata.get("requested_sandbox", record.get("requested_sandbox"))
    observed = observed_sandbox(stdout_text, stderr_text)
    record["environment_issue"] = detect_environment_issue(
        requested=requested if isinstance(requested, str) else None,
        observed=observed,
        stdout_text=stdout_text,
        stderr_text=stderr_text,
        last_message_text=last_message_text,
    )
    return record


def build_report_anomalies(
    last_cycle_runs: list[dict[str, Any]],
    recovery_actions: list[dict[str, Any]],
    commit_actions: list[dict[str, Any]],
    git_action: dict[str, Any],
    *,
    ahead_of_upstream: int | None = None,
    behind_of_upstream: int | None = None,
) -> list[dict[str, Any]]:
    anomalies: list[dict[str, Any]] = []
    current_diverged = bool((ahead_of_upstream or 0) > 0 and (behind_of_upstream or 0) > 0)
    for item in last_cycle_runs:
        exit_code = item.get("exit_code")
        if isinstance(exit_code, int) and exit_code != 0:
            anomalies.append(
                {
                    "type": "agent_nonzero_exit",
                    "severity": "error",
                    "agent_name": item.get("agent_name"),
                    "run_id": item.get("run_id"),
                    "exit_code": exit_code,
                    "timed_out": item.get("timed_out"),
                }
            )
        environment_issue = item.get("environment_issue")
        if environment_issue is not None:
            anomalies.append(
                {
                    "type": "agent_environment_issue",
                    "severity": "error",
                    "agent_name": item.get("agent_name"),
                    "run_id": item.get("run_id"),
                    "environment_issue": environment_issue,
                }
            )
    anomalies.extend(
        {
            "type": "task_recovery",
            "severity": action["severity"],
            "task_name": action["task_name"],
            "action": action["action"],
            "final_status": action["final_status"],
            "path": action["path"],
        }
        for action in recovery_actions
    )
    for action in commit_actions:
        for message in action.get("errors", []):
            anomalies.append(
                {
                    "type": "agent_commit_error",
                    "severity": "error",
                    "agent_name": action.get("agent_name"),
                    "message": message,
                }
            )
    for message in git_action.get("errors", []):
        if (
            isinstance(message, str)
            and "diverged" in message.lower()
            and not current_diverged
        ):
            continue
        anomalies.append({"type": "git_sync_error", "severity": "error", "message": message})
    return anomalies


def parse_iso8601_timestamp(value: str | None) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        return None


def agent_in_environment_backoff(agent: AgentSpec, loop_state: dict[str, Any]) -> bool:
    backoff_seconds = int(agent.dispatch.get("environment_issue_backoff_seconds", 0))
    if backoff_seconds <= 0:
        return False
    last = agent_last_state(loop_state, agent.name)
    if not last.get("environment_issue"):
        return False
    finished_at = parse_iso8601_timestamp(last.get("finished_at"))
    if finished_at is None:
        return False
    delta = datetime.now(UTC) - finished_at
    return delta.total_seconds() < backoff_seconds


def task_timeout_seconds(config: dict[str, Any], agent: AgentSpec) -> int:
    runtime_cfg = config.get("runtime", {})
    return int(agent.dispatch.get("timeout_seconds", runtime_cfg.get("default_timeout_seconds", 1800)))


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
    requested = requested_sandbox(config, agent)
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
    observed = observed_sandbox(stdout_text, stderr_text)
    write_text(stdout_path, stdout_text)
    write_text(stderr_path, stderr_text)
    if not output_path.exists():
        write_text(output_path, "")
    last_message_text = output_path.read_text(encoding="utf-8")
    environment_issue = detect_environment_issue(
        requested=requested,
        observed=observed,
        stdout_text=stdout_text,
        stderr_text=stderr_text,
        last_message_text=last_message_text,
    )

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
        "requested_sandbox": requested,
        "observed_sandbox": observed,
        "environment_issue": environment_issue,
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
        requested_sandbox=requested,
        observed_sandbox=observed,
        environment_issue=environment_issue,
    )


def run_write_probe(agent: AgentSpec, config: dict[str, Any]) -> RunResult:
    paths = runtime_paths(config)
    ensure_runtime_dirs(paths)

    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"{stamp}-{agent.name}-preflight-write-probe"
    run_dir = paths["runs_root"] / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    probe_dir = paths["artifact_root"] / "probes"
    probe_dir.mkdir(parents=True, exist_ok=True)
    probe_path = probe_dir / f"{run_id}.txt"
    probe_token = run_id

    prompt_text = render_write_probe_prompt(relpath(probe_path), probe_token)
    prompt_path = run_dir / "prompt.md"
    output_path = run_dir / "last_message.md"
    stdout_path = run_dir / "stdout.log"
    stderr_path = run_dir / "stderr.log"
    metadata_path = run_dir / "metadata.json"
    write_text(prompt_path, prompt_text)

    command = build_codex_command(config=config, agent=agent, output_path=output_path, cwd=REPO_ROOT)
    env = build_codex_env(config)
    timeout_seconds = int(agent.dispatch.get("probe_timeout_seconds", 120))
    requested = requested_sandbox(config, agent)
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
    observed = observed_sandbox(stdout_text, stderr_text)
    write_text(stdout_path, stdout_text)
    write_text(stderr_path, stderr_text)
    if not output_path.exists():
        write_text(output_path, "")
    last_message_text = output_path.read_text(encoding="utf-8")

    probe_ok = False
    if probe_path.exists():
        try:
            probe_ok = probe_path.read_text(encoding="utf-8").rstrip("\r\n") == probe_token
        except OSError:
            probe_ok = False
        try:
            probe_path.unlink()
        except OSError:
            pass

    environment_issue = detect_environment_issue(
        requested=requested,
        observed=observed,
        stdout_text=stdout_text,
        stderr_text=stderr_text,
        last_message_text=last_message_text,
    )
    if not probe_ok and environment_issue is None:
        environment_issue = "child_write_probe_failed"

    metadata = {
        "agent_name": agent.name,
        "agent_kind": agent.kind,
        "run_id": run_id,
        "task_initial_path": None,
        "task_final_status": None,
        "task_final_path": None,
        "command": command,
        "cwd": str(REPO_ROOT),
        "started_at": started_at,
        "finished_at": finished_at,
        "exit_code": exit_code,
        "timed_out": timed_out,
        "requested_sandbox": requested,
        "observed_sandbox": observed,
        "environment_issue": environment_issue,
        "probe_path": relpath(probe_path),
        "probe_ok": probe_ok,
        "timeout_seconds": timeout_seconds,
        "prompt_path": relpath(prompt_path),
        "stdout_path": relpath(stdout_path),
        "stderr_path": relpath(stderr_path),
        "last_message_path": relpath(output_path),
    }
    write_json(metadata_path, metadata)

    effective_exit_code = exit_code if probe_ok and environment_issue is None else max(exit_code, 75)
    return RunResult(
        agent_name=agent.name,
        agent_kind=agent.kind,
        run_id=run_id,
        exit_code=effective_exit_code,
        timed_out=timed_out,
        run_dir=run_dir,
        task_initial_path=None,
        task_final_path=None,
        task_final_status=None,
        requested_sandbox=requested,
        observed_sandbox=observed,
        environment_issue=environment_issue,
    )


def agent_last_state(loop_state: dict[str, Any], agent_name: str) -> dict[str, Any]:
    agents = loop_state.get("agents")
    if not isinstance(agents, dict):
        return {}
    agent_state = agents.get(agent_name)
    return agent_state if isinstance(agent_state, dict) else {}


def accepted_task_owners(agent: AgentSpec) -> set[str] | None:
    owners = agent.dispatch.get("accepted_owners")
    if owners is None:
        return None
    if isinstance(owners, str):
        return {owners}
    if isinstance(owners, list):
        return {str(owner) for owner in owners}
    return None


def agent_is_due(agent: AgentSpec, loop_state: dict[str, Any], *, force: bool = False) -> bool:
    if not force and agent_in_environment_backoff(agent, loop_state):
        return False
    mode = str(agent.dispatch.get("mode", "every_cycle"))
    if mode == "every_cycle":
        return True
    if mode == "interval":
        if force:
            return True
        interval_seconds = int(agent.dispatch.get("interval_seconds", 300))
        last = agent_last_state(loop_state, agent.name)
        finished_at = parse_iso8601_timestamp(last.get("finished_at"))
        if finished_at is None:
            return True
        delta = datetime.now(UTC) - finished_at
        return delta.total_seconds() >= interval_seconds
    if mode == "task_queue":
        queue = str(agent.dispatch.get("queue", "ready"))
        return bool(claimable_task_files(queue, accepted_task_owners(agent)))
    raise RuntimeError(f"Unsupported dispatch mode for {agent.name}: {mode}")


def dispatch_agent(
    agent: AgentSpec,
    config: dict[str, Any],
    loop_state: dict[str, Any],
    *,
    force: bool = False,
) -> list[RunResult]:
    if not agent_is_due(agent, loop_state, force=force):
        return []

    mode = str(agent.dispatch.get("mode", "every_cycle"))
    if mode in {"every_cycle", "interval"}:
        return [run_agent(agent, config)]
    if mode == "task_queue":
        queue = str(agent.dispatch.get("queue", "ready"))
        claim_to = str(agent.dispatch.get("claim_to", "in_progress"))
        max_runs = int(agent.dispatch.get("max_runs_per_cycle", 1))
        task_owners = accepted_task_owners(agent)
        claimable = claimable_task_files(queue, task_owners)
        if bool(agent.dispatch.get("require_write_probe", False)) and claimable:
            probe_result = run_write_probe(agent, config)
            if probe_result.environment_issue is not None or probe_result.exit_code != 0:
                return [probe_result]
        claimed = claim_tasks(queue, claim_to, max_runs, task_owners)
        return [run_agent(agent, config, task_path=task_path) for task_path in claimed]
    raise RuntimeError(f"Unsupported dispatch mode for {agent.name}: {mode}")


def recovery_policy(config: dict[str, Any]) -> dict[str, Any]:
    return config.get("task_recovery", {})


def recover_stale_in_progress_tasks(
    config: dict[str, Any], task_state: dict[str, Any]
) -> list[dict[str, Any]]:
    policy = recovery_policy(config)
    max_requeues = int(policy.get("max_requeues", 2))
    actions: list[dict[str, Any]] = []

    for path in list_task_files("in_progress"):
        entry = task_state_entry(task_state, path.name)
        requeue_count = int(entry.get("requeue_count", 0))
        if requeue_count < max_requeues:
            dest_status = "ready"
            entry["requeue_count"] = requeue_count + 1
            action_name = "requeued_stale_in_progress"
            severity = "warning"
        else:
            dest_status = "blocked"
            action_name = "blocked_stale_in_progress"
            severity = "error"

        note = (
            f"{utcnow()}: harness {action_name.replace('_', ' ')} because the task was still "
            "in `ops/tasks/in_progress/` at the start of a new bounded cycle."
        )
        new_path = move_task_with_note(path, dest_status, note)
        entry.update(
            {
                "last_action": action_name,
                "last_seen_at": utcnow(),
                "current_status": dest_status,
            }
        )
        actions.append(
            {
                "task_name": path.name,
                "action": action_name,
                "severity": severity,
                "final_status": dest_status,
                "path": relpath(new_path),
            }
        )
    return actions


def finalize_task_result(
    config: dict[str, Any],
    result: RunResult,
    task_state: dict[str, Any],
) -> list[dict[str, Any]]:
    if result.task_initial_path is None:
        return []

    task_name = result.task_initial_path.name
    entry = task_state_entry(task_state, task_name)
    entry["attempt_count"] = int(entry.get("attempt_count", 0)) + 1
    entry["last_run_id"] = result.run_id
    entry["last_exit_code"] = result.exit_code
    entry["last_seen_at"] = utcnow()

    final_status, final_path = locate_task_file(task_name)
    result.task_final_status = final_status
    result.task_final_path = final_path

    if final_status in {"done", "blocked"}:
        entry["current_status"] = final_status
        entry["last_action"] = "terminal"
        if final_status == "done":
            entry["requeue_count"] = 0
        return []

    if final_path is None:
        action = {
            "task_name": task_name,
            "action": "missing_task_file_after_run",
            "severity": "error",
            "final_status": final_status,
            "path": None,
        }
        result.recovery_actions.append(action)
        entry["last_action"] = action["action"]
        entry["current_status"] = "unknown"
        return [action]

    if result.environment_issue in {"sandbox_clamped_to_read_only", "codex_cache_not_writable"}:
        dest_status = "ready"
        action_name = "requeued_environment_sandbox_mismatch"
        severity = "error"
        new_path = move_task(final_path, dest_status)
        result.task_final_status = dest_status
        result.task_final_path = new_path
        entry["current_status"] = dest_status
        entry["last_action"] = action_name
        entry["last_environment_issue"] = result.environment_issue
        action = {
            "task_name": task_name,
            "action": action_name,
            "severity": severity,
            "final_status": dest_status,
            "path": relpath(new_path),
        }
        result.recovery_actions.append(action)
        return [action]

    policy = recovery_policy(config)
    max_requeues = int(policy.get("max_requeues", 2))
    block_on_clean_exit = bool(policy.get("block_on_clean_exit_without_terminal_state", True))
    requeue_count = int(entry.get("requeue_count", 0))

    if result.exit_code == 0 and block_on_clean_exit:
        dest_status = "blocked"
        action_name = "blocked_clean_exit_without_terminal_state"
        severity = "error"
    elif requeue_count < max_requeues:
        dest_status = "ready"
        action_name = "requeued_after_failed_or_incomplete_run"
        severity = "warning"
        entry["requeue_count"] = requeue_count + 1
    else:
        dest_status = "blocked"
        action_name = "blocked_after_requeue_budget_exhausted"
        severity = "error"

    note = (
        f"{utcnow()}: harness {action_name.replace('_', ' ')} after run `{result.run_id}` "
        f"(exit={result.exit_code}, timed_out={str(result.timed_out).lower()})."
    )
    new_path = move_task_with_note(final_path, dest_status, note)
    result.task_final_status = dest_status
    result.task_final_path = new_path
    entry["current_status"] = dest_status
    entry["last_action"] = action_name
    action = {
        "task_name": task_name,
        "action": action_name,
        "severity": severity,
        "final_status": dest_status,
        "path": relpath(new_path),
    }
    result.recovery_actions.append(action)
    return [action]


def prune_run_dirs(config: dict[str, Any], paths: dict[str, Path]) -> dict[str, Any]:
    keep = int(config.get("runtime", {}).get("keep_run_dirs", 200))
    run_dirs = sorted([path for path in paths["runs_root"].iterdir() if path.is_dir()])
    if keep < 0:
        keep = 0
    to_remove = run_dirs[:-keep] if keep and len(run_dirs) > keep else run_dirs if keep == 0 else []
    pruned: list[str] = []
    for path in to_remove:
        shutil.rmtree(path, ignore_errors=True)
        pruned.append(relpath(path))
    return {"keep_run_dirs": keep, "pruned_count": len(pruned), "pruned_paths": pruned}


def result_last_message_text(result: RunResult) -> str:
    return read_text_if_exists(result.run_dir / "last_message.md").strip()


def commit_summary_text(text: str) -> str | None:
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("```"):
            continue
        if line.startswith("- ") or line.startswith("* "):
            line = line[2:].strip()
        line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)
        line = line.replace("`", "").strip().rstrip(".")
        if line:
            return line
    return None


def truncate_commit_subject(text: str, limit: int = 72) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: max(0, limit - 3)].rstrip() + "..."


def compose_agent_commit_message(
    agent_name: str,
    agent_results: list[RunResult],
    recovery_actions: list[dict[str, Any]],
    changed_files: list[str],
) -> str:
    summaries = [
        summary
        for summary in (commit_summary_text(result_last_message_text(result)) for result in agent_results)
        if summary
    ]
    task_names = [
        result.task_initial_path.name
        for result in agent_results
        if result.task_initial_path is not None
    ]
    fallback = task_names[0] if task_names else "update tracked files"
    summary = summaries[0] if summaries else fallback
    subject = truncate_commit_subject(f"{agent_name}: {summary}")

    lines = [subject, "", f"Agent: {agent_name}", f"Committed at: {utcnow()}"]
    if task_names:
        lines.extend(["", "Tasks:"])
        for task_name in task_names:
            lines.append(f"- {task_name}")
    if changed_files:
        lines.extend(["", "Changed files:"])
        for path in changed_files:
            lines.append(f"- {path}")
    if recovery_actions:
        lines.extend(["", "Task actions:"])
        for action in recovery_actions:
            task_name = action.get("task_name", "unknown")
            action_name = action.get("action", "unknown")
            final_status = action.get("final_status", "unknown")
            lines.append(f"- {task_name}: {action_name} -> {final_status}")
    detail_blocks = [
        (result.run_id, result_last_message_text(result))
        for result in agent_results
        if result_last_message_text(result)
    ]
    if detail_blocks:
        lines.extend(["", "Details:"])
        for run_id, block in detail_blocks:
            lines.append(f"Run `{run_id}`:")
            lines.append("")
            lines.extend(block.splitlines())
            lines.append("")
    lines.append(TRAILER)
    return "\n".join(lines).rstrip() + "\n"


def last_cycle_stalled_on_inherited_dirty_worktree(loop_state: dict[str, Any]) -> bool:
    anomalies = loop_state.get("last_cycle_anomalies")
    if not isinstance(anomalies, list):
        return False
    for anomaly in anomalies:
        if not isinstance(anomaly, dict):
            continue
        message = str(anomaly.get("message", ""))
        if "worktree was already dirty" not in message:
            continue
        if "Skipped non-supervisor agent dispatch" in message:
            return True
        if "Skipped post-agent refresh and auto-commit" in message:
            return True
    return False


def maybe_checkpoint_inherited_dirty_worktree(
    config: dict[str, Any],
    supervisor_agent: AgentSpec | None,
    loop_state: dict[str, Any],
) -> dict[str, Any] | None:
    if supervisor_agent is None or not git_worktree_dirty():
        return None
    if not last_cycle_stalled_on_inherited_dirty_worktree(loop_state):
        return None

    paths = runtime_paths(config)
    ensure_runtime_dirs(paths)
    run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "-supervisor-inherited-dirty-checkpoint"
    run_dir = paths["runs_root"] / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    write_text(
        run_dir / "last_message.md",
        (
            "Checkpointed the inherited dirty worktree to unblock queue dispatch\n\n"
            "The previous cycle already stalled on an inherited dirty worktree, so this "
            "checkpoint commit preserves the existing dirty batch as-is before the next "
            "dispatch attempt. No tests were run; this was a harness recovery checkpoint.\n"
        ),
    )
    result = RunResult(
        agent_name=supervisor_agent.name,
        agent_kind=supervisor_agent.kind,
        run_id=run_id,
        exit_code=0,
        timed_out=False,
        run_dir=run_dir,
        task_initial_path=None,
        task_final_path=None,
        task_final_status=None,
    )
    return maybe_commit_agent_changes(config, supervisor_agent, [result], [])


def maybe_commit_agent_changes(
    config: dict[str, Any],
    agent: AgentSpec,
    agent_results: list[RunResult],
    recovery_actions: list[dict[str, Any]],
    *,
    pathspecs: list[str] | None = None,
) -> dict[str, Any] | None:
    if not agent_results or not git_worktree_dirty():
        return None

    command_timeout = int(config.get("git_policy", {}).get("command_timeout_seconds", 30))
    action: dict[str, Any] = {
        "agent_name": agent.name,
        "commit_attempted": False,
        "commit_created": False,
        "commit_sha": None,
        "subject": None,
        "changed_files": [],
        "errors": [],
        "pathspecs": pathspecs or [],
    }

    add_args = ["add", "-A"]
    if pathspecs:
        add_args.extend(["--", *pathspecs])
    try:
        git_run(*add_args, capture_output=True, timeout_seconds=command_timeout)
    except subprocess.TimeoutExpired:
        scope = "selected paths" if pathspecs else "worktree"
        action["errors"].append(
            f"git add timed out after {command_timeout}s while staging {scope}."
        )
        return action

    diff_args = ["diff", "--cached", "--name-only", "--"]
    if pathspecs:
        diff_args.extend(pathspecs)
    changed_files = [line for line in git_stdout(*diff_args).splitlines() if line]
    if not changed_files:
        return None

    message = compose_agent_commit_message(agent.name, agent_results, recovery_actions, changed_files)
    action["subject"] = message.splitlines()[0]
    action["changed_files"] = changed_files
    action["commit_attempted"] = True
    commit_args = ["commit"]
    if pathspecs:
        commit_args.extend(["--only"])
    commit_args.extend(["-F", "-"])
    if pathspecs:
        commit_args.extend(["--", *pathspecs])
    try:
        commit = git_run(*commit_args, input_text=message, timeout_seconds=command_timeout)
    except subprocess.TimeoutExpired:
        action["errors"].append(f"git commit timed out after {command_timeout}s.")
        return action

    if commit.returncode == 0:
        action["commit_created"] = True
        action["commit_sha"] = git_head()
    else:
        action["errors"].append((commit.stderr or commit.stdout or "git commit failed").strip())
    return action


def maybe_commit_and_push(config: dict[str, Any]) -> dict[str, Any]:
    policy = config.get("git_policy", {})
    remote = str(policy.get("push_remote", "origin"))
    branch = str(policy.get("push_branch") or git_branch() or "main")
    upstream = git_upstream_ref(config)
    command_timeout = int(policy.get("command_timeout_seconds", 30))
    push_timeout = int(policy.get("push_timeout_seconds", 120))
    dirty_before = git_worktree_dirty()
    action: dict[str, Any] = {
        "dirty_before": dirty_before,
        "dirty_before_summary": git_dirty_summary() if dirty_before else {},
        "fetch_attempted": False,
        "fetch_succeeded": False,
        "merge_attempted": False,
        "merge_succeeded": False,
        "push_attempted": False,
        "push_succeeded": False,
        "ahead_before_push": None,
        "behind_before_push": None,
        "ahead_after_merge": None,
        "behind_after_merge": None,
        "command_timeout_seconds": command_timeout,
        "push_timeout_seconds": push_timeout,
        "errors": [],
    }

    if bool(policy.get("auto_push", True)):
        action["fetch_attempted"] = True
        try:
            fetch = git_run("fetch", remote, branch, timeout_seconds=command_timeout)
        except subprocess.TimeoutExpired:
            action["errors"].append(
                f"git fetch {remote} {branch} timed out after {command_timeout}s."
            )
            fetch = None
        else:
            if fetch.returncode == 0:
                action["fetch_succeeded"] = True
            else:
                action["errors"].append(
                    (fetch.stderr or fetch.stdout or f"git fetch {remote} {branch} failed").strip()
                )

        ahead = behind = None
        if action["fetch_succeeded"]:
            ahead, behind = git_ahead_behind_counts(config)
        action["ahead_before_push"] = ahead
        action["behind_before_push"] = behind
        if action["fetch_attempted"] and not action["fetch_succeeded"]:
            pass
        elif ahead is None or behind is None:
            action["errors"].append(
                f"Unable to determine ahead/behind state for {remote}/{branch}."
            )
        else:
            if behind > 0:
                action["merge_attempted"] = True
                try:
                    merge = git_run(
                        "merge",
                        "--no-edit",
                        upstream,
                        timeout_seconds=command_timeout,
                    )
                except subprocess.TimeoutExpired:
                    action["errors"].append(
                        f"git merge {upstream} timed out after {command_timeout}s."
                    )
                else:
                    if merge.returncode == 0:
                        action["merge_succeeded"] = True
                        ahead, behind = git_ahead_behind_counts(config)
                        action["ahead_after_merge"] = ahead
                        action["behind_after_merge"] = behind
                    else:
                        action["errors"].append(
                            (merge.stderr or merge.stdout or f"git merge {upstream} failed").strip()
                        )
            if action["merge_attempted"] and not action["merge_succeeded"]:
                pass
            elif ahead is None or behind is None:
                action["errors"].append(
                    f"Unable to determine ahead/behind state for {remote}/{branch} after merge."
                )
            elif behind > 0:
                action["errors"].append(
                    f"Local branch is still behind {remote}/{branch} by {behind} commit(s) after merge; skipped push."
                )
            elif ahead > 0:
                action["push_attempted"] = True
                try:
                    push = git_run("push", remote, branch, timeout_seconds=push_timeout)
                except subprocess.TimeoutExpired:
                    action["errors"].append(f"git push timed out after {push_timeout}s.")
                else:
                    if push.returncode == 0:
                        action["push_succeeded"] = True
                    else:
                        action["errors"].append(
                            (push.stderr or push.stdout or "git push failed").strip()
                        )

    dirty_after = git_worktree_dirty()
    action["dirty_after"] = dirty_after
    action["dirty_after_summary"] = git_dirty_summary() if dirty_after else {}
    action["head_after"] = git_head()
    return action


def build_anomalies(
    results: list[RunResult],
    recovery_actions: list[dict[str, Any]],
    commit_actions: list[dict[str, Any]],
    git_action: dict[str, Any],
) -> list[dict[str, Any]]:
    anomalies: list[dict[str, Any]] = []
    for result in results:
        if result.exit_code != 0:
            anomalies.append(
                {
                    "type": "agent_nonzero_exit",
                    "severity": "error",
                    "agent_name": result.agent_name,
                    "run_id": result.run_id,
                    "exit_code": result.exit_code,
                    "timed_out": result.timed_out,
                }
            )
        if result.environment_issue is not None:
            anomalies.append(
                {
                    "type": "agent_environment_issue",
                    "severity": "error",
                    "agent_name": result.agent_name,
                    "run_id": result.run_id,
                    "environment_issue": result.environment_issue,
                }
            )
    anomalies.extend(
        {
            "type": "task_recovery",
            "severity": action["severity"],
            "task_name": action["task_name"],
            "action": action["action"],
            "final_status": action["final_status"],
            "path": action["path"],
        }
        for action in recovery_actions
    )
    for action in commit_actions:
        for message in action.get("errors", []):
            anomalies.append(
                {
                    "type": "agent_commit_error",
                    "severity": "error",
                    "agent_name": action.get("agent_name"),
                    "message": message,
                }
            )
    for message in git_action.get("errors", []):
        anomalies.append({"type": "git_sync_error", "severity": "error", "message": message})
    return anomalies


def update_loop_state(
    config: dict[str, Any],
    agents: list[AgentSpec],
    results: list[RunResult],
    recovery_actions: list[dict[str, Any]],
    commit_actions: list[dict[str, Any]],
    git_action: dict[str, Any],
    prune_action: dict[str, Any],
) -> dict[str, Any]:
    paths = runtime_paths(config)
    state = read_json(paths["loop_state"], default={})
    if not isinstance(state, dict):
        state = {}

    totals = state.get("totals")
    if not isinstance(totals, dict):
        totals = {}

    anomalies = build_anomalies(results, recovery_actions, commit_actions, git_action)
    error_count = sum(1 for item in anomalies if item.get("severity") == "error")
    warning_count = sum(1 for item in anomalies if item.get("severity") == "warning")
    cycle_completed = sum(1 for result in results if result.task_final_status == "done")
    cycle_blocked = sum(1 for result in results if result.task_final_status == "blocked")
    current_json_blob_count = tracked_json_blob_count()
    previous_json_blob_count = state.get("tracked_json_blob_count")
    if not isinstance(previous_json_blob_count, int):
        previous_json_blob_count = current_json_blob_count

    agent_state = state.get("agents")
    if not isinstance(agent_state, dict):
        agent_state = {}
    live_agent_names = {agent.name for agent in agents}
    agent_state = {
        name: payload
        for name, payload in agent_state.items()
        if name in live_agent_names and isinstance(payload, dict)
    }
    for result in results:
        agent_state[result.agent_name] = {
            "agent_kind": result.agent_kind,
            "run_id": result.run_id,
            "exit_code": result.exit_code,
            "timed_out": result.timed_out,
            "finished_at": utcnow(),
            "task_final_status": result.task_final_status,
            "environment_issue": result.environment_issue,
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
            "tracked_json_blob_count": current_json_blob_count,
            "previous_tracked_json_blob_count": previous_json_blob_count,
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
                    "environment_issue": result.environment_issue,
                }
                for result in results
            ],
            "last_agent_commits": commit_actions,
            "last_cycle_recovery_actions": recovery_actions,
            "last_cycle_anomalies": anomalies,
            "last_git_action": git_action,
            "last_prune_action": prune_action,
            "totals": {
                "cycles": int(totals.get("cycles", 0)) + 1,
                "agent_runs": int(totals.get("agent_runs", 0)) + len(results),
                "task_runs": int(totals.get("task_runs", 0))
                + sum(1 for result in results if result.task_initial_path is not None),
                "tasks_completed": int(totals.get("tasks_completed", 0)) + cycle_completed,
                "tasks_blocked": int(totals.get("tasks_blocked", 0)) + cycle_blocked,
                "auto_commits": int(totals.get("auto_commits", 0))
                + sum(1 for action in commit_actions if action.get("commit_created")),
                "auto_pushes": int(totals.get("auto_pushes", 0))
                + int(bool(git_action.get("push_succeeded"))),
                "pruned_run_dirs": int(totals.get("pruned_run_dirs", 0))
                + int(prune_action.get("pruned_count", 0)),
                "warnings": int(totals.get("warnings", 0)) + warning_count,
                "errors": int(totals.get("errors", 0)) + error_count,
            },
        }
    )
    write_json(paths["loop_state"], state)
    return state


def build_report(config: dict[str, Any]) -> dict[str, Any]:
    paths = runtime_paths(config)
    state = read_json(paths["loop_state"], default={})
    if not isinstance(state, dict):
        state = {}
    live_agents = load_agent_specs(config)
    reporting_cfg = config.get("reporting", {})
    recent_runs_limit = int(reporting_cfg.get("recent_runs", 12))
    recent_tasks_limit = int(reporting_cfg.get("recent_tasks", 10))
    recent_commits_limit = int(reporting_cfg.get("recent_commits", 10))
    recovery_actions = state.get("last_cycle_recovery_actions", [])
    if not isinstance(recovery_actions, list):
        recovery_actions = []
    git_action = state.get("last_git_action", {})
    if not isinstance(git_action, dict):
        git_action = {}
    commit_actions = state.get("last_agent_commits", [])
    if not isinstance(commit_actions, list):
        commit_actions = []
    raw_last_cycle_runs = state.get("last_cycle_runs", [])
    if not isinstance(raw_last_cycle_runs, list):
        raw_last_cycle_runs = []
    last_cycle_runs = [
        normalize_report_run(paths, item)
        for item in raw_last_cycle_runs[:recent_runs_limit]
        if isinstance(item, dict)
    ]
    ahead_of_upstream, behind_of_upstream = git_ahead_behind_counts(config)
    current_json_blob_count = tracked_json_blob_count()
    previous_json_blob_count = state.get("previous_tracked_json_blob_count")
    if not isinstance(previous_json_blob_count, int):
        previous_json_blob_count = current_json_blob_count

    report = {
        "generated_at": utcnow(),
        "repo_root": str(REPO_ROOT),
        "branch": git_branch(),
        "head": git_head(),
        "upstream": git_upstream_ref(config),
        "ahead_of_upstream": ahead_of_upstream,
        "behind_of_upstream": behind_of_upstream,
        "diverged_from_upstream": bool(
            (ahead_of_upstream or 0) > 0 and (behind_of_upstream or 0) > 0
        ),
        "dirty_worktree": git_worktree_dirty(),
        "dirty_worktree_summary": git_dirty_summary(),
        "queue_counts": queue_counts(),
        "tracked_json_blob_count": current_json_blob_count,
        "tracked_json_blob_previous": previous_json_blob_count,
        "tracked_json_blob_delta": current_json_blob_count - previous_json_blob_count,
        "user_ask_counts": user_ask_counts(),
        "totals": state.get("totals", {}),
        "agents": [
            {
                "name": agent.name,
                "kind": agent.kind,
                "cycle_order": agent.cycle_order,
                "dispatch_mode": agent.dispatch.get("mode", "every_cycle"),
                "spec_path": relpath(agent.spec_path),
            }
            for agent in live_agents
        ],
        "last_cycle_runs": last_cycle_runs,
        "last_cycle_anomalies": build_report_anomalies(
            last_cycle_runs,
            recovery_actions,
            commit_actions,
            git_action,
            ahead_of_upstream=ahead_of_upstream,
            behind_of_upstream=behind_of_upstream,
        ),
        "last_cycle_recovery_actions": recovery_actions,
        "last_agent_commits": commit_actions,
        "last_git_action": git_action,
        "last_prune_action": state.get("last_prune_action", {}),
        "recent_done_tasks": recent_tasks("done", recent_tasks_limit),
        "recent_blocked_tasks": recent_tasks("blocked", recent_tasks_limit),
        "recent_commits": recent_git_commits(recent_commits_limit),
        "dashboard_paths": {
            "json": relpath(paths["dashboard_json"]),
            "markdown": relpath(paths["dashboard_markdown"]),
        },
    }
    return report


def render_markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Rebar Dashboard",
        "",
        f"Generated: {report['generated_at']}",
        f"Branch: `{report['branch']}`",
        f"HEAD: `{report['head']}`",
        f"Upstream: `{report['upstream']}`",
        f"Dirty worktree: `{str(report['dirty_worktree']).lower()}`",
        f"Ahead of upstream: `{report['ahead_of_upstream']}`",
        f"Behind upstream: `{report['behind_of_upstream']}`",
        f"Diverged from upstream: `{str(report['diverged_from_upstream']).lower()}`",
        "",
        "## Totals",
    ]

    totals = report.get("totals", {})
    if isinstance(totals, dict):
        for key in sorted(totals):
            lines.append(f"- {key}: `{totals[key]}`")

    lines.extend(["", "## Queue Counts"])
    for key, value in report.get("queue_counts", {}).items():
        lines.append(f"- {key}: `{value}`")
    lines.append(f"- tracked_json_blob_count: `{report.get('tracked_json_blob_count')}`")
    lines.append(f"- tracked_json_blob_delta: `{report.get('tracked_json_blob_delta')}`")

    dirty_summary = report.get("dirty_worktree_summary", {})
    if isinstance(dirty_summary, dict) and dirty_summary.get("count"):
        lines.extend(["", "## Dirty Worktree"])
        lines.append(f"- entries: `{dirty_summary.get('count')}`")
        lines.append(
            f"- sample_truncated: `{str(dirty_summary.get('truncated')).lower()}`"
        )
        for item in dirty_summary.get("sample", []):
            lines.append(f"- `{item}`")

    lines.extend(["", "## Active Agents"])
    agents = report.get("agents", [])
    if agents:
        for item in agents:
            lines.append(
                f"- `{item['name']}` kind=`{item['kind']}` mode=`{item['dispatch_mode']}` order=`{item['cycle_order']}`"
            )
    else:
        lines.append("- none")

    lines.extend(["", "## Last Cycle Runs"])
    runs = report.get("last_cycle_runs", [])
    if runs:
        for item in runs:
            line = (
                f"- `{item['agent_name']}` exit=`{item['exit_code']}` "
                f"timed_out=`{item['timed_out']}` task=`{item['task_initial_path']}` "
                f"final=`{item['task_final_status']}`"
            )
            if item.get("environment_issue"):
                line += f" issue=`{item['environment_issue']}`"
            lines.append(line)
    else:
        lines.append("- none")

    lines.extend(["", "## Last Git Action"])
    last_git = report.get("last_git_action", {})
    if isinstance(last_git, dict):
        for key in (
            "merge_attempted",
            "merge_succeeded",
            "ahead_before_push",
            "behind_before_push",
            "ahead_after_merge",
            "behind_after_merge",
            "push_attempted",
            "push_succeeded",
            "dirty_after",
        ):
            if key in last_git:
                lines.append(f"- {key}: `{last_git[key]}`")
        for message in last_git.get("errors", []):
            lines.append(f"- git_error: `{message}`")

    lines.extend(["", "## Last Agent Commits"])
    commit_actions = report.get("last_agent_commits", [])
    if commit_actions:
        for action in commit_actions:
            lines.append(
                f"- `{action.get('agent_name')}` sha=`{action.get('commit_sha')}` subject=`{action.get('subject')}`"
            )
            for message in action.get("errors", []):
                lines.append(f"- commit_error: `{message}`")
    else:
        lines.append("- none")

    lines.extend(["", "## Last Cycle Anomalies"])
    anomalies = report.get("last_cycle_anomalies", [])
    if anomalies:
        for item in anomalies:
            lines.append(f"- {json.dumps(item, sort_keys=True)}")
    else:
        lines.append("- none")

    lines.extend(["", "## Recent Done Tasks"])
    done_tasks = report.get("recent_done_tasks", [])
    if done_tasks:
        for item in done_tasks:
            lines.append(f"- `{item['name']}` at `{item['updated_at']}`")
    else:
        lines.append("- none")

    lines.extend(["", "## Recent Blocked Tasks"])
    blocked_tasks = report.get("recent_blocked_tasks", [])
    if blocked_tasks:
        for item in blocked_tasks:
            lines.append(f"- `{item['name']}` at `{item['updated_at']}`")
    else:
        lines.append("- none")

    lines.extend(["", "## Recent Commits"])
    commits = report.get("recent_commits", [])
    if commits:
        for item in commits:
            lines.append(f"- `{item['sha']}` `{item['date']}` {item['subject']}")
    else:
        lines.append("- none")

    return "\n".join(lines) + "\n"


def refresh_reports(config: dict[str, Any]) -> dict[str, Any]:
    paths = runtime_paths(config)
    report = build_report(config)
    write_json(paths["dashboard_json"], report)
    write_text(paths["dashboard_markdown"], render_markdown_report(report))
    return report


def load_correctness_harness_module() -> Any:
    ensure_python_source_on_syspath()
    from rebar_harness import correctness as correctness_harness

    return correctness_harness


def expected_correctness_manifest_ids(correctness_harness: Any) -> list[str]:
    fixture_paths = tuple(Path(path) for path in correctness_harness.DEFAULT_FIXTURE_PATHS)
    load_fixture_manifests = getattr(correctness_harness, "load_fixture_manifests", None)
    if callable(load_fixture_manifests):
        manifests, _ = load_fixture_manifests(fixture_paths)
        return [
            manifest_id
            for manifest_id in (
                str(getattr(manifest, "manifest_id", "") or "").strip()
                for manifest in manifests
            )
            if manifest_id
        ]

    manifest_ids: list[str] = []
    for fixture_path in fixture_paths:
        raw_manifest = read_json(fixture_path, default={})
        if not isinstance(raw_manifest, dict):
            continue
        manifest_id = str(raw_manifest.get("manifest_id") or "").strip()
        if manifest_id:
            manifest_ids.append(manifest_id)
    return manifest_ids


def published_correctness_report_needs_refresh(correctness_harness: Any) -> bool:
    payload = read_json(Path(correctness_harness.DEFAULT_REPORT_PATH), default={})
    if not isinstance(payload, dict):
        return True

    fixtures = payload.get("fixtures")
    if not isinstance(fixtures, dict):
        return True

    expected_manifest_ids = expected_correctness_manifest_ids(correctness_harness)
    manifest_count = fixtures.get("manifest_count")
    manifest_ids = fixtures.get("manifest_ids")

    if manifest_count != len(expected_manifest_ids):
        return True
    if manifest_ids != expected_manifest_ids:
        return True
    return False


def refresh_published_correctness_scorecard() -> dict[str, Any] | None:
    correctness_harness = load_correctness_harness_module()
    if not published_correctness_report_needs_refresh(correctness_harness):
        return None
    return correctness_harness.run_correctness_harness()


def run_cycle(
    config: dict[str, Any], *, force_supervisor: bool = False, force_agents: set[str] | None = None
) -> int:
    cycle_inherited_dirty = git_worktree_dirty()
    paths = runtime_paths(config)
    ensure_runtime_dirs(paths)
    task_state = load_task_state(paths)
    user_ask_actions = reroute_misplaced_user_asks()
    stale_actions = recover_stale_in_progress_tasks(config, task_state)

    agents = load_agent_specs(config)
    loop_state = read_json(paths["loop_state"], default={})
    if not isinstance(loop_state, dict):
        loop_state = {}

    recovery_actions = list(user_ask_actions)
    recovery_actions.extend(stale_actions)
    results: list[RunResult] = []
    commit_actions: list[dict[str, Any]] = []
    supervisor_agent = next((agent for agent in agents if agent.kind == "supervisor"), None)
    if cycle_inherited_dirty:
        checkpoint_action = maybe_checkpoint_inherited_dirty_worktree(
            config,
            supervisor_agent,
            loop_state,
        )
        if checkpoint_action is not None:
            commit_actions.append(checkpoint_action)
            cycle_inherited_dirty = git_worktree_dirty()
    skipped_dirty_dispatch_agents: list[str] = []
    skipped_dirty_autocommit_agents: list[str] = []
    forced = force_agents or set()
    for agent in agents:
        force = agent.name in forced or (force_supervisor and agent.kind == "supervisor")
        worktree_dirty_before_agent = git_worktree_dirty()
        inherited_dirty_before_agent = cycle_inherited_dirty and worktree_dirty_before_agent
        if (
            inherited_dirty_before_agent
            and not force
            and not agent_may_dispatch_on_dirty_worktree(agent)
        ):
            skipped_dirty_dispatch_agents.append(agent.name)
            continue
        dirty_paths_before_agent: set[str] = set()
        preexisting_dirty_snapshot: dict[str, tuple[str, int | None, str | None]] = {}
        if worktree_dirty_before_agent:
            dirty_paths_before_agent = git_dirty_paths(untracked_all=True)
            preexisting_dirty_snapshot = snapshot_worktree_paths(dirty_paths_before_agent)
        agent_results = dispatch_agent(agent, config, loop_state, force=force)
        if not agent_results:
            continue
        results.extend(agent_results)
        agent_recovery_actions: list[dict[str, Any]] = []
        for result in agent_results:
            agent_recovery_actions.extend(finalize_task_result(config, result, task_state))
        recovery_actions.extend(agent_recovery_actions)
        write_json(paths["task_state"], task_state)
        if worktree_dirty_before_agent:
            # Only auto-commit when the inherited dirty baseline stayed untouched.
            if not git_worktree_dirty():
                continue
            changed_preexisting_paths = changed_snapshot_paths(preexisting_dirty_snapshot)
            if changed_preexisting_paths:
                skipped_dirty_autocommit_agents.append(
                    f"{agent.name} (touched pre-existing dirty paths: "
                    + ", ".join(changed_preexisting_paths[:3])
                    + (", ..." if len(changed_preexisting_paths) > 3 else "")
                    + ")"
                )
                continue
            dirty_paths_after_agent = git_dirty_paths(untracked_all=True)
            safe_dirty_paths = sorted(dirty_paths_after_agent - dirty_paths_before_agent)
            if not safe_dirty_paths:
                continue
            commit_action = maybe_commit_agent_changes(
                config,
                agent,
                agent_results,
                agent_recovery_actions,
                pathspecs=safe_dirty_paths,
            )
            if commit_action is not None:
                commit_actions.append(commit_action)
            continue
        if git_worktree_dirty():
            refresh_published_correctness_scorecard()
            sync_readme_status(config)
            commit_action = maybe_commit_agent_changes(
                config,
                agent,
                agent_results,
                agent_recovery_actions,
            )
            if commit_action is not None:
                commit_actions.append(commit_action)

    write_json(paths["task_state"], task_state)
    prune_action = prune_run_dirs(config, paths)
    git_action = maybe_commit_and_push(config)
    if skipped_dirty_dispatch_agents:
        git_action.setdefault("errors", []).append(
            "Skipped non-supervisor agent dispatch because the worktree was already dirty "
            "before this cycle started and remained dirty before these agents would have run: "
            + ", ".join(skipped_dirty_dispatch_agents)
            + "."
        )
    if skipped_dirty_autocommit_agents:
        git_action.setdefault("errors", []).append(
            "Skipped post-agent refresh and auto-commit because the worktree was already dirty "
            "before these agents ran: "
            + ", ".join(skipped_dirty_autocommit_agents)
            + "."
        )
    state = update_loop_state(
        config,
        agents,
        results,
        recovery_actions,
        commit_actions,
        git_action,
        prune_action,
    )
    refresh_reports(config)

    anomalies = state.get("last_cycle_anomalies", [])
    error_count = sum(1 for item in anomalies if item.get("severity") == "error")
    return 0 if error_count == 0 else 1


def sleep_seconds_for_exit(config: dict[str, Any], exit_code: int) -> int:
    runtime_cfg = config.get("runtime", {})
    if exit_code == 0:
        paths = runtime_paths(config)
        loop_state = read_json(paths["loop_state"], default={})
        if isinstance(loop_state, dict):
            queue = loop_state.get("queue_counts")
            last_runs = loop_state.get("last_cycle_runs")
            if isinstance(queue, dict) and isinstance(last_runs, list):
                ready = int(queue.get("ready", 0))
                in_progress = int(queue.get("in_progress", 0))
                needs_refill = any(
                    isinstance(item, dict)
                    and item.get("agent_kind") == "task_worker"
                    and item.get("task_final_status") == "done"
                    for item in last_runs
                )
                if needs_refill and ready == 0 and in_progress == 0:
                    return int(runtime_cfg.get("queue_refill_sleep_seconds", 5))
        return int(runtime_cfg.get("sleep_seconds", 300))
    return int(runtime_cfg.get("failure_backoff_seconds", 30))


def cmd_status(config: dict[str, Any]) -> int:
    report = build_report(config)
    summary = {
        "repo_root": report["repo_root"],
        "runtime_dir": str(runtime_paths(config)["artifact_root"]),
        "queue_counts": report["queue_counts"],
        "tracked_json_blob_count": report["tracked_json_blob_count"],
        "tracked_json_blob_delta": report["tracked_json_blob_delta"],
        "user_ask_counts": report["user_ask_counts"],
        "agents": report["agents"],
        "ahead_of_upstream": report["ahead_of_upstream"],
        "behind_of_upstream": report["behind_of_upstream"],
        "diverged_from_upstream": report["diverged_from_upstream"],
        "dirty_worktree": report["dirty_worktree"],
        "last_cycle_anomalies": report["last_cycle_anomalies"],
        "dashboard_path": report["dashboard_paths"]["markdown"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def cmd_render(config: dict[str, Any], agent_name: str, task: str | None) -> int:
    agents = {agent.name: agent for agent in load_agent_specs(config)}
    agent = agents.get(agent_name)
    if agent is None:
        raise RuntimeError(f"Unknown agent: {agent_name}")
    task_path = None if task is None else resolve_repo_path(task)
    sys.stdout.write(render_prompt(agent, config, task_path=task_path))
    return 0


def cmd_cycle(
    config: dict[str, Any], force_supervisor: bool, force_agents: list[str] | None
) -> int:
    force_agent_names = {name for name in (force_agents or []) if name}
    paths = runtime_paths(config)
    ensure_runtime_dirs(paths)
    acquired, holder_pid = acquire_cycle_lock(paths)
    if not acquired:
        holder = holder_pid or "unknown"
        print(
            "Another `scripts/rebar_ops.py cycle` invocation is already running "
            f"(holder pid: {holder}). Stop the live loop or wait for it to finish before "
            "forcing another cycle in this checkout.",
            file=sys.stderr,
        )
        return 73
    atexit.register(release_cycle_lock, paths)
    try:
        return run_cycle(
            config,
            force_supervisor=force_supervisor,
            force_agents=force_agent_names,
        )
    finally:
        release_cycle_lock(paths)


def cmd_sleep_seconds(config: dict[str, Any], exit_code: int) -> int:
    print(sleep_seconds_for_exit(config, exit_code))
    return 0


def cmd_report(config: dict[str, Any], output_format: str) -> int:
    refresh_published_correctness_scorecard()
    sync_readme_status(config)
    report = build_report(config)
    paths = runtime_paths(config)
    rendered = render_markdown_report(report)
    write_json(paths["dashboard_json"], report)
    write_text(paths["dashboard_markdown"], rendered)
    if output_format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        sys.stdout.write(rendered)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the rebar forever harness.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status", help="Print queue, git, and runtime status.")

    render_parser = subparsers.add_parser("render", help="Render a prompt for an agent.")
    render_parser.add_argument("agent", help="Agent name from ops/agents/*.json")
    render_parser.add_argument("--task", help="Optional task path for task-worker prompts.")

    cycle_parser = subparsers.add_parser("cycle", help="Run one full agent cycle.")
    cycle_parser.add_argument(
        "--force-supervisor",
        action="store_true",
        help="Force the supervisor to run even if its future dispatch policy becomes interval-based.",
    )
    cycle_parser.add_argument(
        "--force-agent",
        action="append",
        default=[],
        metavar="AGENT",
        help="Force the named agent to run even if environment backoff would skip it.",
    )

    sleep_parser = subparsers.add_parser(
        "sleep-seconds",
        help="Print the configured post-cycle sleep based on the previous exit code.",
    )
    sleep_parser.add_argument("--exit-code", type=int, required=True)

    report_parser = subparsers.add_parser("report", help="Render the current dashboard.")
    report_parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
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
        return cmd_cycle(config, args.force_supervisor, args.force_agent)
    if args.command == "sleep-seconds":
        return cmd_sleep_seconds(config, args.exit_code)
    if args.command == "report":
        return cmd_report(config, args.format)
    raise RuntimeError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
