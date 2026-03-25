from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import pathlib
from typing import Any

from rebar_harness.benchmarks import (
    BENCHMARK_WORKLOADS_ROOT,
    Workload,
)
from tests.benchmarks.collection_replacement_benchmark_anchor_support import (
    _is_collection_replacement_compiled_pattern_success_workload,
)
from tests.benchmarks.compiled_pattern_module_helper_benchmark_support import (
    _compiled_pattern_module_helper_route,
    _is_module_workflow_compiled_pattern_bounded_wildcard_success_workload,
    _is_module_workflow_compiled_pattern_literal_success_workload,
    _is_module_workflow_compiled_pattern_verbose_bytes_success_workload,
)
from tests.benchmarks.source_tree_contract_benchmark_support import (
    COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS,
    _SourceTreeContractBuilderSpec,
    _contract_source_workloads,
    compiled_pattern_contract_expected_build_calls,
)

MODULE_BOUNDARY_MANIFEST_PATH = BENCHMARK_WORKLOADS_ROOT / "module_boundary.py"
COLLECTION_REPLACEMENT_MANIFEST_PATH = (
    BENCHMARK_WORKLOADS_ROOT / "collection_replacement_boundary.py"
)

_COMPILED_PATTERN_MODULE_SUCCESS_CONTRACT_EXCLUDED_FIELDS = (
    COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS
    | {
        "categories",
        "syntax_features",
        "expected_exception",
        "haystack_text_model",
    }
)


@dataclass(frozen=True, slots=True)
class CompiledPatternModuleSuccessOwnerSpec:
    case_id: str
    manifest_path: pathlib.Path
    include_workload_selectors: tuple[Callable[[Any], bool], ...]
    contract_manifest_id: str
    contract_filename: str
    note_surface: str
    expected_source_workload_ids: tuple[str, ...]
    preserved_payload_fields: tuple[str, ...]
    preserve_replacement_payload_typing: bool

    def contract_builder_spec(self) -> _SourceTreeContractBuilderSpec:
        return _SourceTreeContractBuilderSpec(
            manifest_id=self.contract_manifest_id,
            excluded_fields=_COMPILED_PATTERN_MODULE_SUCCESS_CONTRACT_EXCLUDED_FIELDS,
            timing_scope="module-helper-call",
            notes=(
                "Ensures benchmark manifests keep the bounded "
                "compiled-pattern-first-argument successful "
                f"{self.note_surface} rows unresolved until helper invocation.",
            ),
        )

    def source_workloads(self) -> tuple[Workload, ...]:
        return _contract_source_workloads(
            manifest_path=self.manifest_path,
            include_workload_selectors=self.include_workload_selectors,
            expected_source_workload_ids=self.expected_source_workload_ids,
            drift_message=(
                "compiled-pattern module contract source workloads drifted from the "
                f"{self.case_id} owner-spec surface"
            ),
        )

    def expected_build_calls(
        self,
        source_workload: Workload,
    ) -> list[tuple[object, ...]]:
        return compiled_pattern_contract_expected_build_calls(
            source_workload,
            label=f"{self.case_id} success",
        )

    def expected_callback_result(self, source_workload: Workload) -> object:
        callback_result, _, _, _ = _compiled_pattern_module_helper_route(
            source_workload,
            collection_replacement_callback_flags=source_workload.flags,
        )
        return callback_result

    def expected_callback_call(
        self,
        source_workload: Workload,
    ) -> tuple[object, ...]:
        _, callback_call, _, _ = _compiled_pattern_module_helper_route(
            source_workload,
            collection_replacement_callback_flags=source_workload.flags,
        )
        return callback_call


_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC = (
    CompiledPatternModuleSuccessOwnerSpec(
        case_id="collection-replacement",
        manifest_path=COLLECTION_REPLACEMENT_MANIFEST_PATH,
        include_workload_selectors=(
            _is_collection_replacement_compiled_pattern_success_workload,
        ),
        contract_manifest_id="collection-replacement-boundary",
        contract_filename=(
            "python_benchmark_compiled_pattern_collection_replacement_success_contract.py"
        ),
        note_surface="collection/replacement",
        expected_source_workload_ids=(
            "module-split-literal-warm-str-compiled-pattern",
            "module-findall-literal-purged-bytes-compiled-pattern",
            "module-finditer-literal-warm-str-compiled-pattern",
            "module-sub-literal-warm-str-compiled-pattern",
            "module-subn-literal-purged-bytes-compiled-pattern",
        ),
        preserved_payload_fields=("count", "maxsplit"),
        preserve_replacement_payload_typing=True,
    )
)

_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC = (
    CompiledPatternModuleSuccessOwnerSpec(
        case_id="module-boundary",
        manifest_path=MODULE_BOUNDARY_MANIFEST_PATH,
        include_workload_selectors=(
            _is_module_workflow_compiled_pattern_literal_success_workload,
            _is_module_workflow_compiled_pattern_bounded_wildcard_success_workload,
            _is_module_workflow_compiled_pattern_verbose_bytes_success_workload,
        ),
        contract_manifest_id="module-boundary",
        contract_filename=(
            "python_benchmark_compiled_pattern_module_boundary_success_contract.py"
        ),
        note_surface="module-boundary",
        expected_source_workload_ids=(
            "module-search-literal-warm-hit-str-compiled-pattern",
            "module-match-literal-warm-hit-str-compiled-pattern",
            "module-fullmatch-literal-purged-hit-bytes-compiled-pattern",
            "module-search-bounded-wildcard-ignorecase-warm-hit-str-compiled-pattern",
            "module-match-bounded-wildcard-warm-hit-str-compiled-pattern",
            "module-fullmatch-bounded-wildcard-purged-hit-str-compiled-pattern",
            "module-search-verbose-regression-warm-hit-bytes-compiled-pattern",
            "module-fullmatch-verbose-regression-purged-hit-bytes-compiled-pattern",
        ),
        preserved_payload_fields=("flags",),
        preserve_replacement_payload_typing=False,
    )
)

_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS = (
    _COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC,
    _COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC,
)
