from __future__ import annotations

import re
import warnings

from rebar_harness.correctness import (
    REPO_ROOT,
    REPORT_SCHEMA_VERSION,
    FixtureManifest,
    _normalize_value,
    build_fixture_summary,
    build_observation_summary,
    build_scorecard,
    compare_observations,
    normalize_exception,
    normalize_match_metadata,
    normalize_warning_records,
)


def _fixture_manifest(
    *,
    filename: str,
    manifest_id: str,
    layer: str,
    suite_id: str,
) -> FixtureManifest:
    return FixtureManifest(
        path=REPO_ROOT / "tests" / "conformance" / "fixtures" / filename,
        manifest_id=manifest_id,
        layer=layer,
        suite_id=suite_id,
        schema_version=1,
        defaults={},
        cases=[],
    )


def _observation(
    adapter: str,
    operation: str,
    outcome: str,
    *,
    warnings: list[dict[str, str]] | None = None,
    result: object = None,
    exception: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "adapter": adapter,
        "operation": operation,
        "outcome": outcome,
        "warnings": [] if warnings is None else warnings,
        "result": result,
        "exception": exception,
    }


def _case_result(
    *,
    case_id: str,
    manifest_id: str,
    suite_id: str,
    layer: str,
    family: str,
    operation: str,
    comparison: str,
    text_model: str,
    cpython_observation: dict[str, object],
    rebar_observation: dict[str, object],
) -> dict[str, object]:
    return {
        "id": case_id,
        "manifest_id": manifest_id,
        "suite_id": suite_id,
        "layer": layer,
        "family": family,
        "operation": operation,
        "notes": [],
        "categories": [],
        "comparison": comparison,
        "comparison_notes": [],
        "text_model": text_model,
        "observations": {
            "cpython": cpython_observation,
            "rebar": rebar_observation,
        },
    }


PARSER_MANIFEST = _fixture_manifest(
    filename="parser_matrix.py",
    manifest_id="parser-matrix",
    layer="parser_acceptance_and_diagnostics",
    suite_id="parser.compile",
)
WORKFLOW_MANIFEST = _fixture_manifest(
    filename="module_workflow_surface.py",
    manifest_id="module-workflow-surface",
    layer="module_workflow",
    suite_id="workflow.synthetic",
)
MANIFESTS = (PARSER_MANIFEST, WORKFLOW_MANIFEST)
CASE_RESULTS = [
    _case_result(
        case_id="parser-str-pass",
        manifest_id=PARSER_MANIFEST.manifest_id,
        suite_id=PARSER_MANIFEST.suite_id,
        layer=PARSER_MANIFEST.layer,
        family="parser_literals",
        operation="compile",
        comparison="pass",
        text_model="str",
        cpython_observation=_observation(
            "cpython.re",
            "compile",
            "success",
            result={"pattern": "abc"},
        ),
        rebar_observation=_observation(
            "rebar",
            "compile",
            "success",
            result={"pattern": "abc"},
        ),
    ),
    _case_result(
        case_id="parser-bytes-fail",
        manifest_id=PARSER_MANIFEST.manifest_id,
        suite_id=PARSER_MANIFEST.suite_id,
        layer=PARSER_MANIFEST.layer,
        family="parser_diagnostics",
        operation="compile",
        comparison="fail",
        text_model="bytes",
        cpython_observation=_observation(
            "cpython.re",
            "compile",
            "success",
            warnings=[
                {
                    "category": "FutureWarning",
                    "message": "ambiguous nested set",
                }
            ],
            result={"pattern": "a[b]"},
        ),
        rebar_observation=_observation(
            "rebar",
            "compile",
            "exception",
            warnings=[
                {
                    "category": "RuntimeWarning",
                    "message": "native bridge mismatch",
                }
            ],
            exception={"type": "error", "message": "bad range"},
        ),
    ),
    _case_result(
        case_id="workflow-bytes-unimplemented",
        manifest_id=WORKFLOW_MANIFEST.manifest_id,
        suite_id=WORKFLOW_MANIFEST.suite_id,
        layer=WORKFLOW_MANIFEST.layer,
        family="workflow_search",
        operation="module_call",
        comparison="unimplemented",
        text_model="bytes",
        cpython_observation=_observation(
            "cpython.re",
            "module_call",
            "success",
            result={"matched": True},
        ),
        rebar_observation=_observation(
            "rebar",
            "module_call",
            "unimplemented",
            warnings=[
                {
                    "category": "DeprecationWarning",
                    "message": "temporary shim",
                }
            ],
            exception={"type": "NotImplementedError", "message": "todo"},
        ),
    ),
    _case_result(
        case_id="workflow-str-pass",
        manifest_id=WORKFLOW_MANIFEST.manifest_id,
        suite_id=WORKFLOW_MANIFEST.suite_id,
        layer=WORKFLOW_MANIFEST.layer,
        family="workflow_search",
        operation="pattern_call",
        comparison="pass",
        text_model="str",
        cpython_observation=_observation(
            "cpython.re",
            "pattern_call",
            "success",
            result={"matched": False},
        ),
        rebar_observation=_observation(
            "rebar",
            "pattern_call",
            "success",
            result={"matched": False},
        ),
    ),
]


