"""Phase 0 differential correctness harness for compile-oriented smoke cases."""

from __future__ import annotations

import argparse
import json
import pathlib
import re as cpython_re
import sys
import warnings
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"

if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))

import rebar


TARGET_CPYTHON_SERIES = "3.12.x"
REPORT_SCHEMA_VERSION = "1.0"
FIXTURE_SCHEMA_VERSION = 1
DEFAULT_FIXTURES_PATH = REPO_ROOT / "tests" / "conformance" / "fixtures" / "parser_smoke.json"
DEFAULT_REPORT_PATH = REPO_ROOT / "reports" / "correctness" / "latest.json"


@dataclass(frozen=True)
class FixtureCase:
    """Single compile-oriented differential case."""

    case_id: str
    operation: str
    pattern: str
    flags: int
    text_model: str
    notes: list[str]

    @classmethod
    def from_dict(cls, raw_case: dict[str, Any]) -> "FixtureCase":
        return cls(
            case_id=str(raw_case["id"]),
            operation=str(raw_case["operation"]),
            pattern=str(raw_case["pattern"]),
            flags=int(raw_case.get("flags", 0)),
            text_model=str(raw_case.get("text_model", "str")),
            notes=[str(note) for note in raw_case.get("notes", [])],
        )


def load_fixture_manifest(path: pathlib.Path) -> tuple[dict[str, Any], list[FixtureCase]]:
    raw_manifest = json.loads(path.read_text(encoding="utf-8"))
    schema_version = raw_manifest.get("schema_version")
    if schema_version != FIXTURE_SCHEMA_VERSION:
        raise ValueError(
            f"unsupported fixture schema version {schema_version!r}; "
            f"expected {FIXTURE_SCHEMA_VERSION}"
        )

    cases = [FixtureCase.from_dict(raw_case) for raw_case in raw_manifest.get("cases", [])]
    return raw_manifest, cases


def normalize_warning_records(records: list[warnings.WarningMessage]) -> list[dict[str, str]]:
    return [
        {
            "category": record.category.__name__,
            "message": str(record.message),
        }
        for record in records
    ]


def normalize_success_metadata(compiled_pattern: Any) -> dict[str, Any]:
    groupindex = getattr(compiled_pattern, "groupindex", {})
    return {
        "pattern": compiled_pattern.pattern,
        "flags": compiled_pattern.flags,
        "groups": compiled_pattern.groups,
        "groupindex": dict(sorted(groupindex.items())),
        "pattern_type": type(compiled_pattern.pattern).__name__,
    }


def normalize_exception(exc: BaseException) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "type": type(exc).__name__,
        "message": str(exc),
    }
    for attribute in ("pos", "lineno", "colno"):
        if hasattr(exc, attribute):
            value = getattr(exc, attribute)
            if value is not None:
                payload[attribute] = value
    return payload


class CompileAdapter:
    """Adapter boundary for compile-oriented observations."""

    adapter_name: str

    def observe_compile(self, case: FixtureCase) -> dict[str, Any]:
        raise NotImplementedError


class CpythonReAdapter(CompileAdapter):
    adapter_name = "cpython.re"

    def observe_compile(self, case: FixtureCase) -> dict[str, Any]:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            try:
                compiled = cpython_re.compile(case.pattern, case.flags)
            except Exception as exc:  # pragma: no cover - exercised by fixtures
                return finalize_observation(
                    adapter=self.adapter_name,
                    case=case,
                    outcome="exception",
                    warnings_payload=normalize_warning_records(caught),
                    exception=normalize_exception(exc),
                )

        return finalize_observation(
            adapter=self.adapter_name,
            case=case,
            outcome="success",
            warnings_payload=normalize_warning_records(caught),
            result=normalize_success_metadata(compiled),
        )


class RebarAdapter(CompileAdapter):
    adapter_name = "rebar"

    def observe_compile(self, case: FixtureCase) -> dict[str, Any]:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            try:
                compiled = rebar.compile(case.pattern, case.flags)
            except NotImplementedError as exc:
                return finalize_observation(
                    adapter=self.adapter_name,
                    case=case,
                    outcome="unimplemented",
                    warnings_payload=normalize_warning_records(caught),
                    exception=normalize_exception(exc),
                )
            except Exception as exc:
                return finalize_observation(
                    adapter=self.adapter_name,
                    case=case,
                    outcome="exception",
                    warnings_payload=normalize_warning_records(caught),
                    exception=normalize_exception(exc),
                )

        return finalize_observation(
            adapter=self.adapter_name,
            case=case,
            outcome="success",
            warnings_payload=normalize_warning_records(caught),
            result=normalize_success_metadata(compiled),
        )


def finalize_observation(
    *,
    adapter: str,
    case: FixtureCase,
    outcome: str,
    warnings_payload: list[dict[str, str]],
    result: dict[str, Any] | None = None,
    exception: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "adapter": adapter,
        "operation": case.operation,
        "outcome": outcome,
        "warnings": warnings_payload,
        "result": result,
        "exception": exception,
    }


