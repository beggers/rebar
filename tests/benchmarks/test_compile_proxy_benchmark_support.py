from __future__ import annotations

from tests.benchmarks import benchmark_test_support as benchmark_support
from tests.benchmarks import compile_proxy_benchmark_support as support
from tests.benchmarks import standard_benchmark_anchor_support as standard_support
from tests.benchmarks.source_tree_benchmark_anchor_support import (
    _definition_anchor_expectations,
)


def test_compile_proxy_standard_definition_export_is_lazy_cached_and_owner_built() -> None:
    assert "COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS" not in vars(support)

    first_export = getattr(support, "COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS")
    second_export = getattr(support, "COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS")

    assert first_export is second_export
    assert first_export is support._build_compile_proxy_standard_benchmark_definitions()
    assert len(first_export) == 1
    assert first_export[0].name == "compile-proxy"
    assert "COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS" not in vars(support)


def test_compile_proxy_standard_definition_preserves_manifest_order_and_anchor_mapping(
) -> None:
    definition = support.COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS[0]

    assert definition.manifest_paths == (
        standard_support.COMPILE_MATRIX_MANIFEST_PATH,
        standard_support.REGRESSION_MATRIX_MANIFEST_PATH,
    )
    assert definition.expected_anchor_case_ids == (
        _definition_anchor_expectations(
            standard_support.COMPILE_MATRIX_MANIFEST_PATH,
            {
                "compile-inline-locale-bytes-warm": (
                    "bytes-inline-locale-flag-success",
                ),
                "compile-lookbehind-cold": (
                    "str-fixed-width-lookbehind-success",
                ),
                "compile-character-class-ignorecase-warm": (
                    "str-character-class-ignorecase-success",
                ),
                "compile-possessive-quantifier-cold": (
                    "str-possessive-quantifier-success",
                ),
                "compile-atomic-group-purged": (
                    "str-atomic-group-success",
                ),
                "compile-parser-stress-cold": (
                    "str-parser-stress-compile-proxy-success",
                ),
            },
        )
        | _definition_anchor_expectations(
            standard_support.REGRESSION_MATRIX_MANIFEST_PATH,
            {
                "regression-parser-atomic-lookbehind-cold": (
                    "str-parser-stress-compile-proxy-success",
                ),
                "regression-parser-bytes-backreference-purged": (
                    "bytes-named-backreference-compile-proxy-success",
                ),
                "regression-module-compile-verbose-purged": (
                    "workflow-compile-str-verbose-regression",
                ),
                "regression-module-compile-multiline-purged": (
                    "workflow-compile-str-multiline-regression",
                ),
                "regression-module-compile-multiline-purged-bytes": (
                    "workflow-compile-bytes-multiline-regression",
                ),
                "regression-module-compile-verbose-purged-bytes": (
                    "workflow-compile-bytes-verbose-regression",
                ),
            },
        )
    )


def test_compile_proxy_standard_definition_reuses_compile_proxy_helper_functions() -> None:
    definition = support.COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS[0]

    assert definition.include_workload is benchmark_support.is_compile_proxy_workload
    assert (
        definition.correctness_case_signature
        is benchmark_support.compile_proxy_correctness_case_signature
    )
    assert (
        definition.workload_signature
        is benchmark_support.compile_proxy_workload_signature
    )
