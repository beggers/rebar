## RBR-1339: Delete source-tree contract-builder wrapper methods

Status: done
Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the remaining source-tree-only `contract_builder_spec()` wrapper layer from `tests/benchmarks/benchmark_test_support.py` so the generic benchmark support module stops exposing owner-only contract-spec construction and the benchmark suites call the source-tree owner helpers directly.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- Remove the three source-tree-only `contract_builder_spec()` methods from `tests/benchmarks/benchmark_test_support.py`:
  - `CompiledPatternModuleCompileContractCase.contract_builder_spec`
  - `CompiledPatternModuleSuccessOwnerSpec.contract_builder_spec`
  - `_CompiledPatternModuleHelperKeywordContractSpec.contract_builder_spec`
- Update `tests/benchmarks/test_benchmark_manifest_validation.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the compiled-pattern contract paths call the owner helpers in `tests.benchmarks.source_tree_benchmark_anchor_support` directly instead of routing through the generic benchmark-support wrapper methods:
  - `compiled_pattern_module_compile_contract_builder_spec(...)`
  - `compiled_pattern_module_success_contract_builder_spec(...)`
  - `compiled_pattern_module_helper_keyword_contract_builder_spec(...)`
- Replace the wrapper-routing assertions in `tests/benchmarks/test_benchmark_test_support.py` with ownership checks that prove the generic support module no longer defines those wrapper methods while the source-tree owner helpers remain the only contract-spec construction surface for this slice.
- Keep the cleanup structural only:
  - do not add a new helper module, shim, or alias wrapper
  - do not widen into unrelated source-tree benchmark cleanup outside this contract-builder wrapper surface
  - do not move generic non-source-tree helpers out of `tests/benchmarks/benchmark_test_support.py`

## Verification
- `./.venv/bin/python -m pytest tests/benchmarks/test_benchmark_test_support.py -q`
- `./.venv/bin/python -m pytest tests/benchmarks/test_benchmark_manifest_validation.py -q`
- `./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -q`
- `bash -lc "! rg -n 'def contract_builder_spec\\(' tests/benchmarks/benchmark_test_support.py"`
- `bash -lc "! rg -n '\\.contract_builder_spec\\(' tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Prefer deleting the redundant wrapper methods over introducing another shared abstraction.
- Keep call sites plain: route straight to the owner module helpers instead of replacing one wrapper layer with another.

## Notes
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `bash -lc "rg -n 'RBR-1339|RBR-1340|RBR-1341|RBR-1342' ops/state/current_status.md ops/state/backlog.md || true"` returned no matches in this run
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- This target is live in the current checkout:
  - `rg -n "def contract_builder_spec\\(" tests/benchmarks/benchmark_test_support.py` reports three wrapper definitions in the generic support module
  - `rg -n "\\.contract_builder_spec\\(" tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` reports the remaining source-tree contract-builder wrapper call sites in the two benchmark suites
- Verification status in this planning run:
  - `./.venv/bin/python -m pytest tests/benchmarks/test_benchmark_test_support.py -q` passed with `133 passed in 0.56s`
  - `./.venv/bin/python -m pytest tests/benchmarks/test_benchmark_manifest_validation.py -q` passed with `64 passed in 0.18s`
  - `./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -q` passed with `279 passed, 1821 subtests passed in 12.46s`
  - `bash -lc "! rg -n 'def contract_builder_spec\\(' tests/benchmarks/benchmark_test_support.py"` currently fails because the three source-tree-only wrapper methods still live in the generic support module, and that failure belongs exactly to this cleanup
  - `bash -lc "! rg -n '\\.contract_builder_spec\\(' tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently fails because those two benchmark suites still route through the wrapper methods, and that failure belongs exactly to this cleanup

## Completion
- Deleted the three source-tree-only `contract_builder_spec()` wrapper methods from `tests/benchmarks/benchmark_test_support.py`.
- Updated the manifest-validation and combined-boundary benchmark suites to call the source-tree owner helpers directly for compiled-pattern compile/success/helper-keyword contract specs.
- Replaced the wrapper-route assertions in `tests/benchmarks/test_benchmark_test_support.py` with ownership checks that the generic support classes no longer define `contract_builder_spec` while the owner-module helper functions remain present.
- Verified with:
  - `./.venv/bin/python -m pytest tests/benchmarks/test_benchmark_test_support.py -q` -> `133 passed in 0.55s`
  - `./.venv/bin/python -m pytest tests/benchmarks/test_benchmark_manifest_validation.py -q` -> `64 passed in 0.20s`
  - `./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -q` -> `279 passed, 1821 subtests passed in 12.50s`
  - `bash -lc "! rg -n 'def contract_builder_spec\\(' tests/benchmarks/benchmark_test_support.py"` -> passed
  - `bash -lc "! rg -n '\\.contract_builder_spec\\(' tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` -> passed
