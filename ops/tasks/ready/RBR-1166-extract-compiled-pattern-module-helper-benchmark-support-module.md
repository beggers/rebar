## RBR-1166: Extract compiled-pattern module-helper benchmark support module

Status: ready
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining compiled-pattern module-helper route layer that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving that shared callback/dispatch support into one dedicated benchmark-support module, so the combined owner file stops carrying both the large contract inventory and the canonical compiled-pattern-first-argument helper route reused by multiple owner families.

## Deliverables
- `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`
- `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Add one bounded shared benchmark-support module at `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py` for the current compiled-pattern module-helper route surface that is still embedded in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`:
  - move `_CompiledPatternModuleHelperRoute`;
  - move `_compiled_pattern_module_helper_route(...)`; and
  - move the current compiled-pattern-first-argument CPython helper dispatch/materialization logic behind one support helper, whether that stays named inline or lands as a small extracted helper in the new module.
- Keep that support module as ordinary Python support code specific to the existing compiled-pattern module-helper benchmark surface:
  - the successful collection/replacement and module-boundary compiled-pattern owner specs; and
  - the compiled-pattern wrong-text-model owner specs that already reuse the same route semantics.
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so it imports and uses the moved support instead of defining the route logic inline:
  - `CompiledPatternModuleSuccessOwnerSpec.expected_callback_result(...)` and `.expected_callback_call(...)` must delegate to the moved route support;
  - the `self.use_compiled_pattern` branch of `WrongTextModelOwnerSpec.expected_callback_result(...)`, `.expected_callback_call(...)`, and `.run_cpython_workload(...)` must delegate to the moved support; and
  - remove the moved helper definitions from the owner file once the support module owns them.
- Preserve the current compiled-pattern module-helper behavior exactly after the extraction:
  - `module.search`, `module.match`, and `module.fullmatch` still use callback calls shaped as `(operation, haystack_payload(), 0, {})` and still dispatch through CPython with `(haystack_payload(), flags)`;
  - `module.split` still uses `(operation, haystack_payload(), maxsplit_argument(), callback_flags, {})` and still dispatches through CPython with `(haystack_payload(), maxsplit_argument())`;
  - `module.findall` and `module.finditer` still use `(operation, haystack_payload(), callback_flags)` and still dispatch through CPython with `(haystack_payload(), flags)`;
  - `module.sub` and `module.subn` still use `(operation, replacement_payload(), haystack_payload(), count_argument(), callback_flags, {})` and still dispatch through CPython with `(replacement_payload(), haystack_payload(), count_argument())`;
  - callback results still remain `"module-result"` for the ordinary successful paths, `["module-finditer-result"]` for `module.finditer`, and `("module-result", 0)` for `module.subn`; and
  - the compiled-pattern wrong-text-model CPython helper route still compiles `re.compile(workload.pattern_payload(), workload.flags)` first and still materializes `list(...)` for `module.finditer`.
- Add focused coverage at `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py` for the moved support surface:
  - cover representative route shapes for a module-boundary success row, a collection/replacement success row, a wrong-text-model `module.finditer` row, and a wrong-text-model `module.subn` row;
  - cover the extracted CPython-dispatch helper on at least one materialized-iterator path and one scalar-result path without copying the owner file's full contract matrix; and
  - keep the new tests focused on the extracted support behavior rather than duplicating the large combined-owner integration suite.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k '(standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_rows_until_helper_invocation or test_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing or test_standard_benchmark_manifest_preserves_wrong_text_model_rows_until_helper_invocation or test_wrong_text_model_callbacks_preserve_precompile_contract or test_compiled_pattern_module_contract_rows_stay_anchored_to_published_correctness_cases)'`

## Constraints
- Keep the cleanup structural and limited to the three files above. Do not widen it into benchmark manifests, harness implementation code, correctness fixtures, README text, reports, or tracked ops state prose.
- Prefer deleting the inline compiled-pattern module-helper route block from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` over leaving wrappers there that simply forward into the new support module.
- Do not widen this task into `_contract_source_workloads(...)`, compiled-pattern `module.compile` contract cases, standard benchmark anchor support, or unrelated wrong-text-model selector/signature helpers that already live on other support modules.

## Notes
- `RBR-1166` is the next available unreserved architecture task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n 'RBR-1166|RBR-1167|RBR-1168|RBR-1169|RBR-1170' ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` matched only historical mentions inside completed task files and did not reveal a live reservation or sibling task at `RBR-1166`.
- No blocked architecture task exists to reopen or retire first in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining simplification is concrete and cross-file in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `20752` lines in this run;
  - `rg -n '^def _contract_source_workloads\\(|^class _CompiledPatternModuleHelperRoute|^def _compiled_pattern_module_helper_route\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` returned the shared helper block beginning at lines `16927`, `17059`, and `17066`;
  - `CompiledPatternModuleSuccessOwnerSpec.expected_callback_result(...)` and `.expected_callback_call(...)` still delegate through `_compiled_pattern_module_helper_route(...)` at lines `16807` and `16816`; and
  - the compiled-pattern branch of `WrongTextModelOwnerSpec.expected_callback_result(...)`, `.expected_callback_call(...)`, and `.run_cpython_workload(...)` still delegate through the same route at lines `18073`, `18126`, and `18171`.
- Verification status in this run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k '(standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_rows_until_helper_invocation or test_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing or test_standard_benchmark_manifest_preserves_wrong_text_model_rows_until_helper_invocation or test_wrong_text_model_callbacks_preserve_precompile_contract or test_compiled_pattern_module_contract_rows_stay_anchored_to_published_correctness_cases)'` returned `42 passed, 711 deselected` in this run.
