from __future__ import annotations

import json
import pathlib
import sys
from typing import Any


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"
if str(PYTHON_SOURCE) not in sys.path:
    sys.path.append(str(PYTHON_SOURCE))

from rebar_harness.benchmarks import (
    DEFAULT_MANIFEST_PATHS,
    determine_phase,
    determine_runner_version,
    load_manifests,
    workload_to_payload,
)


BASE_SOURCE_TREE_MANIFEST_IDS = frozenset({"compile-matrix", "regression-matrix"})

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
        "representative_known_gap_workload_ids": ("module-search-ignorecase-ascii-cold-gap",),
        "representative_measured_workload_ids": (),
    },
    "grouped-named-boundary": {
        "known_gap_count": 2,
        "representative_known_gap_workload_ids": ("module-search-grouped-segment-cold-gap",),
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
        "known_gap_count": 2,
        "representative_known_gap_workload_ids": (
            "module-sub-callable-nested-grouped-alternation-cold-gap",
        ),
        "representative_measured_workload_ids": (),
    },
    "nested-group-boundary": {
        "known_gap_count": 2,
        "representative_known_gap_workload_ids": ("module-search-triple-nested-group-cold-gap",),
        "representative_measured_workload_ids": (),
    },
    "nested-group-alternation-boundary": {
        "known_gap_count": 2,
        "representative_known_gap_workload_ids": (
            "module-search-nested-group-quantified-alternation-cold-gap",
        ),
        "representative_measured_workload_ids": (),
    },
    "nested-group-replacement-boundary": {
        "known_gap_count": 1,
        "representative_known_gap_workload_ids": (
            "pattern-subn-template-named-quantified-nested-group-replacement-purged-gap",
        ),
        "representative_measured_workload_ids": (),
    },
    "nested-group-callable-replacement-boundary": {
        "known_gap_count": 2,
        "representative_known_gap_workload_ids": (
            "module-sub-callable-nested-group-alternation-cold-gap",
        ),
        "representative_measured_workload_ids": (),
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
        "representative_known_gap_workload_ids": ("regression-parser-atomic-lookbehind-cold",),
        "representative_measured_workload_ids": (),
    },
}


def manifest_id_for_path(path: pathlib.Path) -> str:
    return path.stem.replace("_", "-")


def relative_manifest_path(path: pathlib.Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def load_manifest_document(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def ordered_operations(workloads: list[dict[str, Any]]) -> list[str]:
    operations: list[str] = []
    for workload in workloads:
        operation = str(workload["operation"])
        if operation not in operations:
            operations.append(operation)
    return operations


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
        (path for path in DEFAULT_MANIFEST_PATHS if manifest_id_for_path(path) == "regression-matrix"),
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
        raise AssertionError(f"target manifest {target_manifest_id!r} is not in DEFAULT_MANIFEST_PATHS")
    if target_manifest_id != "module-boundary":
        if regression_path is None:
            raise AssertionError("DEFAULT_MANIFEST_PATHS is missing regression_matrix.json")
        manifest_paths.append(regression_path)
    return manifest_paths


def expected_summary_for_manifests(
    manifest_documents: list[dict[str, Any]],
) -> tuple[dict[str, int], dict[str, int]]:
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
    summary = {
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
    cache_counts = {
        cache_mode: sum(1 for workload in workloads if workload["cache_mode"] == cache_mode)
        for cache_mode in ("cold", "warm", "purged")
    }
    return summary, cache_counts


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
    manifest_documents = [load_manifest_document(path) for path in manifest_paths]
    _, workloads = load_manifests(list(manifest_paths))
    workload_payloads = [workload_to_payload(workload) for workload in workloads]
    target_manifest = next(
        manifest for manifest in manifest_documents if manifest["manifest_id"] == target_manifest_id
    )
    target_manifest_path = next(
        path for path in manifest_paths if manifest_id_for_path(path) == target_manifest_id
    )
    expected_summary, expected_cache_counts = expected_summary_for_manifests(manifest_documents)
    return {
        "expected_cache_counts": expected_cache_counts,
        "expected_manifest_paths": [relative_manifest_path(path) for path in manifest_paths],
        "expected_phase": determine_phase(workload_payloads),
        "expected_runner_version": determine_runner_version(workload_payloads),
        "expected_summary": expected_summary,
        "manifest_expectation": SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[target_manifest_id],
        "manifest_id": target_manifest_id,
        "manifest_path": relative_manifest_path(target_manifest_path),
        "manifest_paths": manifest_paths,
        "target_manifest": target_manifest,
    }
