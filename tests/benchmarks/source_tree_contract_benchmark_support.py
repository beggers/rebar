from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import pathlib
from typing import Any

from rebar_harness.benchmarks import (
    Workload,
    workload_from_payload,
    workload_to_payload,
)
from tests.benchmarks.source_tree_benchmark_anchor_support import (
    _selected_manifest_workloads,
)

COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS = frozenset(
    {
        "manifest_id",
        "workload_id",
        "warmup_iterations",
        "sample_iterations",
        "timed_samples",
        "notes",
        "smoke",
    }
)


@dataclass(frozen=True, slots=True)
class _SourceTreeContractBuilderSpec:
    manifest_id: str
    excluded_fields: frozenset[str]
    manifest_timed_samples: int = 2
    timing_scope: str | None = None
    notes: tuple[str, ...] = ()


def _source_tree_contract_manifest_payload(
    source_workload: Workload,
    *,
    spec: _SourceTreeContractBuilderSpec,
) -> dict[str, object]:
    payload = workload_to_payload(source_workload)
    manifest_payload: dict[str, object] = {
        "id": f"{source_workload.workload_id}-contract",
        **{
            key: value
            for key, value in payload.items()
            if key not in spec.excluded_fields
        },
    }
    if spec.timing_scope is not None:
        manifest_payload["timing_scope"] = spec.timing_scope
    if spec.notes:
        manifest_payload["notes"] = list(spec.notes)
    return manifest_payload


def _source_tree_contract_workload(
    source_workload: Workload,
    *,
    spec: _SourceTreeContractBuilderSpec,
) -> Workload:
    manifest_payload = _source_tree_contract_manifest_payload(
        source_workload,
        spec=spec,
    )
    return workload_from_payload(
        {
            "manifest_id": spec.manifest_id,
            "workload_id": str(manifest_payload["id"]),
            **{key: value for key, value in manifest_payload.items() if key != "id"},
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
            "categories": [],
            "syntax_features": [],
            "smoke": False,
        }
    )


def _source_tree_contract_manifest(
    source_workloads: tuple[Workload, ...],
    *,
    spec: _SourceTreeContractBuilderSpec,
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "manifest_id": spec.manifest_id,
        "defaults": {
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": spec.manifest_timed_samples,
        },
        "workloads": [
            _source_tree_contract_manifest_payload(workload, spec=spec)
            for workload in source_workloads
        ],
    }


def _contract_source_workloads(
    *,
    manifest_path: pathlib.Path,
    include_workload_selectors: tuple[Callable[[Any], bool], ...],
    expected_source_workload_ids: tuple[str, ...],
    drift_message: str,
) -> tuple[Workload, ...]:
    source_workloads = tuple(
        workload
        for include_workload in include_workload_selectors
        for workload in _selected_manifest_workloads(
            manifest_path,
            include_workload=include_workload,
        )
    )
    if (
        tuple(workload.workload_id for workload in source_workloads)
        != expected_source_workload_ids
    ):
        raise AssertionError(drift_message)
    return source_workloads


def compiled_pattern_contract_expected_build_calls(
    source_workload: Workload,
    *,
    label: str,
) -> list[tuple[object, ...]]:
    compile_call = ("compile", source_workload.pattern_payload(), source_workload.flags)
    if source_workload.cache_mode == "purged":
        return [compile_call, ("purge",)]
    if source_workload.cache_mode == "warm":
        return [compile_call]
    raise AssertionError(
        f"unexpected compiled-pattern {label} workload cache mode "
        f"{source_workload.cache_mode!r}"
    )
