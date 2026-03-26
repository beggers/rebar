## RBR-1378: Delete source-tree zero-gap wrapper pair

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete two thin source-tree benchmark assertion wrappers from the shared source-tree support layer, and rewrite the combined source-tree benchmark suite to assert those zero-gap expectations directly where they are consumed.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Acceptance Criteria
- Delete these wrapper helpers from `tests/benchmarks/source_tree_benchmark_anchor_support.py` without moving them sideways or replacing them with another generic assertion helper:
  - `assert_single_manifest_zero_gap_scorecard_case_reuses_shared_expectation`
  - `assert_zero_gap_representative_workload_subset`
- Rewrite `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to keep the same structural guarantees through direct targeted assertions rather than through those wrappers. Preserve these boundaries explicitly:
  - the numbered-backreference and nested-group manifest checks still prove the single-manifest scorecard case reuses the combined-case representative measured workload ids and keeps zero known gaps;
  - the zero-gap selected-bytes representative checks still prove each expected workload id stays in the public representative set and, when explicit representatives exist, in the manifest expectation’s explicit representative set;
  - the counted-repeat fully-measured checks and all other existing source-tree benchmark coverage stay behaviorally unchanged.
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so it no longer treats those deleted wrappers as part of the shared support surface, while still proving the remaining source-tree support API and “no local combined-suite wrapper” invariants precisely enough to catch regressions.
- Do not change benchmark manifests, workload selection, benchmark execution behavior, or tracked project-state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n '\\b(assert_single_manifest_zero_gap_scorecard_case_reuses_shared_expectation|assert_zero_gap_representative_workload_subset)\\b' tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Prefer deleting the wrappers over recreating them under new names or pushing the same indirection into another support module.
- Keep the run bounded to this zero-gap wrapper cleanup in the source-tree benchmark support area.

## Notes
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1378|RBR-1379|RBR-1380' ops/state/current_status.md ops/state/backlog.md` returned no matches in this run
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate selection in this run:
  - The local `_collection_routed_owner_assignment_names()` helper in `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` was still too single-file and naming-local to justify the post-JSON architecture slot.
  - `assert_single_manifest_zero_gap_scorecard_case_reuses_shared_expectation()` and `assert_zero_gap_representative_workload_subset()` in `tests/benchmarks/source_tree_benchmark_anchor_support.py` are shared only between the combined source-tree benchmark suite and the support module’s own API-shape tests, and both wrappers just restate direct `source_tree_*case()` / representative-set expectations that already belong at the call sites.
  - Removing those two wrappers shrinks one more benchmark-support assertion layer after the JSON burn-down without touching runtime harness behavior or benchmark publications.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed with `387 passed, 1821 subtests passed in 13.49s`
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed
  - `rg -n "assert_single_manifest_zero_gap_scorecard_case_reuses_shared_expectation|assert_zero_gap_representative_workload_subset" tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently reports the exact wrapper definitions and call sites that this task is intended to delete
