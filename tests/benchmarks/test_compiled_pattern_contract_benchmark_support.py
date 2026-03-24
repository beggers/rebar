from __future__ import annotations

from dataclasses import replace

import pytest

from tests.benchmarks import compiled_pattern_contract_benchmark_support as support
from tests.benchmarks.benchmark_test_support import live_manifest_workload


def test_compiled_pattern_contract_shared_excluded_fields_stay_pinned() -> None:
    assert support.COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS == frozenset(
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


@pytest.mark.parametrize(
    ("workload", "expected_calls"),
    (
        pytest.param(
            live_manifest_workload(
                "module_boundary.py",
                "module-search-literal-warm-hit-str-compiled-pattern",
            ),
            [("compile", "abc", 0)],
            id="warm",
        ),
        pytest.param(
            live_manifest_workload(
                "module_boundary.py",
                "module-fullmatch-literal-purged-hit-bytes-compiled-pattern",
            ),
            [("compile", b"abc", 0), ("purge",)],
            id="purged",
        ),
    ),
)
def test_compiled_pattern_contract_expected_build_calls_cover_warm_and_purged_modes(
    workload,
    expected_calls,
) -> None:
    assert support.compiled_pattern_contract_expected_build_calls(
        workload,
        label="support test",
    ) == expected_calls


def test_compiled_pattern_contract_expected_build_calls_rejects_unknown_cache_mode() -> None:
    workload = live_manifest_workload(
        "module_boundary.py",
        "module-search-literal-warm-hit-str-compiled-pattern",
    )
    mutated_workload = replace(workload, cache_mode="cold")

    with pytest.raises(
        AssertionError,
        match="unexpected compiled-pattern support test workload cache mode 'cold'",
    ):
        support.compiled_pattern_contract_expected_build_calls(
            mutated_workload,
            label="support test",
        )
