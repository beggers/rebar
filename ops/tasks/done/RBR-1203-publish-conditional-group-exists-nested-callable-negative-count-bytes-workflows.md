# RBR-1203: Publish conditional group-exists nested callable negative-count bytes workflows

Status: done
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Reopen the shared `conditional-group-exists-callable-replacement-workflows` correctness frontier with the exact nested conditional callable negative-count `bytes` rows that the live direct parity owner path already covers, publishing that bounded `count=-1` no-substitution slice before the adjacent same-pattern Python-path benchmark catch-up widens this family again.

## Pattern Pair
- `rebar.sub(rb"a(b)?c(?(1)(?(1)d|e)|f)", lambda m: m.group(1) + b"x", b"zzabcdzz", -1)`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)(?(word)d|e)|f)").subn(lambda m: m.group("word") + b"x", b"zzacfzz", -1)`

## Deliverables
- `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- Extend `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` with exactly the four adjacent nested conditional callable negative-count `bytes` publication rows that mirror the already-published `str` rows on the shared owner path for `rb"a(b)?c(?(1)(?(1)d|e)|f)"` and `rb"a(?P<word>b)?c(?(word)(?(word)d|e)|f)"`:
  - add the numbered module `sub()` `count=-1` row on `b"zzabcdzz"` using the existing `callable_match_group` helper pinned to group `1`;
  - add the named module `subn()` `count=-1` row on `b"zzacfzz"` using the same helper pinned to group `"word"`;
  - add the numbered compiled-pattern `sub()` `count=-1` row for the same no-substitution workflow; and
  - add the named compiled-pattern `subn()` `count=-1` row for the same zero-replacement tuple workflow.
- Keep the work on the existing conditional callable correctness owner path instead of creating another manifest or detached publication table:
  - update `tests/python/test_callable_replacement_parity_suite.py` only as needed so the shared callable manifest expectations, bytes-mirror assertions, and nested negative-count publication checks stay aligned with the widened `bytes` slice on `conditional-group-exists-callable-replacement-workflows`;
  - update `tests/conformance/test_combined_correctness_scorecards.py` only as needed so the callable negative-count follow-on scorecard expectations include the new nested `bytes` rows without widening the family beyond this exact bounded slice; and
  - preserve the already-published two-arm, alternation-heavy, top-level negative-count, nested present/absent, quantified, and quantified `bytes` callable rows on the same owner path.
- Regenerate `reports/correctness/latest.py` honestly on the tracked combined correctness surface:
  - the tracked report gains the four new nested conditional callable negative-count `bytes` rows for `collection.replacement.conditional_group_exists.callable`;
  - the exact callable manifest moves from `76` passing cases to `80` passing cases with no new explicit failures or unimplemented rows; and
  - the combined correctness summary moves from `1729/1729` passing cases to `1733/1733` passing cases while the manifest count stays at `114`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and nested and negative_count'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'negative_count_follow_on_cases'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/rbr-1203-conditional-nested-negative-count-bytes.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or tracked ops state prose in this run.
- Reuse the existing `conditional_group_exists_callable_replacement_workflows.py` manifest and shared callable parity suite. Do not create another correctness manifest, another callable parity module, or a detached nested callable publication file.
- Keep the scope pinned to the exact four nested conditional callable negative-count `bytes` rows above. Leave the adjacent same-pattern benchmark catch-up and broader callable-helper expansion for later tasks.

## Notes
- `RBR-1203` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this run; and
  - `rg -n "RBR-1203|RBR-1204" ops/tasks ops/state -g '*.md'` matched only historical mentions inside completed task files, not a live reservation for either id.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest done same-family frontier and one narrow adjacent owner-path scan leave this exact `bytes` correctness-publication slice concrete:
  - `ops/tasks/done/RBR-1201-benchmark-conditional-group-exists-nested-callable-negative-count-str-workloads.md` explicitly leaves the adjacent nested negative-count `bytes` correctness-publication mirrors for later on this owner path after landing the `str` benchmark catch-up;
  - `tests/python/test_callable_replacement_parity_suite.py` already exposes the exact nested negative-count direct parity slice on both `str` and `bytes` through `CONDITIONAL_GROUP_EXISTS_NESTED_NEGATIVE_COUNT_CASES`, the shared negative-count callback short-circuit tests, and the bytes-mirror helpers;
  - `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `reports/correctness/latest.py` still stop at the nested negative-count `str` rows and currently leave the matching `bytes` rows unpublished on the tracked correctness surface; and
  - the adjacent benchmark owner path in `benchmarks/workloads/conditional_group_exists_boundary.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` already carries the nested negative-count `str` callable workloads but no `bytes` mirrors for the same pattern pair, which pins the likely post-drain survivor to that exact bounded benchmark catch-up slice rather than a broader same-family synthesis pass.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and nested and negative_count'` returned `17 passed, 5001 deselected`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'negative_count_follow_on_cases'` returned `2 passed, 43 deselected`;
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/feature-planning-conditional-nested-negative-count-bytes-current.py` returned `76 executed / 76 passed`; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` returned `1729 executed / 1729 passed`.

## Completion
- Added the four nested conditional callable negative-count `bytes` publication rows on the existing `conditional-group-exists-callable-replacement-workflows` manifest path, and updated the shared callable parity/scorecard expectations to mirror the widened bounded `bytes` slice without widening the family beyond this task.
- Verification passed:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and nested and negative_count'` returned `17 passed, 5057 deselected`.
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'negative_count_follow_on_cases'` returned `2 passed, 43 deselected`.
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/rbr-1203-conditional-nested-negative-count-bytes.py` returned `80 executed / 80 passed`.
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` returned `1733 executed / 1733 passed`.
- Verified from the tracked `reports/correctness/latest.py` artifact after regeneration:
  - combined correctness is `1733` total / `1733` passed across `114` manifests;
  - `collection.replacement.conditional_group_exists.callable` now publishes `80` total / `80` passed; and
  - the `bytes` and `str` callable sub-summaries each publish `40` total / `40` passed.
