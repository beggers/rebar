# RBR-0948: Collapse compiled-pattern module-helper keyword precompile anchor mirrors

Status: ready
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the remaining handwritten three-row precompile-anchor mirror from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the compiled-pattern module-helper keyword precompile coverage derives from the same live eleven-row source-workload surface already selected from `benchmarks/workloads/collection_replacement_boundary.py` instead of re-looking up three ids through a detached helper-and-tuple layer.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines or relies on the detached single-id lookup helper:
  - `def _compiled_pattern_module_helper_keyword_source_workload(...)`
- Replace the handwritten three-row `@pytest.mark.parametrize(...)` tuple that currently drives `test_compiled_pattern_module_helper_keyword_callbacks_precompile_first_argument_before_timing(...)` with a file-local live selector or projection over `_compiled_pattern_module_helper_keyword_source_workloads()`:
  - keep the selector local to this file; do not add a new shared helper module, registry, or checked-in data layer
  - the selected anchor workloads must still resolve, in order, to exactly:
    - `module-split-maxsplit-keyword-purged-str-compiled-pattern`
    - `module-sub-count-keyword-warm-str-compiled-pattern`
    - `module-subn-count-keyword-purged-bytes-compiled-pattern`
- Keep the precompile-first callback coverage on that exact live three-row surface:
  - `test_compiled_pattern_module_helper_keyword_callbacks_precompile_first_argument_before_timing(...)` parameterizes over live `Workload` objects rather than a handwritten tuple of repeated id lookups
  - the test still proves the same build-call and callback-call expectations for the split/sub/subn anchor examples by deriving them from `_compiled_pattern_module_helper_keyword_expected_build_calls(...)` and `_compiled_pattern_module_helper_keyword_expected_callback_call(...)`
  - the callback still returns the same bounded result surface: `"module-result"` for `module.split` / `module.sub` and `("module-result", 0)` for `module.subn`
- Keep the rest of the compiled-pattern module-helper keyword contract unchanged:
  - do not edit `benchmarks/workloads/collection_replacement_boundary.py`, `python/rebar_harness/benchmarks.py`, reports, README/current-status/backlog prose, or any non-benchmark test file in this run
  - do not broaden beyond the existing eleven-row compiled-pattern module-helper keyword carrier surface or the existing three anchor ids above
  - keep the implementation limited to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword_callbacks_precompile_first_argument_before_timing or compiled_pattern_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time or run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_workloads'`
- `bash -lc "! rg -n 'def _compiled_pattern_module_helper_keyword_source_workload\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from tests.benchmarks.test_source_tree_combined_boundary_benchmarks import (
    _compiled_pattern_module_helper_keyword_source_workloads,
)

anchor_ids = (
    "module-split-maxsplit-keyword-purged-str-compiled-pattern",
    "module-sub-count-keyword-warm-str-compiled-pattern",
    "module-subn-count-keyword-purged-bytes-compiled-pattern",
)
selected = tuple(
    workload.workload_id
    for workload in _compiled_pattern_module_helper_keyword_source_workloads()
    if workload.workload_id in anchor_ids
)

assert selected == anchor_ids, selected
print("ok", len(selected))
PY`

## Constraints
- Keep the task small enough for one architecture-implementation run. The objective is to delete one remaining owner-local tuple mirror, not to rewrite the whole compiled-pattern keyword contract section or reinterpret which workloads stay published.
- Prefer deriving any tiny anchor selector directly from `_compiled_pattern_module_helper_keyword_source_workloads()` over introducing another id-keyed case table, tuple constant, or dataclass.

## Notes
- `RBR-0948` is the next available task id in the current checkout:
  - `rg -n 'RBR-0948|RBR-0949|RBR-0950|RBR-0951' ops/state/backlog.md ops/state/current_status.md` returned no matches in this run, so no reserved frontier ids block `RBR-0948`
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 12` currently ends at `RBR-0947-catch-up-raw-module-split-unexpected-keyword-str-bytes-boundary-pair.md`
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The shared-ready-queue stall rule does not apply in this run:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
- The target duplication is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword_callbacks_precompile_first_argument_before_timing or compiled_pattern_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time or run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_workloads'` currently passes (`36 passed, 578 deselected`)
  - the anchor-surface probe in Verification currently passes (`ok 3`), proving the exact split/sub/subn precompile anchors already exist on the live eleven-row source surface without another handwritten id table
  - `bash -lc "! rg -n 'def _compiled_pattern_module_helper_keyword_source_workload\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently fails only because the detached lookup helper is still present at line `13574`, with the remaining mirror calls at lines `13904`, `13908`, `13913`, `13920`, `13924`, `13929`, `13936`, `13940`, and `13945`
