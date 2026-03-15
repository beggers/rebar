# RBR-0422: Centralize whole-manifest Python parity bundles

Status: ready
Owner: architecture-implementation
Created: 2026-03-15

## Goal
- Replace the repeated whole-manifest `FixtureBundle` loader and contract scaffolding in a first bounded set of Python parity suites with one shared helper in `tests/python/fixture_parity_support.py`, so those suites stop hand-maintaining identical dataclasses, manifest loading, selector-path sorting, and bundle-alignment assertions after selector centralization.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_counted_repeat_quantified_group_parity_suite.py`
- `tests/python/test_simple_backreference_parity_suite.py`
- `tests/python/test_open_ended_quantified_group_parity_suite.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`

## Acceptance Criteria
- `tests/python/fixture_parity_support.py` gains one small shared helper surface for parity suites that load entire published manifests from `FIXTURES_DIR`. That helper surface owns:
  - loading a manifest into a reusable bundle object/value;
  - optional exact `expected_case_ids` validation for suites that pin full-manifest membership;
  - expected pattern-set validation through a caller-supplied pattern extractor such as `case_pattern` or `str_case_pattern`;
  - expected `(operation, helper)` counter validation;
  - the common `{"str"}` text-model assertion; and
  - deriving the sorted published fixture-path tuple from a bundle set for selector-alignment checks.
- The four targeted suites listed above route their shared manifest loading and bundle contract assertions through that helper instead of local `FixtureBundle` dataclasses plus local `_fixture_bundle(...)` loaders.
- The cleanup preserves current suite coverage and case selection:
  - `tests/python/test_counted_repeat_quantified_group_parity_suite.py` still validates exactly the two counted-repeat manifests and their current case ids, pattern sets, and operation-helper counts.
  - `tests/python/test_simple_backreference_parity_suite.py` still validates exactly the named and numbered backreference manifests and their current case ids, pattern sets, and operation-helper counts.
  - `tests/python/test_open_ended_quantified_group_parity_suite.py` still validates the current seven open-ended manifests and their current pattern sets plus operation-helper counts.
  - `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` still validates the current nine wider-ranged-repeat manifests and their current pattern sets plus operation-helper counts.
- `tests/python/test_fixture_parity_support_contract.py` adds focused helper coverage for both supported modes:
  - a whole-manifest bundle with no explicit case-id assertion; and
  - a whole-manifest bundle that also asserts exact case ids.
- After the cleanup:
  - `rg -n 'class FixtureBundle|def _fixture_bundle\(' tests/python/test_counted_repeat_quantified_group_parity_suite.py tests/python/test_simple_backreference_parity_suite.py tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` returns no matches.
  - `rg -n 'sorted\(\(bundle\.manifest\.path for bundle in FIXTURE_BUNDLES\)' tests/python/test_counted_repeat_quantified_group_parity_suite.py tests/python/test_simple_backreference_parity_suite.py tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` returns no matches.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_counted_repeat_quantified_group_parity_suite.py tests/python/test_simple_backreference_parity_suite.py tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`.

## Constraints
- Keep this task on shared parity-fixture support only. Do not change Rust code, `python/rebar/`, correctness fixture contents, harness selector behavior, benchmark workloads, published reports, README reporting, or tracked state files beyond this task file.
- Do not broaden into the more custom parity suites that select partial case subsets, callable replacement flows, nested conditional helpers, or replacement-template helpers; this task is only for the whole-manifest str-only suites listed above.
- Prefer a small helper extension in `tests/python/fixture_parity_support.py` over adding a new support module or another registry layer.

## Notes
- The queue is empty, recent runtime artifacts show no inherited-dirty or post-commit bottleneck, and both tracked and live JSON counts are zero (`tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, `git ls-files '*.json' | wc -l = 0`, `rg --files -g '*.json' | wc -l = 0`), so this run should seed a post-JSON duplicate-fixture cleanup.
- `RBR-0416` centralized correctness fixture selectors, but these four suites still each restate the same whole-manifest `FixtureBundle` dataclass, `load_fixture_manifest(FIXTURES_DIR / fixture_name)` loader, selector-path sorting, and bundle-alignment assertions.
- Leave `tests/python/test_grouped_capture_parity_suite.py`, `tests/python/test_conditional_group_exists_*_parity_suite.py`, `tests/python/test_callable_replacement_parity_suite.py`, and the replacement-template helpers for later follow-ons because they carry extra case filtering or custom match and replacement scaffolding beyond this first helper cut.
