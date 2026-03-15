from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
from collections.abc import Iterable
from functools import cache
from typing import Any


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"
if str(PYTHON_SOURCE) not in sys.path:
    sys.path.append(str(PYTHON_SOURCE))

from rebar_harness.benchmarks import (
    DEFAULT_MANIFEST_PATHS,
    determine_phase,
    determine_runner_version,
    load_manifest,
    load_manifests,
    select_workloads,
    workload_to_payload,
)


BASE_SOURCE_TREE_MANIFEST_IDS = frozenset({"compile-matrix", "regression-matrix"})

SOURCE_TREE_SCORECARD_EXPECTATIONS: dict[str, dict[str, Any]] = {
    "compile-smoke": {
        "manifest_ids": ("compile-smoke",),
        "selection_mode": "full",
        "expected_summary": {
            "known_gap_count": 1,
            "measured_workloads": 1,
            "module_workloads": 0,
            "parser_workloads": 2,
            "regression_workloads": 0,
            "total_workloads": 2,
        },
        "expected_first_deferred": {
            "area": "module-boundary",
            "follow_up": "RBR-0015",
        },
        "manifest_expectations": {
            "compile-smoke": {
                "known_gap_count": 1,
            },
        },
        "representative_measured_workload_ids": ("compile-literal-cold",),
        "representative_known_gap_workload_ids": ("compile-character-class-warm",),
    },
    "compile-matrix": {
        "manifest_ids": ("compile-matrix",),
        "selection_mode": "full",
        "expected_summary": {
            "known_gap_count": 1,
            "measured_workloads": 5,
            "module_workloads": 0,
            "parser_workloads": 6,
            "regression_workloads": 0,
            "total_workloads": 6,
        },
        "expected_first_deferred": {
            "area": "module-boundary",
            "follow_up": "RBR-0015",
        },
        "manifest_expectations": {
            "compile-matrix": {
                "known_gap_count": 1,
            },
        },
        "representative_measured_workload_ids": (
            "compile-inline-locale-bytes-warm",
            "compile-lookbehind-cold",
            "compile-atomic-group-purged",
        ),
        "representative_known_gap_workload_ids": ("compile-parser-stress-cold",),
        "workload_note_substrings": {
            "compile-parser-stress-cold": "outside the current rebar compile surface",
        },
    },
    "post-parser-workflows": {
        "manifest_ids": (
            "module-boundary",
            "collection-replacement-boundary",
            "literal-flag-boundary",
        ),
        "selection_mode": "full",
        "expected_summary": {
            "known_gap_count": 5,
            "measured_workloads": 23,
            "module_workloads": 28,
            "parser_workloads": 0,
            "regression_workloads": 0,
            "total_workloads": 28,
        },
        "manifest_expectations": {
            "module-boundary": {
                "known_gap_count": 3,
            },
            "collection-replacement-boundary": {
                "known_gap_count": 0,
            },
            "literal-flag-boundary": {
                "known_gap_count": 2,
            },
        },
        "representative_measured_workload_ids": (
            "module-search-grouped-literal-cold-hit",
            "module-findall-single-dot-warm-str",
            "module-sub-template-warm-str",
            "pattern-subn-grouped-template-warm-str",
            "module-search-inline-flag-warm-str-hit",
            "pattern-search-inline-flag-warm-str-hit",
            "module-search-locale-purged-bytes-hit",
            "pattern-search-locale-purged-bytes-hit",
        ),
        "representative_known_gap_workload_ids": (
            "module-search-ignorecase-ascii-cold-gap",
            "pattern-search-ignorecase-ascii-warm-gap",
        ),
    },
    "regression-pack-full": {
        "manifest_ids": (
            "compile-matrix",
            "module-boundary",
            "regression-matrix",
        ),
        "selection_mode": "full",
        "expected_summary": {
            "known_gap_count": 7,
            "measured_workloads": 12,
            "module_workloads": 11,
            "parser_workloads": 8,
            "regression_workloads": 5,
            "total_workloads": 19,
        },
        "manifest_expectations": {
            "compile-matrix": {
                "known_gap_count": 1,
            },
            "module-boundary": {
                "known_gap_count": 3,
            },
            "regression-matrix": {
                "known_gap_count": 3,
            },
        },
        "representative_measured_workload_ids": (
            "compile-inline-locale-bytes-warm",
            "regression-import-cold",
            "regression-module-search-bytes-cold-miss",
        ),
        "representative_known_gap_workload_ids": (
            "regression-parser-bytes-backreference-purged",
        ),
    },
    "regression-pack-smoke": {
        "manifest_ids": ("regression-matrix",),
        "selection_mode": "smoke",
        "expected_summary": {
            "known_gap_count": 1,
            "measured_workloads": 1,
            "module_workloads": 1,
            "parser_workloads": 1,
            "regression_workloads": 2,
            "total_workloads": 2,
        },
        "expected_workload_order": (
            "regression-import-cold",
            "regression-parser-atomic-lookbehind-cold",
        ),
        "manifest_expectations": {
            "regression-matrix": {
                "known_gap_count": 1,
            },
        },
        "representative_measured_workload_ids": ("regression-import-cold",),
        "representative_known_gap_workload_ids": (
            "regression-parser-atomic-lookbehind-cold",
        ),
    },
}

SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS = {
    "compile-matrix": {
        "known_gap_count": 1,
        "representative_known_gap_workload_ids": ("compile-parser-stress-cold",),
        "representative_measured_workload_ids": (),
    },
    "module-boundary": {
        "known_gap_count": 3,
        "representative_known_gap_workload_ids": ("module-compile-literal-cold",),
        "representative_measured_workload_ids": (
            "import-module-cold",
            "module-search-grouped-literal-cold-hit",
            "module-search-literal-warm-hit",
            "module-search-bytes-cold-miss",
        ),
    },
    "pattern-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (
            "pattern-search-literal-warm-hit",
            "pattern-fullmatch-bytes-purged-hit",
        ),
    },
    "collection-replacement-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (),
    },
    "literal-flag-boundary": {
        "known_gap_count": 2,
        "representative_known_gap_workload_ids": (
            "module-search-ignorecase-ascii-cold-gap",
        ),
        "representative_measured_workload_ids": (),
    },
    "grouped-named-boundary": {
        "known_gap_count": 2,
        "representative_known_gap_workload_ids": (
            "module-search-grouped-segment-cold-gap",
        ),
        "representative_measured_workload_ids": (),
    },
    "numbered-backreference-boundary": {
        "known_gap_count": 2,
        "representative_known_gap_workload_ids": (
            "module-search-numbered-backreference-segment-cold-gap",
        ),
        "representative_measured_workload_ids": (),
    },
    "grouped-segment-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (),
    },
    "literal-alternation-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (),
    },
    "grouped-alternation-boundary": {
        "known_gap_count": 2,
        "representative_known_gap_workload_ids": (
            "module-sub-template-nested-grouped-alternation-warm-gap",
        ),
        "representative_measured_workload_ids": (),
    },
    "grouped-alternation-replacement-boundary": {
        "known_gap_count": 2,
        "representative_known_gap_workload_ids": (
            "module-sub-template-nested-grouped-alternation-cold-gap",
        ),
        "representative_measured_workload_ids": (),
    },
    "grouped-alternation-callable-replacement-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (
            "module-sub-callable-nested-grouped-alternation-cold-gap",
            "pattern-subn-callable-named-nested-grouped-alternation-purged-gap",
        ),
    },
    "nested-group-boundary": {
        "known_gap_count": 2,
        "representative_known_gap_workload_ids": (
            "module-search-triple-nested-group-cold-gap",
        ),
        "representative_measured_workload_ids": (),
    },
    "nested-group-alternation-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (
            "module-search-nested-group-quantified-alternation-cold-gap",
            "pattern-fullmatch-numbered-quantified-nested-group-alternation-repeated-mixed-purged-str",
            "module-search-named-quantified-nested-group-alternation-lower-bound-c-warm-str",
            "pattern-fullmatch-named-quantified-nested-group-alternation-repeated-mixed-purged-str",
            "module-search-numbered-nested-group-branch-local-backreference-b-branch-warm-str",
            "module-compile-named-nested-group-branch-local-backreference-warm-str",
            "pattern-fullmatch-named-nested-group-branch-local-backreference-purged-gap",
            "module-search-numbered-quantified-nested-group-branch-local-backreference-lower-bound-b-branch-warm-str",
            "module-compile-named-quantified-nested-group-branch-local-backreference-warm-str",
            "pattern-fullmatch-named-quantified-nested-group-branch-local-backreference-repeated-mixed-purged-str",
            "module-search-numbered-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-lower-bound-b-branch-warm-str",
            "module-compile-named-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-warm-str",
            "pattern-fullmatch-named-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-upper-bound-all-c-purged-str",
        ),
    },
    "nested-group-replacement-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (
            "module-sub-template-numbered-quantified-nested-group-replacement-lower-bound-warm-str",
            "module-subn-template-numbered-quantified-nested-group-replacement-first-match-only-warm-str",
            "pattern-sub-template-named-quantified-nested-group-replacement-repeated-outer-purged-str",
            "pattern-subn-template-named-quantified-nested-group-replacement-purged-gap",
        ),
    },
    "nested-group-callable-replacement-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (
            "module-sub-callable-nested-group-alternation-cold-gap",
            "pattern-subn-callable-numbered-nested-group-alternation-c-branch-first-match-only-purged-str",
            "module-sub-callable-named-nested-group-alternation-c-branch-warm-str",
            "pattern-subn-callable-named-nested-group-alternation-b-branch-first-match-only-purged-str",
            "module-sub-callable-numbered-quantified-nested-group-lower-bound-warm-str",
            "module-subn-callable-numbered-quantified-nested-group-first-match-only-warm-str",
            "pattern-sub-callable-named-quantified-nested-group-repeated-outer-purged-str",
            "pattern-subn-callable-named-quantified-nested-group-purged-gap",
        ),
    },
    "branch-local-backreference-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (),
    },
    "optional-group-boundary": {
        "known_gap_count": 1,
        "representative_known_gap_workload_ids": (
            "module-search-numbered-optional-group-conditional-cold-gap",
        ),
        "representative_measured_workload_ids": (),
    },
    "exact-repeat-quantified-group-boundary": {
        "known_gap_count": 1,
        "representative_known_gap_workload_ids": (
            "module-search-numbered-broader-ranged-repeat-group-cold-gap",
        ),
        "representative_measured_workload_ids": (),
    },
    "ranged-repeat-quantified-group-boundary": {
        "known_gap_count": 1,
        "representative_known_gap_workload_ids": (
            "module-search-numbered-ranged-repeat-group-wider-range-cold-gap",
        ),
        "representative_measured_workload_ids": (),
    },
    "wider-ranged-repeat-quantified-group-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (
            "module-search-numbered-wider-ranged-repeat-group-broader-range-cold-gap",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-broader-range-third-repetition-mixed-purged-str",
            "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-upper-bound-mixed-purged-str",
            "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-absent-warm-str",
            "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-lower-bound-bc-warm-str",
            "module-search-named-wider-ranged-repeat-group-nested-broader-range-conditional-lower-bound-de-warm-str",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-mixed-purged-str",
            "pattern-fullmatch-named-wider-ranged-repeat-group-nested-broader-range-conditional-upper-bound-all-de-purged-str",
            "module-search-numbered-wider-ranged-repeat-group-broader-range-conditional-absent-warm-str",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-broader-range-conditional-lower-bound-bc-purged-str",
            "module-search-named-wider-ranged-repeat-group-broader-range-conditional-upper-bound-mixed-warm-str",
            "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-conditional-upper-bound-mixed-purged-str",
            "module-search-numbered-wider-ranged-repeat-group-open-ended-lower-bound-bc-warm-str",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-open-ended-purged-gap",
            "pattern-fullmatch-named-wider-ranged-repeat-group-open-ended-fourth-repetition-de-purged-str",
        ),
    },
    "open-ended-quantified-group-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (
            "module-search-numbered-open-ended-group-broader-range-cold-gap",
            "module-search-numbered-open-ended-group-broader-range-conditional-warm-gap",
            "pattern-fullmatch-named-open-ended-group-broader-range-backtracking-heavy-purged-str",
        ),
    },
    "quantified-alternation-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (),
    },
    "optional-group-alternation-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (),
    },
    "conditional-group-exists-boundary": {
        "known_gap_count": 2,
        "representative_known_gap_workload_ids": (
            "module-sub-template-numbered-conditional-group-exists-replacement-warm-gap",
        ),
        "representative_measured_workload_ids": (),
    },
    "conditional-group-exists-no-else-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (),
    },
    "conditional-group-exists-empty-else-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (),
    },
    "conditional-group-exists-empty-yes-else-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (),
    },
    "conditional-group-exists-fully-empty-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (),
    },
    "regression-matrix": {
        "known_gap_count": 3,
        "representative_known_gap_workload_ids": (
            "regression-parser-atomic-lookbehind-cold",
        ),
        "representative_measured_workload_ids": (),
    },
}


