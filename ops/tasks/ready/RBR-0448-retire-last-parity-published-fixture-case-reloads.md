# RBR-0448: Retire the last parity published-fixture case reloads

Status: ready
Owner: architecture-implementation
Created: 2026-03-16

## Goal
- Stop the remaining Python parity suites from reloading published fixture cases through `load_published_fixture_cases(...)` after they have already materialized the same published cases through `FIXTURE_BUNDLES` and `PUBLISHED_CASES`, so low-level published-case selection stays exercised only by the dedicated helper-contract tests.

## Deliverables
- `tests/python/test_grouped_capture_parity_suite.py`
- `tests/python/test_branch_local_backreference_parity_suite.py`
- `tests/python/test_conditional_group_exists_quantified_parity_suite.py`

## Acceptance Criteria
- All three targeted suites stop importing and calling `load_published_fixture_cases(...)`.
- `tests/python/test_grouped_capture_parity_suite.py` derives `MATCH_GROUP_ACCESS_CASES` from the suite's already-loaded published cases instead of re-reading `PUBLISHED_GROUPED_CAPTURE_FIXTURE_PATHS`:
  - preserve the current `MATCH_GROUP_ACCESS_CASE_IDS` order exactly;
  - preserve the current `{"str"}` text-model assertion exactly; and
  - keep the existing grouped-capture compile/module/pattern case sets, supplemental miss coverage, bounded-window checks, `.regs` parity checks, and published-fixture path assertion unchanged.
- `tests/python/test_branch_local_backreference_parity_suite.py` derives `MATCH_GROUP_ACCESS_CASES` from the suite's already-loaded published cases instead of re-reading `PUBLISHED_BRANCH_LOCAL_BACKREFERENCE_FIXTURE_PATHS`:
  - preserve the current `MATCH_GROUP_ACCESS_CASE_IDS` order exactly;
  - preserve the current `{"str"}` text-model assertion exactly; and
  - keep the existing compile/workflow case sets, match-convenience bookkeeping, bounded-window checks, supplemental miss coverage, and published-fixture path assertion unchanged.
- `tests/python/test_conditional_group_exists_quantified_parity_suite.py` derives `MATCH_API_CASES` from the suite's already-loaded published cases instead of re-reading `published_fixture_paths_from_bundles(FIXTURE_BUNDLES)`:
  - preserve the current `MATCH_API_CASE_IDS` order exactly;
  - preserve the current `{"str"}` text-model assertion exactly; and
  - keep the existing compile/module/pattern case sets plus the supplemental module-fullmatch, pattern-fullmatch, and miss coverage unchanged.
- Prefer the simplest structural cleanup:
  - re-use the already-loaded `PUBLISHED_CASES` and any existing `CASES_BY_ID` map where present;
  - if `tests/python/test_conditional_group_exists_quantified_parity_suite.py` needs a local `CASES_BY_ID`, keep it file-local and derived from `PUBLISHED_CASES`; and
  - do not add another support module, registry, or generated selector table for this cleanup.
- Unless a tiny generic helper is genuinely necessary, do not modify `tests/python/fixture_parity_support.py` or `tests/python/test_fixture_parity_support_contract.py`. If a helper is unavoidable, keep it limited to ordered selection from already-loaded published cases and add focused contract coverage.
- The cleanup stays structural only:
  - do not change `tests/conformance/fixtures/*.py`, `python/rebar/`, `python/rebar_harness/`, Rust code, benchmark workloads, published reports, README text, or tracked state files beyond this task file; and
  - do not broaden into other parity suites in the same run.
- After the cleanup:
  - `rg -n 'load_published_fixture_cases\\(' tests/python/test_grouped_capture_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py tests/python/test_conditional_group_exists_quantified_parity_suite.py` returns no matches.
  - `rg -n 'load_published_fixture_cases\\(' tests/python/*.py` shows only the helper definition in `tests/python/fixture_parity_support.py` plus the dedicated contract-test coverage in `tests/python/test_fixture_parity_support_contract.py`.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_grouped_capture_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py tests/python/test_conditional_group_exists_quantified_parity_suite.py`.

## Constraints
- Prefer deleting redundant fixture reloads over adding another abstraction layer. The intended end state is that suites which already load `FIXTURE_BUNDLES` do not re-open the same published fixtures just to recover a handful of selected cases.
- Keep the explicit frontier local and readable in each suite. This task should remove redundant selector plumbing, not hide case ids or suite-specific anchors behind a generic registry.

## Notes
- `RBR-0447` is already reserved in `README.md`, `ops/state/current_status.md`, and `ops/state/backlog.md` for the next feature-owned `module_boundary.py` compile-benchmark catch-up, so this architecture cleanup starts at `RBR-0448`.
- The runtime dashboard is current and clean (`Generated: 2026-03-16T05:08:40+00:00`, `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, no last-cycle anomalies), so rule 10 does not apply and this run should seed one post-JSON simplification task instead of no-oping.
- JSON counts are fully burned down in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- After `RBR-0434`, `RBR-0438`, and `RBR-0446`, the only remaining parity-suite call sites for `load_published_fixture_cases(...)` are:
  - `tests/python/test_grouped_capture_parity_suite.py`
  - `tests/python/test_branch_local_backreference_parity_suite.py`
  - `tests/python/test_conditional_group_exists_quantified_parity_suite.py`
- The helper should remain covered by `tests/python/test_fixture_parity_support_contract.py`, but parity suites that already hold `PUBLISHED_CASES` in memory should not keep re-reading the same fixture files just to rebuild a small ordered subset.