def test_normalize_match_metadata_preserves_bytes_named_capture_shape() -> None:
    match = re.search(rb"(?P<outer>(ab)?)(?P<inner>c)", b"zabc")

    assert match is not None
    assert normalize_match_metadata(match) == {
        "matched": True,
        "group0": {"encoding": "latin-1", "value": "abc"},
        "groups": [
            {"encoding": "latin-1", "value": "ab"},
            {"encoding": "latin-1", "value": "ab"},
            {"encoding": "latin-1", "value": "c"},
        ],
        "groupdict": {
            "inner": {"encoding": "latin-1", "value": "c"},
            "outer": {"encoding": "latin-1", "value": "ab"},
        },
        "lastgroup": "inner",
        "lastindex": 3,
        "pos": 0,
        "endpos": 4,
        "span": [1, 4],
        "string_type": "bytes",
        "named_groups": {
            "inner": {"encoding": "latin-1", "value": "c"},
            "outer": {"encoding": "latin-1", "value": "ab"},
        },
        "named_group_spans": {
            "inner": [3, 4],
            "outer": [1, 3],
        },
        "group1": {"encoding": "latin-1", "value": "ab"},
        "span1": [1, 3],
        "group_spans": [[1, 3], [1, 3], [3, 4]],
    }


def test_normalize_match_metadata_keeps_missing_optional_named_group_details() -> None:
    match = re.fullmatch(r"(?P<word>a)?b", "b")

    assert match is not None
    assert normalize_match_metadata(match) == {
        "matched": True,
        "group0": "b",
        "groups": [None],
        "groupdict": {"word": None},
        "lastgroup": None,
        "lastindex": None,
        "pos": 0,
        "endpos": 1,
        "span": [0, 1],
        "string_type": "str",
        "named_groups": {"word": None},
        "named_group_spans": {"word": [-1, -1]},
        "group1": None,
        "span1": [-1, -1],
        "group_spans": [[-1, -1]],
    }


def test_normalize_value_exhausts_iterators_and_normalizes_nested_bytes() -> None:
    iterator = iter([b"ab", {"x": (1, b"y")}])

    assert _normalize_value(iterator) == {
        "items": [
            {"encoding": "latin-1", "value": "ab"},
            {"x": [1, {"encoding": "latin-1", "value": "y"}]},
        ],
        "exhausted": True,
    }
    assert next(iterator, None) is None


def test_normalize_warning_and_exception_payloads_preserve_diagnostic_details() -> None:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        warnings.warn("alpha", RuntimeWarning)
        warnings.warn("beta", FutureWarning)

    warning_payload = normalize_warning_records(caught)
    assert warning_payload == [
        {"category": "RuntimeWarning", "message": "alpha"},
        {"category": "FutureWarning", "message": "beta"},
    ]

    try:
        re.compile("(")
    except re.error as exc:
        exception_payload = normalize_exception(exc)
    else:  # pragma: no cover - stdlib compile must raise here.
        raise AssertionError("expected re.compile('(') to raise")

    assert exception_payload["type"] == "error"
    assert "missing )" in exception_payload["message"]
    assert exception_payload["pos"] == 0
    assert exception_payload["lineno"] == 1
    assert exception_payload["colno"] == 1


def test_compare_observations_prefers_unimplemented_result() -> None:
    comparison, mismatch_notes = compare_observations(
        {
            "outcome": "success",
            "warnings": [],
            "result": {"status": "ok"},
            "exception": None,
        },
        {
            "outcome": "unimplemented",
            "warnings": [{"category": "RuntimeWarning", "message": "alpha"}],
            "result": None,
            "exception": {"type": "NotImplementedError", "message": "todo"},
        },
    )

    assert comparison == "unimplemented"
    assert mismatch_notes == ["rebar adapter reports support as unimplemented"]


