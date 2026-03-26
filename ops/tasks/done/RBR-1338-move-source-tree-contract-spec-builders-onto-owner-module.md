## RBR-1338: Move source-tree contract-spec builders onto owner module

Status: done
Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the remaining source-tree-specific `_SourceTreeContractBuilderSpec` constructor split between `tests/benchmarks/benchmark_test_support.py` and `tests/benchmarks/source_tree_benchmark_anchor_support.py` so the source-tree owner module fully owns source-tree contract-spec construction instead of the generic benchmark support layer instantiating owner-only specs inline.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- Move the remaining source-tree-only contract-spec constructor surface out of `tests/benchmarks/benchmark_test_support.py` and onto `tests/benchmarks/source_tree_benchmark_anchor_support.py`:
  - `CompiledPatternModuleCompileContractCase.contract_builder_spec`
  - `_compiled_pattern_wrong_text_model_contract_spec`
  - `CompiledPatternModuleSuccessOwnerSpec.contract_builder_spec`
  - `_CompiledPatternModuleHelperKeywordContractSpec.contract_builder_spec`
- Update `tests/benchmarks/benchmark_test_support.py` to consume those owner helpers through its existing module-level `source_tree_support` alias instead of nested per-method owner imports.
- Tighten the ownership assertions in `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` and/or `tests/benchmarks/test_benchmark_test_support.py` so the owner module locally defines the moved constructor helpers and the generic support module no longer carries source-tree-only constructor logic.
- Keep the cleanup structural only:
  - do not add a new helper module, shim, or alias wrapper
  - do not widen into unrelated benchmark-support cleanup outside this contract-spec constructor surface
  - do not move generic non-source-tree benchmark helpers out of `tests/benchmarks/benchmark_test_support.py`

## Verification
- `./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'compiled-pattern-module-compile or compiled-pattern-wrong-text-model or compiled-pattern-module-helper-keyword or compiled-pattern-module-success' -q`
- `bash -lc "test \"$(rg -n 'source_tree_benchmark_anchor_support as source_tree_support' tests/benchmarks/benchmark_test_support.py | wc -l)\" -eq 1"`

## Constraints
- Prefer moving the existing source-tree contract-spec constructor logic onto `tests/benchmarks/source_tree_benchmark_anchor_support.py` over introducing another abstraction layer.
- Keep call sites plain: route through the owner module alias rather than recreating local helper wrappers.

## Notes
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `bash -lc "rg -n 'RBR-1338|RBR-1339|RBR-1340|RBR-1341' ops/state/current_status.md ops/state/backlog.md || true"` returned no matches in this run
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- This target is live in the current checkout:
  - `rg -n "_SourceTreeContractBuilderSpec|source_tree_benchmark_anchor_support as source_tree_support" tests/benchmarks/benchmark_test_support.py` shows four remaining source-tree-specific constructor sites plus one module-level owner import in the generic support module
  - those remaining constructor sites are at:
    - `CompiledPatternModuleCompileContractCase.contract_builder_spec`
    - `_compiled_pattern_wrong_text_model_contract_spec`
    - `CompiledPatternModuleSuccessOwnerSpec.contract_builder_spec`
    - `_CompiledPatternModuleHelperKeywordContractSpec.contract_builder_spec`
- Verification status in this planning run:
  - `./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'compiled-pattern-module-compile or compiled-pattern-wrong-text-model or compiled-pattern-module-helper-keyword or compiled-pattern-module-success' -q` passed with `4 passed, 79 deselected in 0.45s`
  - `bash -lc "test \"$(rg -n 'source_tree_benchmark_anchor_support as source_tree_support' tests/benchmarks/benchmark_test_support.py | wc -l)\" -eq 1"` currently fails because `tests/benchmarks/benchmark_test_support.py` still contains four nested owner imports in addition to the single module-level import, and that failure belongs exactly to this cleanup
- Completed in this run:
  - Moved the four remaining source-tree-only contract builder constructors onto `tests/benchmarks/source_tree_benchmark_anchor_support.py` as owner-local helper definitions, removed the generic module's inline `_SourceTreeContractBuilderSpec` construction, and routed the three surviving class methods through the existing `source_tree_support` module alias.
  - Tightened ownership assertions so the owner module locally defines the moved constructor helpers and `tests/benchmarks/benchmark_test_support.py` no longer defines the wrong-text-model contract builder or nests per-method owner imports.
- Verification in this run:
  - `./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'compiled-pattern-module-compile or compiled-pattern-wrong-text-model or compiled-pattern-module-helper-keyword or compiled-pattern-module-success' -q` passed with `4 passed, 79 deselected in 0.59s`
  - `./.venv/bin/python -m pytest tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_contract_builder_methods_route_through_owner_module_alias or benchmark_test_support_drops_local_wrong_text_model_contract_builder or benchmark_test_support_owns_compiled_pattern_helper_surface or benchmark_test_support_owns_compiled_pattern_module_success_surface' -q` passed with `4 passed, 129 deselected in 0.43s`
  - `./.venv/bin/python -m pytest tests/benchmarks/test_benchmark_manifest_validation.py -k 'compiled_pattern_wrong_text_model_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation' -q` passed with `2 passed, 62 deselected in 0.24s`
  - `bash -lc "test \"$(rg -n 'source_tree_benchmark_anchor_support as source_tree_support' tests/benchmarks/benchmark_test_support.py | wc -l)\" -eq 1"` passed
