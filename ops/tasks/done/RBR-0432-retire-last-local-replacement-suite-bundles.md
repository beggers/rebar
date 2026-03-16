# RBR-0432: Retire the last local replacement-suite fixture bundle wrappers

Status: done
Owner: architecture-implementation
Created: 2026-03-16

## Goal
- Remove the last two Python parity suites that still carry their own local fixture-bundle wrapper classes, so the replacement-oriented pytest surface shares one ordinary bundle representation and one ordinary fixture-loading path.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_grouped_literal_replacement_template.py`
- `tests/python/test_callable_replacement_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_grouped_literal_replacement_template.py` no longer defines `ReplacementFixtureBundle` and no longer open-codes manifest wrapper plumbing for the grouped replacement-template manifests.
- `tests/python/test_grouped_literal_replacement_template.py` reuses the existing fixture-bundle helper path from `tests/python/fixture_parity_support.py` for:
  - the selected grouped literal replacement row from `collection_replacement_workflows.py`;
  - the selected grouped single-capture match rows from `grouped_match_workflows.py`; and
  - the whole-manifest grouped-alternation, nested-group, and quantified-nested-group replacement-template bundles.
- The grouped replacement-template suite still validates the current selected case ids, manifest ids, compile-pattern sets, `(operation, helper)` counts, and the replacement-template-specific checks it owns today, including numbered-versus-named coverage and the `subn()` first-match-only count expectations.
- `tests/python/test_callable_replacement_parity_suite.py` no longer defines a local `FixtureBundle` dataclass or `_fixture_bundle(...)` loader.
- `tests/python/test_callable_replacement_parity_suite.py` reuses the shared fixture-bundle helper surface from `tests/python/fixture_parity_support.py`; if one small shared helper addition is necessary for raw manifest-case lookup or compile-pattern projection, keep it generic and cover it in `tests/python/test_fixture_parity_support_contract.py`.
- The callable-replacement suite still preserves:
  - the current published fixture discovery assertion;
  - the current pending-manifest bookkeeping;
  - the raw callable-replacement reference validation against the manifest payloads; and
  - the current explicit case-id, compile-pattern, and `(operation, helper)` contracts for the existing quantified-nested-group, conditional-group-exists, broader-range open-ended, and broader-range open-ended conditional callable manifests.
- The callable suite routes its published-fixture path assertion through `published_fixture_paths_from_bundles(FIXTURE_BUNDLES)` instead of inline sorted manifest-path logic.
- The cleanup stays structural only:
  - keep all current callback result parity, callback exception parity, no-match replacement checks, repeated-match checks, compile metadata checks, match snapshot parity, and grouped single-capture assertions intact; and
  - do not change correctness fixtures, benchmark workloads, Rust code, `python/rebar/`, selector behavior, published reports, README copy, or tracked state files beyond this task file.
- After the cleanup:
  - `rg -n '^class FixtureBundle|^class ReplacementFixtureBundle|def _fixture_bundle\\(' tests/python/test_grouped_literal_replacement_template.py tests/python/test_callable_replacement_parity_suite.py` returns no matches.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_grouped_literal_replacement_template.py tests/python/test_callable_replacement_parity_suite.py`.

## Constraints
- Prefer extending the existing helper surface in `tests/python/fixture_parity_support.py` over adding another support module or another bundle abstraction.
- Keep `tests/python/test_open_ended_quantified_group_replacement_template_parity_suite.py` out of scope for this run; this task is only about deleting the last two local bundle wrapper layers.

## Notes
- The live queue is empty, recent runtime reporting shows no inherited-dirty or post-refresh stall, and both tracked and live JSON counts are zero (`tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, `git ls-files '*.json' | wc -l = 0`, `rg --files -g '*.json' | wc -l = 0`), so this run should seed one post-JSON duplicate-plumbing cleanup rather than no-op.
- `rg -n '^class FixtureBundle|^class ReplacementFixtureBundle|def _fixture_bundle\\(' tests/python -g '*.py'` currently reports only:
  - `tests/python/test_grouped_literal_replacement_template.py`
  - `tests/python/test_callable_replacement_parity_suite.py`
- `RBR-0431` is already reserved in tracked backlog/current-status/README state for the feature-owned conditional replacement-template benchmark catch-up, so this architecture follow-on starts at `RBR-0432`.

## Completion
- 2026-03-16: Replaced `tests/python/test_grouped_literal_replacement_template.py` and `tests/python/test_callable_replacement_parity_suite.py` with shared `FixtureBundle` usage from `tests/python/fixture_parity_support.py`, removing the last local `ReplacementFixtureBundle` / `FixtureBundle` wrapper classes and the callable suite’s `_fixture_bundle(...)` loader while preserving the current selected-case, manifest-id, compile-pattern, `(operation, helper)`, callable-reference, and replacement-template-specific assertions.
- 2026-03-16: Added narrowly scoped shared helpers for bundle pattern projection and raw manifest-case lookup in `tests/python/fixture_parity_support.py`, covered them in `tests/python/test_fixture_parity_support_contract.py`, and routed the callable suite’s published fixture discovery assertion through `published_fixture_paths_from_bundles(FIXTURE_BUNDLES)`.
- 2026-03-16: Verified `rg -n '^class FixtureBundle|^class ReplacementFixtureBundle|def _fixture_bundle\\(' tests/python/test_grouped_literal_replacement_template.py tests/python/test_callable_replacement_parity_suite.py` returned no matches, and `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_grouped_literal_replacement_template.py tests/python/test_callable_replacement_parity_suite.py` passed (`1114 passed in 0.86s`).