def test_compare_observations_reports_each_payload_mismatch_in_stable_order() -> None:
    comparison, mismatch_notes = compare_observations(
        {
            "outcome": "success",
            "warnings": [],
            "result": {"status": "ok"},
            "exception": None,
        },
        {
            "outcome": "exception",
            "warnings": [{"category": "RuntimeWarning", "message": "alpha"}],
            "result": {"status": "different"},
            "exception": {"type": "TypeError", "message": "boom"},
        },
    )

    assert comparison == "fail"
    assert mismatch_notes == [
        "outcome mismatch: success != exception",
        "warning payload mismatch",
        "result payload mismatch",
        "exception payload mismatch",
    ]


def test_build_observation_summary_counts_sorted_outcomes_warnings_and_exceptions() -> None:
    observations = [
        {"outcome": "success", "warnings": [], "exception": None},
        {
            "outcome": "exception",
            "warnings": [{"category": "RuntimeWarning", "message": "alpha"}],
            "exception": {"type": "TypeError", "message": "boom"},
        },
        {
            "outcome": "exception",
            "warnings": [{"category": "FutureWarning", "message": "beta"}],
            "exception": {"type": "error", "message": "bad"},
        },
        {
            "outcome": "unimplemented",
            "warnings": [{"category": "RuntimeWarning", "message": "gamma"}],
            "exception": None,
        },
    ]

    assert build_observation_summary(observations) == {
        "outcomes": {
            "exception": 2,
            "success": 1,
            "unimplemented": 1,
        },
        "warning_case_count": 3,
        "exception_case_count": 2,
        "warning_categories": {
            "FutureWarning": 1,
            "RuntimeWarning": 2,
        },
        "exception_types": {
            "TypeError": 1,
            "error": 1,
        },
    }


