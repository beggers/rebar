# RBR-1045: Collapse direct-Pattern wrong-text-model helper routes

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining detached direct-`Pattern` wrong-text-model callback, build-call, and CPython-dispatch helpers from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the two direct-`Pattern` wrong-text-model owner specs derive that behavior through one canonical same-file owner-spec route instead of seven parallel free functions.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines these detached direct-`Pattern` wrong-text-model helpers:
  - `def _pattern_collection_replacement_wrong_text_model_expected_callback_result(...)`
  - `def _pattern_collection_replacement_wrong_text_model_expected_build_calls(...)`
  - `def _pattern_collection_replacement_wrong_text_model_expected_callback_call(...)`
  - `def _run_cpython_pattern_collection_replacement_wrong_text_model_workload(...)`
  - `def _pattern_boundary_wrong_text_model_expected_callback_result(...)`
  - `def _pattern_boundary_wrong_text_model_expected_callback_call(...)`
  - `def _run_cpython_pattern_boundary_wrong_text_model_workload(...)`
- Replace those seven helpers with one canonical same-file route on `WrongTextModelOwnerSpec`, or an equivalently smaller file-local structure, reused by both direct-`Pattern` wrong-text-model owner specs without adding a support module, registry file, or checked-in data layer:
  - `_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_OWNER_SPEC`
  - `_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_OWNER_SPEC`
- Keep the current direct-`Pattern` wrong-text-model callback-result semantics intact while moving them onto that canonical route:
  - collection/replacement rows still return `("pattern-result", 0)` for `pattern.subn`;
  - the remaining collection/replacement rows still return `"pattern-result"`; and
  - pattern-boundary `pattern.search`, `pattern.match`, and `pattern.fullmatch` rows still return `"pattern-result"`.
- Keep the current direct-`Pattern` wrong-text-model callback-call semantics intact while moving them onto that canonical route:
  - `pattern.split` rows still expect `( "pattern.split", haystack_payload(), (maxsplit_argument(),), {} )`;
  - `pattern.sub` and `pattern.subn` rows still expect `(operation, replacement_payload(), haystack_payload(), (count_argument(),), {})`; and
  - pattern-boundary `pattern.search`, `pattern.match`, and `pattern.fullmatch` rows still expect `(operation, haystack_payload(), (), {})`.
- Keep the current direct-`Pattern` wrong-text-model build-call semantics intact while moving them onto that canonical route:
  - the route still starts from `("compile", pattern_payload(), flags)`;
  - `cache_mode == "warm"` still keeps only that compile call;
  - `cache_mode == "purged"` still appends `("purge",)` after the compile call; and
  - unexpected cache modes still fail locally instead of silently widening behavior.
- Keep the current direct-`Pattern` wrong-text-model CPython-dispatch semantics intact while moving them onto that canonical route:
  - the route still compiles `re.compile(workload.pattern_payload(), workload.flags)` before dispatching the helper call;
  - `pattern.split` still dispatches the compiled pattern plus `haystack_payload()` and `maxsplit_argument()`;
  - `pattern.sub` and `pattern.subn` still dispatch the compiled pattern plus `replacement_payload()`, `haystack_payload()`, and `count_argument()`; and
  - pattern-boundary `pattern.search`, `pattern.match`, and `pattern.fullmatch` still dispatch the compiled pattern plus `haystack_payload()` only.
