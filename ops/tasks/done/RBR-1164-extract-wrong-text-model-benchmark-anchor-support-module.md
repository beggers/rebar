## RBR-1164: Extract wrong-text-model benchmark anchor support module

Status: done
Owner: architecture-implementation
Created: 2026-03-24
Completed: 2026-03-24

## Goal
- Remove the remaining wrong-text-model selector/signature helper layer that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving that shared support into one dedicated benchmark-support module, so the combined owner file stops carrying both the standard benchmark definition inventory and the route-specific wrong-text-model helper logic that also feeds the later owner-spec contract tests.

## Deliverables
- `tests/benchmarks/wrong_text_model_benchmark_anchor_support.py`
- `tests/benchmarks/test_wrong_text_model_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Add one bounded shared benchmark-support module at `tests/benchmarks/wrong_text_model_benchmark_anchor_support.py` for the remaining wrong-text-model helper family that is still embedded in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`:
  - move `_is_module_workflow_compiled_pattern_wrong_text_model_workload(...)`;
  - move `_pattern_boundary_wrong_text_model_correctness_case_signature(...)`;
  - move `_pattern_boundary_wrong_text_model_workload_signature(...)`; and
  - move `_is_pattern_boundary_wrong_text_model_workload(...)`.
- Keep that module as ordinary Python support code that stays limited to the current wrong-text-model benchmark-anchor surface:
  - the compiled-pattern-first-argument module-helper wrong-text-model trio on `benchmarks/workloads/module_boundary.py`; and
  - the direct-`Pattern` wrong-text-model trio on `benchmarks/workloads/pattern_boundary.py`.
- Add focused coverage at `tests/benchmarks/test_wrong_text_model_benchmark_anchor_support.py` for the moved helper surface:
  - cover the compiled-pattern module-helper selector's inclusion and exclusion rules around `use_compiled_pattern`, `haystack_text_model`, and the expected `TypeError` payload;
  - cover the pattern-boundary selector's inclusion and exclusion rules for `pattern.search`, `pattern.match`, and `pattern.fullmatch`; and
  - cover the current pattern-boundary correctness/workload signature shapes for representative `str` and `bytes` wrong-text-model rows without copying the owner file's full contract matrix.
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so it imports and uses the moved wrong-text-model support instead of defining that helper family inline:
  - keep the `pattern-boundary-wrong-text-model` and `compiled-pattern-module-boundary-wrong-text-model` `StandardBenchmarkAnchorContractDefinition` entries on the same manifest paths and anchored case ids;
  - keep the later generic owner-spec contract machinery in this file, including `WrongTextModelOwnerSpec`, `_assert_wrong_text_model_payload_round_trip(...)`, and the four concrete `WRONG_TEXT_MODEL_OWNER_SPECS`; and
  - do not widen this task into moving the generic wrong-text-model owner-spec methods, the collection-replacement wrong-text-model support that already lives in `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`, or unrelated benchmark families.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k '(pattern_boundary_wrong_text_model or compiled_pattern_module_helper_wrong_text_model or pattern_helper_collection_replacement_wrong_text_model) and (standard_benchmark_manifest_preserves_wrong_text_model_rows_until_helper_invocation or run_internal_workload_probe_measures_wrong_text_model_contract_workloads or wrong_text_model_callbacks_preserve_precompile_contract or standard_benchmark_haystack_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio or pattern_helper_collection_replacement_wrong_text_model_haystack_materializes_at_callback_time)'`

## Constraints
- Keep the cleanup structural and limited to the three files above. Do not widen it into benchmark manifests, harness implementation code, correctness fixtures, README text, or tracked ops state prose.
- Prefer deleting the inline wrong-text-model helper block from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` over leaving local wrapper aliases that simply forward into the new support module.
- Preserve the current wrong-text-model workload inclusion rules, signature tuple shapes, anchored case-id mappings, and contract-test behavior exactly.

## Notes
- `RBR-1164` is the next available unreserved architecture task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n 'RBR-1164|RBR-1165|RBR-1166|WrongTextModelOwnerSpec|pattern-boundary-wrong-text-model' ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` matched only historical mentions inside completed task files and did not reveal a live reservation or sibling task at `RBR-1164`.
- No blocked architecture task exists to reopen or retire first in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining simplification is concrete and still cross-file in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `20815` lines in this run;
  - `rg -n '^def (_pattern_boundary_wrong_text_model_correctness_case_signature|_pattern_boundary_wrong_text_model_workload_signature|_is_pattern_boundary_wrong_text_model_workload)\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` returned the inline pattern-boundary helper trio at lines `9093`, `9119`, and `9137`;
  - `rg -n '^class WrongTextModelOwnerSpec|^def _assert_wrong_text_model_payload_round_trip\(|^_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_OWNER_SPEC =|^_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_OWNER_SPEC =|^_COMPILED_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_OWNER_SPEC =|^_COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_OWNER_SPEC =|^WRONG_TEXT_MODEL_OWNER_SPECS =' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` shows the later owner-spec contract block still starts at line `18095`, so these route helpers remain shared between two distant sections of the same owner file instead of already living on one support surface; and
  - `_is_module_workflow_compiled_pattern_wrong_text_model_workload(...)` still lives inline at line `8333`, feeding both the `compiled-pattern-module-boundary-wrong-text-model` standard benchmark definition and the later `_COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_OWNER_SPEC`.
- Verification status in this run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_wrong_text_model_benchmark_anchor_support.py` returned `9 passed` in this run.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k '(pattern_boundary_wrong_text_model or compiled_pattern_module_helper_wrong_text_model or pattern_helper_collection_replacement_wrong_text_model) and (standard_benchmark_manifest_preserves_wrong_text_model_rows_until_helper_invocation or run_internal_workload_probe_measures_wrong_text_model_contract_workloads or wrong_text_model_callbacks_preserve_precompile_contract or standard_benchmark_haystack_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio or pattern_helper_collection_replacement_wrong_text_model_haystack_materializes_at_callback_time)'` returned `42 passed, 711 deselected` in this run.
- Completion note:
  - Moved the remaining compiled-pattern module-helper and pattern-boundary wrong-text-model selectors/signatures into `tests/benchmarks/wrong_text_model_benchmark_anchor_support.py`, added focused support tests, and rewired the combined owner benchmark test to import the shared helper surface instead of defining it inline.
