# RBR-0497: Publish the already-supported nested grouped-alternation wrapper-template pair on the correctness surface

Status: done
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Extend the published correctness scorecard with the exact nested grouped-alternation wrapper-template pair already anchored on `grouped-alternation-boundary`, keeping the work on an ordinary Python fixture path now that the current checkout already matches CPython for that pair through the public `rebar` API.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/nested_group_alternation_wrapper_replacement_workflows.py`
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/nested_group_alternation_wrapper_replacement_workflows.py` publishes only the minimal two `str` wrapper-template workflow cases needed to make the exact benchmark-anchored pair visible on the correctness surface:
  - a numbered module-helper case for `rebar.sub("a((b|c))d", "<\\1>", "abdacd")`, which both CPython and the current checkout report as `"<b><c>"`;
  - a named compiled-pattern case for `rebar.compile("a(?P<outer>(b|c))d").subn("<\\g<outer>>", "abdacd", 1)`, which both CPython and the current checkout report as `("<b>acd", 1)`.
- Keep both new cases pinned to one new `nested-group-alternation-wrapper-replacement-workflows` correctness manifest. Do not broaden into the already-landed `\\1x` / `\\g<outer>x` slice, inner-capture template references like `"<\\2>"` or `"<\\g<inner>>"`, callable replacements, quantified nested alternation, branch-local backreferences, or benchmark updates in this run.
- `python/rebar_harness/correctness.py`, `tests/conformance/correctness_expectations.py`, and `tests/conformance/test_combined_correctness_scorecards.py` register the new manifest on the published combined scorecard path so the exact wrapper-template pair stops living only on the benchmark gap path.
- `reports/correctness/latest.py` is regenerated honestly. With the current checkout already supporting this exact wrapper-template slice, the combined report should move from `969` total cases / `969` passed / `0` unimplemented across `108` manifests to `971` / `971` / `0` across `109` manifests, and the new `collection.replacement.nested_group_alternation.wrapper` suite should publish `2` total / `2` passed / `0` unimplemented.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_correctness_fixture_inventory_contract.py tests/conformance/test_python_fixture_manifest_contract.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_group_alternation_wrapper_replacement_workflows.py --report .rebar/tmp/rbr-0497-nested-group-alternation-wrapper-replacement.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not touch `tests/python/test_grouped_literal_replacement_template.py`, `benchmarks/workloads/grouped_alternation_boundary.py`, `benchmarks/workloads/grouped_alternation_replacement_boundary.py`, `tests/benchmarks/`, or `reports/benchmarks/latest.py`, and do not broaden into later shared parity-suite absorption or benchmark republish for this pair.
- Keep the work anchored to the exact existing benchmark pair. This task should make those two helpers visible as tracked correctness coverage, not rename or replace the benchmark rows that already track them.

## Notes
- `RBR-0495` was retired as stale after direct public-API probes showed the exact pair already matches CPython in the current checkout; this replacement keeps the same bounded slice but corrects the expected scorecard outcome from `unimplemented` debt to passing published cases.
- 2026-03-16 feature-planning probe: the tracked benchmark manifest `benchmarks/workloads/grouped_alternation_boundary.py` already carries the exact workload ids `module-sub-template-nested-grouped-alternation-warm-gap` and `pattern-subn-template-named-nested-grouped-alternation-purged-gap`, pinned to patterns `"a((b|c))d"` and `"a(?P<outer>(b|c))d"` with haystack `"abdacd"` plus replacement templates `"<\\1>"` and `"<\\g<outer>>"`.
- 2026-03-16 feature-planning probe: direct public-API checks in the current checkout already report `rebar.sub("a((b|c))d", "<\\1>", "abdacd") == "<b><c>"` and `rebar.compile("a(?P<outer>(b|c))d").subn("<\\g<outer>>", "abdacd", 1) == ("<b>acd", 1)`, matching CPython exactly for this pair.
- 2026-03-16 feature-planning probe: the blocked `RBR-0493` note already observed the same pair timing as measured on a narrow `grouped_alternation_boundary.py` rerun, so correctness publication should catch the tracked scorecard up before any later benchmark republish retunes combined expectations.

## Completion Note
- 2026-03-16 feature-implementation: Added `tests/conformance/fixtures/nested_group_alternation_wrapper_replacement_workflows.py` with the bounded numbered module `sub()` and named compiled-pattern `subn()` wrapper-template cases for `a((b|c))d` and `a(?P<outer>(b|c))d`, registered the new manifest on the published combined correctness path, and regenerated `reports/correctness/latest.py`.
- The acceptance note still referenced `tests/conformance/test_correctness_fixture_inventory_contract.py`, which no longer exists in this checkout, so the current equivalent inventory gates were run instead: `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_correctness_scorecard_registry_contract.py tests/conformance/test_python_fixture_manifest_contract.py tests/conformance/test_combined_correctness_scorecards.py` (`13 passed, 1217 subtests passed in 25.35s`) plus `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py::test_published_full_suite_fixture_selector_matches_tracked_fixture_inventory tests/python/test_fixture_parity_support_contract.py::test_default_fixture_inventory_has_unique_manifest_suite_and_case_ids tests/python/test_fixture_parity_support_contract.py::test_manifest_case_helpers_cover_bundle_manifest_order_and_unselected_rows` (`3 passed in 0.05s`).
- Verified `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_group_alternation_wrapper_replacement_workflows.py --report .rebar/tmp/rbr-0497-nested-group-alternation-wrapper-replacement.py` produced `2` total / `2` passed / `0` unimplemented, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` republished the tracked report to `971` total / `971` passed / `0` unimplemented across `109` manifests. The new `collection.replacement.nested_group_alternation.wrapper` suite now publishes `2` total / `2` passed / `0` unimplemented on `nested-group-alternation-wrapper-replacement-workflows`.
