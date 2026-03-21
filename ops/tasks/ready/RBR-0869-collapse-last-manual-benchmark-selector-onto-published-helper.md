# RBR-0869: Collapse the last manual benchmark selector onto the published helper

Status: ready
Owner: architecture-implementation
Created: 2026-03-21

## Goal
- Remove the last nondefault benchmark selector row in `python/rebar_harness/benchmarks.py` that still hand-maintains a raw filename tuple even though it already resolves to the canonical `published-full-suite` order.
- Leave the benchmark harness with one rule for every nondefault selector: published-subset selectors derive from a helper instead of mixing the live ordered-subset contract with one manual exception.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` stops spelling this selector row as a raw tuple literal:
  - `BUILT_NATIVE_SMOKE_MANIFEST_SELECTOR`
- Replace that row with a published-subset helper and keep its resolved membership and order unchanged:
  - `select_benchmark_manifest_paths(BUILT_NATIVE_SMOKE_MANIFEST_SELECTOR)` still resolves to `pattern_boundary.py`, `collection_replacement_boundary.py`, and `literal_flag_boundary.py` in that order.
- Keep scope bounded to this cleanup:
  - do not change `PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR`;
  - do not add another selector registry, filesystem-discovery logic, or benchmark mode; and
  - do not change workload contents, benchmark reports, README copy, or tracked project-state prose.
- Any adjacent test edits stay limited to the files in Deliverables and only refresh expectations that were coupled to the old raw-tuple spelling.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'benchmark_manifest_selector or published_full_suite_selector or declared_benchmark_manifest_selectors'`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from rebar_harness.benchmarks import (
    BUILT_NATIVE_SMOKE_MANIFEST_SELECTOR,
    PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR,
    _BENCHMARK_MANIFEST_FILENAMES_BY_SELECTOR,
)

published = _BENCHMARK_MANIFEST_FILENAMES_BY_SELECTOR[
    PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR
]
selected = _BENCHMARK_MANIFEST_FILENAMES_BY_SELECTOR[
    BUILT_NATIVE_SMOKE_MANIFEST_SELECTOR
]
expected = tuple(name for name in published if name in set(selected))
assert selected == expected, (selected, expected)
print("ok")
PY`
  - `bash -lc "! rg -n '^\\s*BUILT_NATIVE_SMOKE_MANIFEST_SELECTOR: \\(' python/rebar_harness/benchmarks.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete the last manual nondefault benchmark selector exception, not to widen built-native smoke coverage, retune benchmark selection semantics, or add another helper layer beyond the minimal published-subset helper.
- Prefer deleting the exceptional raw tuple over layering another selector-specific expectation on top of it.

## Notes
- `RBR-0869` is the next available architecture task id in the current checkout:
  - `RBR-0868` is already occupied by the ready feature task in `ops/tasks/ready/`; and
  - `ops/state/backlog.md` plus `ops/state/current_status.md` do not reserve `RBR-0869`.
- No blocked architecture task exists to reopen first, and the queue/runtime state does not trigger the queue-stall no-op rule:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The cleanup target is concrete and already viable in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'benchmark_manifest_selector or published_full_suite_selector or declared_benchmark_manifest_selectors'` currently passes (`4 passed, 392 deselected in 0.11s`);
  - the ordered-subset probe in Acceptance currently prints `ok`, confirming the built-native smoke selector already matches the canonical published-full-suite order for its selected filenames; and
  - `bash -lc "! rg -n '^\\s*BUILT_NATIVE_SMOKE_MANIFEST_SELECTOR: \\(' python/rebar_harness/benchmarks.py"` currently fails exactly on this cleanup because that selector still appears as a raw tuple row.
- This stays on the same selector-normalization track as the recent correctness-side cleanup:
  - `RBR-0829`, `RBR-0831`, and `RBR-0867` already normalized the remaining correctness selectors onto published-order subset helpers; and
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` already enforces the same ordered-subset invariant for every nondefault benchmark selector, so this cleanup brings the live benchmark registry into line with the contract it already publishes.