def compare_compile_observations(
    cpython_observation: dict[str, Any], rebar_observation: dict[str, Any]
) -> tuple[str, list[str]]:
    if rebar_observation["outcome"] == "unimplemented":
        return "unimplemented", ["rebar adapter reports compile support as unimplemented"]

    mismatches: list[str] = []
    if cpython_observation["outcome"] != rebar_observation["outcome"]:
        mismatches.append(
            "outcome mismatch: "
            f"{cpython_observation['outcome']} != {rebar_observation['outcome']}"
        )

    if cpython_observation["warnings"] != rebar_observation["warnings"]:
        mismatches.append("warning payload mismatch")

    if cpython_observation["result"] != rebar_observation["result"]:
        mismatches.append("result payload mismatch")

    if cpython_observation["exception"] != rebar_observation["exception"]:
        mismatches.append("exception payload mismatch")

    return ("pass", []) if not mismatches else ("fail", mismatches)


def evaluate_case(
    case: FixtureCase, cpython_adapter: CompileAdapter, rebar_adapter: CompileAdapter
) -> dict[str, Any]:
    if case.operation != "compile":
        raise ValueError(f"unsupported operation {case.operation!r}")
    if case.text_model != "str":
        raise ValueError(f"unsupported text model {case.text_model!r} in Phase 0 scaffold")

    cpython_observation = cpython_adapter.observe_compile(case)
    rebar_observation = rebar_adapter.observe_compile(case)
    comparison, mismatch_notes = compare_compile_observations(
        cpython_observation, rebar_observation
    )

    return {
        "id": case.case_id,
        "operation": case.operation,
        "text_model": case.text_model,
        "pattern": case.pattern,
        "flags": case.flags,
        "notes": case.notes,
        "comparison": comparison,
        "comparison_notes": mismatch_notes,
        "observations": {
            "cpython": cpython_observation,
            "rebar": rebar_observation,
        },
    }


def build_summary(case_results: list[dict[str, Any]]) -> dict[str, int]:
    comparison_counts = {"pass": 0, "fail": 0, "unimplemented": 0, "skipped": 0}
    for result in case_results:
        comparison_counts[result["comparison"]] += 1

    return {
        "total_cases": len(case_results),
        "executed_cases": len(case_results),
        "passed_cases": comparison_counts["pass"],
        "failed_cases": comparison_counts["fail"],
        "unimplemented_cases": comparison_counts["unimplemented"],
        "skipped_cases": comparison_counts["skipped"],
    }


def build_scorecard(
    *,
    fixture_path: pathlib.Path,
    raw_manifest: dict[str, Any],
    case_results: list[dict[str, Any]],
) -> dict[str, Any]:
    summary = build_summary(case_results)
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "suite": "correctness",
        "phase": "phase0-harness-skeleton",
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "generator": "python -m rebar_harness.correctness",
        "baseline": {
            "python_family": TARGET_CPYTHON_SERIES,
            "oracle": "cpython-stdlib-re",
            "target_module": "rebar",
        },
        "fixtures": {
            "path": str(fixture_path.relative_to(REPO_ROOT)),
            "schema_version": raw_manifest["schema_version"],
            "manifest_id": raw_manifest["manifest_id"],
            "case_count": len(case_results),
        },
        "summary": summary,
        "suites": [
            {
                "id": "parser.compile",
                "layer": "parser_acceptance_and_diagnostics",
                "summary": summary,
            }
        ],
        "cases": case_results,
    }


def write_scorecard(scorecard: dict[str, Any], report_path: pathlib.Path) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(scorecard, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_correctness_harness(
    fixture_path: pathlib.Path = DEFAULT_FIXTURES_PATH,
    report_path: pathlib.Path = DEFAULT_REPORT_PATH,
) -> dict[str, Any]:
    raw_manifest, cases = load_fixture_manifest(fixture_path)
    cpython_adapter = CpythonReAdapter()
    rebar_adapter = RebarAdapter()
    case_results = [evaluate_case(case, cpython_adapter, rebar_adapter) for case in cases]
    scorecard = build_scorecard(
        fixture_path=fixture_path,
        raw_manifest=raw_manifest,
        case_results=case_results,
    )
    write_scorecard(scorecard, report_path)
    return scorecard


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fixtures",
        type=pathlib.Path,
        default=DEFAULT_FIXTURES_PATH,
        help="Path to the correctness fixture manifest.",
    )
    parser.add_argument(
        "--report",
        type=pathlib.Path,
        default=DEFAULT_REPORT_PATH,
        help="Path to the output JSON scorecard.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    scorecard = run_correctness_harness(fixture_path=args.fixtures, report_path=args.report)
    print(json.dumps(scorecard["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
