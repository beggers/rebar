# RBR-1194: Extract benchmark manifest validation tests

Status: done
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining benchmark manifest and payload validation block that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving that bounded validation-only surface into one dedicated benchmark test file, so the giant combined suite stops owning generic manifest-loading and payload-entry-point coverage that does not depend on its broader source-tree benchmark wiring.

## Deliverables
- `tests/benchmarks/test_benchmark_manifest_validation.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Add one focused benchmark test file at `tests/benchmarks/test_benchmark_manifest_validation.py` that becomes the owner for the current manifest/payload validation block now embedded in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Move these existing tests into that dedicated file without widening their scope or changing their assertions:
  - `test_standard_benchmark_manifest_materializes_nested_constant_bytes_without_aliasing`
  - `test_standard_benchmark_manifest_replacement_payload_rejects_unsupported_text_model`
  - `test_standard_benchmark_manifest_rejects_missing_and_non_dict_manifest_values`
  - `test_benchmark_workload_value_normalization_recursively_preserves_literals_and_stringifies_mapping_keys`
  - `test_benchmark_workload_value_normalization_rejects_non_literal_containers`
  - `test_benchmark_expected_exception_normalization_stringifies_scalar_fields`
  - `test_standard_benchmark_expected_exception_validation_matches_manifest_and_payload_entry_points`
  - `test_standard_benchmark_haystack_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio`
  - `test_standard_benchmark_haystack_text_model_validation_matches_manifest_and_payload_entry_points`
  - `test_standard_benchmark_compiled_pattern_module_boundary_validation_matches_manifest_and_payload_entry_points`
- Keep that extracted file pinned to the current live validation surface instead of broadening it:
  - preserve the current nested `callable_constant` bytes materialization and anti-aliasing assertions exactly, including the current nested mapping/list mutation checks and the final bytes-valued callback result;
  - preserve the current unsupported `text_model`, missing/non-dict `MANIFEST`, workload-value normalization, and `expected_exception` normalization/error-string coverage exactly;
  - preserve the current haystack-text-model validation matrix exactly, including the current manifest scope, operation scope, keyword/window carrier rejection, same-text-model rejection, and non-`TypeError` rejection cases; and
  - preserve the current compiled-pattern module-boundary validation matrix exactly, including the current manifest-scope, positional-helper-only, and success-row-versus-wrong-text-model constraints.
- Reuse existing helpers and support imports instead of introducing another shared abstraction layer:
  - keep using `tests/benchmarks/benchmark_test_support.py` for `_write_test_manifest`;
  - keep using `tests/benchmarks/wrong_text_model_benchmark_owner_support.py` and `tests/benchmarks/source_tree_contract_benchmark_support.py` for the bounded wrong-text-model owner-spec contract wiring already extracted; and
  - do not add a new `*_support.py` module just for this extraction.
- Delete the moved validation block from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` instead of leaving wrappers, aliases, or duplicate copies behind.
- Do not widen this task into `python/rebar_harness/benchmarks.py`, benchmark workload manifests, correctness fixtures, reports, README text, or tracked ops state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_manifest_validation.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'keyword_kwargs_validation_matches_manifest_and_payload_entry_points or compiled_pattern_module_compile_validation_matches_manifest_and_payload_entry_points'`
- `bash -lc "! rg -n 'test_standard_benchmark_manifest_materializes_nested_constant_bytes_without_aliasing|test_standard_benchmark_manifest_replacement_payload_rejects_unsupported_text_model|test_standard_benchmark_manifest_rejects_missing_and_non_dict_manifest_values|test_benchmark_workload_value_normalization_recursively_preserves_literals_and_stringifies_mapping_keys|test_benchmark_workload_value_normalization_rejects_non_literal_containers|test_benchmark_expected_exception_normalization_stringifies_scalar_fields|test_standard_benchmark_expected_exception_validation_matches_manifest_and_payload_entry_points|test_standard_benchmark_haystack_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio|test_standard_benchmark_haystack_text_model_validation_matches_manifest_and_payload_entry_points|test_standard_benchmark_compiled_pattern_module_boundary_validation_matches_manifest_and_payload_entry_points' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep this cleanup structural and bounded to the two files above. The point is to move a validation-only block out of the giant combined suite, not to reinterpret benchmark manifest behavior or add new benchmark features.
- Prefer one dedicated validation test file plus existing support imports over another detached helper module, another shared builder layer, or more test-to-test imports.
- Preserve the current error strings, payload shapes, workload ids, and wrong-text-model owner-spec usage exactly.

