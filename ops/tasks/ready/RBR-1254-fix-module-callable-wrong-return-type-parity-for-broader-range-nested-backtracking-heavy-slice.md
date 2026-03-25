Status: ready
Owner: feature-implementation
Created: 2026-03-25

## Goal
- Close the next concrete callable-replacement implementation gap on the shared Python owner path by fixing module-entrypoint wrong-return-type parity for the already-published broader-range nested backtracking-heavy callable slice, then letting the existing module parity test lane cover that manifest without widening into the adjacent open-ended follow-on.

## Pattern Pair
- `a(((bc|b)c){1,4})d`
- `a(?P<outer>(?:(?P<inner>bc|b)c){1,4})d`

## Deliverables
- `python/rebar/__init__.py`
- `tests/python/test_callable_replacement_parity_suite.py`

## Acceptance Criteria
- Fix the shared module callable-substitution path in `python/rebar/__init__.py` so the exact module rows from `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-callable-replacement-workflows` raise CPython-matching `TypeError` args when a callable replacement returns the wrong text model:
  - cover the numbered and named `sub()` / `subn()` rows for both `str` and `bytes`;
  - match CPython on the module-entrypoint wrong-return-type message for lower-bound and first-match-only cases whose first replacement starts at offset `0`; and
  - keep the fix scoped to the existing callable join/coercion path instead of inventing a manifest-specific special case.
- Extend the active module wrong-return-type parity slice in `tests/python/test_callable_replacement_parity_suite.py` to include `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-callable-replacement-workflows`:
  - keep `CALLABLE_RETURN_TYPE_ERROR_MANIFEST_KEYWORDS`, `_callable_return_type_error_expected_manifest_ids()`, `MODULE_RETURN_TYPE_ERROR_CASES`, and `PATTERN_RETURN_TYPE_ERROR_CASES` as the canonical live selectors;
  - widen `MODULE_RETURN_TYPE_ERROR_PARITY_MANIFEST_IDS` (or its exact successor) so `test_module_callable_replacement_wrong_return_type_matches_cpython(...)` exercises the eight module rows from this manifest through the existing helper path; and
  - leave the adjacent open-ended broader-range manifest and any branch-local-backreference or conditional callable follow-ons for later planning passes.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'module_callable_replacement_wrong_return_type or return_type_error_cases_cover_quantified_callable_fixture_frontier'`

## Constraints
- Keep the scope pinned to module-entrypoint wrong-return-type parity for `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-callable-replacement-workflows` only.
- Limit durable edits to `python/rebar/__init__.py` and `tests/python/test_callable_replacement_parity_suite.py`. Do not widen into fixtures, benchmark manifests, reports, or tracked ops/state prose.

## Notes
- `RBR-1254` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this planning run; and
  - the highest filed task before this seed was `RBR-1253`.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The tracked published scorecards remain fully green on the bounded published surface in this run:
  - `reports/correctness/latest.py` reports `1853` total / `1853` passed / `0` failed / `0` unimplemented cases across `114` manifests; and
  - `reports/benchmarks/latest.py` reports `1219` total / `1219` measured workloads with `0` known gaps across `30` manifests.
- One narrow same-owner-path check shows the next gap is implementation, not publication-only:
  - `ops/tasks/done/RBR-1252-add-module-callable-wrong-return-type-parity-for-quantified-nested-group-alternation-slice.md` leaves the broader-range nested backtracking-heavy callable manifest as the next exact module wrong-return-type follow-on on this owner route;
  - `tests/python/test_callable_replacement_parity_suite.py` still restricts `MODULE_RETURN_TYPE_ERROR_PARITY_MANIFEST_IDS` to `quantified-nested-group-callable-replacement-workflows` and `quantified-nested-group-alternation-callable-replacement-workflows`, even though `MODULE_RETURN_TYPE_ERROR_CASES` already includes the broader-range and open-ended manifests;
  - a direct runtime probe on `re.sub(r'a(((bc|b)c){1,4})d', lambda match: b'x', 'abcd')` raised `TypeError('sequence item 0: expected str instance, bytes found')`, while the matching `rebar.sub(...)` call raised `TypeError('sequence item 1: expected str instance, bytes found')`; and
  - the same mismatch reproduces on the named module form `re.sub(r'a(?P<outer>(?:(?P<inner>bc|b)c){1,4})d', lambda match: b'x', 'abccbccd')`, so the missing work is the shared module callable replacement implementation path rather than a missing fixture or benchmark row.
- The next exact post-drain follow-on on this owner path is already pinned by the adjacent manifest inventory:
  - `tests/python/test_callable_replacement_parity_suite.py` orders the same return-type frontier onward to `nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-callable-replacement-workflows`; and
  - that next slice is pinned to `a(((bc|b)c){2,})d` and `a(?P<outer>(?:(?P<inner>bc|b)c){2,})d`.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'module_callable_replacement_wrong_return_type or return_type_error_cases_cover_quantified_callable_fixture_frontier'` returned `35 passed, 6252 deselected`.
