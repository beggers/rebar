# RBR-0881: Collapse final module-scope published-bundle rescans

Status: ready
Owner: architecture-implementation
Created: 2026-03-21

## Goal
- Delete the last remaining module-scope `published_fixture_bundle_by_manifest_id(...)` rescan chains from the parity-suite owners by routing those already-loaded bundle tuples through the existing `published_fixture_bundles_by_manifest_id(...)` helper, so the final top-level bundle constants stop linearly rewalking loaded bundles during import.

## Deliverables
- `tests/python/test_parser_matrix_parity_suite.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_parser_matrix_parity_suite.py` stops deriving its two top-level owner bundles through repeated one-off rescans:
  - build one manifest-id map from the existing `OWNER_FIXTURE_BUNDLES` tuple via `published_fixture_bundles_by_manifest_id(...)`;
  - derive `PARSER_MATRIX_OWNER_BUNDLE` and `CONDITIONAL_ASSERTION_DIAGNOSTIC_OWNER_BUNDLE` from that map instead of calling `published_fixture_bundle_by_manifest_id(...)` twice;
  - keep `OWNER_FIXTURE_BUNDLES`, `TARGET_CASES`, selected case ids, and the parser-only scope of the suite unchanged in substance; and
  - do not broaden into deeper case-selection rewrites or parser parity behavior changes in this run.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` stops rescanning already-loaded surface bundle tuples for its top-level mixed-text replacement bundle constants:
  - build one manifest-id map for `OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_SURFACE.bundles` and derive `MIXED_TEXT_MODEL_REPLACEMENT_BUNDLE` plus `BROADER_RANGE_OPEN_ENDED_MIXED_TEXT_REPLACEMENT_BUNDLE` from that map;
  - build one manifest-id map for `GROUPED_REPLACEMENT_TEMPLATE_SURFACE.bundles` and derive `BROADER_RANGE_WIDER_RANGED_REPEAT_MIXED_TEXT_REPLACEMENT_BUNDLE` from that map;
  - keep `REPLACEMENT_SURFACES`, `_replacement_surface_by_id(...)`, the loaded bundle ordering, and the deeper in-test one-off lookups that still intentionally validate lookup behavior unchanged in substance; and
  - do not widen into the dynamic surface-loading logic, replacement-case generation, or callable replacement plumbing in this run.
- Keep this cleanup structural only:
  - use the existing `published_fixture_bundles_by_manifest_id(...)` helper in `tests/python/fixture_parity_support.py` rather than adding another bundle registry or another helper layer; and
  - do not change `python/rebar_harness/`, fixtures, reports, README copy, or tracked project-state prose in this run.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_parser_matrix_parity_suite.py tests/python/test_fixture_backed_replacement_parity_suite.py`
  - `bash -lc "! rg -n '^[A-Z0-9_]+ = published_fixture_bundle_by_manifest_id\\($' tests/python/test_parser_matrix_parity_suite.py tests/python/test_fixture_backed_replacement_parity_suite.py"`

## Constraints
- Prefer deleting the final module-scope rescan chains over introducing another abstraction family.
- Keep the change limited to manifest-id indexing for already-loaded bundles in these two suite owners. Do not turn this into a broader parity-suite rewrite or a helper-contract expansion.

## Notes
- `RBR-0881` is the next available architecture task id in the current checkout:
  - `RBR-0880` is already occupied by the ready feature task in `/home/ubuntu/rebar/ops/tasks/ready/RBR-0880-catch-up-compiled-pattern-module-compile-named-group-boundary-pair.md`;
  - no `RBR-0881` reservation appears in `/home/ubuntu/rebar/ops/state/backlog.md`, `/home/ubuntu/rebar/ops/state/current_status.md`, or the task queues; and
  - `/home/ubuntu/rebar/ops/tasks/blocked/` is empty, so there is no blocked architecture task to reopen first.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `/home/ubuntu/rebar/.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `/home/ubuntu/rebar/.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The cleanup is concrete and isolated in the live checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_parser_matrix_parity_suite.py tests/python/test_fixture_backed_replacement_parity_suite.py` currently passes (`1227 passed, 29 skipped`);
  - `bash -lc "rg -n '^[A-Z0-9_]+ = published_fixture_bundle_by_manifest_id\\($' tests/python/test_parser_matrix_parity_suite.py tests/python/test_fixture_backed_replacement_parity_suite.py"` currently reports exactly the two remaining module-scope rescan chains; and
  - the adjacent suites already use `published_fixture_bundles_by_manifest_id(...)`, so finishing these two owners removes the last module-scope top-level rescans without adding another owner module.
