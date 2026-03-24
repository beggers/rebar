# RBR-1179: Publish conditional group-exists nested callable workflows

Status: ready
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Reopen the shared `conditional-group-exists-callable-replacement-workflows` correctness frontier with the exact nested conditional callable `str` rows that `RBR-1177` already made Rust-backed on the shared parity owner path, publishing that bounded slice before benchmark catch-up, bytes mirrors, quantified conditional callable follow-ons, or broader callable-helper expansion widen this family again.

## Pattern Pair
- `rebar.sub(r"a(b)?c(?(1)(?(1)d|e)|f)", callable_match_group(1, suffix="x"), "zzabcdzz")`
- `rebar.compile(r"a(?P<word>b)?c(?(word)(?(word)d|e)|f)").subn(callable_match_group("word", suffix="x"), "zzacfzz", 1)`

## Deliverables
- `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- Extend `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` with exactly the eight adjacent nested conditional callable `str` rows already exercised on the shared direct parity owner path for `r"a(b)?c(?(1)(?(1)d|e)|f)"` and `r"a(?P<word>b)?c(?(word)(?(word)d|e)|f)"`:
  - add numbered module `sub()` and `subn()` rows using `callable_match_group(1, suffix="x")`, with the present-arm success case on `"zzabcdzz"` and the absent-capture `TypeError` case on `"zzacfzz"`;
  - add numbered compiled-pattern `sub()` and `subn()` rows for the same present-arm success and absent-capture `TypeError` workflows;
  - add named module `sub()` and `subn()` rows using `callable_match_group("word", suffix="x")`, with the matching present-arm success and absent-capture `TypeError` workflows; and
  - add named compiled-pattern `sub()` and `subn()` rows for the same named workflows.
- Keep the work on the existing conditional callable correctness owner path instead of creating another manifest or detached publication table:
  - update `tests/python/test_callable_replacement_parity_suite.py` only as needed so the shared callable manifest expectations and representative publication assertions stay aligned with the widened nested conditional `str` slice on `conditional-group-exists-callable-replacement-workflows`;
  - update `tests/conformance/test_combined_correctness_scorecards.py` only as needed so the representative `conditional-group-exists-callable-replacement-workflows` scorecard expectations stay aligned with the widened nested conditional callable publication slice; and
  - preserve the already-published simple two-arm, alternation-heavy, and `count=-1` callable rows plus the surrounding replacement-owner families on the same owner path.
- Regenerate `reports/correctness/latest.py` honestly on the tracked combined correctness surface:
  - the tracked report gains the eight new nested conditional callable `str` rows for `collection.replacement.conditional_group_exists.callable`;
  - the exact callable manifest moves from `40` passing cases to `48` passing cases with no new explicit failures or unimplemented rows;
  - the combined correctness summary moves from `1693/1693` passing cases to `1701/1701` passing cases while the manifest count stays at `114`; and
  - do not widen this run into benchmark publication, bytes mirrors, quantified conditional callable follow-ons, or broader callable-helper expansion beyond `callable_match_group`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists_nested_callable_replacement'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/rbr-1179-conditional-nested-callable.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or tracked ops state prose in this run.
- Reuse the existing `conditional_group_exists_callable_replacement_workflows.py` manifest and shared callable parity suite. Do not create another correctness manifest, another callable parity module, or a detached conditional callable publication file.
- Keep the scope pinned to the exact eight nested conditional callable `str` rows above. Leave same-family benchmark catch-up, bytes mirrors, quantified conditional callable follow-ons, and broader callable helper expansion for later tasks.

## Notes
- `RBR-1179` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this run; and
  - `rg -n "RBR-1179|nested-callable-workflows|conditional group-exists nested callable workflows" ops/tasks ops/state -g '*.md'` returned no matches in this planning run.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest done same-family frontier leaves this exact correctness-publication slice concrete after `RBR-1177`:
  - `ops/tasks/done/RBR-1177-implement-conditional-group-exists-nested-callable-parity.md` completed the missing Rust-backed nested conditional callable `str` parity slice and explicitly left correctness publication, benchmark catch-up, bytes mirrors, and quantified conditional callable follow-ons for later on this owner path;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists_nested_callable_replacement'` returned `32 passed, 4250 deselected` in this planning run, confirming the exact numbered and named module/pattern nested conditional callable owner path already matches CPython directly on the shared parity surface;
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/feature-planning-rbr-1179-current.py` returned `40 executed / 40 passed` in this planning run, confirming the current published callable manifest still stops before these nested rows; and
  - the adjacent benchmark owner path in `benchmarks/workloads/conditional_group_exists_boundary.py` still limits the nested conditional slice to module-search, `Pattern.fullmatch`, and constant-replacement probes, so the next smallest same-family follow-on remains correctness publication rather than immediate benchmark catch-up.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists_nested_callable_replacement'` returned `32 passed, 4250 deselected`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py` returned `45 passed, 2332 subtests passed`;
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/rbr-1179-conditional-nested-callable.py` is expected to move from the currently validated `40 executed / 40 passed` to `48 executed / 48 passed` once this publication lands; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` is expected to move from the current `1693 executed / 1693 passed` surface to `1701 executed / 1701 passed` once this publication lands.
