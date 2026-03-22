## RBR-0944: Collapse compiled-pattern module-helper keyword-error contract mirrors

Status: done
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the detached compiled-pattern module-helper keyword-error contract layer from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the same eight-row surface already published in `benchmarks/workloads/collection_replacement_boundary.py` drives the contract manifest, payload round-trip checks, probe coverage, and callback/precompile checks instead of maintaining a second handwritten field-tuple representation.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer keeps the compiled-pattern module-helper keyword-error surface on the detached field-by-field builder currently rooted at:
  - `def _compiled_pattern_module_helper_keyword_error_workload(...)`
  - the repeated handwritten `@pytest.mark.parametrize(...)` tuples that currently spell rows such as `module-split-duplicate-maxsplit-keyword-str-compiled-pattern` and `module-subn-unexpected-keyword-after-positional-count-bytes-compiled-pattern`
- Replace that mirror layer with live manifest-selected `Workload` rows from `COLLECTION_REPLACEMENT_MANIFEST_PATH`, following the same local selector pattern already used by the compiled-pattern collection/replacement success and wrong-text-model sections:
  - use `_selected_manifest_workloads(...)`
  - use the existing `_is_collection_replacement_compiled_pattern_keyword_error_workload(...)` predicate
  - keep the change file-local; do not add a new shared helper module, registry, or tracked manifest data layer
- The manifest-selected source workload ids resolve, in order, to exactly:
  - `module-split-duplicate-maxsplit-keyword-purged-str-compiled-pattern`
  - `module-split-unexpected-keyword-purged-bytes-compiled-pattern`
  - `module-sub-duplicate-count-keyword-warm-str-compiled-pattern`
  - `module-sub-unexpected-keyword-purged-str-compiled-pattern`
  - `module-sub-unexpected-keyword-after-positional-count-purged-str-compiled-pattern`
  - `module-subn-duplicate-count-keyword-warm-bytes-compiled-pattern`
  - `module-subn-unexpected-keyword-purged-bytes-compiled-pattern`
  - `module-subn-unexpected-keyword-after-positional-count-purged-bytes-compiled-pattern`
- The standard manifest-preservation test stops embedding a handwritten triple-quoted manifest and instead derives its contract rows from those eight source workloads, preserving:
  - the same source-workload order
  - generated contract ids with a `-contract` suffix
  - `use_compiled_pattern is True` on every generated contract workload
  - the same `count`/`maxsplit` values, `kwargs` values, `expected_exception` payloads, and `str` versus `bytes` payload typing
  - `haystack_text_model is None` across the selected surface
- The callback/probe/precompile coverage stays on the same published eight-row surface instead of re-stating it as tuple literals:
  - `test_compiled_pattern_module_helper_keyword_error_callbacks_match_cpython_exceptions(...)` parameterizes over the live source workloads and still proves the same numeric materialization field names and exact CPython exception text
  - `test_run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_error_workloads(...)` parameterizes over the live source workloads and still proves the same payload round-trip behavior plus measured probes for both adapters
  - `test_compiled_pattern_module_helper_callbacks_precompile_first_argument_before_timing(...)` derives its expected build/callback calls from the live source workloads instead of ad hoc tuple literals and still proves compiled-pattern-first-argument precompile behavior before helper invocation
- Keep this cleanup structural only:
  - do not edit `benchmarks/workloads/collection_replacement_boundary.py`, `python/rebar_harness/benchmarks.py`, reports, README/current-status/backlog prose, or other benchmark-contract sections in this run
  - keep the implementation limited to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword_error'`
- `bash -lc "! rg -n 'def _compiled_pattern_module_helper_keyword_error_workload\\(|id=\\\"module-split-duplicate-maxsplit-keyword-str-compiled-pattern\\\"|id=\\\"module-subn-unexpected-keyword-after-positional-count-bytes-compiled-pattern\\\"' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from tests.benchmarks.test_source_tree_combined_boundary_benchmarks import (
    COLLECTION_REPLACEMENT_MANIFEST_PATH,
    _is_collection_replacement_compiled_pattern_keyword_error_workload,
    _selected_manifest_workloads,
)

workloads = tuple(
    workload.workload_id
    for workload in _selected_manifest_workloads(
        COLLECTION_REPLACEMENT_MANIFEST_PATH,
        include_workload=_is_collection_replacement_compiled_pattern_keyword_error_workload,
    )
)

assert workloads == (
    "module-split-duplicate-maxsplit-keyword-purged-str-compiled-pattern",
    "module-split-unexpected-keyword-purged-bytes-compiled-pattern",
    "module-sub-duplicate-count-keyword-warm-str-compiled-pattern",
    "module-sub-unexpected-keyword-purged-str-compiled-pattern",
    "module-sub-unexpected-keyword-after-positional-count-purged-str-compiled-pattern",
    "module-subn-duplicate-count-keyword-warm-bytes-compiled-pattern",
    "module-subn-unexpected-keyword-purged-bytes-compiled-pattern",
    "module-subn-unexpected-keyword-after-positional-count-purged-bytes-compiled-pattern",
)

print("ok", len(workloads))
PY`

## Constraints
- Keep the task small enough for one architecture-implementation run. The objective is to delete one more detached benchmark-contract mirror layer, not to broaden benchmark semantics or rewrite nearby benchmark suites.
- Preserve the current eight-row benchmark surface exactly. This task should not reinterpret which compiled-pattern module helper keyword-error rows stay published on the shared collection/replacement boundary.

## Notes
- `RBR-0944` is the next available task id in the current checkout:
  - `rg -n 'RBR-0944|RBR-0945|RBR-0946|RBR-0947' ops/state/backlog.md ops/state/current_status.md` returned no reserved ids in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 12` currently ends at `RBR-0943-catch-up-raw-module-sub-subn-unexpected-keyword-after-positional-count-boundary-pair.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The shared-ready-queue stall rule does not apply in this run:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh/commit path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run is intentionally using the post-JSON fallback lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
- The target duplication is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword_error'` currently passes (`25 passed, 577 deselected, 8 subtests passed`)
  - the selector probe in Verification currently passes (`ok 8`), proving the eight-row surface already exists in `benchmarks/workloads/collection_replacement_boundary.py`
  - `bash -lc "! rg -n 'def _compiled_pattern_module_helper_keyword_error_workload\\(|id=\\\"module-split-duplicate-maxsplit-keyword-str-compiled-pattern\\\"|id=\\\"module-subn-unexpected-keyword-after-positional-count-bytes-compiled-pattern\\\"' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently fails only because the exact mirror layer is still present at lines `16424`, `16667`, `16772`, `16851`, and `16949`

## Completion Note
- Replaced the detached compiled-pattern module-helper keyword-error builder and handwritten parameter tuples in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` with file-local manifest-selected source workloads plus local contract payload helpers derived from `COLLECTION_REPLACEMENT_MANIFEST_PATH`.
- Kept the same eight source workload ids and order, generated `-contract` ids from them, preserved `use_compiled_pattern`, `count`/`maxsplit`, `kwargs`, expected exception payloads, `str`/`bytes` typing, and `haystack_text_model is None`, and moved the callback/probe/precompile checks onto that same live manifest-selected surface.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword_error'`
  - `bash -lc "! rg -n 'def _compiled_pattern_module_helper_keyword_error_workload\\(|id=\\\"module-split-duplicate-maxsplit-keyword-str-compiled-pattern\\\"|id=\\\"module-subn-unexpected-keyword-after-positional-count-bytes-compiled-pattern\\\"' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
  - the selector assertion from the task (`ok 8`)
