from __future__ import annotations

import pathlib

import pytest

from rebar_harness.benchmarks import (
    BENCHMARK_WORKLOADS_ROOT,
    load_manifest,
    workload_to_payload,
)
from tests.benchmarks import source_tree_contract_benchmark_support as support

_COLLECTION_REPLACEMENT_MANIFEST_PATH = (
    BENCHMARK_WORKLOADS_ROOT / "collection_replacement_boundary.py"
)


def _manifest_workload_by_id(
    manifest_path: pathlib.Path,
    workload_id: str,
):
    workloads_by_id = {
        workload.workload_id: workload
        for workload in load_manifest(manifest_path).workloads
    }
    return workloads_by_id[workload_id]


def test_source_tree_contract_manifest_payload_drops_fields_and_injects_metadata() -> None:
    source_workload = _manifest_workload_by_id(
        _COLLECTION_REPLACEMENT_MANIFEST_PATH,
        "module-sub-count-keyword-warm-str-compiled-pattern",
    )
    source_payload = workload_to_payload(source_workload)
    spec = support._SourceTreeContractBuilderSpec(
        manifest_id="collection-replacement-boundary",
        excluded_fields=frozenset(
            {
                "manifest_id",
                "workload_id",
                "warmup_iterations",
                "sample_iterations",
                "timed_samples",
                "notes",
            }
        ),
        timing_scope="module-helper-call",
        notes=("keeps helper invocation unresolved",),
    )

    payload = support._source_tree_contract_manifest_payload(
        source_workload,
        spec=spec,
    )

    assert payload["id"] == (
        "module-sub-count-keyword-warm-str-compiled-pattern-contract"
    )
    assert payload["pattern"] == source_payload["pattern"]
    assert payload["kwargs"] == source_payload["kwargs"]
    assert payload["timing_scope"] == "module-helper-call"
    assert payload["notes"] == ["keeps helper invocation unresolved"]
    for field_name in spec.excluded_fields - {"notes"}:
        assert field_name not in payload


def test_source_tree_contract_workload_reconstructs_contract_workload_with_defaults() -> None:
    source_workload = _manifest_workload_by_id(
        _COLLECTION_REPLACEMENT_MANIFEST_PATH,
        "module-subn-count-keyword-purged-bytes-compiled-pattern",
    )
    spec = support._SourceTreeContractBuilderSpec(
        manifest_id="collection-replacement-boundary",
        excluded_fields=frozenset(
            {
                "manifest_id",
                "workload_id",
                "warmup_iterations",
                "sample_iterations",
                "timed_samples",
                "notes",
            }
        ),
        timing_scope="module-helper-call",
        notes=("contract workload",),
    )

    workload = support._source_tree_contract_workload(source_workload, spec=spec)
    payload = workload_to_payload(workload)

    assert payload["manifest_id"] == "collection-replacement-boundary"
    assert payload["workload_id"] == (
        "module-subn-count-keyword-purged-bytes-compiled-pattern-contract"
    )
    assert payload["warmup_iterations"] == 1
    assert payload["sample_iterations"] == 1
    assert payload["timed_samples"] == 1
    assert payload["categories"] == []
    assert payload["syntax_features"] == []
    assert payload["smoke"] is False
    assert payload["timing_scope"] == "module-helper-call"
    assert payload["notes"] == ["contract workload"]


def test_source_tree_contract_manifest_uses_manifest_defaults_and_contract_ids() -> None:
    source_workloads = (
        _manifest_workload_by_id(
            _COLLECTION_REPLACEMENT_MANIFEST_PATH,
            "module-findall-literal-purged-bytes-compiled-pattern",
        ),
        _manifest_workload_by_id(
            _COLLECTION_REPLACEMENT_MANIFEST_PATH,
            "module-sub-literal-warm-str-compiled-pattern",
        ),
    )
    spec = support._SourceTreeContractBuilderSpec(
        manifest_id="collection-replacement-boundary",
        excluded_fields=frozenset({"manifest_id", "workload_id"}),
        manifest_timed_samples=7,
    )

    manifest = support._source_tree_contract_manifest(source_workloads, spec=spec)

    assert manifest["schema_version"] == 1
    assert manifest["manifest_id"] == "collection-replacement-boundary"
    assert manifest["defaults"] == {
        "warmup_iterations": 1,
        "sample_iterations": 1,
        "timed_samples": 7,
    }
    assert [workload["id"] for workload in manifest["workloads"]] == [
        "module-findall-literal-purged-bytes-compiled-pattern-contract",
        "module-sub-literal-warm-str-compiled-pattern-contract",
    ]


def test_contract_source_workloads_follow_selector_order_on_live_manifest_rows() -> None:
    source_workloads = support._contract_source_workloads(
        manifest_path=_COLLECTION_REPLACEMENT_MANIFEST_PATH,
        include_workload_selectors=(
            lambda workload: workload.workload_id
            in {
                "module-sub-count-keyword-warm-str-compiled-pattern",
                "module-subn-count-keyword-purged-bytes-compiled-pattern",
            },
            lambda workload: workload.workload_id
            == "module-split-maxsplit-keyword-purged-str-compiled-pattern",
        ),
        expected_source_workload_ids=(
            "module-sub-count-keyword-warm-str-compiled-pattern",
            "module-subn-count-keyword-purged-bytes-compiled-pattern",
            "module-split-maxsplit-keyword-purged-str-compiled-pattern",
        ),
        drift_message="source workloads drifted",
    )

    assert tuple(workload.workload_id for workload in source_workloads) == (
        "module-sub-count-keyword-warm-str-compiled-pattern",
        "module-subn-count-keyword-purged-bytes-compiled-pattern",
        "module-split-maxsplit-keyword-purged-str-compiled-pattern",
    )


def test_contract_source_workloads_detect_drift_on_live_manifest_rows() -> None:
    with pytest.raises(AssertionError, match="source workloads drifted"):
        support._contract_source_workloads(
            manifest_path=_COLLECTION_REPLACEMENT_MANIFEST_PATH,
            include_workload_selectors=(
                lambda workload: workload.workload_id
                == "module-sub-count-keyword-warm-str-compiled-pattern",
            ),
            expected_source_workload_ids=(
                "module-split-maxsplit-keyword-purged-str-compiled-pattern",
            ),
            drift_message="source workloads drifted",
        )
