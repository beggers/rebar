# RBR-0889: Collapse residual scorecard boundary pass-throughs

Status: ready
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the remaining accidental scorecard-plumbing leaks where owner tests still reach shared helper/report state through the harness runner modules instead of the shared scorecard descriptor/helper layer, so the module boundaries stay legible after the selector-registry cleanups in `RBR-0883`, `RBR-0885`, and `RBR-0887`.

## Deliverables
- `python/rebar_harness/correctness.py`
- `python/rebar_harness/benchmarks.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/conformance/test_combined_correctness_scorecards.py` stops reaching `ordered_published_subset_filenames(...)` through `rebar_harness.correctness`:
  - route that missing-filename contract check through a direct import from `rebar_harness.scorecard_io`;
  - keep the correctness-specific missing-filename error prefix and the current selector-contract assertion behavior unchanged in substance; and
  - do not add a new wrapper or re-export in `rebar_harness.correctness` to preserve the old path.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` stops reconstructing the tracked published benchmark report path under `REPO_ROOT`:
  - define `TRACKED_REPORT_PATH` from `benchmarks.SCORECARD_REPORT.published_path`;
  - keep the tracked-report regeneration assertions and the rest of the owner test behavior unchanged in substance; and
  - do not add another benchmark-specific descriptor alias or helper layer.
- `python/rebar_harness/correctness.py` and `python/rebar_harness/benchmarks.py` no longer import `ordered_published_subset_filenames` now that selector-registry construction lives behind `build_published_subset_registry(...)` and the remaining test call no longer reaches through those modules.
- Keep this cleanup structural only:
  - do not change selector names, selector membership, fixture/workload contents, scorecard payloads, reports, README copy, or tracked project-state prose; and
  - prefer deleting the residual pass-throughs over adding another compatibility shim.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'correctness_selector_subset_helper_keeps_correctness_specific_missing_filename_error'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'benchmark_selector_subset_helper_keeps_benchmark_specific_missing_filename_error or runner_regenerates_source_tree_scorecards'`
  - `bash -lc "! rg -n 'ordered_published_subset_filenames,' python/rebar_harness/correctness.py python/rebar_harness/benchmarks.py"`
  - `bash -lc "! rg -n 'correctness\\.ordered_published_subset_filenames\\(' tests/conformance/test_combined_correctness_scorecards.py"`
  - `rg -n '^TRACKED_REPORT_PATH = benchmarks\\.SCORECARD_REPORT\\.published_path$' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Constraints
- Keep the change limited to these residual scorecard-boundary pass-throughs. Do not widen into a larger report-descriptor refactor, selector rewrite, or benchmark/correctness harness behavior change.
- Preserve the current tracked report targets and missing-filename diagnostics exactly; the point is to remove accidental cross-module plumbing, not reinterpret report ownership.

## Notes
- `RBR-0889` is the next available architecture task id in the current checkout:
  - `RBR-0888` is already occupied by the ready feature task in `/home/ubuntu/rebar/ops/tasks/ready/RBR-0888-publish-module-workflow-compiled-pattern-compile-noflag-named-group-pair.md`;
  - `ops/state/backlog.md`, `ops/state/current_status.md`, and the task queues do not reserve `RBR-0889`; and
  - `/home/ubuntu/rebar/ops/tasks/blocked/` is empty, so there is no blocked architecture task to reopen, refine, or normalize first.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `/home/ubuntu/rebar/.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `/home/ubuntu/rebar/.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- This cleanup is concrete in the live checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'correctness_selector_subset_helper_keeps_correctness_specific_missing_filename_error'` currently passes (`1 passed, 43 deselected`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'benchmark_selector_subset_helper_keeps_benchmark_specific_missing_filename_error or runner_regenerates_source_tree_scorecards'` currently passes (`2 passed, 546 deselected, 192 subtests passed`);
  - `rg -n 'ordered_published_subset_filenames,' python/rebar_harness/correctness.py python/rebar_harness/benchmarks.py` currently reports the residual unused helper imports at `python/rebar_harness/correctness.py:27` and `python/rebar_harness/benchmarks.py:34`;
  - `rg -n 'correctness\\.ordered_published_subset_filenames\\(' tests/conformance/test_combined_correctness_scorecards.py` currently reports the remaining test-facing pass-through at line 4572; and
  - `rg -n '^TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "benchmarks" / "latest\\.py"$' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently reports the remaining hard-coded tracked benchmark report path at line 56.
- This is the next small boundary cleanup after the selector-registry simplifications already landed:
  - `RBR-0883` collapsed correctness selector-registry boilerplate onto one declarative subset table;
  - `RBR-0885` did the matching benchmark-side selector cleanup and removed its selector-membership mirror; and
  - `RBR-0887` removed the last correctness-side canonical selector-membership mirror, leaving these residual scorecard helper/report path pass-throughs as the next bounded post-JSON simplification.