def _compile_smoke_manifest_path() -> pathlib.Path:
    return DEFAULT_MANIFEST_PATHS[0].with_name("compile_smoke.py")


@cache
def _source_tree_manifest_records() -> dict[str, tuple[pathlib.Path, dict[str, Any]]]:
    records: dict[str, tuple[pathlib.Path, dict[str, Any]]] = {}
    for path in (_compile_smoke_manifest_path(), *DEFAULT_MANIFEST_PATHS):
        raw_manifest, _ = load_manifest(path)
        manifest_id = str(raw_manifest["manifest_id"])
        if manifest_id in records:
            raise AssertionError(f"duplicate benchmark manifest id {manifest_id!r}")
        records[manifest_id] = (path, raw_manifest)
    return records


def manifest_id_for_path(path: pathlib.Path) -> str:
    resolved_path = path.resolve()
    for manifest_id, (manifest_path, _) in _source_tree_manifest_records().items():
        if manifest_path.resolve() == resolved_path:
            return manifest_id
    raise AssertionError(f"unknown benchmark manifest path {path}")


def manifest_path_for_id(manifest_id: str) -> pathlib.Path:
    try:
        return _source_tree_manifest_records()[manifest_id][0]
    except KeyError as exc:
        raise AssertionError(f"unknown benchmark manifest id {manifest_id!r}") from exc


