# RBR-0875: Collapse repeated published bundle lookups onto a manifest-id map

Status: ready
Owner: architecture-implementation
Created: 2026-03-21

## Goal
- Delete the remaining repeated module-scope `published_fixture_bundle_by_manifest_id(...)` lookup chains from a few large parity-suite owners by promoting one canonical manifest-id bundle map helper in `tests/python/fixture_parity_support.py`, so published fixture bundles flow through one indexed lookup path instead of re-scanning the same loaded tuple six to eight times per file.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_grouped_capture_parity_suite.py`
- `tests/python/test_quantified_alternation_parity_suite.py`
- `tests/python/test_open_ended_quantified_group_parity_suite.py`

## Acceptance Criteria
- `tests/python/fixture_parity_support.py` exports one canonical helper for manifest-id-indexed published bundles:
  - add a small helper that takes an iterable of `FixtureBundle` values and returns a `dict[str, FixtureBundle]` keyed by `bundle.manifest.manifest_id`;
  - keep duplicate-manifest validation in that shared path, using the existing duplicate error text shape `published fixture bundles contain duplicate manifest_id ...`;
  - keep `published_fixture_bundle_by_manifest_id(...)` available for call sites that still need a one-off lookup, but route it through the shared indexed path or otherwise keep its current missing/duplicate error messages unchanged; and
  - do not add another selector registry, another fixture-loader layer, or another suite-local map helper family.
- `tests/python/test_fixture_parity_support_contract.py` pins the shared helper behavior:
  - add the smallest adjacent coverage needed for the new manifest-id map helper to prove it returns the expected bundles and rejects duplicate manifest ids; and
  - keep the existing `published_fixture_bundle_by_manifest_id(...)` success and failure contract coverage intact.
- `tests/python/test_grouped_capture_parity_suite.py`, `tests/python/test_quantified_alternation_parity_suite.py`, and `tests/python/test_open_ended_quantified_group_parity_suite.py` stop defining their module-scope bundle constants through repeated `published_fixture_bundle_by_manifest_id(FIXTURE_BUNDLES, ...)` calls:
  - build one local manifest-id map from the already-loaded `FIXTURE_BUNDLES` tuple in each file;
  - derive the existing top-level bundle constants from that map instead of rescanning the tuple for each manifest id;
  - preserve the current `FIXTURE_BUNDLES` load order, bundle membership, manifest ids, generated-spec ordering, and direct-test case ownership exactly; and
  - do not broaden the parity surface, change selected case ids, or move these suites onto another selector path.
- Keep this cleanup structural only:
  - do not change `python/rebar_harness/`, correctness fixtures, reports, README copy, or tracked project-state prose; and
  - do not collapse every remaining suite in the repo onto the new helper in this run if that would turn the task into a broad sweep instead of one bounded refactor.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py -k 'published_fixture_bundle_by_manifest_id or load_published_fixture_bundles'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py tests/python/test_quantified_alternation_parity_suite.py tests/python/test_open_ended_quantified_group_parity_suite.py`
  - `bash -lc "! rg -n '^[A-Z0-9_]+ = published_fixture_bundle_by_manifest_id\\($' tests/python/test_grouped_capture_parity_suite.py tests/python/test_quantified_alternation_parity_suite.py tests/python/test_open_ended_quantified_group_parity_suite.py"`

## Constraints
- Prefer deleting the repeated lookup chains over adding another parallel bundle-owner abstraction.
- Keep the shared helper scoped to manifest-id indexing for already-loaded bundles. Do not turn this into a broader selector rewrite, bundle-order refactor, or generic fixture-discovery layer.

## Notes
- `RBR-0875` is the next available architecture task id in the current checkout:
  - `RBR-0874` is already occupied by the ready feature task in `ops/tasks/ready/`; and
  - `ops/state/backlog.md`, `ops/state/current_status.md`, and the task queues do not reserve or occupy `RBR-0875`.
- No blocked architecture task exists to reopen first, and the queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run should target remaining harness duplication rather than blob deletion:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The cleanup is concrete and already isolated in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py -k 'published_fixture_bundle_by_manifest_id or load_published_fixture_bundles'` currently passes (`6 passed, 290 deselected in 0.08s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py tests/python/test_quantified_alternation_parity_suite.py tests/python/test_open_ended_quantified_group_parity_suite.py` currently passes (`5112 passed in 3.99s`);
  - `bash -lc "! rg -n '^[A-Z0-9_]+ = published_fixture_bundle_by_manifest_id\\($' tests/python/test_grouped_capture_parity_suite.py tests/python/test_quantified_alternation_parity_suite.py tests/python/test_open_ended_quantified_group_parity_suite.py"` currently fails exactly on the remaining repeated module-scope lookup chains in those three suites; and
  - `tests/python/fixture_parity_support.py` already owns the canonical published-bundle loader and one-off manifest-id lookup helper, so adding the indexed lookup path there reduces repetition without introducing another owner module.
