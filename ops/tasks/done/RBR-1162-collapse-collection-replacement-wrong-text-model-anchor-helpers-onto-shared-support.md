## RBR-1162: Collapse collection-replacement wrong-text-model anchor helpers onto shared support

Status: done
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining collection-replacement wrong-text-model benchmark-anchor helper layer that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving that route-specific support onto `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`, so the combined owner file stops carrying both the large wrong-text-model contract inventory and the collection-replacement signature/classification helpers that feed it.

## Deliverables
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Extend `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` so it owns the remaining collection-replacement wrong-text-model helper family that is still embedded in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`:
  - move `_collection_replacement_wrong_text_model_haystack_index(...)`, `_collection_replacement_wrong_text_model_correctness_case_signature(...)`, `_collection_replacement_wrong_text_model_workload_args(...)`, `_collection_replacement_wrong_text_model_workload_signature(...)`, and `_is_collection_replacement_wrong_text_model_workload(...)`;
  - move `_pattern_collection_replacement_wrong_text_model_haystack_index(...)`, `_collection_replacement_pattern_wrong_text_model_correctness_case_signature(...)`, `_collection_replacement_pattern_wrong_text_model_workload_args(...)`, `_collection_replacement_pattern_wrong_text_model_workload_signature(...)`, and `_is_collection_replacement_pattern_wrong_text_model_workload(...)`;
  - keep the module as ordinary Python support code that stays specific to the existing `benchmarks/workloads/collection_replacement_boundary.py` wrong-text-model routes; and
  - do not introduce a new benchmark-definition abstraction, registry, or a wrapper layer that simply forwards back into the owner file.
- Add focused support coverage in `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` for the moved helper surface:
  - cover the compiled-pattern and direct-`Pattern` wrong-text-model workload inclusion rules;
  - cover the current signature shapes for both wrong-text-model anchor families, including the haystack-position logic that differs between `split` and replacement helpers; and
  - keep the new tests focused on the extracted helper behavior instead of copying the owner file's full wrong-text-model contract matrix.
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so it imports and uses the moved collection-replacement wrong-text-model support instead of defining it inline:
  - keep the existing `collection-replacement-compiled-pattern-wrong-text-model` and `pattern-helper-collection-replacement-wrong-text-model` entries in `STANDARD_BENCHMARK_DEFINITIONS` on the same `collection_replacement_boundary.py` manifest path with the same anchored case ids;
  - keep the later generic wrong-text-model contract-owner machinery in this file, including `WrongTextModelOwnerSpec`, `_assert_wrong_text_model_payload_round_trip(...)`, and the pattern-boundary/module-boundary wrong-text-model routes that are not collection-replacement-specific in the current checkout; and
  - remove the moved collection-replacement helper definitions from the owner file once the shared support module owns them.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k '(collection-replacement-compiled-pattern-wrong-text-model or pattern-helper-collection-replacement-wrong-text-model or compiled_pattern_module_helper_wrong_text_model or pattern_helper_collection_replacement_wrong_text_model) and (keeps_expected_workloads_in_scope or stay_anchored_to_published_correctness_cases or stay_pinned_to_exact_case_ids or preserves_wrong_text_model_rows_until_helper_invocation or wrong_text_model_callbacks_preserve_precompile_contract or run_internal_workload_probe_measures_wrong_text_model_contract_workloads or pattern_helper_collection_replacement_wrong_text_model_haystack_materializes_at_callback_time)'`

## Constraints
- Keep the cleanup structural and limited to the three files above. Do not widen it into benchmark manifests, harness implementation code, correctness fixtures, README text, or tracked ops state prose.
- Prefer deleting the inline collection-replacement wrong-text-model helper block from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` over adding aliases or wrappers there.
- Preserve the current wrong-text-model workload inclusion rules, signature tuple shapes, anchored case-id mappings, and callback/precompile behavior exactly.
- Do not fold the generic wrong-text-model owner-spec layer or the pattern-boundary/module-boundary wrong-text-model helpers into this task unless the extraction is required to keep imports coherent in the current checkout.

## Notes
- `RBR-1162` is the next available unreserved architecture task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n 'RBR-1162|RBR-1163|RBR-1164|RBR-1165|RBR-1166' ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` matched only historical mentions inside completed task files and did not reveal a live reservation at `RBR-1162`.
- No blocked architecture task exists to reopen or retire first in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining simplification is concrete and benchmark-side in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `20949` lines in this run;
  - `rg -n '^def (_collection_replacement_wrong_text_model_haystack_index|_collection_replacement_wrong_text_model_correctness_case_signature|_collection_replacement_wrong_text_model_workload_args|_collection_replacement_wrong_text_model_workload_signature|_is_collection_replacement_wrong_text_model_workload|_pattern_collection_replacement_wrong_text_model_haystack_index|_collection_replacement_pattern_wrong_text_model_correctness_case_signature|_collection_replacement_pattern_wrong_text_model_workload_args|_collection_replacement_pattern_wrong_text_model_workload_signature|_is_collection_replacement_pattern_wrong_text_model_workload)\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` returned the remaining inline helper block at lines `7500` through `7776`; and
  - those helpers currently feed both the standard-benchmark definitions around lines `10108` through `10158` and the later wrong-text-model contract-owner section around lines `18457` through `18505`, which keeps the extraction cross-file and structural without widening into unrelated benchmark families.
- Verification status in this run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` returned `6 passed` in this run.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k '(collection-replacement-compiled-pattern-wrong-text-model or pattern-helper-collection-replacement-wrong-text-model or compiled_pattern_module_helper_wrong_text_model or pattern_helper_collection_replacement_wrong_text_model) and (keeps_expected_workloads_in_scope or stay_anchored_to_published_correctness_cases or stay_pinned_to_exact_case_ids or preserves_wrong_text_model_rows_until_helper_invocation or wrong_text_model_callbacks_preserve_precompile_contract or run_internal_workload_probe_measures_wrong_text_model_contract_workloads or pattern_helper_collection_replacement_wrong_text_model_haystack_materializes_at_callback_time)'` returned `35 passed, 718 deselected` in this run.

## Completion Note
- Moved the remaining collection-replacement wrong-text-model helper family out of `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` into `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`, including the shared haystack-index helper still used by the compiled-pattern success route.
- Added focused support coverage for compiled-pattern and direct-`Pattern` wrong-text-model inclusion rules plus split-vs-replacement signature shape differences in `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`.
- Verified the extracted support directly and re-ran the targeted combined-owner contract slice after the move:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` returned `9 passed`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k '(collection-replacement-compiled-pattern-wrong-text-model or pattern-helper-collection-replacement-wrong-text-model or compiled_pattern_module_helper_wrong_text_model or pattern_helper_collection_replacement_wrong_text_model) and (keeps_expected_workloads_in_scope or stay_anchored_to_published_correctness_cases or stay_pinned_to_exact_case_ids or preserves_wrong_text_model_rows_until_helper_invocation or wrong_text_model_callbacks_preserve_precompile_contract or run_internal_workload_probe_measures_wrong_text_model_contract_workloads or pattern_helper_collection_replacement_wrong_text_model_haystack_materializes_at_callback_time)'` returned `35 passed, 718 deselected`.
