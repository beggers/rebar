# RBR-0434: Centralize selector-backed parity fixture selection

Status: done
Owner: architecture-implementation
Created: 2026-03-16

## Goal
- Replace the last two selector-backed published-fixture loops in the Python parity surface with one small shared helper path, so parity suites stop re-implementing whole-manifest bundle loading, manifest-id lookup, and cross-manifest case selection after the earlier bundle cleanup passes.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `tests/python/test_grouped_capture_parity_suite.py`

## Acceptance Criteria
- `tests/python/fixture_parity_support.py` gains one small shared helper surface for selector-backed published fixtures that is built on the existing bundle support rather than a new registry/module. That helper surface owns all of the following:
  - loading an ordered tuple of whole-manifest `FixtureBundle` values from an ordered tuple of published fixture paths;
  - looking up exactly one bundle by `manifest_id` from an existing bundle tuple, with a clear error on missing or duplicate ids; and
  - loading an ordered tuple of `FixtureCase` values for an exact ordered case-id list across an ordered tuple of published fixture paths, with a clear error if any case id is missing or duplicated across the selected fixtures.
- `tests/python/test_fixture_parity_support_contract.py` adds focused coverage for the new shared helper behavior:
  - one happy-path selector-backed whole-manifest bundle load;
  - manifest-id lookup success plus missing-id and duplicate-id failures; and
  - cross-manifest case selection preserving requested order plus a missing-case failure.
- `tests/python/test_callable_replacement_parity_suite.py` switches its selector-backed bundle setup to the shared helper surface:
  - `FIXTURE_BUNDLES` is loaded from `CALLABLE_FIXTURE_PATHS` without an inline `for path in CALLABLE_FIXTURE_PATHS: manifest, cases = load_fixture_manifest(path)` loop;
  - the manifest-specific fixture-alignment tests use the shared manifest-id lookup helper instead of a suite-local `_fixture_bundle_by_manifest_id(...)`; and
  - the suite still preserves its current published-fixture discovery assertion, pending-manifest bookkeeping, raw callable-replacement reference validation, generic eight-row callable fixture-shape contract, and the current explicit case-id, compile-pattern, and `(operation, helper)` contracts for the existing quantified-nested-group, conditional-group-exists, broader-range open-ended, and broader-range open-ended conditional callable manifests.
- `tests/python/test_grouped_capture_parity_suite.py` switches `MATCH_GROUP_ACCESS_CASES` to the shared cross-manifest case-selection helper:
  - `MATCH_GROUP_ACCESS_CASES` is loaded from `PUBLISHED_GROUPED_CAPTURE_FIXTURE_PATHS` and `MATCH_GROUP_ACCESS_CASE_IDS` without a suite-local `load_fixture_manifest(path)` loop;
  - the resulting tuple still preserves the current exact case-id ordering and `{"str"}` text-model assertion; and
  - the suite keeps its current compile/module/pattern case sets, supplemental miss coverage, bounded-window checks, `.regs` parity coverage, and published-fixture path assertion unchanged.
- The cleanup stays structural only:
  - do not change correctness fixture contents, Rust code, `python/rebar/`, harness selector behavior, benchmark workloads, published reports, README/status text, or tracked state files beyond this task file; and
  - do not broaden into `tests/python/test_parser_matrix_parity_suite.py` or other parity suites that are not named above.
- After the cleanup:
  - `rg -n 'load_fixture_manifest|def _fixture_bundle_by_manifest_id|def _load_match_group_access_cases' tests/python/test_callable_replacement_parity_suite.py tests/python/test_grouped_capture_parity_suite.py` returns no matches.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_callable_replacement_parity_suite.py tests/python/test_grouped_capture_parity_suite.py`.

## Constraints
- Prefer extending `tests/python/fixture_parity_support.py` over adding another support module, registry, or generated map.
- Preserve the current exact case membership and assertion semantics. This task is about deleting selector-backed plumbing, not changing parity coverage.
- Keep helper names and signatures ordinary and local to the existing parity-support surface; avoid another layer whose only job is to wrap `load_fixture_bundle(...)`.

## Notes
- The queue is currently empty, recent runtime reporting shows no inherited-dirty or post-refresh stall, and JSON counts are zero in both runtime and live filesystem views (`tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, `git ls-files '*.json' | wc -l = 0`, `rg --files -g '*.json' | wc -l = 0`), so this run should seed one post-JSON duplicate-fixture cleanup rather than no-op.
- `RBR-0433` is already reserved in tracked backlog/current-status/README state for the next feature-owned conditional replacement-template benchmark catch-up, so this architecture follow-on starts at `RBR-0434`.
- After `RBR-0427` and `RBR-0432`, the remaining selector-backed published-fixture loops in `tests/python/` are concentrated in:
  - `tests/python/test_callable_replacement_parity_suite.py`; and
  - `tests/python/test_grouped_capture_parity_suite.py`.

## Completion
- 2026-03-16: Added shared selector-backed fixture helpers to `tests/python/fixture_parity_support.py` for ordered whole-manifest bundle loading, manifest-id lookup with clear missing/duplicate errors, and ordered cross-manifest case selection with clear missing/duplicate case-id errors.
- 2026-03-16: Swapped `tests/python/test_callable_replacement_parity_suite.py` over to `load_published_fixture_bundles(...)` and `published_fixture_bundle_by_manifest_id(...)`, and swapped `tests/python/test_grouped_capture_parity_suite.py` over to `load_published_fixture_cases(...)`, removing the last suite-local selector-backed manifest loops while preserving the existing case membership and parity assertions.
- 2026-03-16: Added focused helper-contract coverage in `tests/python/test_fixture_parity_support_contract.py`, including duplicate-case failure coverage, verified `rg -n 'load_fixture_manifest|def _fixture_bundle_by_manifest_id|def _load_match_group_access_cases' tests/python/test_callable_replacement_parity_suite.py tests/python/test_grouped_capture_parity_suite.py` returned no matches, and `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_callable_replacement_parity_suite.py tests/python/test_grouped_capture_parity_suite.py` passed (`1388 passed in 1.04s`).
