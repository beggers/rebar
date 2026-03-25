## RBR-1276: Move direct-Pattern wrong-text-model contract support onto owner modules

Status: done
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Remove the remaining direct-`Pattern` wrong-text-model contract helpers that still live inside `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` and `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`, so the benchmark layer keeps those workload inventories, contract specs, callback-shape helpers, and CPython runtime probes in the existing owner support modules instead of in large test files.

## Deliverables
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`

## Acceptance Criteria
- Extend `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` so it becomes the single owner of the direct-`Pattern` collection/replacement wrong-text-model contract support surface currently defined in `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`:
  - `_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS`
  - `_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_CONTRACT_SPEC`
  - `_collection_replacement_wrong_text_model_source_workloads(...)`
  - `_collection_replacement_wrong_text_model_expected_callback_call(...)`
  - `_collection_replacement_wrong_text_model_expected_callback_result(...)`
  - `_run_cpython_collection_replacement_wrong_text_model_workload(...)`
- Extend `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py` so it becomes the single owner of the direct-`Pattern` pattern-boundary wrong-text-model contract support surface currently defined in `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`:
  - `_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS`
  - `_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC`
  - `_pattern_boundary_wrong_text_model_source_workloads(...)`
  - `_pattern_boundary_wrong_text_model_expected_callback_call(...)`
  - `_run_cpython_pattern_boundary_wrong_text_model_workload(...)`
- Delete the duplicated local definitions from both test modules and import the owner-owned support surface directly instead.
- Preserve current behavior exactly:
  - keep the same workload ids, ordering, manifest ids, timing scopes, excluded-field sets, and helper-call contract shapes for both wrong-text-model surfaces;
  - keep the same CPython error-triggering behavior and callback result expectations for `pattern.split`, `pattern.sub`, `pattern.subn`, `pattern.search`, `pattern.match`, and `pattern.fullmatch`;
  - keep `_assert_wrong_text_model_payload_round_trip(...)` usage and expectations unchanged in both test files; and
  - keep the current cache-mode precompile behavior unchanged, preferably by reusing the existing shared precompile-call helper in `tests/benchmarks/source_tree_contract_benchmark_support.py` instead of leaving fresh local build-call helpers in the tests.
- Keep the cleanup structural and bounded to the four files above, plus `tests/benchmarks/source_tree_contract_benchmark_support.py` only if a tiny helper rename or generalization is required to support the move. Do not widen it into `python/rebar_harness/benchmarks.py`, workload manifests, other benchmark suites, README text, or tracked `ops/state/` prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
- `bash -lc "! rg -n 'def _collection_replacement_wrong_text_model_source_workloads\\(|def _collection_replacement_wrong_text_model_expected_build_calls\\(|def _collection_replacement_wrong_text_model_expected_callback_call\\(|def _collection_replacement_wrong_text_model_expected_callback_result\\(|def _run_cpython_collection_replacement_wrong_text_model_workload\\(|^_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS\\s*=|^_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_CONTRACT_SPEC\\s*=|def _pattern_boundary_wrong_text_model_source_workloads\\(|def _pattern_boundary_wrong_text_model_expected_build_calls\\(|def _pattern_boundary_wrong_text_model_expected_callback_call\\(|def _run_cpython_pattern_boundary_wrong_text_model_workload\\(|^_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS\\s*=|^_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC\\s*=' tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py"`

## Constraints
- Prefer consolidating onto the existing owner modules in `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` and `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py` over creating another support file. The point is to finish the ownership move, not to add a parallel helper layer.
- Keep imports direct. Do not leave compatibility aliases or forwarding wrappers in the test files.
- Do not change workload selection predicates, callback routing semantics, or error expectations in this task.

## Notes
- `RBR-1276` is the next available unreserved task id in this checkout:
  - `rg -n "RBR-1276|RBR-1277|RBR-1278|RBR-1279|RBR-1280" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked -g '*.md'` returned no matches in this run.
- No blocked architecture task exists to reopen or retire first in this run.
- JSON burn-down is complete in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue and runtime state are not currently stalled:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready tasks, no blocked tasks, and no last-cycle anomalies; and
  - `architecture-implementation` finished `RBR-1275` as `done` in the latest recorded cycle.
- The ownership split is concrete in the live checkout:
  - `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` still defines the direct-`Pattern` collection/replacement wrong-text-model source-workload ids, contract spec, source-workload loader, expected build/callback helpers, and CPython runtime probe locally; and
  - `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py` still defines the direct-`Pattern` pattern-boundary wrong-text-model source-workload ids, contract spec, source-workload loader, expected build/callback helpers, and CPython runtime probe locally.
- Completion:
  - Moved the direct-`Pattern` collection/replacement wrong-text-model source-workload ids, contract spec, source-workload loader, callback expectation helpers, callback result helper, and CPython runtime probe onto `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`.
  - Moved the direct-`Pattern` pattern-boundary wrong-text-model source-workload ids, contract spec, source-workload loader, callback expectation helper, and CPython runtime probe onto `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py`.
  - Deleted the duplicated local definitions from both benchmark test modules and switched their precompile-call assertions to `compiled_pattern_contract_expected_build_calls(...)`.
- Verification status:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py` passed with `81 passed`.
  - The negative `rg` check in `Verification` now passes; the duplicated wrong-text-model helpers no longer exist in either test module.
