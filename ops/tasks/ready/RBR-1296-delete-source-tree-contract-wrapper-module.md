# RBR-1296: Delete source-tree contract wrapper module

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Delete the redundant `tests/benchmarks/source_tree_contract_benchmark_support.py` wrapper by folding its tiny remaining surface onto the existing `tests/benchmarks/benchmark_test_support.py` owner, so the benchmark-support layer stops carrying a dedicated broker module whose main job is re-exporting helpers that already live elsewhere.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py`
- `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py`
- `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`
- `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
- delete `tests/benchmarks/source_tree_contract_benchmark_support.py`
- delete `tests/benchmarks/test_source_tree_contract_benchmark_support.py`

## Acceptance Criteria
- Extend `tests/benchmarks/benchmark_test_support.py` so it directly owns the full surface currently split across the generic builder helpers and the tiny `tests/benchmarks/source_tree_contract_benchmark_support.py` wrapper:
  - `_SourceTreeContractBuilderSpec`
  - `_contract_source_workloads`
  - `_source_tree_contract_manifest_payload`
  - `_source_tree_contract_workload`
  - `_source_tree_contract_manifest`
  - `COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS`
  - `compiled_pattern_contract_expected_build_calls`
- Update the live import sites that still depend on `tests.benchmarks.source_tree_contract_benchmark_support` so they import the contract builders and compiled-pattern contract helpers from `tests.benchmarks.benchmark_test_support` instead. This includes:
  - `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py`
  - `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`
  - `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
  - `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py`
  - `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`
  - `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
- Delete `tests/benchmarks/source_tree_contract_benchmark_support.py` once nothing in `tests/benchmarks/` imports it anymore.
- Delete `tests/benchmarks/test_source_tree_contract_benchmark_support.py` and move any non-wrapper-specific coverage it still provides onto the existing benchmark-support owner tests. Do not keep a replacement identity test whose only purpose is proving one module re-exports another.
- Keep the current compiled-pattern contract behavior intact:
  - `compiled_pattern_contract_expected_build_calls()` must still return `[("compile", pattern, flags)]` for warm workloads and append `("purge",)` for purged workloads;
  - it must still reject unexpected cache modes with the current assertion shape; and
  - the shared excluded-field set must stay pinned to the same fields now covered by the deleted wrapper test.
- Do not add a new helper broker module. The point of this task is to remove a layer, not rename it.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
- `bash -lc "test ! -e tests/benchmarks/source_tree_contract_benchmark_support.py && test ! -e tests/benchmarks/test_source_tree_contract_benchmark_support.py && ! rg -n 'source_tree_contract_benchmark_support' tests/benchmarks"`

## Constraints
- Keep this cleanup structural and bounded to the benchmark-support/test layer above. Do not widen it into benchmark manifests, benchmark runner behavior, scorecard publication, README text, or tracked `ops/state/` prose.
- Preserve the existing source-tree contract builder payload shape, contract-manifest defaults, compiled-pattern helper build-call expectations, and the current compiled-pattern benchmark support behavior.
- Do not replace the deleted wrapper with another one-file forwarding layer under a different name.

## Notes
- `RBR-1296` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run; and
  - `rg -n "RBR-1296|RBR-1297|RBR-1298" ops/state/current_status.md ops/state/backlog.md ops/tasks -g '*.md'` matched only historical mentions inside older done-task notes, not a live reservation for `RBR-1296`.
- No blocked architecture task exists to reopen or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue/runtime state is not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready tasks, and no blocked tasks; and
  - the most recent `architecture-implementation` run finished `done`.
- The simplification target is still concrete in the live checkout:
  - `tests/benchmarks/source_tree_contract_benchmark_support.py` is only `38` lines long;
  - it currently re-exports `_SourceTreeContractBuilderSpec`, `_contract_source_workloads`, `_source_tree_contract_manifest_payload`, `_source_tree_contract_workload`, and `_source_tree_contract_manifest` from `tests/benchmarks/benchmark_test_support.py` while adding only one pinned excluded-field constant and one small build-call helper; and
  - `rg -n "source_tree_contract_benchmark_support" tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_source_tree_contract_benchmark_support.py` currently reports seven import sites that still depend on the wrapper.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py` passed with `222 passed in 2.49s`;
  - `bash -lc "test ! -e tests/benchmarks/source_tree_contract_benchmark_support.py && test ! -e tests/benchmarks/test_source_tree_contract_benchmark_support.py && ! rg -n 'source_tree_contract_benchmark_support' tests/benchmarks"` currently fails because the wrapper module, its dedicated test, and live imports are still present; that failure belongs to the exact cleanup this task is queuing; and
  - a broader suite probe that included `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` is not suitable as acceptance in this checkout because it currently has an unrelated failing assertion about quantified conditional callable slice identity.
