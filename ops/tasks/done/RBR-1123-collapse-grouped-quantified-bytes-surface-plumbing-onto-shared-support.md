# RBR-1123: Collapse grouped quantified bytes surface plumbing onto shared parity support

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining owner-local bytes follow-on surface plumbing from the grouped quantified parity suites by routing both the open-ended and wider-ranged-repeat owners through one shared support path on `tests/python/fixture_parity_support.py` instead of keeping near-parallel dataclasses, id callbacks, and wider-ranged-repeat bytes case tables inline.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_open_ended_quantified_group_parity_suite.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`

## Acceptance Criteria
- Add one shared support surface on `tests/python/fixture_parity_support.py`, or a strictly smaller equivalent on that existing path, that is canonical for the grouped quantified bytes follow-on owners and:
  - represents the bytes follow-on surface records needed by both suites without adding a new helper module or abstraction tier;
  - carries the current bundle reference, supplemental bytes cases, expected operation/helper counts, expected module-search text map, expected pattern-fullmatch text map, and optional short follow-on id;
  - is reusable by both `tests/python/test_open_ended_quantified_group_parity_suite.py` and `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`; and
  - preserves current ordering and payload access instead of rebuilding mirrored sidecars from the shared records.
- Move the five wider-ranged-repeat bytes case tables off `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` and onto `tests/python/fixture_parity_support.py`, alongside the already-shared open-ended bytes case tables, so the wider-ranged-repeat owner no longer carries those top-level bytes payload definitions inline.
- `tests/python/test_open_ended_quantified_group_parity_suite.py` stops defining its owner-local `BytesCaseSurfaceSpec` dataclass and the local bundle/spec id callbacks, and instead imports the shared support path.
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` stops defining its owner-local `DirectBytesFollowOnSpec` dataclass, the five top-level wider-ranged-repeat bytes case tables, and the local bundle/spec id callbacks, and instead imports the shared support path.
- Extend `tests/python/test_fixture_parity_support_contract.py` with focused coverage for the shared grouped quantified bytes surface support, including:
  - a success case that proves the shared surface preserves bundle ordering and optional follow-on ids; and
  - a success case that proves the wider-ranged-repeat bytes payloads remain reachable through the shared support path.
- Preserve current behavior after the cleanup:
  - the open-ended and wider-ranged-repeat suites keep the same direct-bytes follow-on ids, bundle ordering, case ordering, expected operation/helper counts, and expected text maps;
  - no bytes follow-on case payloads, no-match rows, or manifest routing change;
  - `partition_direct_bytes_follow_on_case_buckets(...)` continues to receive the same bundle set as before; and
  - no correctness expectations, backend behavior, or published fixture coverage change.
