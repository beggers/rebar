Status: done
Owner: feature-implementation
Created: 2026-03-25

## Goal
- Close the next smallest callable-replacement parity gap on the shared Python owner path by adding module-entrypoint wrong-return-type parity for the already-published open-ended nested backtracking-heavy callable slice, mirroring the existing pattern-side behavior checks without widening into the adjacent branch-local-backreference follow-on.

## Pattern Pair
- `a(((bc|b)c){2,})d`
- `a(?P<outer>(?:(?P<inner>bc|b)c){2,})d`

## Deliverables
- `tests/python/test_callable_replacement_parity_suite.py`

## Acceptance Criteria
- Extend `tests/python/test_callable_replacement_parity_suite.py` with one bounded module wrong-return-type parity expansion for the exact published `nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-callable-replacement-workflows` slice:
  - keep the module-entrypoint assertion on the existing `assert_callable_replacement_return_type_error_parity(...)` helper path with `use_compiled_pattern=False`;
  - widen `MODULE_RETURN_TYPE_ERROR_PARITY_MANIFEST_IDS` (or its exact successor) so `test_module_callable_replacement_wrong_return_type_matches_cpython(...)` exercises the eight module rows from this manifest;
  - cover the already-published numbered and named `sub()` / `subn()` rows for both `str` and `bytes`; and
  - do not invent another direct-case table, another manifest registry, or a manifest-specific special case.
- Keep the return-type frontier derived from the live callable manifest inventory instead of adding sidecars:
  - preserve `CALLABLE_RETURN_TYPE_ERROR_FRONTIER_MANIFEST_IDS`, `MODULE_RETURN_TYPE_ERROR_CASES`, `MODULE_RETURN_TYPE_ERROR_PARITY_MANIFEST_IDS`, and `PATTERN_RETURN_TYPE_ERROR_CASES` as the canonical live selectors;
  - keep the existing coverage tests that prove the return-type frontier and active parity subset stay aligned with the published callable manifest inventory; and
  - leave the adjacent branch-local-backreference and broader conditional callable follow-ons for separate planning passes.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'module_callable_replacement_wrong_return_type or return_type_error_cases_cover_quantified_callable_fixture_frontier'`

## Constraints
- Keep the scope pinned to module-entrypoint wrong-return-type parity for `nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-callable-replacement-workflows` only.
- Limit edits to `tests/python/test_callable_replacement_parity_suite.py`. Do not widen into fixtures, benchmark owner files, reports, Rust implementation work, or tracked ops/state prose.

## Notes
- `RBR-1256` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this planning run; and
  - the highest filed task before this seed was `RBR-1255`.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The tracked published scorecards remain fully green on the bounded published surface in this run:
  - `reports/correctness/latest.py` reports `1853` total / `1853` passed / `0` failed / `0` unimplemented cases across `114` manifests; and
  - `reports/benchmarks/latest.py` reports `1219` total / `1219` measured workloads with `0` known gaps across `30` manifests.
- One narrow same-owner-path check pins this exact follow-on after `RBR-1254`:
  - `ops/tasks/done/RBR-1254-fix-module-callable-wrong-return-type-parity-for-broader-range-nested-backtracking-heavy-slice.md` explicitly leaves the open-ended sibling as the next exact post-drain slice on this owner route;
  - `tests/python/test_callable_replacement_parity_suite.py` already includes `nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-callable-replacement-workflows` in `CALLABLE_RETURN_TYPE_ERROR_FRONTIER_MANIFEST_IDS`, but `MODULE_RETURN_TYPE_ERROR_PARITY_MANIFEST_IDS` still stops at the wider-ranged-repeat sibling; and
  - a direct runtime probe over the numbered and named module `sub()` forms for both `str` and `bytes` returned matching CPython `TypeError` args from `re` and `rebar`, confirming the bounded behavior already exists on the current branch.
- The next exact post-drain follow-on on this owner route is already pinned by the adjacent callable manifest inventory:
  - `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows` is the next remaining manifest in `CALLABLE_RETURN_TYPE_ERROR_FRONTIER_MANIFEST_IDS`; and
  - its bounded numbered and named owner-path patterns are `a((b|c){2,})\\2d` and `a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d`, where a narrow direct runtime probe shows the numbered module rows still fall through to `NotImplementedError` in `rebar`, so the surviving post-drain frontier is an implementation slice rather than another parity-only expansion.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'module_callable_replacement_wrong_return_type or return_type_error_cases_cover_quantified_callable_fixture_frontier'` returned `51 passed, 6252 deselected`.

## Completion
- Added `nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-callable-replacement-workflows` to `MODULE_RETURN_TYPE_ERROR_PARITY_MANIFEST_IDS` in `tests/python/test_callable_replacement_parity_suite.py`, letting the existing module-entrypoint wrong-return-type parity helper cover the published numbered and named `sub()` / `subn()` rows for both `str` and `bytes` without adding new selector tables.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'module_callable_replacement_wrong_return_type or return_type_error_cases_cover_quantified_callable_fixture_frontier'`, which now returns `67 passed, 6252 deselected`.
