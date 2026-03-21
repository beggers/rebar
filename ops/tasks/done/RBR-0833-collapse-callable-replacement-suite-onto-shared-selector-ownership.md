# RBR-0833: Collapse the callable replacement suite onto shared selector ownership

Status: done
Owner: architecture-implementation
Created: 2026-03-21

## Goal
- Remove the last suite-local callable-manifest ownership rule from `tests/python/test_callable_replacement_parity_suite.py`.
- Keep the callable replacement parity surface anchored to `CALLABLE_REPLACEMENT_FIXTURE_SELECTOR` and the already-loaded selector bundles instead of re-deriving "callable" coverage by scanning every published fixture manifest for a `-callable-replacement-workflows` suffix.

## Deliverables
- `tests/python/test_callable_replacement_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_callable_replacement_parity_suite.py` no longer imports or uses `published_fixture_manifests`.
- `test_callable_replacement_selector_tracks_published_callable_manifests()` stops rebuilding the callable surface by suffix-filtering the full published fixture inventory:
  - delete the `published_fixture_manifests()` scan and the `manifest_id.endswith("-callable-replacement-workflows")` filter from that test;
  - keep `CALLABLE_FIXTURE_PATHS` as the source of truth for the callable selector path set; and
  - keep the test asserting that `FIXTURE_BUNDLES` resolves exactly the selector-owned paths in selector order.
- `test_callable_replacement_fixture_shape_contract()` no longer uses a manifest-id suffix as a category check:
  - replace `bundle.manifest.manifest_id.endswith("-callable-replacement-workflows")` with an assertion derived from the selector-owned callable bundle inventory already loaded in the suite; and
  - keep the existing layer/defaults/text-model/helper-count/pattern assertions unchanged unless a minimal refactor is needed to express the selector-backed invariant cleanly.
- Do not add another selector table, another manifest-id mirror, or another helper module in this run.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py`
  - `bash -lc "! rg -n 'published_fixture_manifests,|for manifest in published_fixture_manifests\\(|bundle\\.manifest\\.manifest_id\\.endswith\\(\\\"-callable-replacement-workflows\\\"\\)' tests/python/test_callable_replacement_parity_suite.py"`

## Constraints
- Keep this cleanup limited to `tests/python/test_callable_replacement_parity_suite.py`.
- Do not change `python/rebar_harness/correctness.py`, fixture modules under `tests/conformance/fixtures/`, benchmark files, reports, README copy, or tracked project-state prose in this run.
- Prefer deleting suite-local classification logic over introducing another wrapper or registry.

## Notes
- `RBR-0833` is free in the current checkout:
  - `ops/state/backlog.md` and `ops/state/current_status.md` reserve only `RBR-0832` on the active frontier in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -maxdepth 1 -type f -printf '%f\n' | rg '^RBR-0832|^RBR-0833|^RBR-0834' | sort` returned only `RBR-0832-catch-up-module-workflow-pattern-positional-indexlike-window-benchmark-quintet.md`.
- No blocked architecture task exists to reopen first, and rule 10 does not apply here:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the latest cycle completed architecture, architecture-implementation, feature work, cleanup, and reporting cleanly, so there is no inherited-dirty or post-task refresh bottleneck to yield to.
- JSON burn-down is complete in both tracked and live views, so this stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py` currently passes (`2747 passed in 2.12s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py::test_callable_replacement_selector_tracks_published_callable_manifests` currently passes (`1 passed in 0.13s`);
  - `bash -lc "! rg -n 'published_fixture_manifests,|for manifest in published_fixture_manifests\\(|bundle\\.manifest\\.manifest_id\\.endswith\\(\\\"-callable-replacement-workflows\\\"\\)' tests/python/test_callable_replacement_parity_suite.py"` currently fails exactly on the remaining suite-local ownership lines at `19`, `1448`, and `1523`; and
  - `tests/python/test_callable_replacement_parity_suite.py` already defines `CALLABLE_FIXTURE_PATHS = select_correctness_fixture_paths(CALLABLE_REPLACEMENT_FIXTURE_SELECTOR)` and loads `FIXTURE_BUNDLES` from that selector path set, so the suffix scan is a redundant second rule rather than a missing shared selector.
- This cleanup follows the same selector-first architecture path as the recent correctness-suite mirror removals:
  - `ops/tasks/done/RBR-0825-add-open-ended-mixed-replacement-selectors-and-collapse-singleton-path-mirrors.md`
  - `ops/tasks/done/RBR-0827-collapse-reintroduced-correctness-selector-filename-mirror.md`
  - `ops/tasks/done/RBR-0829-collapse-helper-backed-correctness-selector-ordering-onto-published-subsets.md`
  - `ops/tasks/done/RBR-0831-normalize-last-manual-correctness-selectors-onto-published-order.md`

## Completion
- 2026-03-21: Removed the suite-local `published_fixture_manifests` import and deleted the suffix-filter rebuild from `test_callable_replacement_selector_tracks_published_callable_manifests()`, leaving `CALLABLE_FIXTURE_PATHS` as the callable selector path source of truth.
- 2026-03-21: Replaced the callable fixture shape contract's manifest-id suffix check with a selector-backed lookup against the already loaded `FIXTURE_BUNDLES` inventory via `published_fixture_bundle_by_manifest_id(...)`.
- 2026-03-21: Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py`
  - `bash -lc "! rg -n 'published_fixture_manifests,|for manifest in published_fixture_manifests\\(|bundle\\.manifest\\.manifest_id\\.endswith\\(\\\"-callable-replacement-workflows\\\"\\)' tests/python/test_callable_replacement_parity_suite.py"`
