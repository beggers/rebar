# RBR-1198: Extract grouped-alternation benchmark anchor support

Status: done
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining grouped-alternation anchor-signature helpers that still live inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving that bounded support surface into one dedicated benchmark support module, so the giant combined suite stops owning another family of reusable benchmark-anchor plumbing directly.

## Deliverables
- `tests/benchmarks/grouped_alternation_benchmark_anchor_support.py`
- `tests/benchmarks/test_grouped_alternation_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Add one bounded support module at `tests/benchmarks/grouped_alternation_benchmark_anchor_support.py` for the grouped-alternation anchor-signature logic that currently lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Move these existing helpers into that support module without widening their scope or changing their behavior:
  - `_grouped_alternation_correctness_case_signature`
  - `_grouped_alternation_workload_args`
  - `_grouped_alternation_workload_signature`
  - `_grouped_alternation_replacement_correctness_case_signature`
  - `_grouped_alternation_replacement_workload_args`
  - `_grouped_alternation_replacement_workload_signature`
- Keep the extracted contract surface pinned to the current grouped-alternation behavior exactly:
  - preserve the current operation routing for `module.compile`, `module.search`, `pattern.fullmatch`, `module.sub`, `module.subn`, `pattern.sub`, and `pattern.subn`;
  - preserve the current `None` versus concrete pattern position in the returned signatures for module versus pattern helper routes;
  - preserve the current `freeze_signature_value(...)` treatment of positional args, the empty frozen kwargs tuple, the current `flags`/`text_model` handling, and the current "append count only when truthy" behavior for replacement workloads; and
  - keep the grouped-alternation and grouped-alternation-replacement `StandardBenchmarkAnchorContractDefinition` entries in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` on the same helper imports and current legacy-gap workload coverage after the move.
- Add one focused support test file at `tests/benchmarks/test_grouped_alternation_benchmark_anchor_support.py` that pins the extracted helpers directly on the live grouped-alternation manifests:
  - cover representative non-replacement rows from `benchmarks/workloads/grouped_alternation_boundary.py`;
  - cover representative replacement rows from `benchmarks/workloads/grouped_alternation_replacement_boundary.py`; and
  - cover the current rejecting assertion surface for unsupported grouped-alternation operations instead of silently accepting broader workload shapes.
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to import the new support module directly and delete the moved inline helper definitions instead of leaving aliases, wrappers, or duplicate copies behind.
- Keep this cleanup structural and bounded to the three files above; do not widen it into `python/rebar_harness/benchmarks.py`, benchmark workload manifests, correctness fixtures, reports, README text, or tracked ops/state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_grouped_alternation_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'grouped_alternation'`
- `bash -lc "! rg -n 'def _grouped_alternation_correctness_case_signature|def _grouped_alternation_workload_signature|def _grouped_alternation_replacement_correctness_case_signature|def _grouped_alternation_replacement_workload_signature' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep this cleanup structural and limited to the grouped-alternation benchmark-anchor support above.
- Prefer one ordinary support module plus one focused support test file over more owner-to-owner imports or another copied block inside the combined suite.
- Do not turn this into a broader breakup of `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`; this task is only the bounded grouped-alternation support extraction above.

## Notes
- `RBR-1198` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n "RBR-1198|RBR-1199|RBR-1200|RBR-1201|RBR-1202|RBR-1203" ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` matched only historical mentions inside completed task files, not a live reservation for this range in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Rule 10 does not block another architecture cleanup in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `Dirty worktree: false`, and `Last Cycle Anomalies: none`; and
  - the last cycle completed both the prior architecture cleanup and the current feature task through the normal done path.
- This simplification is still concrete and unfinished in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `16691` lines in this run;
  - `rg -n 'def _grouped_alternation_correctness_case_signature|def _grouped_alternation_workload_signature|def _grouped_alternation_replacement_correctness_case_signature|def _grouped_alternation_replacement_workload_signature' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still matches lines `9011`, `9063`, `9096`, and `9140`; and
  - neither `tests/benchmarks/grouped_alternation_benchmark_anchor_support.py` nor `tests/benchmarks/test_grouped_alternation_benchmark_anchor_support.py` exists in this checkout yet.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_grouped_alternation_benchmark_anchor_support.py` currently fails with `ERROR: file or directory not found: tests/benchmarks/test_grouped_alternation_benchmark_anchor_support.py`, which belongs exactly to the cleanup queued here;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'grouped_alternation'` returned `4 passed, 550 deselected in 0.18s` in this run; and
  - the negative `rg` check named above currently fails exactly on this cleanup because the grouped-alternation helpers still live in the combined suite.

## Completion Note
- Extracted the grouped-alternation benchmark anchor helpers into `tests/benchmarks/grouped_alternation_benchmark_anchor_support.py`, rewired the combined suite to import them directly, and added focused live-manifest support tests in `tests/benchmarks/test_grouped_alternation_benchmark_anchor_support.py`.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_grouped_alternation_benchmark_anchor_support.py`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'grouped_alternation'`
  - `bash -lc "! rg -n 'def _grouped_alternation_correctness_case_signature|def _grouped_alternation_workload_signature|def _grouped_alternation_replacement_correctness_case_signature|def _grouped_alternation_replacement_workload_signature' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
