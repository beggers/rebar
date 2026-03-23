## RBR-1013: Collapse mixed-text replacement shared-surface routing glue

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the repeated mixed-text manifest routing glue from `tests/python/test_fixture_backed_replacement_parity_suite.py` so the adjacent shared-surface routing tests assert through one smaller file-local helper surface instead of each rebuilding the same str/bytes case-id partitions, bundle operation selections, and manifest-scoped surface filters by hand.

## Deliverables
- `tests/python/test_fixture_backed_replacement_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_fixture_backed_replacement_parity_suite.py` adds one explicit file-local helper surface for the repeated mixed-text manifest routing contract, or a strictly smaller equivalent, shared by:
  - `test_mixed_replacement_manifest_routes_bytes_rows_through_shared_parity_surface()`
  - `test_broader_range_open_ended_replacement_manifest_routes_bytes_rows_through_shared_parity_surface()`
  - `test_broader_range_wider_ranged_repeat_replacement_manifest_keeps_mixed_text_on_shared_parity_surface()`
- Repoint those tests through that shared helper surface instead of leaving each body to open-code some combination of:
  - `str_cases, bytes_cases = assert_mixed_text_model_case_pairs(bundle)` plus case-id projections;
  - `fixture_cases_for_operation((bundle,), "module_call")` and `fixture_cases_for_operation((bundle,), "pattern_call")` to rebuild the expected module/pattern case ids;
  - repeated `if case.manifest_id == ...` filtering over `surface.module_cases`, `surface.pattern_cases`, `surface.replacement_cases`, `surface.match_group_access_cases`, and `surface.template_expand_cases`; and
  - one-off set/tuple conversions around those same manifest-scoped case-id collections.
- Preserve the current manifest-routing contracts exactly while shrinking the glue:
  - `test_mixed_replacement_manifest_routes_bytes_rows_through_shared_parity_surface()` still proves that, for `MIXED_TEXT_MODEL_REPLACEMENT_BUNDLE` on `OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_SURFACE`, the shared module and pattern case ids match the bundle's `module_call` and `pattern_call` operations exactly, and both `match_group_access_cases` and `template_expand_cases` for `bundle.expected_manifest_id` still equal the union of the paired str/bytes case ids.
  - `test_broader_range_open_ended_replacement_manifest_routes_bytes_rows_through_shared_parity_surface()` still proves that, for `BROADER_RANGE_OPEN_ENDED_MIXED_TEXT_REPLACEMENT_BUNDLE` on `OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_SURFACE`, `Counter((case.operation, case.helper) for case in bundle.cases)` stays `MIXED_TEXT_MODEL_OPERATION_HELPER_COUNTS`, the shared module and pattern case ids still match the bundle's `module_call` and `pattern_call` operations exactly, and the shared `template_expand_cases` for `bundle.expected_manifest_id` still equal the union of the paired str/bytes case ids.
  - `test_broader_range_wider_ranged_repeat_replacement_manifest_keeps_mixed_text_on_shared_parity_surface()` still proves that, for `BROADER_RANGE_WIDER_RANGED_REPEAT_MIXED_TEXT_REPLACEMENT_BUNDLE` on `GROUPED_REPLACEMENT_TEMPLATE_SURFACE`, `Counter((case.operation, case.helper) for case in bundle.cases)` stays `MIXED_TEXT_MODEL_OPERATION_HELPER_COUNTS`, the bundle case ids still equal `_expected_selected_replacement_case_ids(surface, manifest_id=manifest_id)`, the manifest-scoped `replacement_cases`, `module_cases`, `pattern_cases`, and `template_expand_cases` on the surface still match the same expected selected/module/pattern case-id tuples exactly, `_expected_uncovered_replacement_case_ids(surface, manifest_id)` still stays empty, and `assert_fixture_bundle_tracks_published_case_frontier(...)` still passes with `expected_uncovered_case_ids=()`.
- Prefer reuse of the existing file-local manifest helpers over another parallel abstraction layer:
  - reuse `_cases_for_manifest_ids(...)`, `_expected_selected_replacement_case_ids(...)`, `_expected_uncovered_replacement_case_ids(...)`, or a strictly smaller local successor where that reduces duplication;
  - keep the cleanup structural and local to `tests/python/test_fixture_backed_replacement_parity_suite.py`;
  - do not widen this run into replacement execution/parity behavior, fixture manifests, correctness-harness modules, benchmark files, reports, or tracked state prose; and
  - do not add a shared helper module, registry, or checked-in data representation.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'mixed_replacement_manifest_routes_bytes_rows_through_shared_parity_surface or broader_range_open_ended_replacement_manifest_routes_bytes_rows_through_shared_parity_surface or broader_range_wider_ranged_repeat_replacement_manifest_keeps_mixed_text_on_shared_parity_surface'`

## Constraints
- Keep the cleanup structural and local to `tests/python/test_fixture_backed_replacement_parity_suite.py`.
- Preserve the exact shared-surface manifest-routing contracts for the three targeted mixed-text publication tests while shrinking the repeated case-id plumbing.
- Do not edit fixture manifests, harness modules, benchmark files, reports, README/current-status/backlog prose, or non-replacement parity files in this run.

## Notes
- Completed 2026-03-23: added one file-local mixed-text manifest-routing helper surface in `tests/python/test_fixture_backed_replacement_parity_suite.py` and repointed the three targeted shared-surface tests through it so they now share the same bundle/text-model/manifest-scoped case-id extraction without changing the asserted routing contracts.
- Verified with `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'mixed_replacement_manifest_routes_bytes_rows_through_shared_parity_surface or broader_range_open_ended_replacement_manifest_routes_bytes_rows_through_shared_parity_surface or broader_range_wider_ranged_repeat_replacement_manifest_keeps_mixed_text_on_shared_parity_surface'` (`3 passed, 1298 deselected`).
- `RBR-1013` is unreserved in the live queue/state files for this run:
  - `python3` inspection over `ops/state/backlog.md`, `ops/state/current_status.md`, and the task queues reported `next_free=1013`, `max_existing=1012`, and no reserved `RBR-` ids above the live task frontier.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The simplification target is concrete in the live checkout:
  - `tests/python/test_fixture_backed_replacement_parity_suite.py` already has adjacent mixed-text routing helpers at lines `1441`-`1507`, but the three targeted manifest-routing tests at lines `1760`-`1894` still rebuild the same str/bytes partitions, module/pattern operation ids, and manifest-scoped surface filters inline instead of sharing one file-local routing contract.
  - the first two tests at lines `1760`-`1840` both derive expected module/pattern case ids from the bundle and compare them against manifest-scoped case ids on the same shared surface, differing mainly in whether they additionally assert `match_group_access_cases` or `Counter((case.operation, case.helper) for case in bundle.cases)`.
  - the third test at lines `1843`-`1894` repeats the same manifest-scoped route extraction pattern while additionally checking `replacement_cases`, `_expected_selected_replacement_case_ids(...)`, `_expected_uncovered_replacement_case_ids(...)`, and `assert_fixture_bundle_tracks_published_case_frontier(...)`.
- The verification slice is green before the cleanup:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'mixed_replacement_manifest_routes_bytes_rows_through_shared_parity_surface or broader_range_open_ended_replacement_manifest_routes_bytes_rows_through_shared_parity_surface or broader_range_wider_ranged_repeat_replacement_manifest_keeps_mixed_text_on_shared_parity_surface'` currently passes with `3 passed, 1298 deselected`.
