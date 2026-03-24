# RBR-1161: Publish conditional group-exists callable bytes negative-count workflows

Status: ready
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Reopen the shared `conditional-group-exists-callable-replacement-workflows` correctness frontier with the exact bytes `count=-1` callable-replacement rows that the live runtime already matches against CPython on the shared parity owner path, publishing that bounded conditional callable outcome before any same-family benchmark catch-up or broader callable follow-on widens this family again.

## Pattern Pair
- `rebar.sub(rb"a(b)?c(?(1)d|e)", callable_match_group(1, suffix=b"x"), b"abcdaceabcd", -1)`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)d|e)").subn(callable_match_group("word", suffix=b"x"), b"abcdaceabcd", -1)`

## Deliverables
- `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- Extend `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` with exactly the four adjacent bytes `count=-1` callable rows already exercised on the shared parity owner path:
  - add the numbered module `sub()` bytes row for `rb"a(b)?c(?(1)d|e)"` with a `callable_match_group` replacement targeting group `1`, suffix `b"x"`, haystack `b"abcdaceabcd"`, and `count == -1`;
  - add the named module `subn()` bytes row for `rb"a(?P<word>b)?c(?(word)d|e)"` with a `callable_match_group` replacement targeting group `"word"`, suffix `b"x"`, haystack `b"abcdaceabcd"`, and `count == -1`;
  - add the numbered compiled-pattern `sub()` bytes row for `rb"a(b)?c(?(1)d|e)"` with the same `callable_match_group` descriptor, haystack, and `count == -1`; and
  - add the named compiled-pattern `subn()` bytes row for `rb"a(?P<word>b)?c(?(word)d|e)"` with the same `callable_match_group` descriptor, haystack, and `count == -1`.
- Keep the work on the existing conditional callable correctness owner path instead of creating another manifest or detached publication table:
  - update `tests/python/test_callable_replacement_parity_suite.py` only as needed so the shared conditional callable manifest spec and mixed-text frontier assertions expect the four new bytes negative-count rows on `conditional-group-exists-callable-replacement-workflows`;
  - update `tests/conformance/test_combined_correctness_scorecards.py` only as needed so the representative `conditional-group-exists-callable-replacement-workflows` cases stay aligned with the widened bytes publication slice; and
  - preserve the already-published present/absent `str` and bytes rows plus the adjacent `str` negative-count rows on the same owner path.
- Regenerate `reports/correctness/latest.py` honestly on the tracked combined correctness surface:
  - the tracked report gains the four new bytes negative-count rows for `collection.replacement.conditional_group_exists.callable`;
  - the exact callable manifest moves from `20` passing cases to `24` passing cases with no new explicit failures or unimplemented rows;
  - the combined correctness summary moves from `1673/1673` passing cases to `1677/1677` passing cases while the manifest count stays at `114`; and
  - do not widen this run into benchmark publication, first-match-only or absent-exception follow-ons, callable helper expansion beyond `callable_match_group`, template replacement work, alternation-heavy conditionals, nested conditionals, quantified conditionals, or broader replacement-owner families.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py::test_module_bytes_callable_replacement_negative_count_short_circuits_without_callback tests/python/test_callable_replacement_parity_suite.py::test_pattern_bytes_callable_replacement_negative_count_short_circuits_without_callback`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py::CorrectnessScorecardRegistryContractTest::test_mixed_text_feature_scorecards_mirror_representative_bytes_rows tests/conformance/test_combined_correctness_scorecards.py::CorrectnessScorecardRegistryContractTest::test_combined_scorecard_mixed_text_manifests_cover_both_representative_text_models`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/rbr-1161-conditional-callable-negative-count-bytes.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or tracked ops state prose in this run.
- Reuse the existing `conditional_group_exists_callable_replacement_workflows.py` manifest and shared callable parity suite. Do not create another correctness manifest, another callable parity module, or a detached conditional callable publication file.
- Keep the scope pinned to the exact four bytes `count=-1` rows above. Leave any same-family benchmark catch-up, first-match-only or absent-exception follow-ons, callable-helper expansion, and broader conditional callable work for later tasks.

## Notes
- `RBR-1161` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this run; and
  - `rg -n 'RBR-1161' ops/tasks ops/state -g '*.md'` matched only historical mentions inside completed task files, not a live reservation.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after `RBR-1159` because the newest done same-family frontier leaves broader callable follow-ons deferred, and the narrow owner-path scan shows this exact bytes negative-count publication slice is the smallest still-missing accepted surface on the shared conditional callable route.
- 2026-03-24 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py::test_module_bytes_callable_replacement_negative_count_short_circuits_without_callback tests/python/test_callable_replacement_parity_suite.py::test_pattern_bytes_callable_replacement_negative_count_short_circuits_without_callback` returned `192 passed` in this run, confirming the bytes negative-count callable parity route already matches CPython on the shared owner path;
  - `rg -n 'module-sub-callable-conditional-group-exists-negative-count-bytes|module-subn-callable-named-conditional-group-exists-negative-count-bytes|pattern-sub-callable-conditional-group-exists-negative-count-bytes|pattern-subn-callable-named-conditional-group-exists-negative-count-bytes' tests/conformance/fixtures tests/conformance/test_combined_correctness_scorecards.py reports/correctness/latest.py tests/python/test_callable_replacement_parity_suite.py` returned no matches in this run, confirming the tracked correctness publication still omits this exact bytes slice;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py::CorrectnessScorecardRegistryContractTest::test_mixed_text_feature_scorecards_mirror_representative_bytes_rows tests/conformance/test_combined_correctness_scorecards.py::CorrectnessScorecardRegistryContractTest::test_combined_scorecard_mixed_text_manifests_cover_both_representative_text_models` returned `2 passed, 51 subtests passed` in this run; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/feature-planning-conditional-callable-current.py` returned `20` executed and `20` passing cases in this run, while `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report .rebar/tmp/feature-planning-full-correctness.py` returned `1673` executed and `1673` passing cases across the tracked combined surface.
