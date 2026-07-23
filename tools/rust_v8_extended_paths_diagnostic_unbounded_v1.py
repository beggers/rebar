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
from collections import Counter
from pathlib import Path

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

        rng = random.Random(FROZEN_SEED)
        previous = checks
        for index in range(SEEDED_CASES):
            case = frozen.generated(rng, index)
            checks += frozen.check(module, *case, f"seeded-{index}", failures)
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


def isolated_worker(module: str, output: Path) -> tuple[dict, dict]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONPATH"] = str(ROOT)
    command = [
        sys.executable,
        "-B",
        str(Path(__file__).resolve()),
        "_worker",
        "--module",
        module,
        "--output",
        str(output),
    ]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        errors="backslashreplace",
        check=False,
    )
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
    }


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
    worker_parser = commands.add_parser("_worker")
    worker_parser.add_argument("--module", required=True)
    worker_parser.add_argument("--output", type=Path, required=True)
    verify_parser = commands.add_parser("verify")
    verify_parser.add_argument(
        "--module",
        choices=("candidates.vm_candidate", "candidates.zig_candidate"),
        required=True,
    )
    verify_parser.add_argument("--self-test", type=Path, required=True)
    verify_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "self-test":
        return self_test(args.output)
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
    return verify(args.module, args.self_test, args.output)


if __name__ == "__main__":
    raise SystemExit(main())