def test_build_scorecard_aggregates_correctness_summaries_and_suite_fanout() -> None:
    scorecard = build_scorecard(manifests=MANIFESTS, case_results=CASE_RESULTS)

    assert scorecard["schema_version"] == REPORT_SCHEMA_VERSION
    assert scorecard["suite"] == "correctness"
    assert scorecard["phase"] == "phase3-module-workflow-pack"
    assert scorecard["generator"] == "python -m rebar_harness.correctness"
    assert scorecard["generated_at"].endswith("Z")

    assert scorecard["fixtures"] == {
        "manifest_count": 2,
        "manifest_ids": ["parser-matrix", "module-workflow-surface"],
        "paths": [
            "tests/conformance/fixtures/parser_matrix.py",
            "tests/conformance/fixtures/module_workflow_surface.py",
        ],
        "case_count": 4,
    }
    assert scorecard["summary"] == {
        "total_cases": 4,
        "executed_cases": 4,
        "passed_cases": 2,
        "failed_cases": 1,
        "unimplemented_cases": 1,
        "skipped_cases": 0,
    }
    assert scorecard["diagnostics"] == {
        "by_adapter": {
            "cpython": {
                "outcomes": {"success": 4},
                "warning_case_count": 1,
                "exception_case_count": 0,
                "warning_categories": {"FutureWarning": 1},
                "exception_types": {},
            },
            "rebar": {
                "outcomes": {
                    "exception": 1,
                    "success": 2,
                    "unimplemented": 1,
                },
                "warning_case_count": 2,
                "exception_case_count": 2,
                "warning_categories": {
                    "DeprecationWarning": 1,
                    "RuntimeWarning": 1,
                },
                "exception_types": {
                    "NotImplementedError": 1,
                    "error": 1,
                },
            },
        }
    }

    assert scorecard["layers"] == {
        "module_workflow": {
            "manifest_ids": ["module-workflow-surface"],
            "suite_ids": ["workflow.synthetic"],
            "case_count": 2,
            "families": ["workflow_search"],
            "operations": ["module_call", "pattern_call"],
            "text_models": ["bytes", "str"],
            "summary": {
                "total_cases": 2,
                "executed_cases": 2,
                "passed_cases": 1,
                "failed_cases": 0,
                "unimplemented_cases": 1,
                "skipped_cases": 0,
            },
            "diagnostics": {
                "by_adapter": {
                    "cpython": {
                        "outcomes": {"success": 2},
                        "warning_case_count": 0,
                        "exception_case_count": 0,
                        "warning_categories": {},
                        "exception_types": {},
                    },
                    "rebar": {
                        "outcomes": {"success": 1, "unimplemented": 1},
                        "warning_case_count": 1,
                        "exception_case_count": 1,
                        "warning_categories": {"DeprecationWarning": 1},
                        "exception_types": {"NotImplementedError": 1},
                    },
                }
            },
        },
        "parser_acceptance_and_diagnostics": {
            "manifest_ids": ["parser-matrix"],
            "suite_ids": ["parser.compile"],
            "case_count": 2,
            "families": ["parser_diagnostics", "parser_literals"],
            "operations": ["compile"],
            "text_models": ["bytes", "str"],
            "summary": {
                "total_cases": 2,
                "executed_cases": 2,
                "passed_cases": 1,
                "failed_cases": 1,
                "unimplemented_cases": 0,
                "skipped_cases": 0,
            },
            "diagnostics": {
                "by_adapter": {
                    "cpython": {
                        "outcomes": {"success": 2},
                        "warning_case_count": 1,
                        "exception_case_count": 0,
                        "warning_categories": {"FutureWarning": 1},
                        "exception_types": {},
                    },
                    "rebar": {
                        "outcomes": {"exception": 1, "success": 1},
                        "warning_case_count": 1,
                        "exception_case_count": 1,
                        "warning_categories": {"RuntimeWarning": 1},
                        "exception_types": {"error": 1},
                    },
                }
            },
        },
    }

    assert [suite["id"] for suite in scorecard["suites"]] == [
        "parser.compile",
        "parser.compile.bytes",
        "parser.compile.str",
        "workflow.synthetic",
        "workflow.synthetic.bytes",
        "workflow.synthetic.str",
        "workflow.synthetic.module_call",
        "workflow.synthetic.pattern_call",
    ]
    assert scorecard["suites"][0] == {
        "id": "parser.compile",
        "layer": "parser_acceptance_and_diagnostics",
        "manifest_ids": ["parser-matrix"],
        "case_count": 2,
        "families": ["parser_diagnostics", "parser_literals"],
        "operations": ["compile"],
        "text_models": ["bytes", "str"],
        "summary": {
            "total_cases": 2,
            "executed_cases": 2,
            "passed_cases": 1,
            "failed_cases": 1,
            "unimplemented_cases": 0,
            "skipped_cases": 0,
        },
        "diagnostics": scorecard["layers"]["parser_acceptance_and_diagnostics"][
            "diagnostics"
        ],
    }
    assert scorecard["suites"][-1] == {
        "id": "workflow.synthetic.pattern_call",
        "layer": "module_workflow",
        "manifest_ids": ["module-workflow-surface"],
        "case_count": 1,
        "families": ["workflow_search"],
        "operations": ["pattern_call"],
        "text_models": ["str"],
        "summary": {
            "total_cases": 1,
            "executed_cases": 1,
            "passed_cases": 1,
            "failed_cases": 0,
            "unimplemented_cases": 0,
            "skipped_cases": 0,
        },
        "diagnostics": {
            "by_adapter": {
                "cpython": {
                    "outcomes": {"success": 1},
                    "warning_case_count": 0,
                    "exception_case_count": 0,
                    "warning_categories": {},
                    "exception_types": {},
                },
                "rebar": {
                    "outcomes": {"success": 1},
                    "warning_case_count": 0,
                    "exception_case_count": 0,
                    "warning_categories": {},
                    "exception_types": {},
                },
            }
        },
    }

    assert scorecard["families"] == [
        {
            "id": "parser_diagnostics",
            "case_count": 1,
            "layers": ["parser_acceptance_and_diagnostics"],
            "operations": ["compile"],
            "text_models": ["bytes"],
            "summary": {
                "total_cases": 1,
                "executed_cases": 1,
                "passed_cases": 0,
                "failed_cases": 1,
                "unimplemented_cases": 0,
                "skipped_cases": 0,
            },
        },
        {
            "id": "parser_literals",
            "case_count": 1,
            "layers": ["parser_acceptance_and_diagnostics"],
            "operations": ["compile"],
            "text_models": ["str"],
            "summary": {
                "total_cases": 1,
                "executed_cases": 1,
                "passed_cases": 1,
                "failed_cases": 0,
                "unimplemented_cases": 0,
                "skipped_cases": 0,
            },
        },
        {
            "id": "workflow_search",
            "case_count": 2,
            "layers": ["module_workflow"],
            "operations": ["module_call", "pattern_call"],
            "text_models": ["bytes", "str"],
            "summary": {
                "total_cases": 2,
                "executed_cases": 2,
                "passed_cases": 1,
                "failed_cases": 0,
                "unimplemented_cases": 1,
                "skipped_cases": 0,
            },
        },
    ]


def test_build_fixture_summary_exposes_single_manifest_metadata_on_narrow_runs() -> None:
    summary = build_fixture_summary((WORKFLOW_MANIFEST,), CASE_RESULTS[2:])

    assert summary == {
        "manifest_count": 1,
        "manifest_ids": ["module-workflow-surface"],
        "paths": ["tests/conformance/fixtures/module_workflow_surface.py"],
        "case_count": 2,
        "path": "tests/conformance/fixtures/module_workflow_surface.py",
        "schema_version": 1,
        "manifest_id": "module-workflow-surface",
    }
