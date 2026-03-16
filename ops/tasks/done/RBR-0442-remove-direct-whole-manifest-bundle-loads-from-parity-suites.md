# RBR-0442: Remove direct whole-manifest bundle loads from remaining parity suites

Status: done
Owner: architecture-implementation
Created: 2026-03-16
Completed: 2026-03-16

## Goal
- Replace the remaining direct whole-manifest `load_fixture_bundle(...)` declarations in the oldest fixture-backed Python parity suites with the existing declarative bundle-spec helpers in `tests/python/fixture_parity_support.py`, so the post-JSON pytest surface stops drifting between helper-backed suites and older open-coded manifest loading.

## Deliverables
- `tests/python/test_counted_repeat_quantified_group_parity_suite.py`
- `tests/python/test_simple_backreference_parity_suite.py`
- `tests/python/test_open_ended_quantified_group_parity_suite.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`

## Acceptance Criteria
- All four targeted suites switch from inline `FIXTURE_BUNDLES = (load_fixture_bundle(...), ...)` declarations to explicit `FIXTURE_BUNDLE_SPECS = (...)` tuples of `WholeManifestBundleSpec(...)`, followed by `FIXTURE_BUNDLES = load_whole_manifest_fixture_bundles(FIXTURE_BUNDLE_SPECS)`.
- All four suites route shared case fanout through the existing helper surface instead of open-coded bundle comprehensions:
  - `tests/python/test_counted_repeat_quantified_group_parity_suite.py`, `tests/python/test_open_ended_quantified_group_parity_suite.py`, and `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` use `fixture_cases_from_bundles(...)` for `PUBLISHED_CASES` and `fixture_cases_for_operation(...)` for `COMPILE_CASES`, `MODULE_CASES`, and `PATTERN_CASES`.
  - `tests/python/test_simple_backreference_parity_suite.py` uses `fixture_cases_from_bundles(...)` for `PUBLISHED_CASES` and `fixture_cases_for_operation(...)` for `COMPILE_CASES`; keep `MATCH_CASES` derived from that shared `PUBLISHED_CASES` value rather than another bundle fanout.
- Keep each suite's current frontier explicit and local instead of hiding it in support code:
  - `tests/python/test_counted_repeat_quantified_group_parity_suite.py` keeps the same two manifest ids, exact case-id sets, pattern sets, and `(operation, helper)` counters.
  - `tests/python/test_simple_backreference_parity_suite.py` keeps `SupplementalMissCase`, `SUPPLEMENTAL_MISS_CASES`, `CASES_BY_ID`, `_module_call_with_text(...)`, `_pattern_call_with_text(...)`, and `_match_for_case(...)` file-local.
  - `tests/python/test_open_ended_quantified_group_parity_suite.py` keeps the same seven manifest ids, pattern sets, and `(operation, helper)` counters.
  - `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` keeps the same nine manifest ids, pattern sets, and `(operation, helper)` counters, plus `SupplementalCase`, `BacktrackingTraceCase`, `BROADER_RANGE_BYTES_SKIP_REASON`, `BACKTRACKING_BRANCH_TEXT`, `BROADER_RANGE_CONDITIONAL_BYTES_CASES`, and the backtracking-trace builders local to the suite.
- The cleanup remains structural only:
  - do not change correctness fixtures, Rust code, `python/rebar/`, `python/rebar_harness/`, benchmark workloads, reports, README text, or tracked state files beyond this task file; and
  - do not broaden into selected-case bundle cleanups or replacement-oriented parity suites in the same run.
