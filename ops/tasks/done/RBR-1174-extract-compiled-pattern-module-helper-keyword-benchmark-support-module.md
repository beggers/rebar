## RBR-1174: Extract compiled-pattern module-helper keyword benchmark support module

Status: done
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining compiled-pattern module-helper keyword-contract layer that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving that shared contract/spec/selector support into one dedicated benchmark-support module, so the giant combined benchmark suite stops owning both the route consumer tests and the bounded keyword-contract mechanics that already form a coherent sub-surface.

## Deliverables
- `tests/benchmarks/compiled_pattern_module_helper_keyword_benchmark_support.py`
- `tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Add one bounded shared benchmark-support module at `tests/benchmarks/compiled_pattern_module_helper_keyword_benchmark_support.py` for the current compiled-pattern module-helper keyword-contract surface that is still embedded in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`:
  - move `_CompiledPatternModuleHelperKeywordContractSpec`;
  - move `_CompiledPatternModuleHelperKeywordContractSurface`;
  - move `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_PAYLOAD_DROP_FIELDS`;
  - move the success and keyword-error contract spec constants plus their live source-workload/precompile-anchor selectors and param builders;
  - move the bounded payload-round-trip, CPython-outcome, and expected-materialized-field-name logic that currently hangs off that contract surface; and
  - move the current compiled-pattern expected-build-call helper if that is the smallest way to let both the extracted keyword-contract support and the remaining compiled-pattern success owner surface keep using one canonical build-call contract.
- Keep that support module as ordinary Python benchmark support code limited to the existing compiled-pattern-first-argument module-helper keyword-contract surface:
  - the successful `module.split` / `module.sub` / `module.subn` keyword-carrier rows;
  - the keyword-error rows that preserve exact `TypeError` text and expected-exception payloads; and
  - the existing compiled-pattern module-helper route support already provided by `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`.
- Add focused coverage at `tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py` for the moved support surface without copying the giant combined-owner suite:
  - cover representative success-lane and keyword-error source-workload selection order against the live manifest rows;
  - cover representative payload round-trip behavior for one success row and one keyword-error row, including the current `expected_exception` preservation split and bool keyword type preservation;
  - cover representative expected-materialized-field-name behavior for a `module.split` positional-keyword row and a `module.sub` or `module.subn` keyword row; and
  - cover the current three-row precompile-anchor order plus one success-lane and one keyword-error CPython-outcome path.
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so it imports and uses the moved support instead of defining that keyword-contract block inline:
  - keep the existing contract filenames, source workload ids, precompile-anchor ids, timing scopes, notes, payload-drop behavior, and callback/build-call expectations unchanged;
  - keep `test_compiled_pattern_module_helper_keyword_cases_cover_bool_count_complements(...)`, `test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_keyword_contract_rows_until_helper_invocation(...)`, `test_compiled_pattern_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time(...)`, `test_run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_contract_workloads(...)`, and `test_compiled_pattern_module_helper_keyword_contract_callbacks_precompile_first_argument_before_timing(...)` on the same workload rows and behavioral assertions after the extraction; and
  - remove the moved compiled-pattern module-helper keyword-contract definitions from the combined benchmark file once the support module owns them.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword'`

## Constraints
- Keep the cleanup structural and limited to the three files above. Do not widen it into benchmark manifests, harness implementation code, correctness fixtures, README text, reports, or tracked ops state prose.
- Prefer deleting the inline compiled-pattern module-helper keyword-contract block from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` over leaving local wrapper aliases there.
- Do not widen this task into compiled-pattern module success anchor extraction, compiled-pattern `module.compile` contract support, wrong-text-model owner support, standard benchmark anchor support, or unrelated benchmark-family refactors.

## Notes
- `RBR-1174` is the next available unreserved architecture task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n 'RBR-1174|RBR-1175|RBR-1176|compiled_pattern_module_helper_keyword_benchmark_support' ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` matched only historical mentions inside completed task files and did not reveal a live reservation or sibling task at `RBR-1174`.
- No blocked architecture task exists to reopen or retire first in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining simplification is concrete and still cross-file in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `19921` lines in this run;
  - `rg -n '^class _CompiledPatternModuleHelperKeywordContractSpec|^class _CompiledPatternModuleHelperKeywordContractSurface|^def _compiled_pattern_contract_expected_build_calls\\(|^def test_compiled_pattern_module_helper_keyword_cases_cover_bool_count_complements\\(|^def test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_keyword_contract_rows_until_helper_invocation\\(|^def test_compiled_pattern_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time\\(|^def test_run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_contract_workloads\\(|^def test_compiled_pattern_module_helper_keyword_contract_callbacks_precompile_first_argument_before_timing\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` returned the embedded block at lines `16090`, `16139`, `16360`, `16479`, `16527`, `16584`, `16615`, and `16648`;
  - `_compiled_pattern_contract_expected_build_calls(...)` is still shared by the keyword-contract surface and the compiled-pattern success owner surface at lines `16158` and `16720`; and
  - the extracted route support already lives separately in `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`, so this keyword-contract block is now the remaining compiled-pattern module-helper support layer still embedded in the combined suite.
- Verification status in this run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword'` returned `67 passed, 687 deselected, 10 subtests passed` in this run.

## Completion
- Extracted the compiled-pattern module-helper keyword contract block into `tests/benchmarks/compiled_pattern_module_helper_keyword_benchmark_support.py`, including the shared build-call helper now reused by the remaining compiled-pattern success owner surface through imports.
- Added `tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py` to cover live source-workload ordering, payload round trips, materialized field names, precompile-anchor ordering, and representative success/error CPython outcome paths without copying the combined owner suite.
- Updated `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to import the moved support and removed the inline keyword-contract definitions.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword'`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py`
