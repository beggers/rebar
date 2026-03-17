from __future__ import annotations

from rebar_harness.correctness import (
    REPO_ROOT,
    REPORT_SCHEMA_VERSION,
    FixtureManifest,
    build_fixture_summary,
    build_scorecard,
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
