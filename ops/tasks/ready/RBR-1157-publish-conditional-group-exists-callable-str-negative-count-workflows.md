# RBR-1157: Publish conditional group-exists callable str negative-count workflows

Status: ready
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Reopen the shared `conditional-group-exists-callable-replacement-workflows` correctness frontier with the exact `str count=-1` callable-replacement rows that the live runtime and direct parity owner path already cover, publishing that bounded conditional callable outcome before any same-family benchmark catch-up or bytes negative-count follow-on widens this family again.

## Pattern Pair
- `rebar.sub(r"a(b)?c(?(1)d|e)", callable_match_group(1, suffix="x"), "abcdaceabcd", -1)`
- `rebar.compile(r"a(?P<word>b)?c(?(word)d|e)").subn(callable_match_group("word", suffix="x"), "abcdaceabcd", -1)`

## Deliverables
- `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- Extend `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` with exactly the four adjacent `str count=-1` callable rows already exercised on the shared direct parity owner path:
  - add the numbered module `sub()` row for `r"a(b)?c(?(1)d|e)"` with a `callable_match_group` replacement targeting group `1`, suffix `"x"`, haystack `"abcdaceabcd"`, and `count == -1`;
  - add the named module `subn()` row for `r"a(?P<word>b)?c(?(word)d|e)"` with a `callable_match_group` replacement targeting group `"word"`, suffix `"x"`, haystack `"abcdaceabcd"`, and `count == -1`;
  - add the numbered compiled-pattern `sub()` row for `r"a(b)?c(?(1)d|e)"` with the same `callable_match_group` descriptor, haystack, and `count == -1`; and
  - add the named compiled-pattern `subn()` row for `r"a(?P<word>b)?c(?(word)d|e)"` with the same `callable_match_group` descriptor, haystack, and `count == -1`.
- Keep the work on the existing conditional callable correctness owner path instead of creating another manifest or detached publication table:
  - update `tests/python/test_callable_replacement_parity_suite.py` only as needed so the shared callable manifest expectations and representative mixed-text publication assertions include these four new conditional `str` negative-count rows on `conditional-group-exists-callable-replacement-workflows`;
  - update `tests/conformance/test_combined_correctness_scorecards.py` only as needed so the representative `conditional-group-exists-callable-replacement-workflows` scorecard expectations stay aligned with the widened `str` publication slice; and
  - preserve the already-published present and absent-exception `str` and bytes rows plus the surrounding callable replacement families on the same owner path.
- Regenerate `reports/correctness/latest.py` honestly on the tracked combined correctness surface:
  - the tracked report gains the four new `str count=-1` rows for `collection.replacement.conditional_group_exists.callable`;
  - the exact callable manifest moves from `16` to `20` passing cases with no new explicit failures or unimplemented rows;
  - the combined correctness summary moves from `1669/1669` passing cases to `1673/1673` passing cases while the manifest count stays at `114`; and
  - do not widen this run into benchmark publication, bytes negative-count publication, callable-helper expansion beyond `callable_match_group`, template replacement work, alternation-heavy conditionals, nested conditionals, quantified conditionals, or broader replacement-owner families.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py::test_module_callable_replacement_negative_count_short_circuits_without_callback tests/python/test_callable_replacement_parity_suite.py::test_pattern_callable_replacement_negative_count_short_circuits_without_callback`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py::CorrectnessScorecardRegistryContractTest::test_mixed_text_feature_scorecards_mirror_representative_bytes_rows tests/conformance/test_combined_correctness_scorecards.py::CorrectnessScorecardRegistryContractTest::test_combined_scorecard_mixed_text_manifests_cover_both_representative_text_models`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/rbr-1157-conditional-callable-negative-count-str.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or tracked ops state prose in this run.
- Reuse the existing `conditional_group_exists_callable_replacement_workflows.py` manifest and shared callable parity suite. Do not create another correctness manifest, another callable parity module, or a detached conditional callable publication file.
- Keep the scope pinned to the exact four `str count=-1` rows above. Leave same-family benchmark catch-up, bytes negative-count publication, first-match-only or absent-exception follow-ons, and broader conditional callable expansion for later tasks.

## Notes
- `RBR-1157` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this run; and
  - `rg -n 'RBR-1157' ops/tasks ops/state -g '*.md'` matched only historical mentions inside completed task files, not a live reservation.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest done same-family frontier leaves this exact callable publication slice concrete after `RBR-1155`:
  - `ops/tasks/done/RBR-1155-benchmark-conditional-group-exists-template-str-negative-count-workloads.md` closed the adjacent template `str count=-1` benchmark catch-up and explicitly left callable follow-ons for later on this same conditional replacement family;
  - `tests/python/test_callable_replacement_parity_suite.py` already proves the live runtime short-circuits `count=-1` without invoking the callback across the shared module and compiled-pattern callable owner path, including the conditional group-exists cases on this manifest;
  - `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` and the live suite entry in `reports/correctness/latest.py` still publish only `16` present/absent callable rows for `collection.replacement.conditional_group_exists.callable`; and
  - the current narrow correctness harness run for this manifest reports `16` executed and passing cases, so correctness publication is the smallest surviving same-family slice and no implementation prerequisite blocks it.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py::test_module_callable_replacement_negative_count_short_circuits_without_callback tests/python/test_callable_replacement_parity_suite.py::test_pattern_callable_replacement_negative_count_short_circuits_without_callback` returned `432 passed` in this run;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py::CorrectnessScorecardRegistryContractTest::test_mixed_text_feature_scorecards_mirror_representative_bytes_rows tests/conformance/test_combined_correctness_scorecards.py::CorrectnessScorecardRegistryContractTest::test_combined_scorecard_mixed_text_manifests_cover_both_representative_text_models` returned `2 passed, 51 subtests passed` in this run; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/feature-planning-conditional-callable-current.py` returned `16` executed and passing cases in this run.
