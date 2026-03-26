## RBR-1379: Delete workload-case pair id wrappers

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the two thin workload/case-id wrapper helpers from the shared benchmark-support layer, and rewrite the collection-replacement and benchmark-support tests to derive those tuple projections directly where they are consumed.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Acceptance Criteria
- Delete these wrapper helpers from `tests/benchmarks/benchmark_test_support.py` without moving them sideways or replacing them with another generic helper:
  - `_workload_case_pairs_workload_ids`
  - `_workload_case_pairs_case_ids`
- Rewrite the affected collection-replacement support code and benchmark-support tests to keep the same structural guarantees through direct tuple projections from `workload_case_pairs`. Preserve these boundaries explicitly:
  - the collection-replacement route objects still expose the same `workload_ids()` and `case_ids()` results for their anchored workload/case pairs;
  - the grouped callable collection-replacement selectors and correctness-signature filters still match the same bounded workload ids and case ids as before;
  - `tests/benchmarks/test_benchmark_test_support.py` and `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` no longer treat those deleted wrappers as part of the shared helper surface, while still proving the surviving benchmark-support ownership and no-local-duplicate invariants precisely enough to catch regressions.
- Do not change benchmark manifests, workload selection, benchmark execution behavior, or tracked project-state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `bash -lc "! rg -n '\\b(_workload_case_pairs_workload_ids|_workload_case_pairs_case_ids)\\b' tests/benchmarks/benchmark_test_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py"`

## Constraints
- Prefer deleting the wrappers over recreating them under new names or replacing them with another shared projection helper.
- Keep the run bounded to this workload/case-id wrapper cleanup in the benchmark-support ownership layer.

## Notes
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1379|RBR-1380|RBR-1381' ops/state/current_status.md ops/state/backlog.md` returned no matches in this run
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate selection in this run:
  - Candidate 1 stayed in `tests/benchmarks/source_tree_benchmark_anchor_support.py`, but the remaining zero-gap and combined-slice assertion helpers there are still substantive shared benchmark-contract checks rather than a narrow wrapper pair.
  - `_workload_case_pairs_workload_ids()` and `_workload_case_pairs_case_ids()` in `tests/benchmarks/benchmark_test_support.py` are shared only as tuple-projection wrappers for `workload_case_pairs`, with the remaining live consumers bounded to `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` plus the support-surface tests.
  - Removing those two wrappers shrinks one more shared benchmark-support layer after the JSON burn-down without touching runtime harness behavior or published benchmark reports.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed with `281 passed in 1.51s`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed with `147 passed in 1.75s`
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed
  - `bash -lc "! rg -n '\\b(_workload_case_pairs_workload_ids|_workload_case_pairs_case_ids)\\b' tests/benchmarks/benchmark_test_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py"` currently fails with the exact definitions and call sites this task is intended to delete