- Update the existing wrong-text-model call sites to use that canonical route while preserving the current owner coverage and local behavior asserted by these tests:
  - `test_standard_benchmark_manifest_preserves_wrong_text_model_rows_until_helper_invocation`
  - `test_run_internal_workload_probe_measures_wrong_text_model_contract_workloads`
  - `test_wrong_text_model_callbacks_preserve_precompile_contract`
  - `test_pattern_helper_collection_replacement_wrong_text_model_rows_stay_anchored_to_published_correctness_cases`
  - `test_standard_benchmark_haystack_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio`

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_preserves_wrong_text_model_rows_until_helper_invocation or run_internal_workload_probe_measures_wrong_text_model_contract_workloads or wrong_text_model_callbacks_preserve_precompile_contract or pattern_helper_collection_replacement_wrong_text_model_rows_stay_anchored_to_published_correctness_cases or standard_benchmark_haystack_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio'`
- `bash -lc "! rg -n 'def _pattern_collection_replacement_wrong_text_model_expected_callback_result\\(|def _pattern_collection_replacement_wrong_text_model_expected_build_calls\\(|def _pattern_collection_replacement_wrong_text_model_expected_callback_call\\(|def _run_cpython_pattern_collection_replacement_wrong_text_model_workload\\(|def _pattern_boundary_wrong_text_model_expected_callback_result\\(|def _pattern_boundary_wrong_text_model_expected_callback_call\\(|def _run_cpython_pattern_boundary_wrong_text_model_workload\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep the cleanup file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Do not widen into the compiled-pattern wrong-text-model owner specs, compiled-pattern success-owner helpers, keyword-error helper families, workload manifests under `benchmarks/workloads/`, harness code under `python/rebar_harness/`, or non-benchmark test files.
- Prefer deleting detached helper plumbing over introducing another abstraction layer.
- Do not edit README/current-status/backlog prose, reports, or implementation code.

## Notes
- `RBR-1045` is the next available unreserved task id in the current checkout:
  - `ops/tasks/done/` currently ends at `RBR-1044-catch-up-module-sub-bytes-repeated-count-one-pair.md`; and
  - `rg -n 'RBR-1045|RBR-1046|RBR-1047|RBR-1048|RBR-1049' ops/state/backlog.md ops/state/current_status.md` returned no matches in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-ready-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest dashboard shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled post-task refresh path.
- The duplication target was concrete in the pre-run checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` defined `WrongTextModelOwnerSpec` at line `17552`, `_pattern_collection_replacement_wrong_text_model_expected_callback_result(...)` at line `14996`, `_pattern_collection_replacement_wrong_text_model_expected_build_calls(...)` at line `15004`, `_pattern_collection_replacement_wrong_text_model_expected_callback_call(...)` at line `15018`, `_run_cpython_pattern_collection_replacement_wrong_text_model_workload(...)` at line `15042`, `_pattern_boundary_wrong_text_model_expected_callback_result(...)` at line `15067`, `_pattern_boundary_wrong_text_model_expected_callback_call(...)` at line `15082`, `_run_cpython_pattern_boundary_wrong_text_model_workload(...)` at line `15102`, `_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_OWNER_SPEC` at line `17766`, and `_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_OWNER_SPEC` at line `17795`;
  - the targeted pytest slice in Verification already passed (`50 passed, 671 deselected in 0.20s`); and
  - the negative `rg` check in Verification failed only because those exact helper definitions were still present.

## Completion Note
- 2026-03-23: Moved the direct-pattern wrong-text-model callback-result, callback-call, build-call, and CPython dispatch semantics into `WrongTextModelOwnerSpec` behind one file-local `direct_pattern_route`, removed the seven detached helper functions, and rewired the two direct-pattern owner specs plus the compiled-pattern build-call field names accordingly.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_preserves_wrong_text_model_rows_until_helper_invocation or run_internal_workload_probe_measures_wrong_text_model_contract_workloads or wrong_text_model_callbacks_preserve_precompile_contract or pattern_helper_collection_replacement_wrong_text_model_rows_stay_anchored_to_published_correctness_cases or standard_benchmark_haystack_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio'`
  - `bash -lc "! rg -n 'def _pattern_collection_replacement_wrong_text_model_expected_callback_result\\(|def _pattern_collection_replacement_wrong_text_model_expected_build_calls\\(|def _pattern_collection_replacement_wrong_text_model_expected_callback_call\\(|def _run_cpython_pattern_collection_replacement_wrong_text_model_workload\\(|def _pattern_boundary_wrong_text_model_expected_callback_result\\(|def _pattern_boundary_wrong_text_model_expected_callback_call\\(|def _run_cpython_pattern_boundary_wrong_text_model_workload\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
