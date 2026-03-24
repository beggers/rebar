Status: ready
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Close the next smallest callable-replacement parity gap on the shared Python owner path by adding module-entrypoint wrong-return-type parity for the already-published quantified nested-group alternation callable slice, mirroring the existing pattern-side behavior checks without widening into the broader-range or branch-local-backreference manifests.

## Pattern Pair
- `a((b|c)+)d`
- `a(?P<outer>(?P<inner>b|c)+)d`

## Deliverables
- `tests/python/test_callable_replacement_parity_suite.py`

## Acceptance Criteria
- Extend `tests/python/test_callable_replacement_parity_suite.py` with one bounded module wrong-return-type parity check for the exact published `quantified-nested-group-alternation-callable-replacement-workflows` slice:
  - add a module-entrypoint parity test that parametrizes over the existing `MODULE_RETURN_TYPE_ERROR_CASES`;
  - scope that new behavioral assertion to the eight module cases whose `manifest_id` is `quantified-nested-group-alternation-callable-replacement-workflows`;
  - keep the coverage on the existing wrong-return-type helper path by calling `assert_callable_replacement_return_type_error_parity(...)` with `use_compiled_pattern=False`; and
  - cover the already-published numbered and named `sub()` / `subn()` rows for both `str` and `bytes` without inventing another direct-case table or another manifest registry.
- Keep the return-type frontier derived from the live callable manifest inventory instead of adding sidecars:
  - preserve `CALLABLE_RETURN_TYPE_ERROR_MANIFEST_KEYWORDS`, `_callable_return_type_error_expected_manifest_ids()`, `MODULE_RETURN_TYPE_ERROR_CASES`, and `PATTERN_RETURN_TYPE_ERROR_CASES` as the canonical selectors;
  - keep the existing coverage tests that prove the return-type-error frontier is restricted to the quantified, broader-range, and open-ended callable manifests; and
  - do not widen this run into published fixture edits, benchmark manifests, reports, Rust implementation work, or the adjacent broader-range/open-ended and branch-local-backreference callable follow-ons.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'module_callable_replacement_wrong_return_type or return_type_error_cases_cover_quantified_callable_fixture_frontier'`

## Constraints
- Keep the scope pinned to module-entrypoint wrong-return-type parity for `quantified-nested-group-alternation-callable-replacement-workflows` only. Leave the adjacent broader-range/open-ended and branch-local-backreference callable return-type-error follow-ons for separate planning passes.
- Limit edits to `tests/python/test_callable_replacement_parity_suite.py`. Do not widen into fixtures, benchmark owner files, reports, or tracked ops/state prose.

## Notes
- `RBR-1252` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this planning run; and
  - the highest filed task before this seed was `RBR-1251`.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The tracked published scorecards already reflect the closed prior frontier in this run:
  - `reports/correctness/latest.py` reports `1853` total / `1853` passed / `0` failed / `0` unimplemented cases across `114` manifests; and
  - `reports/benchmarks/latest.py` reports `1219` total / `1219` measured workloads with `0` known gaps across `30` manifests.
- One narrow same-owner-path check pins this exact follow-on after `RBR-1250`:
  - `ops/tasks/done/RBR-1250-add-module-callable-wrong-return-type-parity-for-quantified-nested-group-slice.md` explicitly leaves `quantified-nested-group-alternation-callable-replacement-workflows` as the next exact post-drain module wrong-return-type slice on this owner route;
  - `tests/python/test_callable_replacement_parity_suite.py` still restricts `test_module_callable_replacement_wrong_return_type_matches_cpython(...)` to `quantified-nested-group-callable-replacement-workflows`, even though `MODULE_RETURN_TYPE_ERROR_CASES` already includes the adjacent quantified nested-group alternation module rows; and
  - a direct runtime probe over `module-sub-callable-quantified-nested-group-alternation-numbered-lower-bound-b-branch-str` returned the same `TypeError('sequence item 1: expected str instance, bytes found')` from both `re` and `rebar`, confirming the bounded module behavior already exists on the current branch.
- The next exact post-drain follow-on on this owner path is already pinned by the same direct case inventory:
  - the manifest order in `MODULE_RETURN_TYPE_ERROR_CASES` continues from `quantified-nested-group-alternation-callable-replacement-workflows` to `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-callable-replacement-workflows`; and
  - that adjacent owner-path slice is pinned to `a(((bc|b)c){1,4})d` and `a(?P<outer>(?:(?P<inner>bc|b)c){1,4})d`.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'module_callable_replacement_wrong_return_type or return_type_error_cases_cover_quantified_callable_fixture_frontier'` returned `18 passed, 6252 deselected`.
