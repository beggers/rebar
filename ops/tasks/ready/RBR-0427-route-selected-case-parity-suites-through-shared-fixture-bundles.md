# RBR-0427: Route selected-case parity suites through shared fixture bundles

Status: ready
Owner: architecture-implementation
Created: 2026-03-15

## Goal
- Replace the repeated selected-case `FixtureBundle` dataclass, `_fixture_bundle(...)` loader, and manifest-alignment assertion blocks in a bounded set of Python parity suites with the existing helpers in `tests/python/fixture_parity_support.py`, so those suites stop hand-maintaining identical fixture-bundle plumbing after `RBR-0422`.

## Deliverables
- `tests/python/test_bounded_wildcard_parity_suite.py`
- `tests/python/test_grouped_capture_parity_suite.py`
- `tests/python/test_literal_flag_parity_suite.py`
- `tests/python/test_literal_collection_helpers.py`

## Acceptance Criteria
- The targeted suites reuse the existing selected-case helper surface from `tests/python/fixture_parity_support.py` instead of defining local bundle scaffolding:
  - `load_expected_fixture_bundle(...)`
  - `assert_expected_fixture_bundle_contract(...)`
  - `published_fixture_paths_from_bundles(...)` where the suite still checks selector/path alignment
- `tests/python/test_bounded_wildcard_parity_suite.py`:
  - loads both current one-row bundles through `load_expected_fixture_bundle(...)` instead of a local `FixtureBundle` plus `_fixture_bundle(...)`;
  - keeps the current selected case ids, manifest ids, pattern set `{ "a.c" }`, and `(operation, helper)` counts for the `literal-flag-workflows` and `collection-replacement-workflows` rows; and
  - routes the published-fixture path assertion through `published_fixture_paths_from_bundles(FIXTURE_BUNDLES)`.
- `tests/python/test_grouped_capture_parity_suite.py`:
  - loads the current eight selected-case bundles through `load_expected_fixture_bundle(...)`;
  - keeps the current selected case ids, manifest ids, pattern sets, and `(operation, helper)` counts for all eight grouped-capture manifests; and
  - routes the published-fixture path assertion through `published_fixture_paths_from_bundles(FIXTURE_BUNDLES)`.
- `tests/python/test_literal_flag_parity_suite.py`:
  - replaces the local bundle dataclass/loader with `load_expected_fixture_bundle(...)`;
  - adds explicit expected pattern validation for the current selected rows so the shared helper owns the manifest-alignment check, with the selected bundle still covering the same ten case ids and the pattern set `{ "abc", "AbC", "(?i)abc", b"abc", b"AbC" }`;
  - keeps the current `(operation, helper)` counts for the ten selected rows; and
  - keeps the nonliteral wildcard row out of this suite so `flag-unsupported-nonliteral-ignorecase-search` remains owned by `tests/python/test_bounded_wildcard_parity_suite.py`.
- `tests/python/test_literal_collection_helpers.py`:
  - replaces the local bundle dataclass/loader with `load_expected_fixture_bundle(...)`;
  - adds explicit expected pattern validation for the current selected rows so the shared helper owns the manifest-alignment check, with the selected bundle still covering the same seven case ids and the pattern set `{ "abc", b"abc" }`;
  - keeps the current `(operation, helper)` counts for the selected rows; and
  - keeps `module-findall-nonliteral-str` owned by `tests/python/test_bounded_wildcard_parity_suite.py` rather than duplicating that nonliteral row here.
- The cleanup stays structural only:
  - keep all existing supplemental parity cases, fake-boundary scaffolding, cache checks, type-error checks, group-access parity checks, and match/replacement assertions in place; and
  - do not add a new helper layer or change fixture contents, Rust code, `python/rebar/`, harness selector behavior, published reports, README copy, or tracked state files beyond this task file.
- After the cleanup:
  - `rg -n 'class FixtureBundle|def _fixture_bundle\\(' tests/python/test_bounded_wildcard_parity_suite.py tests/python/test_grouped_capture_parity_suite.py tests/python/test_literal_flag_parity_suite.py tests/python/test_literal_collection_helpers.py` returns no matches.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_bounded_wildcard_parity_suite.py tests/python/test_grouped_capture_parity_suite.py tests/python/test_literal_flag_parity_suite.py tests/python/test_literal_collection_helpers.py`.

## Constraints
- Prefer the existing helper surface in `tests/python/fixture_parity_support.py` over extending it. If a tiny helper adjustment becomes necessary, keep it narrowly scoped to selected-case bundle reuse and do not add another registry-style layer.
- Do not broaden this task into the more custom bundle owners:
  - `tests/python/test_branch_local_backreference_parity_suite.py`
  - `tests/python/test_callable_replacement_parity_suite.py`
  - `tests/python/test_quantified_alternation_parity_suite.py`
  - `tests/python/test_open_ended_quantified_group_replacement_template_parity_suite.py`
- Do not fold feature work or new parity coverage into this cleanup; preserve the current case selection and assertion semantics exactly.

## Notes
- The ready queue is empty, recent runtime artifacts show no inherited-dirty or post-task refresh stall, and both tracked and live JSON counts are zero (`tracked_json_blob_count: 0`, `git ls-files '*.json' | wc -l = 0`, `rg --files -g '*.json' | wc -l = 0`), so this run should seed one post-JSON duplicate-plumbing cleanup rather than no-op.
- `RBR-0422` already introduced shared whole-manifest and selected-case fixture-bundle helpers in `tests/python/fixture_parity_support.py`, but these four suites still each define a local `FixtureBundle` and `_fixture_bundle(...)` wrapper on top of the same manifest-loading path.
- `RBR-0426` is already reserved in tracked backlog/current-status text for the next feature-owned conditional replacement-template correctness slice, so this architecture follow-on starts at `RBR-0427`.
