"""Differential correctness harness for parser compile conformance cases."""

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
from rebar_harness.metadata import build_cpython_baseline


TARGET_CPYTHON_SERIES = "3.12.x"
REPORT_SCHEMA_VERSION = "1.0"
FIXTURE_SCHEMA_VERSION = 1
DEFAULT_FIXTURES_PATH = REPO_ROOT / "tests" / "conformance" / "fixtures" / "parser_matrix.json"
DEFAULT_REPORT_PATH = REPO_ROOT / "reports" / "correctness" / "latest.json"


@dataclass(frozen=True)
class FixtureCase:
    """Single compile-oriented differential case."""

    case_id: str
    family: str
    operation: str
    pattern: str
    flags: int
    text_model: str
    pattern_encoding: str
    notes: list[str]
    categories: list[str]

    @classmethod
    def from_dict(cls, raw_case: dict[str, Any], defaults: dict[str, Any]) -> "FixtureCase":
        return cls(
            case_id=str(raw_case["id"]),
            family=str(raw_case.get("family", defaults.get("family", "parser"))),
            operation=str(raw_case.get("operation", defaults.get("operation", "compile"))),
            pattern=str(raw_case["pattern"]),
            flags=int(raw_case.get("flags", defaults.get("flags", 0))),
            text_model=str(raw_case.get("text_model", defaults.get("text_model", "str"))),
            pattern_encoding=str(
                raw_case.get(
                    "pattern_encoding",
                    defaults.get("pattern_encoding", "latin-1"),
                )
            ),
            notes=[str(note) for note in raw_case.get("notes", [])],
            categories=[str(category) for category in raw_case.get("categories", [])],
        )

    def pattern_payload(self) -> str | bytes:
        if self.text_model == "str":
            return self.pattern
        if self.text_model == "bytes":
            return self.pattern.encode(self.pattern_encoding)
        raise ValueError(f"unsupported text model {self.text_model!r}")


def load_fixture_manifest(path: pathlib.Path) -> tuple[dict[str, Any], list[FixtureCase]]:
    raw_manifest = json.loads(path.read_text(encoding="utf-8"))
    schema_version = raw_manifest.get("schema_version")
    if schema_version != FIXTURE_SCHEMA_VERSION:
        raise ValueError(
            f"unsupported fixture schema version {schema_version!r}; "
            f"expected {FIXTURE_SCHEMA_VERSION}"
        )

    defaults = raw_manifest.get("defaults", {})
    if not isinstance(defaults, dict):
        raise ValueError("fixture manifest defaults must be an object")

    cases = [
        FixtureCase.from_dict(raw_case, defaults) for raw_case in raw_manifest.get("cases", [])
    ]
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
        "pattern": normalize_pattern_value(compiled_pattern.pattern),
        "flags": compiled_pattern.flags,
        "groups": compiled_pattern.groups,
        "groupindex": dict(sorted(groupindex.items())),
        "pattern_type": type(compiled_pattern.pattern).__name__,
    }


def normalize_pattern_value(pattern: str | bytes) -> str | dict[str, str]:
    if isinstance(pattern, bytes):
        return {
            "encoding": "latin-1",
            "value": pattern.decode("latin-1"),
        }
    return pattern


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
        pattern = case.pattern_payload()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            try:
                compiled = cpython_re.compile(pattern, case.flags)
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
        pattern = case.pattern_payload()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            try:
                compiled = rebar.compile(pattern, case.flags)
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

    cpython_observation = cpython_adapter.observe_compile(case)
    rebar_observation = rebar_adapter.observe_compile(case)
    comparison, mismatch_notes = compare_compile_observations(
        cpython_observation, rebar_observation
    )

    return {
        "id": case.case_id,
        "family": case.family,
        "operation": case.operation,
        "text_model": case.text_model,
        "pattern": case.pattern,
        "flags": case.flags,
        "notes": case.notes,
        "categories": case.categories,
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


def build_observation_summary(observations: list[dict[str, Any]]) -> dict[str, Any]:
    outcomes: dict[str, int] = {}
    warning_categories: dict[str, int] = {}
    exception_types: dict[str, int] = {}
    warning_case_count = 0
    exception_case_count = 0

    for observation in observations:
        outcome = str(observation["outcome"])
        outcomes[outcome] = outcomes.get(outcome, 0) + 1

        warnings_payload = observation.get("warnings", [])
        if warnings_payload:
            warning_case_count += 1
            for warning_record in warnings_payload:
                category = str(warning_record["category"])
                warning_categories[category] = warning_categories.get(category, 0) + 1

        exception = observation.get("exception")
        if exception is not None:
            exception_case_count += 1
            exception_type = str(exception["type"])
            exception_types[exception_type] = exception_types.get(exception_type, 0) + 1

    return {
        "outcomes": dict(sorted(outcomes.items())),
        "warning_case_count": warning_case_count,
        "exception_case_count": exception_case_count,
        "warning_categories": dict(sorted(warning_categories.items())),
        "exception_types": dict(sorted(exception_types.items())),
    }


def build_diagnostics_summary(case_results: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "by_adapter": {
            "cpython": build_observation_summary(
                [result["observations"]["cpython"] for result in case_results]
            ),
            "rebar": build_observation_summary(
                [result["observations"]["rebar"] for result in case_results]
            ),
        }
    }


def build_suite_summary(
    *,
    suite_id: str,
    layer: str,
    case_results: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "id": suite_id,
        "layer": layer,
        "case_count": len(case_results),
        "families": sorted({result["family"] for result in case_results}),
        "text_models": sorted({result["text_model"] for result in case_results}),
        "summary": build_summary(case_results),
        "diagnostics": build_diagnostics_summary(case_results),
    }


def build_family_summaries(case_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    families = sorted({result["family"] for result in case_results})
    return [
        {
            "id": family,
            "case_count": len(
                [result for result in case_results if result["family"] == family]
            ),
            "text_models": sorted(
                {result["text_model"] for result in case_results if result["family"] == family}
            ),
            "summary": build_summary(
                [result for result in case_results if result["family"] == family]
            ),
        }
        for family in families
    ]


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
        "phase": "phase1-parser-conformance-pack",
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "generator": "python -m rebar_harness.correctness",
        "baseline": {
            **build_cpython_baseline(version_family=TARGET_CPYTHON_SERIES),
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
        "diagnostics": build_diagnostics_summary(case_results),
        "suites": [
            build_suite_summary(
                suite_id="parser.compile",
                layer="parser_acceptance_and_diagnostics",
                case_results=case_results,
            ),
            *[
                build_suite_summary(
                    suite_id=f"parser.compile.{text_model}",
                    layer="parser_acceptance_and_diagnostics",
                    case_results=[
                        result for result in case_results if result["text_model"] == text_model
                    ],
                )
                for text_model in ("str", "bytes")
                if any(result["text_model"] == text_model for result in case_results)
            ],
        ],
        "families": build_family_summaries(case_results),
        "cases": case_results,
    }


def write_scorecard(scorecard: dict[str, Any], report_path: pathlib.Path) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(scorecard, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_correctness_harness(
    fixture_path: pathlib.Path = DEFAULT_FIXTURES_PATH,
    report_path: pathlib.Path = DEFAULT_REPORT_PATH,
) -> dict[str, Any]:
    fixture_path = fixture_path.resolve()
    report_path = report_path.resolve()
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
