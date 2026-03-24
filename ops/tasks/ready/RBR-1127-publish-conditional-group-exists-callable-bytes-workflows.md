# RBR-1127: Publish conditional group-exists callable bytes workflows

Status: ready
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Catch the exact two-arm conditional group-exists callable bytes slice up on the published correctness owner path once `RBR-1125` lands, so the existing bounded bytes runtime support for `a(b)?c(?(1)d|e)` and `a(?P<word>b)?c(?(word)d|e)` becomes part of the backend-parameterized correctness surface before any same-family benchmark catch-up widens the frontier.

## Pattern Pair
- `rebar.sub(rb"a(b)?c(?(1)d|e)", lambda m: m.group(1) + b"x", b"zzabcdzz")`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)d|e)").subn(lambda m: m.group("word") + b"x", b"zzacezz", 1)`

## Deliverables
- `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `python/rebar_harness/correctness.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- Extend the existing `conditional-group-exists-callable-replacement-workflows` manifest with only the adjacent bytes cases for the exact bounded numbered and named two-arm conditional callable slice that `RBR-1125` is meant to land:
  - add numbered module `sub()` and `subn(count=1)` bytes rows for `rb"a(b)?c(?(1)d|e)"` on the existing present-capture and absent-capture haystacks;
  - add numbered compiled-pattern `sub()` and `subn(count=1)` bytes rows for that same pattern and bounded callback helper shape;
  - add named module and compiled-pattern bytes `sub()` / `subn(count=1)` rows for `rb"a(?P<word>b)?c(?(word)d|e)"`; and
  - keep the helper pinned to `match.group(1)` / `match.group("word")` so the existing bounded absent-capture `TypeError` observations remain the published callable contract rather than widening into a different callback family.
- Keep the work on the existing callable owner path instead of introducing a detached correctness pack or parity file:
  - update `tests/python/test_callable_replacement_parity_suite.py` only as needed so the manifest contract for `conditional-group-exists-callable-replacement-workflows` expects the new bytes case ids, mixed text-model coverage, and the existing exact compile-pattern pair;
  - update `python/rebar_harness/correctness.py` only as needed so the published correctness selection continues to include this manifest through the ordinary callable replacement path; and
  - preserve the already-landed str conditional callable rows plus neighboring quantified nested-group, alternation, and branch-local-backreference callable manifests on the same owner path.
- Regenerate `reports/correctness/latest.py` so the tracked publication reflects the adjacent bytes workflows without widening beyond this exact slice:
  - the conditional callable manifest no longer appears as `collection.replacement.conditional_group_exists.callable.str` only;
  - the published manifest now includes the eight new bytes rows alongside the existing eight str rows for this exact numbered/named module/pattern `sub()` / `subn(count=1)` slice; and
  - the combined correctness report remains fully passing with no new explicit failures or unimplemented cases.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and callable and bytes'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'conditional_group_exists_callable_replacement_workflows or collection_replacement_conditional_group_exists_callable'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the task bounded to correctness publication for the exact bytes two-arm conditional callable slice above. Do not widen into broader conditional callable shapes, benchmark manifests, README text, or tracked ops prose in this run.
- Treat `RBR-1125` as the implementation prerequisite. If the bounded bytes runtime support is still missing when this task starts, stop and move the task to `blocked/` instead of faking publication through a Python-only fallback.
- Reuse the existing `conditional-group-exists-callable-replacement-workflows` owner path and adjacent callable manifest contract rather than creating another manifest or another correctness suite family for the same bounded slice.

## Notes
- `RBR-1127` is the next available unreserved feature task id in this checkout:
  - the highest live task id across `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, and `ops/tasks/blocked/` is `1126`; and
  - `rg -n 'RBR-1127' ops/tasks ops/state -g '*.md'` returned no matches in this run before this task was written.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The narrow same-family owner-path check in this run shows correctness publication, not another broader runtime task, is the exact post-`RBR-1125` survivor:
  - `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` still publishes only the eight `str` rows for this manifest;
  - `tests/python/test_callable_replacement_parity_suite.py` still records `expected_text_models=STR_ONLY_TEXT_MODELS` and only the eight `str` ids for `conditional-group-exists-callable-replacement-workflows`;
  - `reports/correctness/latest.py` still surfaces `collection.replacement.conditional_group_exists.callable.str` for this manifest, confirming that bytes workflows are unpublished today; and
  - the live ready frontier already reserves the exact prerequisite implementation slice as `RBR-1125`, so the next bounded follow-on on this owner path is publication rather than a sibling parity task.
