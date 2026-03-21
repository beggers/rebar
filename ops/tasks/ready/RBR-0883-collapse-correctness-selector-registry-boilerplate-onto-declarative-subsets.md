# RBR-0883: Collapse correctness selector registry boilerplate onto declarative subsets

Status: ready
Owner: architecture-implementation
Created: 2026-03-21

## Goal
- Delete the repeated per-selector `ordered_published_subset_filenames(...)` boilerplate in `python/rebar_harness/correctness.py` by expressing the nondefault correctness selectors as one declarative selector-to-requested-filenames table and deriving the resolved registry through one shared construction path.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/python/test_fixture_parity_support_contract.py`

## Acceptance Criteria
- `python/rebar_harness/correctness.py` stops building `_CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR` through one long `.update({...})` block that repeats the same helper call shape for every nondefault selector:
  - keep `PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR` and `_PUBLISHED_CORRECTNESS_FIXTURE_FILENAMES` as the single published-order source of truth;
  - add one plain declarative mapping for the nondefault selectors that stores only the selector-owned requested filenames in their intended membership order, without pre-resolving paths or introducing another selector registry layer;
  - derive the resolved `_CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR` entries for those nondefault selectors through one shared code path that applies `ordered_published_subset_filenames(...)` with the existing `_PUBLISHED_CORRECTNESS_FIXTURE_MISSING_ERROR_PREFIX`; and
  - keep selector names, selector membership, selector order, missing-filename error text, and `select_correctness_fixture_paths(...)` behavior unchanged in substance.
- Keep this cleanup structural only:
  - do not change fixture contents, manifest ids, reports, benchmark code, README copy, or tracked project-state prose;
  - do not widen into benchmark selector cleanup in this run; and
  - prefer deleting the repeated wrapper boilerplate over adding another bespoke helper family.
- `tests/python/test_fixture_parity_support_contract.py` keeps the selector-contract coverage anchored to the live registry behavior rather than the old construction style:
  - preserve the existing declared-selector, published-subset, and missing-filename invariants;
  - update the test only if a small contract adjustment is needed to keep those invariants explicit after the registry construction is simplified; and
  - do not add a mirrored selector table or another hand-maintained expectation layer.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py -k 'shared_correctness_fixture_selectors_resolve_published_paths or correctness_selector_subset_helper_keeps_fixture_specific_missing_filename_error or declared_correctness_fixture_selectors_match_registry_keys or declared_nondefault_correctness_fixture_selectors_are_parametrized_once'`
  - `bash -lc "! rg -n '_CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR\\.update\\(' python/rebar_harness/correctness.py"`
  - `bash -lc "[[ $(rg -F -c 'ordered_published_subset_filenames(' python/rebar_harness/correctness.py) -le 2 ]]"`

## Constraints
- Keep the change limited to correctness-selector registry construction. Do not turn it into a broader harness rewrite, selector renaming pass, or cross-harness abstraction sweep.
- Preserve the existing canonical published-order behavior for every selector; the point is to remove repeated construction plumbing, not to reinterpret any selector's scope.

## Notes
- `RBR-0883` is the next available architecture task id in the current checkout:
  - `RBR-0882` is already occupied by the ready feature task in `ops/tasks/ready/RBR-0882-catch-up-compiled-pattern-module-compile-int-zero-named-group-boundary-pair.md`;
  - `ops/state/backlog.md`, `ops/state/current_status.md`, and the task queues do not reserve `RBR-0883`; and
  - `ops/tasks/blocked/` is empty, so there is no blocked architecture task to reopen, refine, or normalize first.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- This exact cleanup is still live in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py -k 'shared_correctness_fixture_selectors_resolve_published_paths or correctness_selector_subset_helper_keeps_fixture_specific_missing_filename_error or declared_correctness_fixture_selectors_match_registry_keys or declared_nondefault_correctness_fixture_selectors_are_parametrized_once'` currently passes (`22 passed, 288 deselected`);
  - `bash -lc "! rg -n '_CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR\\.update\\(' python/rebar_harness/correctness.py"` currently fails because the file still contains the single long `.update(...)` construction block;
  - `bash -lc "[[ $(rg -F -c 'ordered_published_subset_filenames(' python/rebar_harness/correctness.py) -le 2 ]]"` currently fails because `python/rebar_harness/correctness.py` still contains 19 per-selector calls; and
  - `ops/tasks/`, `ops/state/`, and the latest architecture done tasks show adjacent selector-ordering and helper-consolidation work, but no existing ready or blocked task removes this remaining correctness-registry construction boilerplate.
