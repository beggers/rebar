## RBR-1172: Extract compiled-pattern module compile benchmark support module

Status: ready
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining compiled-pattern `module.compile` contract-support layer that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving that shared case/route/dispatch support into one dedicated benchmark-support module, so the giant combined benchmark suite stops owning both the compile-contract inventory and the mechanics that exercise it.

## Deliverables
- `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py`
- `tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Add one bounded shared benchmark-support module at `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py` for the current compiled-pattern `module.compile` contract surface that is still embedded in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`:
  - move the compiled-pattern `module.compile` payload-round-trip helpers;
  - move the compiled-pattern `module.compile` correctness/workload signature and include-workload helpers for both the success and `flags=` keyword contract lanes;
  - move the compiled-pattern `module.compile` CPython dispatch and callback-flags helpers for both contract lanes;
  - move `_CompiledPatternModuleCompileContractRoute`;
  - move `CompiledPatternModuleCompileContractCase`;
  - move `_CompiledPatternModuleContractAnchorLane`; and
  - move the route constants and shared contract-case/anchor-lane assembly that feed the compiled-pattern `module.compile` contract tests.
- Keep that support module as ordinary Python support code specific to the existing compiled-pattern-first-argument `module.compile` benchmark-contract surface:
  - the success lane that re-compiles an already compiled pattern through `module.compile`;
  - the bounded `flags=` keyword lanes already driven by `_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS`; and
  - the existing source-tree contract-builder support imported from `tests/benchmarks/source_tree_contract_benchmark_support.py`.
- Add focused coverage at `tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py` for the moved support surface without copying the full owner matrix from the large combined suite:
  - cover representative success-lane payload round-trip behavior on a live compiled-pattern-first-argument `module.compile` workload;
  - cover representative keyword-lane payload round-trip and keyword-signature behavior on a live `flags=` workload, including the current exact keyword-value type preservation;
  - cover representative CPython dispatch behavior for one success lane and one keyword lane; and
  - cover the extracted anchor/case metadata enough to prove source workload ids and expected anchored workload/case pairs stay pinned to the current contract rows.
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so it imports and uses the moved support instead of defining that compiled-pattern `module.compile` contract layer inline:
  - keep the existing `_CompiledPatternModuleCompileKeywordOwnerSpec` and `_CompiledPatternModuleCompileSuccessOwnerSpec` inventory in place unless the moved support makes a smaller equivalent possible inside this same bounded cleanup;
  - keep the existing manifest ids, contract filenames, `-contract` workload ids, timing scopes, drift wording, expected anchor pairs, and callback materialization behavior unchanged; and
  - remove the moved compiled-pattern `module.compile` contract helpers from the combined benchmark file once the new support module owns them.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile'`

## Constraints
- Keep the cleanup structural and limited to the three files above. Do not widen it into benchmark manifests, harness implementation code, correctness fixtures, README text, reports, or tracked ops state prose.
- Prefer deleting the inline compiled-pattern `module.compile` contract block from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` over leaving wrappers there that only forward into the new support module.
- Do not widen this task into compiled-pattern module-helper route support, wrong-text-model owner support, source-tree contract-builder support, standard benchmark anchor support, or unrelated collection/replacement helper extractions that already live on support modules.

## Notes
- `RBR-1172` is the next available unreserved architecture task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run; and
  - `rg -n 'RBR-1172|RBR-1173|compiled_pattern_module_compile_benchmark_support' ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` did not reveal a live reservation or sibling task for this cleanup.
- No blocked architecture task exists to reopen or retire first in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining simplification is concrete and still cross-file in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `20510` lines in this run;
  - `rg -n '^def _compiled_pattern_module_compile_keyword_signature\\(|^class CompiledPatternModuleCompileContractCase|^class _CompiledPatternModuleContractAnchorLane|^def test_standard_benchmark_manifest_preserves_compiled_pattern_module_compile_success_and_keyword_contract_rows_until_helper_invocation|^def test_compiled_pattern_module_contract_rows_stay_anchored_to_published_correctness_cases|^def test_compiled_pattern_module_compile_keyword_kwargs_materialize_at_callback_time|^def test_run_internal_workload_probe_measures_compiled_pattern_module_compile_success_and_keyword_contract_workloads|^def test_compiled_pattern_module_compile_success_and_keyword_contract_callbacks_precompile_first_argument_before_timing' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` returned the remaining contract-support block at lines `17249`, `17455`, `17672`, `17727`, `17794`, `17840`, `17885`, and `17918`;
  - the owner-spec inventory earlier in the same file still instantiates `CompiledPatternModuleCompileContractCase` directly at lines `8036` and `8051`; and
  - the current compile-contract tests still span manifest synthesis, anchoring, callback materialization, workload probing, and precompile-before-timing behavior through that same inline support layer.
- Verification status in this run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile'` returned `82 passed, 672 deselected, 22 subtests passed` in this run.
