## RBR-1180: Extract compiled-pattern module success owner support

Status: ready
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining compiled-pattern successful-helper owner-contract surface that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving that bounded support into one dedicated benchmark-support module, and delete the dead anchor-spec layer that is already unreferenced so the giant combined suite stops owning another private owner-spec mini-framework.

## Deliverables
- `tests/benchmarks/compiled_pattern_module_success_benchmark_support.py`
- `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Add one bounded shared benchmark-support module at `tests/benchmarks/compiled_pattern_module_success_benchmark_support.py` for the current compiled-pattern successful-helper owner-contract surface that is still embedded in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`:
  - move `CompiledPatternModuleSuccessOwnerSpec`;
  - move `_COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS`;
  - move `_COMPILED_PATTERN_MODULE_SUCCESS_CONTRACT_EXCLUDED_FIELDS`;
  - move `_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC`;
  - move `_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC`;
  - move `_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS`;
  - move `_assert_compiled_pattern_module_success_payload_round_trip`; and
  - move `_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS`.
- Keep that extracted support pinned to the current live compiled-pattern successful-helper surface instead of widening it:
  - preserve the current contract manifest ids, contract filenames, note text, expected source workload ids, preserved payload field sets, and replacement-payload typing behavior;
  - preserve the existing callback/build-call expectations by continuing to use the current compiled-pattern module-helper route and shared build-call helper support; and
  - preserve the existing module-boundary selector set, including the bounded verbose-bytes rows.
- Delete the dead compiled-pattern success anchor mini-layer instead of moving it into another file:
  - remove `_CompiledPatternModuleSuccessAnchorSpec`;
  - remove `_COMPILED_PATTERN_MODULE_SUCCESS_ANCHOR_SPECS`;
  - remove `_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_SOURCE_WORKLOADS`; and
  - remove `_COMPILED_PATTERN_MODULE_BOUNDARY_VERBOSE_BYTES_SUCCESS_SOURCE_WORKLOADS`.
- Move the dedicated compiled-pattern successful-helper owner-contract tests out of `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and into `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py` without copying unrelated combined-suite coverage:
  - `test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_rows_until_helper_invocation(...)`;
  - `test_run_internal_workload_probe_measures_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_workloads(...)`; and
  - `test_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing(...)`.
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so it imports the moved support instead of defining that block inline:
  - keep `test_standard_benchmark_compiled_pattern_validation_matches_manifest_and_payload_entry_points(...)` on the same rows and expectations;
  - keep the adjacent compiled-pattern helper-keyword error behavior unchanged; and
  - delete the moved owner-spec/test block rather than leaving aliases or wrapper passthroughs behind.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_collection_replacement_success or compiled_pattern_module_boundary_success or compiled_pattern_validation_matches_manifest_and_payload_entry_points'`

## Constraints
- Keep the cleanup structural and limited to the three files above. Do not widen it into benchmark manifests, harness implementation code, correctness fixtures, README text, reports, or tracked ops state prose.
- Prefer deleting the dead anchor-spec layer over rehoming it into a new support abstraction.
- Do not widen this task into compiled-pattern `module.compile` support, compiled-pattern module-helper keyword support, wrong-text-model support, standard benchmark anchor support, or unrelated benchmark-family refactors.

## Notes
- `RBR-1180` is the next available unreserved architecture task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n "RBR-1180|RBR-1181|RBR-1182" ops/tasks ops/state/backlog.md ops/state/current_status.md -g '*.md'` returned no matches in this run.
- No blocked architecture task exists to reopen or retire first in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining simplification is still concrete and bounded in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `18707` lines in this run;
  - `rg -n "^class CompiledPatternModuleSuccessOwnerSpec|^class _CompiledPatternModuleSuccessAnchorSpec|^_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS =|^_COMPILED_PATTERN_MODULE_SUCCESS_ANCHOR_SPECS =|^def test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_rows_until_helper_invocation\\(|^def test_run_internal_workload_probe_measures_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_workloads\\(|^def test_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing\\(" tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still shows the remaining inline owner-spec/test block at lines `16035`, `16147`, `16154`, `16209`, `16325`, `16386`, and `16420`; and
  - `rg -n "_COMPILED_PATTERN_MODULE_SUCCESS_ANCHOR_SPECS|CompiledPatternModuleSuccessAnchorSpec" tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks` only matches those definitions in the combined file in this run, so the anchor-spec sublayer is dead code and should be deleted instead of moved.
- Verification status in this run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py` currently fails with `ERROR: file or directory not found: tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`, which belongs to the exact cleanup queued here.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_collection_replacement_success or compiled_pattern_module_boundary_success or compiled_pattern_validation_matches_manifest_and_payload_entry_points'` returned `44 passed, 590 deselected` in this run.
