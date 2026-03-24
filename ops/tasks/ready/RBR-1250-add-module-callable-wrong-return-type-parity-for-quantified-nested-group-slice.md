Status: ready
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Close the smallest remaining callable-replacement parity gap on the shared Python owner path by adding module-entrypoint wrong-return-type parity for the already-published quantified nested-group callable slice, mirroring the existing pattern-side behavior checks without widening into the adjacent alternation or broader-range manifests.

## Pattern Pair
- `a((bc)+)d`
- `a(?P<outer>(?P<inner>bc)+)d`

## Deliverables
- `tests/python/test_callable_replacement_parity_suite.py`

## Acceptance Criteria
- Extend `tests/python/test_callable_replacement_parity_suite.py` with one bounded module wrong-return-type parity check for the exact published `quantified-nested-group-callable-replacement-workflows` slice:
  - add a module-entrypoint parity test that parametrizes over the existing `MODULE_RETURN_TYPE_ERROR_CASES`;
  - scope that new behavioral assertion to the eight module cases whose `manifest_id` is `quantified-nested-group-callable-replacement-workflows`;
  - keep the coverage on the existing wrong-return-type helper path by calling `assert_callable_replacement_return_type_error_parity(...)` with `use_compiled_pattern=False`; and
  - cover the already-published numbered and named `sub()` / `subn()` rows for both `str` and `bytes` without inventing another direct-case table or another manifest registry.
- Keep the return-type frontier derived from the live callable manifest inventory instead of adding sidecars:
  - preserve `CALLABLE_RETURN_TYPE_ERROR_MANIFEST_KEYWORDS`, `_callable_return_type_error_expected_manifest_ids()`, `MODULE_RETURN_TYPE_ERROR_CASES`, and `PATTERN_RETURN_TYPE_ERROR_CASES` as the canonical selectors;
  - keep the existing coverage tests that prove the return-type-error frontier is restricted to the quantified, broader-range, and open-ended callable manifests; and
  - do not widen this run into published fixture edits, benchmark manifests, reports, Rust implementation work, or the adjacent quantified nested-group alternation follow-on.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'wrong_return_type or return_type_error_cases_cover_quantified_callable_fixture_frontier'`

## Constraints
- Keep the scope pinned to module-entrypoint wrong-return-type parity for `quantified-nested-group-callable-replacement-workflows` only. Leave the adjacent quantified nested-group alternation slice and later broader-range callable return-type-error follow-ons for separate planning passes.
- Limit edits to `tests/python/test_callable_replacement_parity_suite.py`. Do not widen into fixtures, benchmark owner files, reports, or tracked ops/state prose.

## Notes
- `RBR-1250` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this planning run; and
  - the highest filed task before this seed was `RBR-1249`.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The prior conditional callable `count=None` frontier is fully caught up on the published correctness and benchmark surfaces in this run:
  - `reports/correctness/latest.py` reports `1853` total / `1853` passed / `0` failed / `0` unimplemented cases across `114` manifests; and
  - `reports/benchmarks/latest.py` reports `1219` total / `1219` measured workloads with `0` known gaps across `30` manifests.
- One narrow adjacent owner-path check pins this exact follow-on after the conditional callable count-contract lane closed:
  - `ops/tasks/done/RBR-1242-benchmark-conditional-group-exists-quantified-callable-none-count-workloads.md` closes the last concrete quantified conditional callable `count=None` benchmark catch-up slice and leaves no tighter same-family count-contract follow-on pinned;
  - `tests/python/test_callable_replacement_parity_suite.py` already defines `MODULE_RETURN_TYPE_ERROR_CASES` and `PATTERN_RETURN_TYPE_ERROR_CASES`, but only `test_pattern_callable_replacement_wrong_return_type_matches_cpython(...)` currently exercises live wrong-return-type behavior;
  - the first exact missing module slice on that same broader callable owner route is `quantified-nested-group-callable-replacement-workflows`, which contributes eight module rows for `a((bc)+)d` and `a(?P<outer>(?P<inner>bc)+)d` across `str` and `bytes`; and
  - a direct runtime probe over `module-sub-callable-quantified-nested-group-numbered-lower-bound-str` returned the same `TypeError('sequence item 1: expected str instance, bytes found')` from both `re` and `rebar`, confirming the bounded module behavior already exists on the current branch.
- The next exact post-drain follow-on on this owner path is already pinned by the same direct case inventory:
  - `quantified-nested-group-alternation-callable-replacement-workflows` is the adjacent manifest in `MODULE_RETURN_TYPE_ERROR_CASES`; and
  - it contributes the next eight module wrong-return-type rows for `a((b|c)+)d` and `a(?P<outer>(?P<inner>b|c)+)d`.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'wrong_return_type or return_type_error_cases_cover_quantified_callable_fixture_frontier'` returned `154 passed, 6100 deselected`.
