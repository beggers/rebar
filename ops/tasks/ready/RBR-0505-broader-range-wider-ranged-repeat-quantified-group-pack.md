# RBR-0505: Publish a broader-range wider-ranged-repeat quantified-group correctness pack

Status: ready
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Extend the published correctness scorecard with one bounded broader `{1,4}` wider-ranged-repeat quantified-group manifest so the counted-repeat frontier reopens immediately after `RBR-0503` closed the optional-group conditional benchmark catch-up slice.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/broader_range_wider_ranged_repeat_quantified_group_workflows.py`
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated broader-range wider-ranged-repeat quantified-group manifest instead of replacing any existing fixture pack.
- `tests/conformance/fixtures/broader_range_wider_ranged_repeat_quantified_group_workflows.py` publishes only the minimal six `str` cases needed to make the exact broader counted-repeat pair visible on the correctness surface:
  - a numbered compile-metadata case for `a(bc){1,4}d`;
  - a numbered module `search()` upper-bound success for `a(bc){1,4}d` on `"zzabcbcbcbcdzz"`, aligned with the existing benchmark gap anchors;
  - a numbered compiled-`Pattern` `fullmatch()` lower-bound success for `a(bc){1,4}d` on `"abcd"`;
  - a named compile-metadata case for `a(?P<word>bc){1,4}d`;
  - a named module `search()` upper-bound success for `a(?P<word>bc){1,4}d` on `"zzabcbcbcbcdzz"`;
  - a named compiled-`Pattern` `fullmatch()` lower-bound success for `a(?P<word>bc){1,4}d` on `"abcd"`.
- Keep all six cases pinned to one new `broader-range-wider-ranged-repeat-quantified-group-workflows` correctness manifest. Do not broaden into grouped alternation, grouped conditionals, benchmark updates, bytes coverage, open-ended repeats, or unrelated harness cleanup in this run.
- `python/rebar_harness/correctness.py`, `tests/conformance/correctness_expectations.py`, and `tests/conformance/test_combined_correctness_scorecards.py` register the new manifest on the published combined scorecard path, and `tests/python/test_fixture_parity_support_contract.py` refreshes the explicit published-fixture inventory so the new manifest is tracked by both `PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR` and `WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_FIXTURE_SELECTOR`.
- `reports/correctness/latest.py` is regenerated honestly. With the current checkout still lacking this exact pair, the combined report should move from `977` total cases / `977` passed / `0` unimplemented across `110` manifests to `983` / `977` / `6` across `111` manifests, and the new `match.broader_range_wider_ranged_repeat_quantified_group` suite should publish `6` total / `0` passed / `6` unimplemented.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_correctness_scorecard_registry_contract.py tests/conformance/test_python_fixture_manifest_contract.py tests/conformance/test_combined_correctness_scorecards.py tests/python/test_fixture_parity_support_contract.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/broader_range_wider_ranged_repeat_quantified_group_workflows.py --report .rebar/tmp/rbr-0505-broader-range-wider-ranged-repeat.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task focused on correctness publication, selector inventory, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not touch `benchmarks/workloads/exact_repeat_quantified_group_boundary.py`, `benchmarks/workloads/ranged_repeat_quantified_group_boundary.py`, `tests/benchmarks/`, `reports/benchmarks/latest.py`, or Rust/native implementation files in this run.
- Keep later parity and benchmark catch-up anchored to the existing workload ids `module-search-numbered-broader-ranged-repeat-group-cold-gap` and `module-search-numbered-ranged-repeat-group-wider-range-cold-gap`; do not fork another benchmark family for this same bounded slice.

## Notes
- Build on `RBR-0503`.
- Keep the parity follow-on on the existing wider-ranged-repeat Python-path parity surface in `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` instead of creating a one-off suite unless that file cannot express the exact pair cleanly.
- 2026-03-17 feature-planning probe: direct public-API checks in the current checkout still raise `NotImplementedError` for both target patterns at `rebar.compile(...)`, so this task is not stale.
