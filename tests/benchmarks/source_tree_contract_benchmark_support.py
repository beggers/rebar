from __future__ import annotations

from rebar_harness.benchmarks import Workload
from tests.benchmarks.benchmark_test_support import (
    _SourceTreeContractBuilderSpec,
    _contract_source_workloads,
    _source_tree_contract_manifest,
    _source_tree_contract_manifest_payload,
    _source_tree_contract_workload,
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
