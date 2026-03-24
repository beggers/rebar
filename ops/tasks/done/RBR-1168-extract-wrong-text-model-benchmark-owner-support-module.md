## RBR-1168: Extract wrong-text-model benchmark owner support module

Status: done
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining wrong-text-model contract-owner helper layer that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving the route, callback, and payload-round-trip support into one dedicated benchmark-support module, so the combined owner file stops carrying both the owner-spec inventory and the mechanics that exercise it.

## Deliverables
- `tests/benchmarks/wrong_text_model_benchmark_owner_support.py`
- `tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Add one bounded shared benchmark-support module at `tests/benchmarks/wrong_text_model_benchmark_owner_support.py` for the remaining wrong-text-model owner-support surface that is still embedded in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`:
  - move `_WRONG_TEXT_MODEL_PATTERN_CONTRACT_EXCLUDED_FIELDS`;
  - move `_wrong_text_model_expected_callback_result(...)`;
  - move `_wrong_text_model_expected_build_calls(...)`;
  - move `_wrong_text_model_expected_callback_call(...)`;
  - move `_run_cpython_wrong_text_model_workload(...)`; and
  - move `_assert_wrong_text_model_payload_round_trip(...)`.
- Keep that support module as ordinary Python support code specific to the existing wrong-text-model contract surface:
  - the direct-`Pattern` collection/replacement wrong-text-model trio on `benchmarks/workloads/collection_replacement_boundary.py`;
  - the direct-`Pattern` pattern-boundary wrong-text-model trio on `benchmarks/workloads/pattern_boundary.py`; and
  - the compiled-pattern-first-argument wrong-text-model trios that already reuse `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`.
- Add focused coverage at `tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py` for the moved support surface:
  - cover representative compiled-pattern route behavior on at least one materialized-iterator row and one scalar-result row;
  - cover representative direct-`Pattern` collection/replacement and pattern-boundary callback-call/build-call shapes; and
  - cover the payload round-trip helper on representative `str` and `bytes` wrong-text-model rows without copying the large combined-owner contract matrix.
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so it imports and uses the moved wrong-text-model owner support instead of defining that logic inline:
  - keep the four concrete wrong-text-model owner-spec inventory entries on the same manifest paths with the same expected source workload ids and timing scopes;
  - reduce `WrongTextModelOwnerSpec` to the metadata it still needs for contract-builder construction and source-workload selection, and route the wrong-text-model tests through the imported support helpers instead of inline callback/CPython/payload helpers; and
  - remove the moved helper implementations from the owner file once the support module owns them.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k '(wrong_text_model and (preserves_wrong_text_model_rows_until_helper_invocation or run_internal_workload_probe_measures_wrong_text_model_contract_workloads or wrong_text_model_callbacks_preserve_precompile_contract or stays_anchored_to_published_correctness_cases or pattern_helper_collection_replacement_wrong_text_model_haystack_materializes_at_callback_time))'`

## Constraints
- Keep the cleanup structural and limited to the three files above. Do not widen it into benchmark manifests, harness implementation code, correctness fixtures, README text, reports, or tracked ops state prose.
- Prefer deleting the inline wrong-text-model route/callback/payload helper block from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` over leaving compatibility aliases or wrapper functions there.
- Do not widen this task into `_SourceTreeContractBuilderSpec`, `_source_tree_contract_manifest(...)`, `_source_tree_contract_workload(...)`, compiled-pattern module compile contract cases, or unrelated benchmark anchor helpers that already live on support modules.

## Notes
- `RBR-1168` is the next available unreserved architecture task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n 'RBR-1168|RBR-1169|RBR-1170|RBR-1171|RBR-1172' ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` matched only historical mentions inside completed task files and did not reveal a live reservation or sibling task at `RBR-1168`.
- No blocked architecture task exists to reopen or retire first in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining simplification is concrete and still cross-file in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `20634` lines in this run;
  - `WrongTextModelOwnerSpec` still starts at line `17923`, `_assert_wrong_text_model_payload_round_trip(...)` still starts at line `18112`, and the four wrong-text-model owner-spec instances still occupy lines `18141` through `18229`;
  - the owner-spec tests at lines `18257` through `18388` still depend on the inline callback-result, build-call, callback-call, CPython-route, and payload-round-trip logic; and
  - the selector/signature layer and compiled-pattern module-helper route already live on `tests/benchmarks/wrong_text_model_benchmark_anchor_support.py` and `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`, so moving the remaining owner-support logic is a bounded continuation rather than a new abstraction.
- Verification status in this run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k '(wrong_text_model and (preserves_wrong_text_model_rows_until_helper_invocation or run_internal_workload_probe_measures_wrong_text_model_contract_workloads or wrong_text_model_callbacks_preserve_precompile_contract or stays_anchored_to_published_correctness_cases or pattern_helper_collection_replacement_wrong_text_model_haystack_materializes_at_callback_time))'` returned `49 passed, 704 deselected` in this run.

## Completion Note
- Extracted the remaining wrong-text-model owner helpers into `tests/benchmarks/wrong_text_model_benchmark_owner_support.py`, reduced `WrongTextModelOwnerSpec` back to owner metadata in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and added focused coverage in `tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py`.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k '(wrong_text_model and (preserves_wrong_text_model_rows_until_helper_invocation or run_internal_workload_probe_measures_wrong_text_model_contract_workloads or wrong_text_model_callbacks_preserve_precompile_contract or stays_anchored_to_published_correctness_cases or pattern_helper_collection_replacement_wrong_text_model_haystack_materializes_at_callback_time))'`
