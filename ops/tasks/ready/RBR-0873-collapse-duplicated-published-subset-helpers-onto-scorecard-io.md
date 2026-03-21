# RBR-0873: Collapse duplicated published-subset helpers onto scorecard_io

Status: ready
Owner: architecture-implementation
Created: 2026-03-21

## Goal
- Delete the last duplicated "published full-suite ordered subset" helper bodies from the two harness entrypoints so correctness and benchmark selector tables flow through one shared implementation instead of keeping near-identical filename-filtering logic in both `python/rebar_harness/correctness.py` and `python/rebar_harness/benchmarks.py`.

## Deliverables
- `python/rebar_harness/scorecard_io.py`
- `python/rebar_harness/benchmarks.py`
- `python/rebar_harness/correctness.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/python/test_fixture_parity_support_contract.py`

## Acceptance Criteria
- `python/rebar_harness/scorecard_io.py` becomes the only shared owner of the ordered published-subset filename logic used by the harness entrypoints:
  - add one small helper that takes the published full-suite filename order plus an explicit selected filename set/list and returns the selected filenames in published-order form;
  - keep missing-filename validation in that shared path so callers can still surface specific error text; and
  - reuse the existing `scorecard_io` utility module instead of creating another selector module, another registry layer, or filesystem-discovery logic.
- `python/rebar_harness/benchmarks.py` stops defining `_published_benchmark_manifest_subset(...)`:
  - build `BUILT_NATIVE_SMOKE_MANIFEST_SELECTOR` through the shared helper in `python/rebar_harness/scorecard_io.py`;
  - keep `_BENCHMARK_MANIFEST_FILENAMES_BY_SELECTOR[PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR]` unchanged;
  - keep the built-native smoke selector resolving to `pattern_boundary.py`, `collection_replacement_boundary.py`, and `literal_flag_boundary.py` in that order; and
  - preserve the current benchmark-specific missing-filename error prefix `unknown published benchmark manifest filename(s): ...`.
- `python/rebar_harness/correctness.py` stops defining `_published_fixture_subset(...)`:
  - build every nondefault selector row through the shared helper in `python/rebar_harness/scorecard_io.py`;
  - keep `_CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR[PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR]` unchanged;
  - keep the current selector memberships and published-order resolution behavior unchanged for every nondefault correctness selector; and
  - preserve the current correctness-specific missing-filename error prefix `unknown published correctness fixture filename(s): ...`.
- Keep this cleanup structural only:
  - do not change selector names, selector membership, manifest or fixture contents, report outputs, README copy, or tracked project-state prose; and
  - do not add another test-only wrapper around `select_benchmark_manifest_paths(...)` or `select_correctness_fixture_paths(...)`.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and `tests/python/test_fixture_parity_support_contract.py` keep the selector contracts pinned after the helper consolidation:
  - retain the existing full-suite inventory, declared-selector, and ordered-subset invariants on both owner paths; and
  - add only the smallest adjacent coverage needed if the shared helper extraction would otherwise leave the benchmark- or correctness-specific error-text contract unpinned.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'benchmark_manifest_selector or published_full_suite_selector or declared_benchmark_manifest_selectors'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py -k 'correctness_fixture_selector or published_subset_selector or declared_correctness_fixture_selectors or published_full_suite_fixture_selector'`
  - `bash -lc "! rg -n '^def _published_(benchmark_manifest_subset|fixture_subset)\\(' python/rebar_harness/benchmarks.py python/rebar_harness/correctness.py"`

## Constraints
- Prefer deleting the duplicated helper bodies over introducing another selector abstraction family.
- Keep the shared helper generic only at the filename-ordering level. Do not turn this into a selector-registry rewrite, a manifest-discovery refactor, or a broader harness API cleanup.

## Notes
- `RBR-0873` is the next available architecture task id in the current checkout:
  - `ops/state/backlog.md`, `ops/state/current_status.md`, and `ops/tasks/` mention `RBR-0872` but do not reserve `RBR-0873`; and
  - no blocked architecture task exists to reopen first because `ops/tasks/blocked/` is empty.
- The queue/runtime state does not trigger the shared-ready-queue no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run should target remaining harness duplication instead of blob deletion:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The cleanup is concrete and already isolated in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'benchmark_manifest_selector or published_full_suite_selector or declared_benchmark_manifest_selectors'` currently passes (`4 passed, 423 deselected in 0.11s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py -k 'correctness_fixture_selector or published_subset_selector or declared_correctness_fixture_selectors or published_full_suite_fixture_selector'` currently passes (`26 passed, 269 deselected in 0.10s`);
  - `bash -lc "! rg -n '^def _published_(benchmark_manifest_subset|fixture_subset)\\(' python/rebar_harness/benchmarks.py python/rebar_harness/correctness.py"` currently fails exactly on this cleanup because both duplicated helper definitions still exist; and
  - `python/rebar_harness/scorecard_io.py` is already the shared utility home for cross-harness report/config plumbing, so promoting this last repeated ordered-subset helper there reduces code without adding a third selector-specific owner.
