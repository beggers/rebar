# RBR-0913: Collapse the compiled-pattern collection/replacement success contract manifest mirror

Status: done
Owner: architecture-implementation
Created: 2026-03-22
Completed: 2026-03-22

## Goal
- Remove the duplicated inline contract-manifest dict from the compiled-pattern collection/replacement success contract coverage in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, so the neighboring contract and anchor tests both build that manifest through one file-local owner helper instead of repeating the same `collection-replacement-boundary` structure.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` gains one tiny file-local helper for this owner slice, such as `_compiled_pattern_module_collection_replacement_success_manifest()` or an equivalently narrow name:
  - build the manifest from `COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_CASES` and `_compiled_pattern_module_collection_replacement_success_manifest_payload(case)`;
  - keep the manifest id exactly `collection-replacement-boundary`;
  - keep the defaults exactly `warmup_iterations=1`, `sample_iterations=1`, and `timed_samples=2`; and
  - keep the workload ordering identical to the current `COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_CASES` sequence.
- Both owner tests route through that helper instead of each rebuilding the same inline dict:
  - `test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_success_rows_until_helper_invocation()`;
  - `test_compiled_pattern_module_collection_replacement_success_rows_stay_anchored_to_published_correctness_cases()`.
- Preserve the current benchmark-owner behavior exactly:
  - keep the existing contract filenames `python_benchmark_compiled_pattern_collection_replacement_success_contract.py` and `python_benchmark_compiled_pattern_collection_replacement_success_anchor_contract.py`;
  - keep the current anchor expectations, workload ids, case ids, and `use_compiled_pattern` / `haystack_text_model` assertions unchanged; and
  - do not alter `COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_CASES`, `_compiled_pattern_module_collection_replacement_success_manifest_payload()`, `_compiled_pattern_module_collection_replacement_success_workload()`, runtime benchmark behavior, or correctness-anchor mapping.
- Keep this cleanup structural only:
  - do not widen into the adjacent compiled-pattern keyword, compile-success, boundary-success, or wrong-text-model contract families in the same file; and
  - prefer deleting the repeated inline manifest block over introducing a broader shared benchmark-helper layer.
- Verification passes with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_collection_replacement_success'`

## Constraints
- Keep the change limited to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`. Do not edit benchmark workload modules, harness runtime code, reports, README/state files, or task-queue plumbing in this run.
- Preserve the current compiled-pattern collection/replacement success contract coverage exactly; the point is to remove one owner-local manifest mirror, not to reinterpret what the benchmark owner measures.

## Notes
- `RBR-0913` is the next available architecture-task id in the current checkout:
  - `ops/state/backlog.md` and `ops/state/current_status.md` contain no reserved `RBR-0913` or later `RBR-091x` follow-on ids in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | rg '^RBR-091[0-9]|^RBR-09[2-9][0-9]'` shows only `RBR-0910`, `RBR-0911`, and `RBR-0912` already present.
- There is no blocked architecture task to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The mirror target is concrete and bounded in the live checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently repeats the same inline `manifest = {...}` block for this owner slice at lines `12965-12977` and `13017-13029`, with both copies using the same manifest id, defaults, and workload comprehension;
  - that duplication is confined to the compiled-pattern collection/replacement success contract coverage rather than the broader benchmark owner; and
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_collection_replacement_success'` currently passes (`17 passed, 538 deselected in 0.15s`).
- 2026-03-22T07:33:57+00:00: harness requeued after failed or incomplete run after run `20260322T073320Z-architecture-implementation-RBR-0913-collapse-compiled-pattern-collection-replacement-success-contract-manifest-mirror` (exit=1, timed_out=false).

## Completion
- Retired this stale ready task after confirming the checkout already satisfies the cleanup: `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` now defines `_compiled_pattern_module_collection_replacement_success_manifest()` and both owner tests route through that helper instead of rebuilding the same inline manifest dict twice.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_collection_replacement_success'`
- The ready entry remained behind because the prior architecture-implementation run hit model TPM rate limiting after landing the scoped refactor and before it could move the task file out of the queue; this run only normalized the queue to match the already-green checkout.