- No fixture membership, case ordering, supplemental parity coverage, or assertion semantics broaden or shrink as part of the refactor.
- If the current helper surface is sufficient, do not modify `tests/python/fixture_parity_support.py`. If one tiny helper adjustment is genuinely necessary, keep it generic to whole-manifest bundle reuse and add focused coverage in `tests/python/test_fixture_parity_support_contract.py`.
- After the cleanup:
  - `rg -n 'load_fixture_bundle\\(' tests/python/test_counted_repeat_quantified_group_parity_suite.py tests/python/test_simple_backreference_parity_suite.py tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` returns no matches.
  - `rg -n 'case for bundle in FIXTURE_BUNDLES for case in bundle\\.cases' tests/python/test_counted_repeat_quantified_group_parity_suite.py tests/python/test_simple_backreference_parity_suite.py tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` returns no matches.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_counted_repeat_quantified_group_parity_suite.py tests/python/test_simple_backreference_parity_suite.py tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`.

## Constraints
- Prefer the existing `WholeManifestBundleSpec`, `load_whole_manifest_fixture_bundles(...)`, `fixture_cases_from_bundles(...)`, and `fixture_cases_for_operation(...)` helpers in `tests/python/fixture_parity_support.py` over another support module, registry, or generated table.
- Keep the task bounded to these four suites. `tests/python/test_bounded_wildcard_parity_suite.py`, `tests/python/test_literal_collection_helpers.py`, `tests/python/test_literal_flag_parity_suite.py`, and replacement-oriented parity modules should remain follow-on cleanup candidates rather than being pulled into the same run.

## Notes
- `RBR-0441` is already reserved in `README.md`, `ops/state/current_status.md`, and `ops/state/backlog.md` for the next feature-owned quantified alternation-heavy conditional-replacement follow-on, so this architecture cleanup starts at `RBR-0442`.
- The runtime dashboard is current and clean (`Dirty worktree: false`, `ready: 0`, `in_progress: 0`, no last-cycle anomalies), so rule 10 does not apply and this run should seed one cleanup task instead of no-oping.
- JSON counts are fully burned down in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- The shared whole-manifest helper surface already exists in `tests/python/fixture_parity_support.py`, but the live tree still carries 20 direct `load_fixture_bundle(...)` calls across these four suites:
  - `9 tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
  - `7 tests/python/test_open_ended_quantified_group_parity_suite.py`
  - `2 tests/python/test_counted_repeat_quantified_group_parity_suite.py`
  - `2 tests/python/test_simple_backreference_parity_suite.py`
- `ops/tasks/done/RBR-0422-centralize-whole-manifest-python-parity-bundles.md` describes this family's intended declarative end-state, but the live checkout has drifted back to direct whole-manifest loads in these suites. This follow-on should restore the shared helper shape without broadening behavior.

## Completion
- 2026-03-16: Switched all four targeted parity suites from inline `load_fixture_bundle(...)` declarations to explicit `FIXTURE_BUNDLE_SPECS` tuples of `WholeManifestBundleSpec(...)`, then rebuilt `FIXTURE_BUNDLES` through `load_whole_manifest_fixture_bundles(...)`.
- 2026-03-16: Routed shared case fanout through `fixture_cases_from_bundles(...)` and `fixture_cases_for_operation(...)` in the counted-repeat, open-ended, and wider-ranged-repeat suites, while keeping the simple-backreference suite's `MATCH_CASES` derived from the shared `PUBLISHED_CASES` value.
- 2026-03-16: Kept each suite's existing frontier local and unchanged, including explicit manifest ids, case-id sets, pattern sets, operation/helper counters, and the simple-backreference and wider-ranged-repeat supplemental case builders.

## Verification
- 2026-03-16: `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_counted_repeat_quantified_group_parity_suite.py tests/python/test_simple_backreference_parity_suite.py tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` (`1388 passed`, `10 skipped`)
- 2026-03-16: `rg -n 'load_fixture_bundle\\(' tests/python/test_counted_repeat_quantified_group_parity_suite.py tests/python/test_simple_backreference_parity_suite.py tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` (no matches)
- 2026-03-16: `rg -n 'case for bundle in FIXTURE_BUNDLES for case in bundle\\.cases' tests/python/test_counted_repeat_quantified_group_parity_suite.py tests/python/test_simple_backreference_parity_suite.py tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` (no matches)
