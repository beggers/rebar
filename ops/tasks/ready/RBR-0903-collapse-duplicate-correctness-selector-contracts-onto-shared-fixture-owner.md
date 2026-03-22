# RBR-0903: Collapse duplicate correctness selector contracts onto the shared fixture owner

Status: ready
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the duplicate correctness-selector contract block from `tests/conformance/test_combined_correctness_scorecards.py` so the shared selector registry invariants live only in `tests/python/test_fixture_parity_support_contract.py`, while the combined correctness owner keeps only scorecard/publication-specific coverage.

## Deliverables
- `tests/conformance/test_combined_correctness_scorecards.py`

## Acceptance Criteria
- `tests/conformance/test_combined_correctness_scorecards.py` stops owning selector-registry coverage that is already pinned in `tests/python/test_fixture_parity_support_contract.py`:
  - delete these six duplicate tests from the combined correctness owner:
    - `test_default_correctness_fixture_selector_rejects_unknown_selector`
    - `test_default_correctness_published_full_suite_selector_covers_tracked_fixtures`
    - `test_shared_correctness_fixture_selectors_resolve_published_subset_invariants`
    - `test_correctness_selector_subset_helper_keeps_correctness_specific_missing_filename_error`
    - `test_declared_correctness_fixture_selectors_match_registry_keys`
    - `test_default_correctness_published_manifest_helper_is_cached_and_preserves_selector_order`
  - keep the selector-inventory contract itself alive in `tests/python/test_fixture_parity_support_contract.py`; do not re-home it to another new file or helper.
- Trim the now-unused selector-only imports from `tests/conformance/test_combined_correctness_scorecards.py`:
  - remove `declared_string_constants_by_suffix`; and
  - remove `ordered_published_subset_filenames`.
- Keep the combined correctness owner focused on scorecard/publication behavior:
  - preserve the tracked-report, representative-case, manifest-expectation, harness-rerun, and published-scorecard assertions that are unique to `tests/conformance/test_combined_correctness_scorecards.py`;
  - do not delete or weaken `published_fixture_manifests()` coverage that is still needed for scorecard-specific manifest ordering and expectation checks; and
  - do not change `python/rebar_harness/correctness.py`, fixture modules under `tests/conformance/fixtures/`, reports, README text, or tracked project-state prose in this run.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py tests/python/test_fixture_parity_support_contract.py`
  - `bash -lc "! rg -n 'def test_default_correctness_fixture_selector_rejects_unknown_selector|def test_default_correctness_published_full_suite_selector_covers_tracked_fixtures|def test_shared_correctness_fixture_selectors_resolve_published_subset_invariants|def test_correctness_selector_subset_helper_keeps_correctness_specific_missing_filename_error|def test_declared_correctness_fixture_selectors_match_registry_keys|def test_default_correctness_published_manifest_helper_is_cached_and_preserves_selector_order' tests/conformance/test_combined_correctness_scorecards.py"`
  - `bash -lc "! rg -n 'declared_string_constants_by_suffix|ordered_published_subset_filenames' tests/conformance/test_combined_correctness_scorecards.py"`

## Constraints
- Keep this cleanup limited to deleting duplicate selector-contract coverage from `tests/conformance/test_combined_correctness_scorecards.py`. Do not widen into benchmark tests, selector-registry rewrites, fixture-order changes, or scorecard payload changes.
- Prefer deleting the duplicate report-owner assertions over adding another shared helper, another selector test module, or another indirection layer between the scorecard owner and the shared fixture contract.

## Notes
- `RBR-0903` is the next available architecture task id in the current checkout:
  - `rg -n 'RBR-0903' ops/state/backlog.md ops/state/current_status.md` returned no reserved follow-on id; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | rg '^RBR-0903'` returned no existing task file.
- There is no blocked architecture task to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplicate surface is concrete in the live checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py tests/python/test_fixture_parity_support_contract.py` currently passes (`354 passed, 2190 subtests passed in 31.33s`);
  - `rg -n 'def test_default_correctness_fixture_selector_rejects_unknown_selector|def test_default_correctness_published_full_suite_selector_covers_tracked_fixtures|def test_shared_correctness_fixture_selectors_resolve_published_subset_invariants|def test_correctness_selector_subset_helper_keeps_correctness_specific_missing_filename_error|def test_declared_correctness_fixture_selectors_match_registry_keys|def test_default_correctness_published_manifest_helper_is_cached_and_preserves_selector_order' tests/conformance/test_combined_correctness_scorecards.py` currently returns exactly the six duplicate test definitions at lines `4508`, `4515`, `4534`, `4566`, `4588`, and `4601`;
  - `rg -n 'declared_string_constants_by_suffix|ordered_published_subset_filenames' tests/conformance/test_combined_correctness_scorecards.py` currently returns only the selector-only imports/usages at lines `17`, `18`, `4578`, and `4589`; and
  - the shared owner file `tests/python/test_fixture_parity_support_contract.py` already covers the same unknown-selector, published-full-suite inventory, ordered-subset, missing-filename, declared-selector, and manifest-helper cache invariants, so the combined scorecard owner is maintaining a second copy of the same contract today.
