# RBR-0500: Publish the exact optional-group conditional pair on the correctness surface

Status: done
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Extend the published correctness scorecard with the exact optional-group conditional pair already exposed as the last optional-group source-tree benchmark gap on `optional_group_boundary.py`, keeping the work on an ordinary Python fixture path before Rust-backed parity and benchmark catch-up revisit that same benchmark anchor.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/optional_group_conditional_workflows.py`
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/optional_group_conditional_workflows.py` publishes only the minimal six `str` cases needed to make the exact optional-group conditional pair visible on the correctness surface:
  - a numbered compile-metadata case for `a(b)?(?(1)c|d)e`;
  - a numbered module `search()` present-capture case for `a(b)?(?(1)c|d)e` on `"zzabcezz"`;
  - a numbered compiled-`Pattern` `fullmatch()` absent-capture case for `a(b)?(?(1)c|d)e` on `"ade"`;
  - a named compile-metadata case for `a(?P<word>b)?(?(word)c|d)e`;
  - a named module `search()` present-capture case for `a(?P<word>b)?(?(word)c|d)e` on `"zzabcezz"`;
  - a named compiled-`Pattern` `fullmatch()` absent-capture case for `a(?P<word>b)?(?(word)c|d)e` on `"ade"`.
- Keep all six cases pinned to one new `optional-group-conditional-workflows` correctness manifest. Do not broaden into the already-landed `conditional-group-exists` `a(b)?c(?(1)d|e)` slice, empty-arm conditionals, alternation-heavy conditional arms, counted-repeat `{1,4}` follow-ons, or benchmark updates in this run.
- `python/rebar_harness/correctness.py`, `tests/conformance/correctness_expectations.py`, and `tests/conformance/test_combined_correctness_scorecards.py` register the new manifest on the published combined scorecard path so the remaining `optional-group-boundary` benchmark gap stops living only on the benchmark surface.
- `reports/correctness/latest.py` is regenerated honestly. With the current checkout still lacking this exact optional-group conditional pair, the combined report should move from `971` total cases / `971` passed / `0` unimplemented across `109` manifests to `977` / `971` / `6` across `110` manifests, and the new `match.optional_group_conditional` suite should publish `6` total / `0` passed / `6` unimplemented.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_correctness_scorecard_registry_contract.py tests/conformance/test_python_fixture_manifest_contract.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/optional_group_conditional_workflows.py --report .rebar/tmp/rbr-0500-optional-group-conditional.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not touch `benchmarks/workloads/optional_group_boundary.py`, `tests/benchmarks/`, `reports/benchmarks/latest.py`, or any Rust/native implementation files in this run.
- Keep the work anchored to the existing benchmark gap row `module-search-numbered-optional-group-conditional-cold-gap`. This task should make the matching numbered/named pair visible as tracked correctness debt, not rename or replace the benchmark row that already anchors the slice.

## Notes
- `benchmarks/workloads/optional_group_boundary.py` already carries the exact numbered benchmark anchor `a(b)?(?(1)c|d)e` on `"zzabcezz"` as `module-search-numbered-optional-group-conditional-cold-gap`; later benchmark catch-up should stay on that existing Python-path manifest instead of adding another benchmark family.
- The adjacent published conditional group-exists correctness and parity surfaces already cover `a(b)?c(?(1)d|e)` and `a(?P<word>b)?c(?(word)d|e)`, so this follow-on should reopen the frontier through one exact optional-group-before-conditional composition instead of jumping to broader counted repeats.
- 2026-03-16 feature-planning probe: `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/optional_group_boundary.py --report .rebar/tmp/feature-planning-optional-group.py` currently reports `7` total workloads / `6` measured workloads / `1` known gap, and the exact target row still publishes `status == "unimplemented"` with the scaffold-placeholder compile reason in the source-tree shim.

## Completion Note
- 2026-03-16 feature-implementation: Added `tests/conformance/fixtures/optional_group_conditional_workflows.py` with the bounded numbered and named compile/search/fullmatch cases for `a(b)?(?(1)c|d)e` and `a(?P<word>b)?(?(word)c|d)e`, registered the new manifest on the published combined correctness path, and refreshed the published full-suite selector contract snapshot.
- Verified `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_correctness_scorecard_registry_contract.py tests/conformance/test_python_fixture_manifest_contract.py tests/conformance/test_combined_correctness_scorecards.py tests/python/test_fixture_parity_support_contract.py::test_published_full_suite_fixture_selector_matches_tracked_fixture_inventory tests/python/test_fixture_parity_support_contract.py::test_published_full_suite_fixture_selector_preserves_count_and_order_digest tests/python/test_fixture_parity_support_contract.py::test_default_fixture_inventory_has_unique_manifest_suite_and_case_ids tests/python/test_fixture_parity_support_contract.py::test_manifest_case_helpers_cover_bundle_manifest_order_and_unselected_rows` (`17 passed, 1225 subtests passed in 25.83s`).
- Verified `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/optional_group_conditional_workflows.py --report .rebar/tmp/rbr-0500-optional-group-conditional.py` produced `6` total / `0` passed / `6` unimplemented, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` republished the tracked report to `977` total / `971` passed / `6` unimplemented across `110` manifests. The new `match.optional_group_conditional` suite now publishes `6` total / `0` passed / `6` unimplemented on `optional-group-conditional-workflows`.