## Notes
- `RBR-1194` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n "RBR-1194|RBR-1195|RBR-1196|RBR-1197|RBR-1198|RBR-1199|RBR-1200" ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` returned no live reservation for this range in this run.
- No blocked architecture task exists to reopen or retire first in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining simplification is concrete and still worthwhile in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `17665` lines in this run;
  - `rg -n "test_standard_benchmark_manifest_materializes_nested_constant_bytes_without_aliasing|test_standard_benchmark_manifest_replacement_payload_rejects_unsupported_text_model|test_standard_benchmark_manifest_rejects_missing_and_non_dict_manifest_values|test_benchmark_workload_value_normalization_recursively_preserves_literals_and_stringifies_mapping_keys|test_benchmark_workload_value_normalization_rejects_non_literal_containers|test_benchmark_expected_exception_normalization_stringifies_scalar_fields|test_standard_benchmark_expected_exception_validation_matches_manifest_and_payload_entry_points|test_standard_benchmark_haystack_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio|test_standard_benchmark_haystack_text_model_validation_matches_manifest_and_payload_entry_points|test_standard_benchmark_compiled_pattern_module_boundary_validation_matches_manifest_and_payload_entry_points" tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still matches the inline validation block at lines `15823`, `15930`, `15966`, `15988`, `16013`, `16036`, `16074`, `16143`, `16440`, and `16588`; and
  - the moved block depends only on existing benchmark helpers/support imports rather than the rest of the combined suite's anchor inventory, so it can be split without waiting on feature work.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_manifest_validation.py` currently fails with `ERROR: file or directory not found: tests/benchmarks/test_benchmark_manifest_validation.py`, which belongs exactly to the cleanup queued here.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'keyword_kwargs_validation_matches_manifest_and_payload_entry_points or compiled_pattern_module_compile_validation_matches_manifest_and_payload_entry_points'` returned `13 passed, 583 deselected` in this run.
  - `bash -lc "! rg -n 'test_standard_benchmark_manifest_materializes_nested_constant_bytes_without_aliasing|test_standard_benchmark_manifest_replacement_payload_rejects_unsupported_text_model|test_standard_benchmark_manifest_rejects_missing_and_non_dict_manifest_values|test_benchmark_workload_value_normalization_recursively_preserves_literals_and_stringifies_mapping_keys|test_benchmark_workload_value_normalization_rejects_non_literal_containers|test_benchmark_expected_exception_normalization_stringifies_scalar_fields|test_standard_benchmark_expected_exception_validation_matches_manifest_and_payload_entry_points|test_standard_benchmark_haystack_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio|test_standard_benchmark_haystack_text_model_validation_matches_manifest_and_payload_entry_points|test_standard_benchmark_compiled_pattern_module_boundary_validation_matches_manifest_and_payload_entry_points' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently fails exactly on this cleanup because the moved tests still live in the combined suite.

## Completion
- Extracted the ten manifest and payload validation tests into `tests/benchmarks/test_benchmark_manifest_validation.py` without changing their assertions or helper ownership, and deleted the moved block from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Verified with `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_manifest_validation.py`, `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'keyword_kwargs_validation_matches_manifest_and_payload_entry_points or compiled_pattern_module_compile_validation_matches_manifest_and_payload_entry_points'`, and the negative `rg` check named in this task.
