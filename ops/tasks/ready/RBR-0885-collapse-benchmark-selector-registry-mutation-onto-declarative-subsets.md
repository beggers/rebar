# RBR-0885: Collapse benchmark selector registry mutation onto declarative subsets

Status: ready
Owner: architecture-implementation
Created: 2026-03-21

## Goal
- Delete the remaining post-declaration mutation in `python/rebar_harness/benchmarks.py` by expressing the nondefault benchmark selectors as one declarative selector-to-requested-filenames table and deriving the resolved registry through one shared construction path.
- Remove the reintroduced one-off selector-membership mirror from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the benchmark selector contract stays pinned to the harness-owned selector table instead of a second handwritten filename tuple.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` stops building `_BENCHMARK_MANIFEST_FILENAMES_BY_SELECTOR` through a post hoc `.update({...})` mutation:
  - keep `PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR` and `_PUBLISHED_BENCHMARK_MANIFEST_FILENAMES` as the single published-order source of truth;
  - add one plain declarative mapping for the nondefault selectors that stores only the selector-owned requested filenames in their intended membership order, without pre-resolving paths or adding another selector registry layer;
  - derive the resolved `_BENCHMARK_MANIFEST_FILENAMES_BY_SELECTOR` entries for those nondefault selectors through one shared code path that applies `ordered_published_subset_filenames(...)` with the existing `_PUBLISHED_BENCHMARK_MANIFEST_MISSING_ERROR_PREFIX`; and
  - keep selector names, selector membership, selector order, missing-filename error text, and `select_benchmark_manifest_paths(...)` behavior unchanged in substance.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` stops maintaining a second hard-coded canonical selector-membership table:
  - remove `CANONICAL_PUBLISHED_SUBSET_SELECTOR_EXPECTATIONS`;
  - keep the explicit built-native smoke selector membership contract covered by asserting directly against the harness-owned nondefault selector table or one equally direct live-registry assertion path, without adding another mirrored filename tuple in the test file; and
  - preserve the existing unknown-selector, published-full-suite inventory, declared-selector, and published-order subset invariants in substance.
- Keep this cleanup structural only:
  - do not change workload contents, benchmark modes, benchmark reports, README copy, or tracked project-state prose; and
  - prefer deleting the remaining mutation and mirrored expectation table over adding another helper family or another test-only abstraction layer.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'benchmark_manifest_selector or published_full_suite_selector or declared_benchmark_manifest_selectors'`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from rebar_harness import benchmarks

selector = benchmarks.BUILT_NATIVE_SMOKE_MANIFEST_SELECTOR
expected = (
    "pattern_boundary.py",
    "collection_replacement_boundary.py",
    "literal_flag_boundary.py",
)

assert benchmarks._NONDEFAULT_BENCHMARK_MANIFEST_SELECTOR_REQUESTED_FILENAMES[
    selector
] == expected
assert benchmarks._BENCHMARK_MANIFEST_FILENAMES_BY_SELECTOR[selector] == expected
print("ok")
PY`
  - `bash -lc "! rg -n '_BENCHMARK_MANIFEST_FILENAMES_BY_SELECTOR\\.update\\(' python/rebar_harness/benchmarks.py"`
  - `bash -lc "! rg -n '^CANONICAL_PUBLISHED_SUBSET_SELECTOR_EXPECTATIONS =' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep the change limited to benchmark selector registry construction plus the direct selector-contract coverage in the benchmark owner test.
- Do not widen into benchmark workload discovery, benchmark anchor expectations, built-native mode behavior, or a cross-harness selector rewrite in this run.

## Notes
- `RBR-0885` is the next available architecture task id in the current checkout:
  - `RBR-0884` is already occupied by the ready feature task in `/home/ubuntu/rebar/ops/tasks/ready/RBR-0884-catch-up-compiled-pattern-module-compile-bool-false-named-group-boundary-pair.md`;
  - `ops/state/backlog.md`, `ops/state/current_status.md`, and the live task queues do not reserve `RBR-0885`; and
  - `ops/tasks/blocked/` is empty, so there is no blocked architecture task to reopen, refine, or normalize first.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `/home/ubuntu/rebar/.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `/home/ubuntu/rebar/.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The cleanup is concrete and isolated in the live checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'benchmark_manifest_selector or published_full_suite_selector or declared_benchmark_manifest_selectors'` currently passes (`4 passed, 515 deselected`);
  - `rg -n '_BENCHMARK_MANIFEST_FILENAMES_BY_SELECTOR\\.update\\(' python/rebar_harness/benchmarks.py` currently reports the remaining registry mutation at line 91;
  - `rg -n '^CANONICAL_PUBLISHED_SUBSET_SELECTOR_EXPECTATIONS =' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently reports the reintroduced mirrored expectation table at line 59; and
  - the current selector resolution still matches the intended explicit membership for `BUILT_NATIVE_SMOKE_MANIFEST_SELECTOR`, so this task is structural cleanup rather than a behavior change.
- This is the benchmark-side follow-on to the adjacent selector simplification already landed on the correctness path:
  - `RBR-0879` collapsed the duplicated selector introspection helpers onto `scorecard_io`; and
  - `RBR-0883` collapsed the correctness selector registry boilerplate onto one declarative nondefault-selector table, leaving the benchmark registry mutation as the matching remaining selector-construction cleanup.
