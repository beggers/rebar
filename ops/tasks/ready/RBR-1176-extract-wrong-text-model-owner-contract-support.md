## RBR-1176: Extract wrong-text-model owner contract support

Status: ready
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining wrong-text-model owner-spec inventory and owner-contract test surface that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by extending the existing wrong-text-model benchmark support files, so the giant combined benchmark suite stops owning a second dedicated wrong-text-model contract lane after the route and payload helpers already moved out.

## Deliverables
- `tests/benchmarks/wrong_text_model_benchmark_owner_support.py`
- `tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Extend `tests/benchmarks/wrong_text_model_benchmark_owner_support.py` so it owns the remaining wrong-text-model contract-owner inventory that is still embedded in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`:
  - move `WrongTextModelOwnerSpec`;
  - move the four concrete owner-spec constants for the pattern collection/replacement, pattern-boundary, compiled-pattern collection/replacement, and compiled-pattern module-boundary wrong-text-model rows;
  - move `WRONG_TEXT_MODEL_OWNER_SPECS`;
  - move `_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_PARAMS`; and
  - keep the current contract-builder construction, source-workload selection, excluded-field sets, timing scopes, note text, and direct-pattern route metadata unchanged.
- Move the dedicated wrong-text-model owner-contract tests out of `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and into `tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py` without copying the giant combined suite:
  - `test_standard_benchmark_manifest_preserves_wrong_text_model_rows_until_helper_invocation(...)`;
  - `test_run_internal_workload_probe_measures_wrong_text_model_contract_workloads(...)`; and
  - `test_wrong_text_model_callbacks_preserve_precompile_contract(...)`.
- Keep the extracted support and focused tests pinned to the current live wrong-text-model surface:
  - the same four owner specs and expected source workload ids;
  - the same contract manifest ids and filename stems;
  - the same `use_compiled_pattern`, `timing_scope`, `excluded_fields`, `note_surface`, and `direct_pattern_route` values; and
  - the same callback/build-call, CPython `TypeError`, and payload-round-trip expectations already exercised through `tests/benchmarks/wrong_text_model_benchmark_owner_support.py`.
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so it imports the moved owner-spec support instead of defining that block inline:
  - keep `test_standard_benchmark_haystack_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio(...)` on the same pattern-boundary rows by importing the moved owner spec;
  - keep the adjacent compiled-pattern keyword-error test behavior unchanged; and
  - delete the moved wrong-text-model owner-spec/test block from the combined file instead of leaving wrapper aliases behind.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'haystack_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio or compiled_pattern_module_helper_keyword_error_callbacks_match_cpython_exceptions'`

## Constraints
- Keep the cleanup structural and limited to the three files above. Do not widen it into benchmark manifests, harness implementation code, correctness fixtures, README text, reports, or tracked ops state prose.
- Prefer deleting the inline wrong-text-model owner-spec inventory and owner-contract tests from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` over leaving local aliases or pass-through wrappers there.
- Do not widen this task into wrong-text-model anchor support, compiled-pattern module-helper route support, compiled-pattern `module.compile` contract support, source-tree contract builder helpers, or unrelated benchmark-family refactors.

## Notes
- `RBR-1176` is the next available unreserved architecture task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n 'RBR-1176|wrong_text_model_benchmark_owner_support|WrongTextModelOwnerSpec' ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md' || true` matched only historical mentions inside completed task files and did not reveal a live reservation or sibling task at `RBR-1176`.
- No blocked architecture task exists to reopen or retire first in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining simplification is concrete and still cross-file in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `19628` lines in this run;
  - `tests/benchmarks/wrong_text_model_benchmark_owner_support.py` is only `204` lines and `tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py` is `188` lines, so the existing dedicated support surface is still much smaller than the combined suite that owns the remaining contract block;
  - `rg -n '^class WrongTextModelOwnerSpec|^def test_standard_benchmark_manifest_preserves_wrong_text_model_rows_until_helper_invocation\(|^def test_run_internal_workload_probe_measures_wrong_text_model_contract_workloads\(|^def test_wrong_text_model_callbacks_preserve_precompile_contract\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` shows the remaining owner-spec block and its three dedicated tests at lines `17076`, `17232`, `17304`, and `17339`; and
  - `test_standard_benchmark_haystack_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio(...)` still depends on `_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_OWNER_SPEC` later in the same file at lines `18103` and `18110`, so this cleanup still needs one shared owner-support import point rather than another local duplication pass.
- Verification status in this run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py` returned `6 passed` in this run.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'haystack_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio or compiled_pattern_module_helper_keyword_error_callbacks_match_cpython_exceptions'` returned `13 passed, 748 deselected` in this run.
