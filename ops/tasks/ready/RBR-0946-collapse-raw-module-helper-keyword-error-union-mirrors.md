# RBR-0946: Collapse raw module-helper keyword-error union mirrors

Status: ready
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the detached raw module-helper keyword-error case layer from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the callback and internal-probe coverage derives from the same seven live workload rows already published across `benchmarks/workloads/module_boundary.py` and `benchmarks/workloads/collection_replacement_boundary.py` instead of maintaining a second handwritten tuple-and-builder surface.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines or relies on the detached raw keyword-error builder rooted at:
  - `def _module_helper_keyword_error_probe_workload(...)`
  - the repeated handwritten `@pytest.mark.parametrize(...)` tuple blocks that currently drive `test_module_helper_workflow_keyword_error_callbacks_match_cpython_exceptions(...)` and `test_run_internal_workload_probe_measures_module_helper_keyword_error_workloads(...)`
- Replace that mirror layer with file-local live source-workload selectors over the tracked manifests already used elsewhere in the file:
  - use `MODULE_BOUNDARY_MANIFEST_PATH` with `_selected_manifest_workloads(..., include_workload=_is_module_workflow_keyword_error_workload)` for the raw module-workflow rows; and
  - use `COLLECTION_REPLACEMENT_MANIFEST_PATH` with `_selected_manifest_workloads(...)` plus a file-local filter that keeps only raw non-compiled-pattern module helper keyword-error rows for the existing collection/replacement subset
- The combined live source surface resolves, in order, to exactly these seven workload ids:
  - `module-search-duplicate-flags-keyword-warm-str`
  - `module-fullmatch-unexpected-keyword-purged-str`
  - `module-split-duplicate-maxsplit-keyword-purged-str`
  - `module-sub-duplicate-count-keyword-warm-str`
  - `module-sub-unexpected-keyword-purged-str`
  - `module-sub-unexpected-keyword-after-positional-count-purged-str`
  - `module-subn-unexpected-keyword-after-positional-count-purged-bytes`
- Keep the callback-time materialization and exception checks on that exact seven-row surface:
  - `test_module_helper_workflow_keyword_error_callbacks_match_cpython_exceptions(...)` parameterizes over live `Workload` objects instead of handwritten tuples
  - the direct CPython baseline comes from the workload itself, reusing existing workload-execution helpers where they fit, instead of a new handwritten lambda table
  - the same materialization field-name expectations stay intact for the seven rows:
    - `module-search-duplicate-flags-keyword-warm-str` -> `("kwargs.flags",)`
    - `module-fullmatch-unexpected-keyword-purged-str` -> `("kwargs.missing",)`
    - `module-split-duplicate-maxsplit-keyword-purged-str` -> `("maxsplit", "kwargs.maxsplit")`
    - `module-sub-duplicate-count-keyword-warm-str` -> `("count", "kwargs.count")`
    - `module-sub-unexpected-keyword-purged-str` -> `("kwargs.missing",)`
    - `module-sub-unexpected-keyword-after-positional-count-purged-str` -> `("count", "kwargs.missing")`
    - `module-subn-unexpected-keyword-after-positional-count-purged-bytes` -> `("count", "kwargs.missing")`
- Keep the internal probe coverage on that same seven-row live surface:
  - `test_run_internal_workload_probe_measures_module_helper_keyword_error_workloads(...)` parameterizes over the live source workloads rather than the deleted tuple block and helper builder
  - the probe assertions still prove payload round-trip preservation for `expected_exception`, `kwargs`, and the source workload ids before measuring both adapters
- Keep this cleanup structural only:
  - do not edit `benchmarks/workloads/module_boundary.py`, `benchmarks/workloads/collection_replacement_boundary.py`, `python/rebar_harness/benchmarks.py`, reports, README/current-status/backlog prose, or any non-benchmark test file in this run
  - keep the implementation limited to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'module_helper_workflow_keyword_error or run_internal_workload_probe_measures_module_helper_keyword_error_workloads'`
- `bash -lc "! rg -n 'def _module_helper_keyword_error_probe_workload\\(|id=\\\"module-search-duplicate-flags-keyword\\\"|id=\\\"module-subn-unexpected-keyword-after-positional-count-bytes\\\"' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from tests.benchmarks.test_source_tree_combined_boundary_benchmarks import (
    COLLECTION_REPLACEMENT_MANIFEST_PATH,
    MODULE_BOUNDARY_MANIFEST_PATH,
    _is_collection_replacement_keyword_workload,
    _is_module_workflow_keyword_error_workload,
    _selected_manifest_workloads,
)

module_ids = tuple(
    workload.workload_id
    for workload in _selected_manifest_workloads(
        MODULE_BOUNDARY_MANIFEST_PATH,
        include_workload=_is_module_workflow_keyword_error_workload,
    )
)
collection_ids = tuple(
    workload.workload_id
    for workload in _selected_manifest_workloads(
        COLLECTION_REPLACEMENT_MANIFEST_PATH,
        include_workload=lambda workload: (
            _is_collection_replacement_keyword_workload(workload)
            and not workload.use_compiled_pattern
            and workload.operation in {"module.split", "module.sub", "module.subn"}
            and workload.workload_id
            in {
                "module-split-duplicate-maxsplit-keyword-purged-str",
                "module-sub-duplicate-count-keyword-warm-str",
                "module-sub-unexpected-keyword-purged-str",
                "module-sub-unexpected-keyword-after-positional-count-purged-str",
                "module-subn-unexpected-keyword-after-positional-count-purged-bytes",
            }
        ),
    )
)

assert module_ids == (
    "module-search-duplicate-flags-keyword-warm-str",
    "module-fullmatch-unexpected-keyword-purged-str",
)
assert collection_ids == (
    "module-split-duplicate-maxsplit-keyword-purged-str",
    "module-sub-duplicate-count-keyword-warm-str",
    "module-sub-unexpected-keyword-purged-str",
    "module-sub-unexpected-keyword-after-positional-count-purged-str",
    "module-subn-unexpected-keyword-after-positional-count-purged-bytes",
)

print("ok", len(module_ids) + len(collection_ids))
PY`

## Constraints
- Keep the task small enough for one architecture-implementation run. The objective is to delete one more detached benchmark-owner mirror layer, not to broaden the raw keyword-error benchmark surface, reinterpret which rows stay published, or refactor other contract sections in the same file.
- Prefer deriving any tiny file-local expectation helpers from the selected `Workload` objects and existing benchmark helper functions over introducing a new shared helper module, registry, or second id-keyed side table.

## Notes
- `RBR-0946` is the next available task id in the current checkout:
  - `rg -n 'RBR-0946|RBR-0947|RBR-0948|RBR-0949' ops/state/backlog.md ops/state/current_status.md` returned no reserved ids in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 12` currently ends at `RBR-0945-publish-module-workflow-module-split-unexpected-keyword-str-bytes-pair.md`
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
- The duplication target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'module_helper_workflow_keyword_error or run_internal_workload_probe_measures_module_helper_keyword_error_workloads'` currently passes (`24 passed, 582 deselected`)
  - the selector probe in Verification currently passes (`ok 7`), proving the seven-row surface already exists across the tracked manifests
  - `bash -lc "! rg -n 'def _module_helper_keyword_error_probe_workload\\(|id=\\\"module-search-duplicate-flags-keyword\\\"|id=\\\"module-subn-unexpected-keyword-after-positional-count-bytes\\\"' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently fails only because the detached mirror layer is still present at lines `13212`, `13399`, `13533`, `13607`, `13671`, and `13755`
