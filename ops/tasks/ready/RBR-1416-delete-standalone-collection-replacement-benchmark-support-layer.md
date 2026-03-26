## RBR-1416: Delete the standalone collection-replacement benchmark support layer

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove the dedicated `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` layer now that the repo is already at zero tracked and live JSON blobs.
- The collection/replacement benchmark lane is the last standalone owner module beside the shared `benchmark_test_support.py` and the broader `source_tree_benchmark_anchor_support.py` layer, and the current split keeps one more import path, owner alias surface, and deleted-module guard target alive than the checkout needs.
- Fold that owner surface into `tests/benchmarks/source_tree_benchmark_anchor_support.py` so the benchmark harness carries one fewer bespoke owner module.

## Deliverables
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` (delete)
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`

## Acceptance Criteria
- Delete `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`.
- Recreate the deleted module's public owner surface on `tests/benchmarks/source_tree_benchmark_anchor_support.py` with the same behavior for the collection/replacement lane, including:
  - `COLLECTION_REPLACEMENT_STANDARD_BENCHMARK_DEFINITIONS`
  - the `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_*` contract specs, source workload sets, surfaces, and parameter tuples
  - the collection/replacement keyword, positional-indexlike, literal-replacement, grouped-callable, and wrong-text-model workload selectors and signature helpers currently asserted by the scoped owner tests
  - the `CONDITIONAL_GROUP_EXISTS_*_WORKLOAD_IDS` constants and `COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS`
- Update the scoped benchmark-owner tests so the collection/replacement lane is asserted as source-tree-owned rather than routed through a dedicated `collection_replacement_benchmark_anchor_support` module.
- Add or update deleted-module assertions in `tests/benchmarks/test_benchmark_test_support.py` so the removed module is required to stay absent and unimportable, following the existing deleted-support-module pattern in that file.
- Remove live imports of `tests.benchmarks.collection_replacement_benchmark_anchor_support` from the files listed above.
- Keep genuinely shared helpers in `tests/benchmarks/benchmark_test_support.py`; this task should delete a support module, not reopen another helper-by-helper migration inside shared support.
- Do not widen into benchmark manifest edits, benchmark report regeneration, README/status updates, or non-benchmark test support.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py -q`
- `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py`
- `bash -lc '! test -e tests/benchmarks/collection_replacement_benchmark_anchor_support.py'`

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the runtime counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` only contained `.gitkeep`, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1416|RBR-1417|RBR-1418" ops/state/current_status.md ops/state/backlog.md ops/state/decision_log.md ops/tasks` found no reserved future-id use for `RBR-1416`; the only hits were historical notes inside completed `RBR-1414` and `RBR-1415` task files.
- Candidate selection in this run:
  - `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` is still a standalone owner module with test-only consumers in the benchmark support/test layer.
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` already imports that module, so deleting it removes one whole owner layer and one import path instead of just shaving another local helper.
  - I stopped after this first viable post-JSON candidate because it deletes an entire benchmark-support module, which is the highest-payoff simplification still visible in the checkout.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py -q` passed with `838 passed, 1557 subtests passed in 15.36s`.
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py` passed.
  - `bash -lc '! test -e tests/benchmarks/collection_replacement_benchmark_anchor_support.py'` currently fails only because the standalone support module still exists, which is the exact cleanup this task queues.
