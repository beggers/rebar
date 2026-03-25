Status: ready
Owner: feature-implementation
Created: 2026-03-25

## Goal
- Close the next smallest callable-replacement parity gap on the shared Python owner path by adding module-entrypoint wrong-return-type parity for the already-published open-ended nested branch-local-backreference callable slice, mirroring the existing pattern-side behavior checks without widening into the adjacent conditional follow-on.

## Pattern Pair
- `a((b|c){2,})\\2d`
- `a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d`

## Deliverables
- `tests/python/test_callable_replacement_parity_suite.py`

## Acceptance Criteria
- Extend `tests/python/test_callable_replacement_parity_suite.py` with one bounded module wrong-return-type parity expansion for the exact published `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows` slice:
  - keep the module-entrypoint assertion on the existing `assert_callable_replacement_return_type_error_parity(...)` helper path with `use_compiled_pattern=False`;
  - widen `MODULE_RETURN_TYPE_ERROR_PARITY_MANIFEST_IDS` (or its exact successor) so `test_module_callable_replacement_wrong_return_type_matches_cpython(...)` exercises the eight module rows from this manifest;
  - cover the already-published numbered and named `sub()` / `subn()` rows for both `str` and `bytes`; and
  - do not invent another direct-case table, another manifest registry, or a manifest-specific special case.
- Keep the return-type frontier derived from the live callable manifest inventory instead of adding sidecars:
  - preserve `CALLABLE_RETURN_TYPE_ERROR_FRONTIER_MANIFEST_IDS`, `MODULE_RETURN_TYPE_ERROR_CASES`, `MODULE_RETURN_TYPE_ERROR_PARITY_MANIFEST_IDS`, and `PATTERN_RETURN_TYPE_ERROR_CASES` as the canonical live selectors;
  - keep the existing coverage tests that prove the return-type frontier and active parity subset stay aligned with the published callable manifest inventory; and
  - leave the adjacent conditional branch-local-backreference callable follow-on for a separate planning pass.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'module_callable_replacement_wrong_return_type or pattern_callable_replacement_wrong_return_type or return_type_error_cases_cover_quantified_callable_fixture_frontier'`

## Constraints
- Keep the scope pinned to module-entrypoint wrong-return-type parity for `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows` only.
- Limit edits to `tests/python/test_callable_replacement_parity_suite.py`. Do not widen into fixtures, benchmark owner files, reports, runtime implementation work, or tracked ops/state prose.

## Notes
- `RBR-1258` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this planning run; and
  - the highest filed task before this seed was `RBR-1257`.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The tracked published scorecards remain fully green on the bounded published surface in this run:
  - `reports/correctness/latest.py` reports `1853` total / `1853` passed / `0` failed / `0` unimplemented cases across `114` manifests; and
  - `reports/benchmarks/latest.py` reports `1219` total / `1219` measured workloads with `0` known gaps across `30` manifests.
- One narrow same-owner-path check pins this exact follow-on after `RBR-1256`:
  - `ops/tasks/done/RBR-1256-add-module-callable-wrong-return-type-parity-for-open-ended-nested-backtracking-heavy-slice.md` explicitly leaves the open-ended branch-local-backreference sibling as the next exact post-drain manifest on this owner route;
  - `tests/python/test_callable_replacement_parity_suite.py` already includes `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows` in `CALLABLE_RETURN_TYPE_ERROR_FRONTIER_MANIFEST_IDS` and `PATTERN_RETURN_TYPE_ERROR_PARITY_MANIFEST_IDS`, but `MODULE_RETURN_TYPE_ERROR_PARITY_MANIFEST_IDS` still stops at the adjacent backtracking-heavy sibling; and
  - a direct runtime probe over all eight module `sub()` / `subn()` rows for this manifest returned matching CPython `TypeError` args from `re` and `rebar`, confirming the bounded behavior already exists on the current branch and the missing work is parity-selector catch-up rather than another implementation slice.
- The next exact post-drain follow-on on this owner path is already pinned by one adjacent same-family check:
  - `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-callable-replacement-workflows` is the next remaining manifest in `CALLABLE_RETURN_TYPE_ERROR_FRONTIER_MANIFEST_IDS`; and
  - a direct runtime probe over its eight module `sub()` / `subn()` rows also returned matching CPython `TypeError` args from `re` and `rebar`, so the surviving post-drain frontier is the conditional sibling parity catch-up pinned to `a((b|c){2,})\\2(?(2)d|e)` and `a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)`.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'module_callable_replacement_wrong_return_type or pattern_callable_replacement_wrong_return_type or return_type_error_cases_cover_quantified_callable_fixture_frontier'` returned `220 passed, 6100 deselected`.
