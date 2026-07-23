#!/usr/bin/env python3
"""Losslessly report the unchanged frozen extended-path compatibility checks."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib
import importlib.util
import json
import os
import random
import subprocess
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path
from unittest import mock

from tools import rust_v6_paths_probe as frozen


ROOT = Path(__file__).resolve().parents[1]
FROZEN_PATH = ROOT / "tools/rust_v6_paths_probe.py"
FROZEN_SHA256 = "40e773053c348420a34f9ab3594035d11faeabc7b48c74df96594e3dca690dd3"
PINNED_PYTHON = (3, 14, 6)
FROZEN_SEED = 2026072307
SEEDED_CASES = 512
FROZEN_CHECKS = 72248
SCHEMA = "rebar-v8-lossless-frozen-extended-path-diagnostic-v1"
SELF_SCHEMA = "rebar-v8-lossless-frozen-extended-path-self-test-v1"
BOUNDED_SELF_SCHEMA = "rebar-v8-bounded-frozen-manual-path-self-test-v1"
BOUNDED_MANUAL_SCHEMA = "rebar-v8-bounded-frozen-manual-path-diagnostic-v1"
MAX_MANUAL_CASES = 16
MANUAL_CASE_TIMEOUT_SECONDS = 3
MANUAL_GLOBAL_TIMEOUT_SECONDS = 60
FULL_WORKER_TIMEOUT_SECONDS = 60


class FrozenWorkerTimeout(RuntimeError):
    """An actual isolated correctness worker exceeded its explicit limit."""

    def __init__(self, module: str, seconds: float, stdout, stderr):
        self.module = module
        self.seconds = seconds
        self.stdout = stream_text(stdout)
        self.stderr = stream_text(stderr)
        super().__init__(
            f"isolated frozen diagnostic exceeded its {seconds:g}-second limit: "
            f"{module}"
        )


def stream_text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", "backslashreplace")
    return str(value)


def progress(event: str, **fields) -> None:
    print(json.dumps({"event": event, **fields}, sort_keys=True), flush=True)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_frozen_source() -> None:
    if tuple(sys.version_info[:3]) != PINNED_PYTHON:
        raise RuntimeError("the diagnostic requires frozen CPython 3.14.6")
    if frozen.SEED != FROZEN_SEED:
        raise RuntimeError("the frozen extended-path seed changed")
    if digest(FROZEN_PATH) != FROZEN_SHA256:
        raise RuntimeError("the frozen extended-path source changed")


def write_report(path: Path, report: dict) -> None:
    payload = (
        json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        if path.suffix == ".gz":
            with gzip.GzipFile(
                filename="", mode="wb", fileobj=stream, compresslevel=6, mtime=0
            ) as compressed:
                compressed.write(payload)
        else:
            stream.write(payload)


def read_report(path: Path) -> dict:
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as stream:
            return json.load(stream)
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def pattern_types(module) -> tuple[type, ...]:
    result = [frozen.re.Pattern]
    candidate_type = getattr(module, "Pattern", None)
    if isinstance(candidate_type, type) and candidate_type not in result:
        result.append(candidate_type)
    return tuple(result)


def canonicalize(value, compiled_types: tuple[type, ...]):
    if isinstance(value, compiled_types):
        return {
            "__diagnostic_type__": "compiled-regex-pattern-v1",
            "pattern": canonicalize(frozen.normalized(value.pattern), compiled_types),
            "flags": int(value.flags),
            "groups": int(value.groups),
            "groupindex": canonicalize(dict(value.groupindex), compiled_types),
        }
    if isinstance(value, dict):
        return {
            str(key): canonicalize(item, compiled_types)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [canonicalize(item, compiled_types) for item in value]
    if isinstance(value, tuple):
        return {
            "tuple": [canonicalize(item, compiled_types) for item in value]
        }
    if isinstance(value, (bytes, bytearray, memoryview)):
        return canonicalize(frozen.normalized(value), compiled_types)
    return value


def poison_controls(module, compiled_types: tuple[type, ...]) -> dict:
    original = frozen.observed
    left = canonicalize(original(lambda: frozen.re.compile("(?P<word>a)")), compiled_types)
    equal = canonicalize(original(lambda: frozen.re.compile("(?P<word>a)")), compiled_types)
    changed_pattern = canonicalize(
        original(lambda: frozen.re.compile("(?P<word>b)")), compiled_types
    )
    changed_flags = canonicalize(
        original(lambda: frozen.re.compile("(?P<word>a)", frozen.re.I)),
        compiled_types,
    )
    compiler_failure = canonicalize(original(lambda: frozen.re.compile("(")), compiled_types)
    candidate = canonicalize(original(lambda: module.compile("(?P<word>a)")), compiled_types)
    controls = {
        "identical_compiled_patterns": frozen.equivalent(left, equal),
        "different_compiled_patterns_rejected": not frozen.equivalent(
            left, changed_pattern
        ),
        "different_compiled_flags_rejected": not frozen.equivalent(
            left, changed_flags
        ),
        "compiler_failure_cannot_be_concealed": not frozen.equivalent(
            left, compiler_failure
        ),
        "compiler_failure_retains_pattern_error": (
            compiler_failure.get("error") == "PatternError"
            and "pattern_error" in compiler_failure
        ),
        "uniform_candidate_pattern_metadata": frozen.equivalent(left, candidate),
        "original_frozen_equivalence_used": frozen.equivalent.__module__
        == "tools.rust_v6_paths_probe",
    }
    if not all(controls.values()):
        raise RuntimeError(f"diagnostic poison control failed: {controls!r}")
    return controls


def production_artifacts(module_name: str, module) -> list[dict]:
    paths = []
    origin = getattr(module, "__file__", None)
    if module_name != "re" and origin:
        paths.append(Path(origin).resolve())
    if module_name == "candidates.vm_candidate":
        paths.append(ROOT / "candidates/_vm_native.c")
        spec = importlib.util.find_spec("candidates._vm_native")
        if spec is None or spec.origin is None:
            raise RuntimeError("the owned C native module is missing")
        paths.append(Path(spec.origin).resolve())
    elif module_name == "candidates.zig_candidate":
        paths.extend(
            (
                ROOT / "candidates/zig/py_bridge.c",
                ROOT / "candidates/zig/mini_regex.zig",
            )
        )
        spec = importlib.util.find_spec("candidates._zig_bridge")
        if spec is None or spec.origin is None:
            raise RuntimeError("the owned Zig bridge is missing")
        paths.append(Path(spec.origin).resolve())
        paths.append(ROOT / "candidates/_zig_probe.so")
    records = []
    seen = set()
    for path in paths:
        path = path.resolve()
        if path in seen:
            continue
        seen.add(path)
        if not path.is_file():
            raise RuntimeError(f"candidate artifact is missing: {path}")
        try:
            relative = path.relative_to(ROOT).as_posix()
        except ValueError:
            relative = str(path)
        records.append({"path": relative, "sha256": digest(path)})
    return records


def phase(label: str) -> str:
    if label.startswith("manual-"):
        return "manual"
    if label.startswith("seeded-"):
        return "seeded"
    if label.startswith("error."):
        return "public-error"
    if label.startswith("invalid-window-"):
        return "invalid-window"
    if label.startswith("surrogate-"):
        return "surrogate"
    if label.startswith("backreference-"):
        return "backreference"
    raise RuntimeError(f"unexpected frozen extended-path label: {label!r}")


def run_frozen_suite(module_name: str) -> dict:
    check_frozen_source()
    progress("frozen-full-worker-start", module=module_name)
    module = importlib.import_module(module_name)
    artifacts_before = production_artifacts(module_name, module)
    types = pattern_types(module)
    controls = poison_controls(module, types)
    original_observed = frozen.observed
    original_equivalent = frozen.equivalent
    expected_stream = hashlib.sha256()
    actual_stream = hashlib.sha256()
    observation_count = 0

    def lossless_observed(action):
        nonlocal observation_count
        result = canonicalize(original_observed(action), types)
        payload = json.dumps(
            result, ensure_ascii=True, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        stream = expected_stream if observation_count % 2 == 0 else actual_stream
        stream.update(str(len(payload)).encode("ascii"))
        stream.update(b":")
        stream.update(payload)
        stream.update(b"\n")
        observation_count += 1
        return result

    failures = []
    checks = 0
    phase_checks = {}
    frozen.observed = lossless_observed
    try:
        manual = frozen.manual_cases()
        previous = checks
        for index, case in enumerate(manual):
            checks += frozen.check(module, *case, f"manual-{index}", failures)
            if index and index % 128 == 0:
                progress(
                    "frozen-full-manual-progress",
                    module=module_name,
                    completed_cases=index + 1,
                    correctness_checks=checks,
                    mismatches=len(failures),
                )
        phase_checks["manual"] = checks - previous

        for name, function in (
            ("public-error", frozen.error_surface),
            ("invalid-window", frozen.invalid_window_matrix),
            ("surrogate", frozen.surrogate_matrix),
            ("backreference", frozen.backreference_matrix),
        ):
            previous = checks
            checks += function(module, failures)
            phase_checks[name] = checks - previous
            progress(
                "frozen-full-phase-complete",
                module=module_name,
                phase=name,
                correctness_checks=checks,
                mismatches=len(failures),
            )

        rng = random.Random(FROZEN_SEED)
        previous = checks
        for index in range(SEEDED_CASES):
            case = frozen.generated(rng, index)
            checks += frozen.check(module, *case, f"seeded-{index}", failures)
            if index and index % 64 == 0:
                progress(
                    "frozen-full-seeded-progress",
                    module=module_name,
                    completed_cases=index + 1,
                    correctness_checks=checks,
                    mismatches=len(failures),
                )
        phase_checks["seeded"] = checks - previous
    finally:
        frozen.observed = original_observed

    check_frozen_source()
    if frozen.equivalent is not original_equivalent:
        raise RuntimeError("the original frozen equivalence was replaced")
    if checks != FROZEN_CHECKS:
        raise RuntimeError(
            f"frozen extended-path denominator drift: {checks} != {FROZEN_CHECKS}"
        )
    if observation_count != checks * 2:
        raise RuntimeError(
            f"frozen observation count drift: {observation_count} != {checks * 2}"
        )
    artifacts_after = production_artifacts(module_name, module)
    if artifacts_after != artifacts_before:
        raise RuntimeError("candidate production artifacts changed during diagnosis")

    by_phase = Counter()
    by_operation = Counter()
    for row in failures:
        by_phase[phase(row["label"])] += 1
        by_operation[row["operation"]] += 1

    return {
        "schema": SCHEMA,
        "status": "PASS" if not failures else "MISMATCH",
        "module": module_name,
        "python": ".".join(map(str, PINNED_PYTHON)),
        "python_executable": sys.executable,
        "frozen_suite": {
            "path": "tools/rust_v6_paths_probe.py",
            "sha256": FROZEN_SHA256,
            "seed": FROZEN_SEED,
            "seeded_cases": SEEDED_CASES,
            "equivalence": "unchanged tools.rust_v6_paths_probe.equivalent",
            "only_observation_change": (
                "uniform structural pattern, flags, groups, and groupindex "
                "encoding for successfully compiled patterns"
            ),
        },
        "correctness_checks": checks,
        "observation_pairs": observation_count // 2,
        "phase_checks": dict(sorted(phase_checks.items())),
        "expected_observations_sha256": expected_stream.hexdigest(),
        "actual_observations_sha256": actual_stream.hexdigest(),
        "failed": len(failures),
        "failures_by_phase": dict(sorted(by_phase.items())),
        "failures_by_operation": dict(sorted(by_operation.items())),
        "first_failure": failures[0] if failures else None,
        "failures": failures,
        "poison_controls": controls,
        "production_artifacts": artifacts_before,
        "holdout_cases_read": 0,
        "performance_fixtures_read": 0,
        "timing_performed": False,
        "performance": "NOT MEASURED",
    }


def isolated_worker(
    module: str,
    output: Path,
    *,
    timeout_seconds: float = FULL_WORKER_TIMEOUT_SECONDS,
    case_index: int | None = None,
) -> tuple[dict, dict]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONPATH"] = str(ROOT)
    command = [
        sys.executable,
        "-B",
        str(Path(__file__).resolve()),
        "_worker" if case_index is None else "_manual-case-worker",
        "--module",
        module,
        "--output",
        str(output),
    ]
    if case_index is not None:
        command.extend(("--case-index", str(case_index)))
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="backslashreplace",
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise FrozenWorkerTimeout(
            module,
            timeout_seconds,
            error.stdout,
            error.stderr,
        ) from error
    if completed.returncode:
        raise RuntimeError(
            f"isolated frozen diagnostic failed for {module}: "
            f"exit={completed.returncode}; stderr={completed.stderr[-6000:]}; "
            f"stdout={completed.stdout[-3000:]}"
        )
    if not output.is_file():
        raise RuntimeError(f"isolated diagnostic omitted its actual evidence: {module}")
    return read_report(output), {
        "process_exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "timeout_seconds": timeout_seconds,
    }


def run_frozen_manual_case(module_name: str, case_index: int) -> dict:
    check_frozen_source()
    if not 0 <= case_index < MAX_MANUAL_CASES:
        raise ValueError("the bounded diagnostic accepts only frozen manual cases 0-15")
    pattern, subject, flags = frozen.manual_cases()[case_index]
    progress(
        "bounded-frozen-manual-case-start",
        module=module_name,
        case_index=case_index,
        pattern=repr(pattern),
        subject=repr(subject),
        flags=int(flags),
    )
    module = importlib.import_module(module_name)
    artifacts_before = production_artifacts(module_name, module)
    types = pattern_types(module)
    controls = poison_controls(module, types)
    original_observed = frozen.observed
    original_equivalent = frozen.equivalent
    expected_stream = hashlib.sha256()
    actual_stream = hashlib.sha256()
    observation_count = 0

    def lossless_observed(action):
        nonlocal observation_count
        result = canonicalize(original_observed(action), types)
        payload = json.dumps(
            result, ensure_ascii=True, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        stream = expected_stream if observation_count % 2 == 0 else actual_stream
        stream.update(str(len(payload)).encode("ascii"))
        stream.update(b":")
        stream.update(payload)
        stream.update(b"\n")
        observation_count += 1
        return result

    failures = []
    frozen.observed = lossless_observed
    try:
        checks = frozen.check(
            module,
            pattern,
            subject,
            flags,
            f"manual-{case_index}",
            failures,
        )
    finally:
        frozen.observed = original_observed
    check_frozen_source()
    if frozen.equivalent is not original_equivalent:
        raise RuntimeError("the original frozen manual-case equivalence was replaced")
    if observation_count != checks * 2:
        raise RuntimeError("the original frozen manual-case observation count changed")
    if production_artifacts(module_name, module) != artifacts_before:
        raise RuntimeError("a candidate artifact changed during its isolated case")
    progress(
        "bounded-frozen-manual-case-complete",
        module=module_name,
        case_index=case_index,
        correctness_checks=checks,
        mismatches=len(failures),
    )
    return {
        "schema": "rebar-v8-bounded-frozen-manual-case-v1",
        "status": "PASS" if not failures else "MISMATCH",
        "module": module_name,
        "case_index": case_index,
        "label": f"manual-{case_index}",
        "pattern": repr(pattern),
        "subject": repr(subject),
        "flags": int(flags),
        "correctness_checks": checks,
        "observation_pairs": observation_count // 2,
        "expected_observations_sha256": expected_stream.hexdigest(),
        "actual_observations_sha256": actual_stream.hexdigest(),
        "failed": len(failures),
        "failures": failures,
        "poison_controls": controls,
        "frozen_source_sha256": FROZEN_SHA256,
        "production_artifacts": artifacts_before,
        "full_suite_performed": False,
        "holdout_cases_read": 0,
        "performance_fixtures_read": 0,
        "timing_performed": False,
        "performance": "NOT MEASURED",
    }


def bounded_timeout_control() -> dict:
    fake_timeout = subprocess.TimeoutExpired(
        cmd=["frozen-diagnostic-timeout-poison"],
        timeout=1,
        output=b"frozen-timeout-poison-stdout\n",
        stderr=b"frozen-timeout-poison-stderr\n",
    )
    with mock.patch("subprocess.run", side_effect=fake_timeout) as mocked:
        try:
            isolated_worker(
                "re",
                Path("timeout-poison-must-not-be-created.json"),
                timeout_seconds=1,
                case_index=0,
            )
        except FrozenWorkerTimeout as error:
            controls = {
                "timeout_is_fail_closed": True,
                "timeout_stdout_is_preserved": (
                    error.stdout == "frozen-timeout-poison-stdout\n"
                ),
                "timeout_stderr_is_preserved": (
                    error.stderr == "frozen-timeout-poison-stderr\n"
                ),
                "timeout_has_explicit_limit": error.seconds == 1,
                "timeout_never_retries": mocked.call_count == 1,
            }
        else:
            raise RuntimeError("the mocked timeout was incorrectly treated as a result")
    if not all(controls.values()):
        raise RuntimeError(f"bounded diagnostic timeout poison failed: {controls!r}")
    return controls


def remaining_case_timeout(deadline: float, module: str) -> float:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise FrozenWorkerTimeout(module, MANUAL_GLOBAL_TIMEOUT_SECONDS, "", "")
    return min(float(MANUAL_CASE_TIMEOUT_SECONDS), remaining)


def bounded_self_test(output: Path, case_limit: int) -> int:
    check_frozen_source()
    if not 1 <= case_limit <= MAX_MANUAL_CASES:
        raise ValueError("the bounded self-test must contain between 1 and 16 cases")
    controls = bounded_timeout_control()
    deadline = time.monotonic() + MANUAL_GLOBAL_TIMEOUT_SECONDS
    rows = []
    reference_a_checks = 0
    reference_b_checks = 0
    failure = None
    with tempfile.TemporaryDirectory(
        prefix="rebar-v8-bounded-manual-self-", dir="/tmp"
    ) as temporary:
        directory = Path(temporary)
        for index in range(case_limit):
            progress("bounded-self-reference-case-start", case_index=index)
            try:
                first, first_process = isolated_worker(
                    "re",
                    directory / f"reference-a-{index}.json",
                    timeout_seconds=remaining_case_timeout(deadline, "re"),
                    case_index=index,
                )
                second, second_process = isolated_worker(
                    "re",
                    directory / f"reference-b-{index}.json",
                    timeout_seconds=remaining_case_timeout(deadline, "re"),
                    case_index=index,
                )
            except FrozenWorkerTimeout as error:
                failure = {
                    "kind": "REFERENCE_TIMEOUT",
                    "case_index": index,
                    "timeout_seconds": error.seconds,
                    "stdout": error.stdout,
                    "stderr": error.stderr,
                }
                break
            requirements = {
                "reference_a_zero_failures": first["failed"] == 0,
                "reference_b_zero_failures": second["failed"] == 0,
                "reference_check_counts_match": (
                    first["correctness_checks"] == second["correctness_checks"]
                ),
                "independent_reference_observations_match": (
                    first["expected_observations_sha256"]
                    == second["expected_observations_sha256"]
                ),
                "reference_a_expected_equals_actual": (
                    first["expected_observations_sha256"]
                    == first["actual_observations_sha256"]
                ),
                "reference_b_expected_equals_actual": (
                    second["expected_observations_sha256"]
                    == second["actual_observations_sha256"]
                ),
                "reference_a_poison_controls": all(first["poison_controls"].values()),
                "reference_b_poison_controls": all(second["poison_controls"].values()),
            }
            reference_a_checks += first["correctness_checks"]
            reference_b_checks += second["correctness_checks"]
            rows.append(
                {
                    "case_index": index,
                    "label": first["label"],
                    "pattern": first["pattern"],
                    "subject": first["subject"],
                    "flags": first["flags"],
                    "checks_per_reference": first["correctness_checks"],
                    "expected_observations_sha256": first[
                        "expected_observations_sha256"
                    ],
                    "controls": requirements,
                    "reference_a": first_process,
                    "reference_b": second_process,
                }
            )
            progress(
                "bounded-self-reference-case-complete",
                case_index=index,
                checks_per_reference=first["correctness_checks"],
                mismatches=first["failed"] + second["failed"],
            )
            if not all(requirements.values()):
                failure = {
                    "kind": "REFERENCE_MISMATCH",
                    "case_index": index,
                    "controls": requirements,
                }
                break
    controls["original_frozen_source_unchanged"] = (
        digest(FROZEN_PATH) == FROZEN_SHA256
    )
    controls["exact_frozen_case_order"] = [row["case_index"] for row in rows] == list(
        range(len(rows))
    )
    controls["partial_scope_never_claims_full_suite"] = True
    status = (
        "PASS"
        if failure is None and len(rows) == case_limit and all(controls.values())
        else "FAIL"
    )
    report = {
        "schema": BOUNDED_SELF_SCHEMA,
        "status": status,
        "scope": "only the first frozen manual cases; not the full extended-path suite",
        "frozen_suite": {
            "path": "tools/rust_v6_paths_probe.py",
            "sha256": FROZEN_SHA256,
            "seed": FROZEN_SEED,
            "equivalence": "unchanged tools.rust_v6_paths_probe.equivalent",
        },
        "manual_case_limit": case_limit,
        "completed_manual_cases": len(rows),
        "case_timeout_seconds": MANUAL_CASE_TIMEOUT_SECONDS,
        "global_timeout_seconds": MANUAL_GLOBAL_TIMEOUT_SECONDS,
        "independent_reference_processes_per_case": 2,
        "reference_a_correctness_checks": reference_a_checks,
        "reference_b_correctness_checks": reference_b_checks,
        "self_oracle_failures": 0 if failure is None else 1,
        "controls": controls,
        "cases": rows,
        "failure": failure,
        "full_suite_performed": False,
        "holdout_cases_read": 0,
        "performance_fixtures_read": 0,
        "timing_performed": False,
        "performance": "NOT MEASURED",
    }
    write_report(output, report)
    progress(
        "bounded-self-test-complete",
        status=status,
        completed_manual_cases=len(rows),
        reference_a_correctness_checks=reference_a_checks,
        reference_b_correctness_checks=reference_b_checks,
        output=str(output),
    )
    return 0 if status == "PASS" else 1


def bounded_manual(module: str, self_path: Path, output: Path) -> int:
    check_frozen_source()
    self_reference = read_report(self_path)
    if (
        self_reference.get("schema") != BOUNDED_SELF_SCHEMA
        or self_reference.get("status") != "PASS"
        or not all(self_reference.get("controls", {}).values())
        or self_reference.get("frozen_suite", {}).get("sha256") != FROZEN_SHA256
        or not 1 <= self_reference.get("manual_case_limit", 0) <= MAX_MANUAL_CASES
    ):
        raise RuntimeError("the independently bounded frozen self-reference did not pass")
    case_limit = self_reference["manual_case_limit"]
    deadline = time.monotonic() + MANUAL_GLOBAL_TIMEOUT_SECONDS
    completed = []
    failure = None
    with tempfile.TemporaryDirectory(
        prefix="rebar-v8-bounded-manual-candidate-", dir="/tmp"
    ) as temporary:
        directory = Path(temporary)
        for index in range(case_limit):
            expected = self_reference["cases"][index]
            if expected["case_index"] != index:
                raise RuntimeError("the frozen manual case order changed")
            progress(
                "bounded-candidate-case-start",
                module=module,
                case_index=index,
                pattern=expected["pattern"],
            )
            try:
                actual, process = isolated_worker(
                    module,
                    directory / f"candidate-{index}.json",
                    timeout_seconds=remaining_case_timeout(deadline, module),
                    case_index=index,
                )
            except FrozenWorkerTimeout as error:
                failure = {
                    "kind": "RESOURCE_TIMEOUT",
                    "case_index": index,
                    "label": expected["label"],
                    "pattern": expected["pattern"],
                    "subject": expected["subject"],
                    "flags": expected["flags"],
                    "timeout_seconds": error.seconds,
                    "worker_stdout": error.stdout,
                    "worker_stderr": error.stderr,
                    "match_result": "NOT OBSERVED",
                }
                progress(
                    "bounded-candidate-case-timeout",
                    module=module,
                    case_index=index,
                    pattern=expected["pattern"],
                    timeout_seconds=error.seconds,
                )
                break
            if (
                actual["expected_observations_sha256"]
                != expected["expected_observations_sha256"]
                or actual["correctness_checks"] != expected["checks_per_reference"]
                or not all(actual["poison_controls"].values())
            ):
                failure = {
                    "kind": "SELF_ORACLE_DRIFT",
                    "case_index": index,
                    "label": expected["label"],
                    "expected_observations_sha256": expected[
                        "expected_observations_sha256"
                    ],
                    "actual_reference_observations_sha256": actual[
                        "expected_observations_sha256"
                    ],
                }
                break
            actual["isolated_process"] = process
            completed.append(actual)
            progress(
                "bounded-candidate-case-complete",
                module=module,
                case_index=index,
                correctness_checks=actual["correctness_checks"],
                mismatches=actual["failed"],
            )
            if actual["failed"]:
                failure = {
                    "kind": "CORRECTNESS_MISMATCH",
                    "case_index": index,
                    "label": expected["label"],
                    "pattern": expected["pattern"],
                    "subject": expected["subject"],
                    "flags": expected["flags"],
                    "failed": actual["failed"],
                    "first_failure": actual["failures"][0],
                }
                break
    if failure is None and len(completed) == case_limit:
        status = "PASS"
    elif failure is not None and failure["kind"] == "CORRECTNESS_MISMATCH":
        status = "MISMATCH"
    else:
        status = "RESOURCE_FAILURE"
    check_frozen_source()
    report = {
        "schema": BOUNDED_MANUAL_SCHEMA,
        "status": status,
        "module": module,
        "scope": "only the first frozen manual cases; not the full extended-path suite",
        "frozen_suite": self_reference["frozen_suite"],
        "manual_case_limit": case_limit,
        "completed_manual_cases": len(completed),
        "candidate_correctness_checks": sum(
            row["correctness_checks"] for row in completed
        ),
        "completed_candidate_mismatches": sum(row["failed"] for row in completed),
        "case_timeout_seconds": MANUAL_CASE_TIMEOUT_SECONDS,
        "global_timeout_seconds": MANUAL_GLOBAL_TIMEOUT_SECONDS,
        "independent_self_reference": {
            "path": str(self_path),
            "sha256": digest(self_path),
            "isolated_processes_per_case": 2,
            "completed_manual_cases": self_reference["completed_manual_cases"],
            "self_oracle_failures": self_reference["self_oracle_failures"],
        },
        "production_artifacts": (
            completed[0]["production_artifacts"] if completed else []
        ),
        "completed_cases": completed,
        "failure": failure,
        "full_suite_performed": False,
        "holdout_cases_read": 0,
        "performance_fixtures_read": 0,
        "timing_performed": False,
        "performance": "NOT MEASURED",
    }
    write_report(output, report)
    progress(
        "bounded-candidate-diagnostic-complete",
        module=module,
        status=status,
        completed_manual_cases=len(completed),
        candidate_correctness_checks=report["candidate_correctness_checks"],
        completed_candidate_mismatches=report["completed_candidate_mismatches"],
        failure_kind=None if failure is None else failure["kind"],
        output=str(output),
    )
    return 0 if status == "PASS" else 1


def self_test(output: Path) -> int:
    check_frozen_source()
    with tempfile.TemporaryDirectory(prefix="rebar-v8-frozen-path-self-", dir="/tmp") as temporary:
        directory = Path(temporary)
        first, first_process = isolated_worker("re", directory / "reference-a.json")
        second, second_process = isolated_worker("re", directory / "reference-b.json")
        requirements = {
            "reference_a_denominator": first["correctness_checks"] == FROZEN_CHECKS,
            "reference_b_denominator": second["correctness_checks"] == FROZEN_CHECKS,
            "reference_a_zero_failures": first["failed"] == 0,
            "reference_b_zero_failures": second["failed"] == 0,
            "reference_a_expected_equals_actual": (
                first["expected_observations_sha256"]
                == first["actual_observations_sha256"]
            ),
            "reference_b_expected_equals_actual": (
                second["expected_observations_sha256"]
                == second["actual_observations_sha256"]
            ),
            "independent_reference_digests_match": (
                first["expected_observations_sha256"]
                == second["expected_observations_sha256"]
            ),
            "reference_a_poison_controls": all(first["poison_controls"].values()),
            "reference_b_poison_controls": all(second["poison_controls"].values()),
            "original_frozen_source_unchanged": digest(FROZEN_PATH) == FROZEN_SHA256,
        }
        report = {
            "schema": SELF_SCHEMA,
            "status": "PASS" if all(requirements.values()) else "FAIL",
            "python": ".".join(map(str, PINNED_PYTHON)),
            "python_executable": sys.executable,
            "frozen_suite": first["frozen_suite"],
            "correctness_checks_per_reference": FROZEN_CHECKS,
            "independent_reference_processes": 2,
            "expected_observations_sha256": first["expected_observations_sha256"],
            "reference_a": {
                "checks": first["correctness_checks"],
                "failed": first["failed"],
                "observations_sha256": first["actual_observations_sha256"],
                "phase_checks": first["phase_checks"],
                "poison_controls": first["poison_controls"],
                "process": first_process,
            },
            "reference_b": {
                "checks": second["correctness_checks"],
                "failed": second["failed"],
                "observations_sha256": second["actual_observations_sha256"],
                "phase_checks": second["phase_checks"],
                "poison_controls": second["poison_controls"],
                "process": second_process,
            },
            "controls": requirements,
            "holdout_cases_read": 0,
            "performance_fixtures_read": 0,
            "timing_performed": False,
            "performance": "NOT MEASURED",
        }
    write_report(output, report)
    print(
        json.dumps(
            {
                "schema": SELF_SCHEMA,
                "status": report["status"],
                "references": 2,
                "checks_per_reference": FROZEN_CHECKS,
                "self_oracle_failures": first["failed"] + second["failed"],
                "controls": requirements,
                "output": str(output),
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0 if all(requirements.values()) else 1


def verify(module: str, self_path: Path, output: Path) -> int:
    check_frozen_source()
    self_reference = read_report(self_path)
    if (
        self_reference.get("schema") != SELF_SCHEMA
        or self_reference.get("status") != "PASS"
        or self_reference.get("correctness_checks_per_reference") != FROZEN_CHECKS
        or not all(self_reference.get("controls", {}).values())
        or self_reference.get("frozen_suite", {}).get("sha256") != FROZEN_SHA256
    ):
        raise RuntimeError("the two frozen isolated standard-library references did not pass")
    with tempfile.TemporaryDirectory(prefix="rebar-v8-frozen-path-candidate-", dir="/tmp") as temporary:
        report, process = isolated_worker(module, Path(temporary) / "candidate.json")
    if report["correctness_checks"] != FROZEN_CHECKS:
        raise RuntimeError("the candidate did not execute all frozen extended-path cases")
    if report["expected_observations_sha256"] != self_reference["expected_observations_sha256"]:
        raise RuntimeError("the candidate process silently changed frozen stdlib expectations")
    if not all(report["poison_controls"].values()):
        raise RuntimeError("the candidate diagnostic poison controls did not pass")
    report["isolated_process"] = process
    report["independent_self_reference"] = {
        "path": str(self_path),
        "sha256": digest(self_path),
        "reference_processes": 2,
        "checks_per_reference": FROZEN_CHECKS,
        "self_oracle_failures": 0,
        "expected_observations_sha256": self_reference["expected_observations_sha256"],
    }
    check_frozen_source()
    write_report(output, report)
    print(
        json.dumps(
            {
                "schema": SCHEMA,
                "status": report["status"],
                "module": module,
                "correctness_checks": report["correctness_checks"],
                "failed": report["failed"],
                "self_oracle_failures": 0,
                "failures_by_phase": report["failures_by_phase"],
                "failures_by_operation": report["failures_by_operation"],
                "frozen_source_sha256": FROZEN_SHA256,
                "output": str(output),
            },
            ensure_ascii=True,
            sort_keys=True,
        ),
        flush=True,
    )
    return 0 if not report["failed"] else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    self_parser = commands.add_parser("self-test")
    self_parser.add_argument("--output", type=Path, required=True)
    bounded_self_parser = commands.add_parser("bounded-self-test")
    bounded_self_parser.add_argument("--output", type=Path, required=True)
    bounded_self_parser.add_argument(
        "--case-limit", type=int, default=MAX_MANUAL_CASES
    )
    worker_parser = commands.add_parser("_worker")
    worker_parser.add_argument("--module", required=True)
    worker_parser.add_argument("--output", type=Path, required=True)
    manual_worker_parser = commands.add_parser("_manual-case-worker")
    manual_worker_parser.add_argument("--module", required=True)
    manual_worker_parser.add_argument("--case-index", type=int, required=True)
    manual_worker_parser.add_argument("--output", type=Path, required=True)
    verify_parser = commands.add_parser("verify")
    verify_parser.add_argument(
        "--module",
        choices=("candidates.vm_candidate", "candidates.zig_candidate"),
        required=True,
    )
    verify_parser.add_argument("--self-test", type=Path, required=True)
    verify_parser.add_argument("--output", type=Path, required=True)
    bounded_verify_parser = commands.add_parser("bounded-manual")
    bounded_verify_parser.add_argument(
        "--module",
        choices=("candidates.vm_candidate", "candidates.zig_candidate"),
        required=True,
    )
    bounded_verify_parser.add_argument("--self-test", type=Path, required=True)
    bounded_verify_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "self-test":
        return self_test(args.output)
    if args.command == "bounded-self-test":
        return bounded_self_test(args.output, args.case_limit)
    if args.command == "_worker":
        report = run_frozen_suite(args.module)
        write_report(args.output, report)
        print(
            json.dumps(
                {
                    "schema": SCHEMA,
                    "module": args.module,
                    "correctness_checks": report["correctness_checks"],
                    "failed": report["failed"],
                },
                sort_keys=True,
            ),
            flush=True,
        )
        return 0
    if args.command == "_manual-case-worker":
        report = run_frozen_manual_case(args.module, args.case_index)
        write_report(args.output, report)
        progress(
            "bounded-frozen-manual-case-report-written",
            module=args.module,
            case_index=args.case_index,
            correctness_checks=report["correctness_checks"],
            mismatches=report["failed"],
        )
        return 0
    if args.command == "bounded-manual":
        return bounded_manual(args.module, args.self_test, args.output)
    return verify(args.module, args.self_test, args.output)


if __name__ == "__main__":
    raise SystemExit(main())
