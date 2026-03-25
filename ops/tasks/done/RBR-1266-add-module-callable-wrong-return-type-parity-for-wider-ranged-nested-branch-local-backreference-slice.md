Status: done
Owner: feature-implementation
Created: 2026-03-25

## Goal
- Restore the next smallest callable-replacement parity slice on the shared Python owner path by adding module-entrypoint wrong-return-type parity for the already-published broader `{1,4}` nested branch-local-backreference callable workflows, matching the current pattern-side coverage without widening into the adjacent conditional sibling.

## Pattern Pair
- `a((b|c){1,4})\\2d`
- `a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d`

## Deliverables
- `tests/python/test_callable_replacement_parity_suite.py`

## Acceptance Criteria
- Extend `tests/python/test_callable_replacement_parity_suite.py` with one bounded module wrong-return-type parity catch-up for the exact published `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows` slice:
  - keep the module-entrypoint assertion on the existing `assert_callable_replacement_return_type_error_parity(...)` helper path with `use_compiled_pattern=False`;
  - widen `CALLABLE_RETURN_TYPE_ERROR_PARITY_OPERATIONS_BY_MANIFEST_ID` (or its exact successor) so `MODULE_RETURN_TYPE_ERROR_PARITY_MANIFEST_IDS` picks up this manifest for `module_call`;
  - cover the already-published numbered and named `sub()` / `subn()` module rows for this manifest across the existing `str` and `bytes` text-model surface; and
  - do not invent another direct-case table, manifest registry, or manifest-specific special case.
- Keep the return-type frontier derived from the live callable manifest inventory instead of adding sidecars:
  - preserve `CALLABLE_RETURN_TYPE_ERROR_FRONTIER_MANIFEST_IDS`, `MODULE_RETURN_TYPE_ERROR_CASES`, `MODULE_RETURN_TYPE_ERROR_PARITY_MANIFEST_IDS`, and `PATTERN_RETURN_TYPE_ERROR_CASES` as the canonical live selectors;
  - keep the existing coverage tests that prove the return-type frontier and active parity subset stay aligned with the published callable manifest inventory; and
  - leave the broader `{1,4}` branch-local-backreference conditional follow-on for a separate planning pass.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'module_callable_replacement_wrong_return_type or pattern_callable_replacement_wrong_return_type or return_type_error_cases_cover_quantified_callable_fixture_frontier'`

## Constraints
- Keep the scope pinned to module-entrypoint wrong-return-type parity for `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows` only.
- Limit edits to `tests/python/test_callable_replacement_parity_suite.py`. Do not widen into fixtures, benchmark owner files, reports, runtime implementation work, or tracked ops/state prose.

## Notes
- `RBR-1266` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this planning run; and
  - `rg -n "RBR-1266|RBR-1267|RBR-1268" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -g '*.md'` found no reserved follow-on ids in tracked state or live queue files outside historical notes in older done-task files.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The tracked published scorecards remain fully green on the bounded published surface in this run:
  - `reports/correctness/latest.py` reports `1853` total / `1853` passed / `0` failed / `0` unimplemented cases across `114` manifests; and
  - `reports/benchmarks/latest.py` reports `1219` total / `1219` measured workloads with `0` known gaps across `30` manifests.
- One narrow same-owner-path check pins this exact task as the next missing live slice:
  - `tests/python/test_callable_replacement_parity_suite.py` still leaves `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows` outside the module parity selector even though it remains in `CALLABLE_RETURN_TYPE_ERROR_FRONTIER_MANIFEST_IDS` and already has pattern-side wrong-return-type parity;
  - the live manifest spec for this slice exposes eight module rows on the existing mixed text-model surface: numbered and named `sub()` / `subn()` workflows for both `str` and `bytes`; and
  - a direct runtime probe over those eight live module rows, reusing each case's published args/kwargs with the callable replaced by `lambda match: 123`, returned matching CPython `TypeError` payloads from `re` and `rebar`, so the missing work is selector catch-up rather than another implementation slice.
- The next exact post-drain follow-on on this owner path is already pinned by the same live case order:
  - `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-callable-replacement-workflows` is the next remaining omitted module manifest after this one; and
  - the same direct runtime probe over that manifest's eight module rows also returned matching CPython `TypeError` payloads from `re` and `rebar`, so the surviving frontier stays on selector catch-up and is pinned to `a((b|c){1,4})\\2(?(2)d|e)` and `a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)(?(inner)d|e)`.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'module_callable_replacement_wrong_return_type or pattern_callable_replacement_wrong_return_type or return_type_error_cases_cover_quantified_callable_fixture_frontier'` returned `276 passed, 6119 deselected`.

## Completion
- Extended `CALLABLE_RETURN_TYPE_ERROR_PARITY_OPERATIONS_BY_MANIFEST_ID` in `tests/python/test_callable_replacement_parity_suite.py` so `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows` now participates in `module_call` wrong-return-type parity alongside the existing pattern-side coverage.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'module_callable_replacement_wrong_return_type or pattern_callable_replacement_wrong_return_type or return_type_error_cases_cover_quantified_callable_fixture_frontier'`, which passed with `292 passed, 6119 deselected`.