def manifest_document_for_id(manifest_id: str) -> dict[str, Any]:
    try:
        return _source_tree_manifest_records()[manifest_id][1]
    except KeyError as exc:
        raise AssertionError(f"unknown benchmark manifest id {manifest_id!r}") from exc


def relative_manifest_path(path: pathlib.Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def run_source_tree_benchmark_scorecard(
    manifest_paths: Iterable[pathlib.Path],
    *,
    smoke: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    with tempfile.TemporaryDirectory() as temp_dir:
        report_path = pathlib.Path(temp_dir) / "benchmarks.json"
        command = [sys.executable, "-m", "rebar_harness.benchmarks"]
        for manifest_path in manifest_paths:
            command.extend(("--manifest", str(manifest_path)))
        if smoke:
            command.append("--smoke")
        command.extend(("--report", str(report_path)))

        result = subprocess.run(
            command,
            check=True,
            cwd=REPO_ROOT,
            env={"PYTHONPATH": str(PYTHON_SOURCE)},
            capture_output=True,
            text=True,
        )
        summary = json.loads(result.stdout.strip())
        scorecard = json.loads(report_path.read_text(encoding="utf-8"))

    return summary, scorecard


def ordered_operations(workloads: list[dict[str, Any]]) -> list[str]:
    operations: list[str] = []
    for workload in workloads:
        operation = str(workload["operation"])
        if operation not in operations:
            operations.append(operation)
    return operations


def source_tree_scorecard_case_ids() -> tuple[str, ...]:
    return tuple(SOURCE_TREE_SCORECARD_EXPECTATIONS)


def source_tree_scorecard_case(case_id: str) -> dict[str, Any]:
    if case_id not in SOURCE_TREE_SCORECARD_EXPECTATIONS:
        raise AssertionError(f"unknown source-tree scorecard case {case_id!r}")

    case_definition = SOURCE_TREE_SCORECARD_EXPECTATIONS[case_id]
    manifest_ids = tuple(case_definition["manifest_ids"])
    manifest_paths = [manifest_path_for_id(manifest_id) for manifest_id in manifest_ids]
    raw_manifests, manifest_workloads = load_manifests(manifest_paths)
    selected_workloads = select_workloads(
        manifest_workloads,
        smoke_only=case_definition["selection_mode"] == "smoke",
    )
    workload_payloads = [
        workload_to_payload(workload)
        for workload in selected_workloads
    ]

    return {
        **case_definition,
        "case_id": case_id,
        "expected_adapter": (
            "rebar.module-surface"
            if any(workload.family == "module" for workload in selected_workloads)
            else "rebar.compile"
        ),
        "expected_manifest_paths": [
            relative_manifest_path(path) for path in manifest_paths
        ],
        "expected_phase": determine_phase(workload_payloads),
        "expected_runner_version": determine_runner_version(workload_payloads),
        "manifest_documents": raw_manifests,
        "manifest_documents_by_id": {
            str(raw_manifest["manifest_id"]): raw_manifest for raw_manifest in raw_manifests
        },
        "manifest_paths": manifest_paths,
        "manifest_paths_by_id": {
            manifest_id: relative_manifest_path(manifest_path_for_id(manifest_id))
            for manifest_id in manifest_ids
        },
        "selected_workload_ids_by_manifest": {
            manifest_id: tuple(
                workload.workload_id
                for workload in selected_workloads
                if workload.manifest_id == manifest_id
            )
            for manifest_id in manifest_ids
        },
    }


def source_tree_combined_target_manifest_ids() -> tuple[str, ...]:
    target_manifest_ids = tuple(
        manifest_id_for_path(path)
        for path in DEFAULT_MANIFEST_PATHS
        if manifest_id_for_path(path) not in BASE_SOURCE_TREE_MANIFEST_IDS
    )
    target_ids = set(target_manifest_ids)
    missing_expectations = target_ids - set(SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS)
    if missing_expectations:
        raise AssertionError(
            "source-tree combined manifest expectations drifted from DEFAULT_MANIFEST_PATHS: "
            f"missing {sorted(missing_expectations)}"
        )
    return target_manifest_ids


def selected_manifest_paths_for_target_manifest(target_manifest_id: str) -> list[pathlib.Path]:
    manifest_paths: list[pathlib.Path] = []
    regression_path = next(
        (
            path
            for path in DEFAULT_MANIFEST_PATHS
            if manifest_id_for_path(path) == "regression-matrix"
        ),
        None,
    )
    for path in DEFAULT_MANIFEST_PATHS:
        manifest_id = manifest_id_for_path(path)
        if manifest_id == "regression-matrix":
            continue
        manifest_paths.append(path)
        if manifest_id == target_manifest_id:
            break
    else:
        raise AssertionError(
            f"target manifest {target_manifest_id!r} is not in DEFAULT_MANIFEST_PATHS"
        )
    if target_manifest_id != "module-boundary":
        if regression_path is None:
            raise AssertionError("DEFAULT_MANIFEST_PATHS is missing the regression-matrix manifest")
        manifest_paths.append(regression_path)
    return manifest_paths


def expected_summary_for_manifests(
    manifest_documents: list[dict[str, Any]],
) -> dict[str, int]:
    workloads = [
        workload
        for manifest in manifest_documents
        for workload in manifest["workloads"]
    ]
    known_gap_count = sum(
        SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[str(manifest["manifest_id"])]["known_gap_count"]
        for manifest in manifest_documents
        if str(manifest["manifest_id"]) in SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS
    )
    return {
        "known_gap_count": known_gap_count,
        "measured_workloads": len(workloads) - known_gap_count,
        "module_workloads": sum(1 for workload in workloads if workload["family"] == "module"),
        "parser_workloads": sum(1 for workload in workloads if workload["family"] == "parser"),
        "regression_workloads": sum(
            len(manifest["workloads"])
            for manifest in manifest_documents
            if manifest["manifest_id"] == "regression-matrix"
        ),
        "total_workloads": len(workloads),
    }


def representative_measured_workload_ids(
    scorecard: dict[str, Any],
    manifest_document: dict[str, Any],
    *,
    extra_workload_ids: tuple[str, ...] = (),
) -> list[str]:
    manifest_id = str(manifest_document["manifest_id"])
    representative_ids = list(extra_workload_ids)
    for operation in ordered_operations(manifest_document["workloads"]):
        for workload in scorecard["workloads"]:
            if workload["manifest_id"] != manifest_id:
                continue
            if workload["operation"] != operation or workload["status"] != "measured":
                continue
            workload_id = str(workload["id"])
            if workload_id not in representative_ids:
                representative_ids.append(workload_id)
            break
    return representative_ids


def source_tree_combined_case(target_manifest_id: str) -> dict[str, Any]:
    manifest_paths = selected_manifest_paths_for_target_manifest(target_manifest_id)
    raw_manifests, workloads = load_manifests(list(manifest_paths))
    workload_payloads = [workload_to_payload(workload) for workload in workloads]
    target_manifest = next(
        manifest for manifest in raw_manifests if manifest["manifest_id"] == target_manifest_id
    )
    return {
        "expected_adapter": (
            "rebar.module-surface"
            if any(workload.family == "module" for workload in workloads)
            else "rebar.compile"
        ),
        "expected_manifest_paths": [relative_manifest_path(path) for path in manifest_paths],
        "expected_phase": determine_phase(workload_payloads),
        "expected_runner_version": determine_runner_version(workload_payloads),
        "expected_summary": expected_summary_for_manifests(raw_manifests),
        "manifest_documents": raw_manifests,
        "manifest_documents_by_id": {
            str(raw_manifest["manifest_id"]): raw_manifest for raw_manifest in raw_manifests
        },
        "manifest_expectation": SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[target_manifest_id],
        "manifest_id": target_manifest_id,
        "manifest_path": relative_manifest_path(manifest_path_for_id(target_manifest_id)),
        "manifest_paths": manifest_paths,
        "manifest_paths_by_id": {
            str(raw_manifest["manifest_id"]): relative_manifest_path(path)
            for path, raw_manifest in zip(manifest_paths, raw_manifests, strict=True)
        },
        "selected_workload_ids_by_manifest": {
            str(raw_manifest["manifest_id"]): tuple(
                workload.workload_id
                for workload in workloads
                if workload.manifest_id == str(raw_manifest["manifest_id"])
            )
            for raw_manifest in raw_manifests
        },
        "selection_mode": "full",
        "target_manifest": target_manifest,
    }