- Keep the cleanup structural and limited to the four files above. Do not widen it into harness implementation code, reports, README text, benchmark files, or tracked project-state prose.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py -k 'load_published_fixture_bundles or published_fixture_bundles_by_manifest_id' tests/python/test_open_ended_quantified_group_parity_suite.py -k 'bytes_case_surface_contracts or direct_bytes_follow_on_bundle_routing or source_fixture_contract' tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py -k 'follow_on_case_surfaces or direct_bytes_follow_on_bundle_routing or source_fixture_contract'`
- `bash -lc "! rg -n 'class DirectBytesFollowOnSpec|class BytesCaseSurfaceSpec|def fixture_bundle_manifest_id\\(|def bytes_case_surface_manifest_id\\(|def bytes_case_surface_follow_on_id\\(|def direct_bytes_follow_on_spec_id\\(|^BROADER_RANGE_CONDITIONAL_BYTES_CASES = \\(|^BROADER_RANGE_BACKTRACKING_HEAVY_BYTES_CASES = \\(|^NESTED_BROADER_RANGE_ALTERNATION_BYTES_CASES = \\(|^NESTED_BROADER_RANGE_CONDITIONAL_BYTES_CASES = \\(|^NESTED_BROADER_RANGE_BACKTRACKING_HEAVY_BYTES_CASES = \\(' tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py"`

## Constraints
- Reuse `tests/python/fixture_parity_support.py` as the shared-support home; do not add a new helper module, registry, or cache layer.
- Keep the shared surface structural and data-oriented; do not add suite-specific behavior beyond the existing bytes follow-on record fields and small id helpers needed for parametrization.
- Preserve the existing owner-local trace-case builders and other non-bytes parity helpers in both suites; this task is about deleting duplicate bytes-surface plumbing, not rewriting the full parity owners.

## Notes
- `RBR-1123` is the next available unreserved task id in this checkout:
  - the highest live task id across `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, and `ops/tasks/blocked/` is `1122`; and
  - `rg -n 'RBR-1123|RBR-1124|RBR-1125|RBR-1126' ops/state/backlog.md ops/state/current_status.md` returned no reserved future ids in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` contains no task files in this checkout.
- JSON burn-down remains complete and current in both tracked and live views for this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest runtime cycle shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled post-task refresh path.
- The current duplication is concrete and bounded in the live checkout:
  - `tests/python/test_open_ended_quantified_group_parity_suite.py:96` still defines a local `BytesCaseSurfaceSpec` plus local id callbacks for the shared grouped quantified bytes surface;
  - `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py:47` still defines a parallel `DirectBytesFollowOnSpec`;
  - `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py:82`, `:100`, `:118`, `:134`, and `:150` still define the wider-ranged-repeat bytes payload tables inline even though the adjacent open-ended owner already sources comparable bytes tables from `tests/python/fixture_parity_support.py`; and
  - the negative `rg` verification above currently fails exactly on those owner-local definitions.
- The focused verification slice is green in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py -k 'load_published_fixture_bundles or published_fixture_bundles_by_manifest_id' tests/python/test_open_ended_quantified_group_parity_suite.py -k 'bytes_case_surface_contracts or direct_bytes_follow_on_bundle_routing or source_fixture_contract' tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py -k 'follow_on_case_surfaces or direct_bytes_follow_on_bundle_routing or source_fixture_contract'` returned `11 passed, 5638 deselected` in this run.

## Completion
- Landed the shared grouped-quantified bytes surface support on `tests/python/fixture_parity_support.py`, including the reusable shared spec/id helpers plus the five wider-ranged-repeat bytes payload tables that were previously inline in the wider-ranged suite.
- Updated both grouped quantified parity suites to consume the shared support path without owner-local bytes-surface dataclasses or owner-local bytes-surface id callbacks.
- Extended `tests/python/test_fixture_parity_support_contract.py` with focused shared-support coverage for bundle ordering, optional follow-on ids, and wider-ranged-repeat payload reachability.
- Verified with:
  - `./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py -k 'load_published_fixture_bundles or published_fixture_bundles_by_manifest_id or grouped_quantified_bytes_surface_spec' tests/python/test_open_ended_quantified_group_parity_suite.py -k 'bytes_case_surface_contracts or direct_bytes_follow_on_bundle_routing or source_fixture_contract' tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py -k 'follow_on_case_surfaces or direct_bytes_follow_on_bundle_routing or source_fixture_contract'`
  - `./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py::test_grouped_quantified_bytes_surface_spec_preserves_bundle_order_and_optional_follow_on_ids tests/python/test_fixture_parity_support_contract.py::test_grouped_quantified_bytes_surface_spec_keeps_wider_ranged_repeat_payloads_reachable`
  - `bash -lc "! rg -n 'class DirectBytesFollowOnSpec|class BytesCaseSurfaceSpec|def fixture_bundle_manifest_id\\(|def bytes_case_surface_manifest_id\\(|def bytes_case_surface_follow_on_id\\(|def direct_bytes_follow_on_spec_id\\(|^BROADER_RANGE_CONDITIONAL_BYTES_CASES = \\(|^BROADER_RANGE_BACKTRACKING_HEAVY_BYTES_CASES = \\(|^NESTED_BROADER_RANGE_ALTERNATION_BYTES_CASES = \\(|^NESTED_BROADER_RANGE_CONDITIONAL_BYTES_CASES = \\(|^NESTED_BROADER_RANGE_BACKTRACKING_HEAVY_BYTES_CASES = \\(' tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py"`
