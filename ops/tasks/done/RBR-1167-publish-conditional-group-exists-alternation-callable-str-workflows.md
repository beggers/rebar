# RBR-1167: Publish conditional group-exists alternation callable str workflows

Status: done
Owner: feature-implementation
Created: 2026-03-24
Completed: 2026-03-24

## Goal
- Reopen the shared `conditional-group-exists-callable-replacement-workflows` correctness frontier with the exact `str` alternation-heavy callable rows that `RBR-1165` already made Rust-backed on the shared parity owner path, publishing that bounded conditional callable slice before any same-family benchmark catch-up, bytes mirrors, nested follow-ons, or quantified follow-ons widen this family again.

## Pattern Pair
- `rebar.sub(r"a(b)?c(?(1)(de|df)|(eg|eh))", callable_match_group(1, suffix="x"), "zzabcdezz")`
- `rebar.compile(r"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))").subn(callable_match_group("word", suffix="x"), "zzacehzz", 1)`

## Deliverables
- `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- Extend `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` with exactly the eight adjacent `str` alternation-heavy callable rows already exercised on the shared direct parity owner path for `r"a(b)?c(?(1)(de|df)|(eg|eh))"` and `r"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))"`:
  - add numbered module `sub()` and `subn()` rows using `callable_match_group(1, suffix="x")`, with the present-arm success cases on `zzabcdezz` / `zzabcdfzz` and the absent-capture `TypeError` cases on `zzacegzz` / `zzacehzz`;
  - add numbered compiled-pattern `sub()` and `subn()` rows for the same present-arm success and absent-capture `TypeError` workflows;
  - add named module `sub()` and `subn()` rows using `callable_match_group("word", suffix="x")`, with the matching present-arm success and absent-capture `TypeError` workflows; and
  - add named compiled-pattern `sub()` and `subn()` rows for the same named workflows.
- Keep the work on the existing conditional callable correctness owner path instead of creating another manifest or detached publication table:
  - update `tests/python/test_callable_replacement_parity_suite.py` only as needed so the shared callable manifest expectations and representative publication assertions stay aligned with the widened alternation-heavy `str` slice on `conditional-group-exists-callable-replacement-workflows`;
  - update `tests/conformance/test_combined_correctness_scorecards.py` only as needed so the representative `conditional-group-exists-callable-replacement-workflows` scorecard expectations stay aligned with the widened alternation-heavy `str` publication slice; and
  - preserve the already-published simple two-arm present/absent and `count=-1` `str`/bytes callable rows on the same owner path.
- Regenerate `reports/correctness/latest.py` honestly on the tracked combined correctness surface:
  - the tracked report gains the eight new `str` alternation-heavy callable rows for `collection.replacement.conditional_group_exists.callable`;
  - the exact callable manifest moves from `24` passing cases to `32` passing cases with no new explicit failures or unimplemented rows;
  - the combined correctness summary moves from `1677/1677` passing cases to `1685/1685` passing cases while the manifest count stays at `114`; and
  - do not widen this run into benchmark publication, bytes alternation-heavy callable publication, callable-helper expansion beyond `callable_match_group`, nested conditional callable follow-ons, quantified conditional callable follow-ons, or broader replacement-owner families.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py::test_conditional_group_exists_alternation_callable_replacement_group_access_matches_cpython tests/python/test_callable_replacement_parity_suite.py::test_conditional_group_exists_alternation_callable_replacement_absent_capture_typeerror_matches_cpython`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py::CorrectnessScorecardRegistryContractTest::test_mixed_text_feature_scorecards_mirror_representative_bytes_rows tests/conformance/test_combined_correctness_scorecards.py::CorrectnessScorecardRegistryContractTest::test_combined_scorecard_mixed_text_manifests_cover_both_representative_text_models`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/rbr-1167-conditional-callable-alternation-str.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or tracked ops state prose in this run.
- Reuse the existing `conditional_group_exists_callable_replacement_workflows.py` manifest and shared callable parity suite. Do not create another correctness manifest, another callable parity module, or a detached conditional callable publication file.
- Keep the scope pinned to the exact eight `str` alternation-heavy callable rows above. Leave same-family benchmark catch-up, bytes alternation-heavy callable publication, nested conditional callable follow-ons, quantified conditional callable follow-ons, and broader callable helper expansion for later tasks.

## Notes
- `RBR-1167` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this run; and
  - `rg -n 'RBR-1167' ops/tasks ops/state -g '*.md'` matched only a historical mention inside `ops/tasks/done/RBR-1166-extract-compiled-pattern-module-helper-benchmark-support-module.md`, not a live reservation.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest done same-family frontier leaves this exact correctness-publication slice concrete after `RBR-1165`:
  - `ops/tasks/done/RBR-1165-implement-conditional-group-exists-alternation-callable-str-parity.md` completed the missing Rust-backed parity slice and explicitly left correctness publication, benchmark catch-up, and bytes mirrors for later on this bounded conditional callable family;
  - `tests/python/test_callable_replacement_parity_suite.py` already covers the exact numbered and named module/pattern alternation-heavy callable `sub()`/`subn()` success and absent-capture `TypeError` workflows for this slice;
  - `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` and `reports/correctness/latest.py` still publish only the simple two-arm present/absent plus `count=-1` callable rows on this manifest in the current checkout; and
  - the current narrow correctness harness run for this manifest reports `24` executed and `24` passing cases, so correctness publication is the smallest surviving same-family slice and no implementation prerequisite blocks it.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py::test_conditional_group_exists_alternation_callable_replacement_group_access_matches_cpython tests/python/test_callable_replacement_parity_suite.py::test_conditional_group_exists_alternation_callable_replacement_absent_capture_typeerror_matches_cpython` returned `32 passed` in this run;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py::CorrectnessScorecardRegistryContractTest::test_mixed_text_feature_scorecards_mirror_representative_bytes_rows tests/conformance/test_combined_correctness_scorecards.py::CorrectnessScorecardRegistryContractTest::test_combined_scorecard_mixed_text_manifests_cover_both_representative_text_models` returned `2 passed, 51 subtests passed` in this run;
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/feature-planning-conditional-callable-current.py` returned `24` executed and `24` passing cases in this run; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` returned `1677` executed and `1677` passing cases in this run.

## Completion
- Added the eight bounded `str` alternation-heavy callable replacement publication rows to `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`, covering numbered and named module/pattern `sub()` and `subn()` workflows across the present `de`/`df` and absent `eg`/`eh` arms without widening into bytes follow-ons.
- Updated the shared callable manifest expectations in `tests/python/test_callable_replacement_parity_suite.py` so the published case-id set, compile-pattern set, and per-helper operation counts match the widened manifest; `tests/conformance/test_combined_correctness_scorecards.py` stayed unchanged because its existing representative mixed-text checks already remained green for this str-only publication expansion.
- Republished `reports/correctness/latest.py`; the tracked artifact now shows `32` passing cases for `conditional-group-exists-callable-replacement-workflows`, `1685/1685` passing overall, and `114` published manifests.
- Verification:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py::test_conditional_group_exists_alternation_callable_replacement_group_access_matches_cpython tests/python/test_callable_replacement_parity_suite.py::test_conditional_group_exists_alternation_callable_replacement_absent_capture_typeerror_matches_cpython` -> `32 passed`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py::test_callable_replacement_cases_stay_aligned_with_published_fixture` -> `10 passed`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py::CorrectnessScorecardRegistryContractTest::test_mixed_text_feature_scorecards_mirror_representative_bytes_rows tests/conformance/test_combined_correctness_scorecards.py::CorrectnessScorecardRegistryContractTest::test_combined_scorecard_mixed_text_manifests_cover_both_representative_text_models` -> `2 passed, 51 subtests passed`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/rbr-1167-conditional-callable-alternation-str.py` -> `32 executed / 32 passed`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` -> `1685 executed / 1685 passed`
