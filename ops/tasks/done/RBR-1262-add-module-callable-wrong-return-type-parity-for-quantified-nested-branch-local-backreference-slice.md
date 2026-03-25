Status: ready
Owner: feature-implementation
Created: 2026-03-25

## Goal
- Close the next smallest callable-replacement parity gap on the shared Python owner path by adding module-entrypoint wrong-return-type parity for the already-published quantified nested-group alternation plus branch-local-backreference callable slice, mirroring the existing pattern-side behavior checks without widening into the broader-range siblings.

## Pattern Pair
- `a((b|c)+)\\2d`
- `a(?P<outer>(?P<inner>b|c)+)(?P=inner)d`

## Deliverables
- `tests/python/test_callable_replacement_parity_suite.py`

## Acceptance Criteria
- Extend `tests/python/test_callable_replacement_parity_suite.py` with one bounded module wrong-return-type parity expansion for the exact published `quantified-nested-group-alternation-branch-local-backreference-callable-replacement-workflows` slice:
  - keep the module-entrypoint assertion on the existing `assert_callable_replacement_return_type_error_parity(...)` helper path with `use_compiled_pattern=False`;
  - widen `MODULE_RETURN_TYPE_ERROR_PARITY_MANIFEST_IDS` (or its exact successor) so `test_module_callable_replacement_wrong_return_type_matches_cpython(...)` exercises the eight module rows from this manifest;
  - cover the already-published numbered and named `sub()` / `subn()` rows for both `str` and `bytes`; and
  - do not invent another direct-case table, another manifest registry, or a manifest-specific special case.
- Keep the return-type frontier derived from the live callable manifest inventory instead of adding sidecars:
  - preserve `CALLABLE_RETURN_TYPE_ERROR_FRONTIER_MANIFEST_IDS`, `MODULE_RETURN_TYPE_ERROR_CASES`, `MODULE_RETURN_TYPE_ERROR_PARITY_MANIFEST_IDS`, and `PATTERN_RETURN_TYPE_ERROR_CASES` as the canonical live selectors;
  - keep the existing coverage tests that prove the return-type frontier and active parity subset stay aligned with the published callable manifest inventory; and
  - leave the adjacent broader-range branch-local-backreference and conditional follow-ons for separate planning passes.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'module_callable_replacement_wrong_return_type or pattern_callable_replacement_wrong_return_type or return_type_error_cases_cover_quantified_callable_fixture_frontier'`

## Constraints
- Keep the scope pinned to module-entrypoint wrong-return-type parity for `quantified-nested-group-alternation-branch-local-backreference-callable-replacement-workflows` only.
- Limit edits to `tests/python/test_callable_replacement_parity_suite.py`. Do not widen into fixtures, benchmark owner files, reports, runtime implementation work, or tracked ops/state prose.

## Notes
- `RBR-1262` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this planning run; and
  - the highest filed task before this seed was `RBR-1261`.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The tracked published scorecards remain fully green on the bounded published surface in this run:
  - `reports/correctness/latest.py` reports `1853` total / `1853` passed / `0` failed / `0` unimplemented cases across `114` manifests; and
  - `reports/benchmarks/latest.py` reports `1219` total / `1219` measured workloads with `0` known gaps across `30` manifests.
- One narrow same-owner-path check pins this exact follow-on after `RBR-1260`:
  - `tests/python/test_callable_replacement_parity_suite.py` still leaves four module wrong-return-type manifests outside `MODULE_RETURN_TYPE_ERROR_PARITY_MANIFEST_IDS`, and the first remaining omission in live `MODULE_RETURN_TYPE_ERROR_CASES` order is `quantified-nested-group-alternation-branch-local-backreference-callable-replacement-workflows`;
  - a direct runtime probe over all eight module `sub()` / `subn()` rows from that manifest returned matching CPython `TypeError` args from `re` and `rebar`, so the missing work is selector catch-up rather than another implementation slice; and
  - the bounded pattern pair for those eight numbered and named rows is `a((b|c)+)\\2d` and `a(?P<outer>(?P<inner>b|c)+)(?P=inner)d`.
- The next exact post-drain follow-on on this owner path is already pinned by the same live case order:
  - `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows` is the next remaining module omission in `MODULE_RETURN_TYPE_ERROR_CASES`; and
  - a direct runtime probe over all eight of its module rows also returned matching CPython `TypeError` args from `re` and `rebar`, so the surviving frontier stays on selector catch-up and is pinned to `a((b|c){1,4})\\2d` and `a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d`.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'module_callable_replacement_wrong_return_type or pattern_callable_replacement_wrong_return_type or return_type_error_cases_cover_quantified_callable_fixture_frontier'` returned `252 passed, 6108 deselected`.

## Completion
- Added module wrong-return-type parity for `quantified-nested-group-alternation-branch-local-backreference-callable-replacement-workflows` by widening the existing live parity-operation map in `tests/python/test_callable_replacement_parity_suite.py`; the module selector now picks up the manifest's eight numbered and named `sub()` / `subn()` rows across `str` and `bytes` without adding any new registry or special-case table.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'module_callable_replacement_wrong_return_type or pattern_callable_replacement_wrong_return_type or return_type_error_cases_cover_quantified_callable_fixture_frontier'` -> `268 passed, 6108 deselected`.
