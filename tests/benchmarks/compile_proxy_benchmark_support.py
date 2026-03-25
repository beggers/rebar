from __future__ import annotations

from functools import cache
from typing import TYPE_CHECKING, Any

from tests.benchmarks.benchmark_test_support import (
    compile_proxy_correctness_case_signature,
    compile_proxy_workload_signature,
    is_compile_proxy_workload,
)
from tests.benchmarks.source_tree_benchmark_anchor_support import (
    _definition_anchor_expectations,
)
from tests.conftest import REPO_ROOT

if TYPE_CHECKING:
    from tests.benchmarks.standard_benchmark_anchor_support import (
        StandardBenchmarkAnchorContractDefinition,
    )


COMPILE_MATRIX_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "compile_matrix.py"
REGRESSION_MATRIX_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "regression_matrix.py"
)


@cache
def _build_compile_proxy_standard_benchmark_definitions(
) -> tuple[StandardBenchmarkAnchorContractDefinition, ...]:
    from tests.benchmarks.standard_benchmark_anchor_support import (
        StandardBenchmarkAnchorContractDefinition,
    )

    return (
        StandardBenchmarkAnchorContractDefinition(
            name="compile-proxy",
            manifest_paths=(
                COMPILE_MATRIX_MANIFEST_PATH,
                REGRESSION_MATRIX_MANIFEST_PATH,
            ),
            expected_anchor_case_ids=(
                _definition_anchor_expectations(
                    COMPILE_MATRIX_MANIFEST_PATH,
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
                    REGRESSION_MATRIX_MANIFEST_PATH,
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
            ),
            include_workload=is_compile_proxy_workload,
            correctness_case_signature=compile_proxy_correctness_case_signature,
            workload_signature=compile_proxy_workload_signature,
        ),
    )


def __getattr__(name: str) -> Any:
    if name == "COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS":
        return _build_compile_proxy_standard_benchmark_definitions()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
