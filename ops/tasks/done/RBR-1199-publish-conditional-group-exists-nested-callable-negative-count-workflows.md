# RBR-1199: Publish conditional group-exists nested callable negative-count workflows

Status: done
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Reopen the shared `conditional-group-exists-callable-replacement-workflows` correctness frontier with the exact nested conditional callable negative-count `str` rows that the live direct parity owner path already covers, publishing that bounded `count=-1` no-substitution slice before broader callable-helper expansion widens this family again.

## Pattern Pair
- `rebar.sub(r"a(b)?c(?(1)(?(1)d|e)|f)", lambda m: m.group(1) + "x", "zzabcdzz", -1)`
- `rebar.compile(r"a(?P<word>b)?c(?(word)(?(word)d|e)|f)").subn(lambda m: m.group("word") + "x", "zzacfzz", -1)`

## Deliverables
- `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- Extend `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` with exactly the four adjacent nested conditional callable negative-count `str` publication rows already exercised on the shared direct parity owner path for `a(b)?c(?(1)(?(1)d|e)|f)` and `a(?P<word>b)?c(?(word)(?(word)d|e)|f)`:
  - add the numbered module `sub()` `count=-1` row on `"zzabcdzz"` using `lambda m: m.group(1) + "x"`;
  - add the named module `subn()` `count=-1` row on `"zzacfzz"` using `lambda m: m.group("word") + "x"`;
  - add the numbered compiled-pattern `sub()` `count=-1` row for the same shared no-substitution workflow; and
  - add the named compiled-pattern `subn()` `count=-1` row for the same zero-replacement tuple workflow.
- Keep the work on the existing conditional callable correctness owner path instead of creating another manifest or detached publication table:
  - update `tests/python/test_callable_replacement_parity_suite.py` only as needed so the shared callable manifest expectations and representative publication assertions stay aligned with the widened nested negative-count slice on `conditional-group-exists-callable-replacement-workflows`;
  - update `tests/conformance/test_combined_correctness_scorecards.py` only as needed so the callable negative-count follow-on scorecard expectations stay aligned with the widened nested slice; and
  - preserve the already-published two-arm, alternation-heavy, nested present/absent, quantified, and quantified `bytes` callable rows plus the existing top-level negative-count rows on the same owner path.
- Regenerate `reports/correctness/latest.py` honestly on the tracked combined correctness surface:
  - the tracked report gains the four new nested conditional callable negative-count `str` rows for `collection.replacement.conditional_group_exists.callable`;
  - the exact callable manifest moves from `72` passing cases to `76` passing cases with no new explicit failures or unimplemented rows;
  - the combined correctness summary moves from `1725/1725` passing cases to `1729/1729` passing cases while the manifest count stays at `114`; and
  - do not widen this run into benchmark publication, Rust implementation work, or broader callable-helper expansion beyond `match.group(...) + "x"`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and nested and negative_count'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'negative_count_follow_on_cases'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/rbr-1199-conditional-nested-negative-count.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or tracked ops state prose in this run.
- Reuse the existing `conditional_group_exists_callable_replacement_workflows.py` manifest and shared callable parity suite. Do not create another correctness manifest, another callable parity module, or a detached nested callable publication file.
- Keep the scope pinned to the exact four nested conditional callable negative-count `str` rows above. Leave benchmark-side nested negative-count anchor work, `bytes` mirrors, and broader callable-helper expansion for later tasks.

## Notes
- `RBR-1199` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this run; and
  - `rg -n "RBR-1199|RBR-1200|RBR-1201" ops/tasks ops/state -g '*.md'` matched only historical mentions inside completed task files, not a live reservation for this id.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest done same-family frontier leaves this exact correctness-publication slice concrete after `RBR-1197`, and the narrow owner-path scan confirms it is the smallest still-missing accepted slice on this callable family:
  - `ops/tasks/done/RBR-1195-publish-conditional-group-exists-quantified-callable-bytes-workflows.md` and `ops/tasks/done/RBR-1197-benchmark-conditional-group-exists-quantified-callable-bytes-workloads.md` closed the quantified callable `bytes` publication and benchmark catch-up slices, leaving no queued same-family follow-on;
  - `tests/python/test_callable_replacement_parity_suite.py` already exposes the exact nested negative-count direct parity slice through `CONDITIONAL_GROUP_EXISTS_NESTED_NEGATIVE_COUNT_CASES` plus `test_conditional_group_exists_nested_callable_replacement_negative_count_short_circuits_without_callback`, covering numbered and named module/pattern `sub()` and `subn()` `count=-1` no-callback workflows on the pattern pair above;
  - `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` and `reports/correctness/latest.py` still stop at the top-level conditional callable negative-count rows and do not yet publish any nested negative-count callable cases on this owner path; and
  - `benchmarks/workloads/conditional_group_exists_boundary.py` likewise exposes no nested callable negative-count benchmark anchor yet, so no exact post-publication benchmark follow-on is pinned in this run beyond broader callable-helper expansion.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and nested and negative_count'` returned `16 passed, 4969 deselected`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'negative_count_follow_on_cases'` returned `2 passed, 43 deselected`;
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/feature-planning-conditional-nested-negative-count-current.py` returned `72 executed / 72 passed`; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` returned `1725 executed / 1725 passed`.

## Completion
- Added the four nested conditional callable `count=-1` `str` publication rows on the existing `conditional-group-exists-callable-replacement-workflows` manifest path and synced the shared callable parity/scorecard expectations without widening into bytes mirrors or benchmark work.
- Verified:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and nested and negative_count'` returned `16 passed, 5001 deselected`.
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'negative_count_follow_on_cases'` returned `2 passed, 43 deselected`.
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/rbr-1199-conditional-nested-negative-count.py` returned `76 executed / 76 passed`.
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` returned `1729 executed / 1729 passed`.
- Tracked publication check: `reports/correctness/latest.py` now records `collection.replacement.conditional_group_exists.callable` at `76` passed / `76` total cases, and the combined tracked summary at `1729` executed / `1729` passed / `1729` total cases across the unchanged `114` published manifests.
