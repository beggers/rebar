# RBR-0475: Publish the grouped-segment leading-capture search pair on the shared grouped-segment correctness surface

Status: done
Owner: feature-implementation
Created: 2026-03-16
Completed: 2026-03-16

## Goal
- Extend the published correctness scorecard with the exact leading-capture grouped-segment search pair already exposed as `module-search-grouped-segment-cold-gap` and `pattern-search-grouped-segment-warm-gap` on `grouped-named-boundary`, while keeping the work on the ordinary `grouped-segment-workflows` correctness path before Rust-backed parity or source-tree benchmark catch-up revisit that captured-prefix slice.

## Deliverables
- `tests/conformance/fixtures/grouped_segment_workflows.py`
- `tests/conformance/correctness_expectations.py`
- `tests/python/test_grouped_capture_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/grouped_segment_workflows.py` grows only by the minimal two numbered `str` workflow cases needed to publish the exact helper pair:
  - `grouped-segment-leading-capture-module-search-str` for `rebar.search("(ab)c", "zabcz")`
  - `grouped-segment-leading-capture-pattern-search-str` for `rebar.compile("(ab)c").search("zabcz")`
- Keep both new cases pinned to the existing grouped-segment correctness surface on `grouped-segment-workflows`. Do not create a new correctness manifest, do not add named variants, and do not broaden into grouped alternation, backreferences, nested groups, or quantified grouped execution in this run.
- `tests/python/test_grouped_capture_parity_suite.py` keeps the published frontier contract honest for the new leading-capture pair without pretending that direct parity already exists:
  - the new case ids are visible through the existing grouped-segment fixture/frontier inventory checks; and
  - until real support lands, they stay out of the direct compile, module-helper, pattern-helper, match-group-access, and supplemental-miss parametrizations that currently require successful `rebar` grouped-segment behavior.
- `tests/conformance/correctness_expectations.py` updates the `grouped-segment-workflows` representative-case set so both new leading-capture case ids stay visible in the combined publication instead of landing as unpublished tail cases.
- `reports/correctness/latest.py` is regenerated honestly. With the current checkout still raising scaffold placeholders for both exact leading-capture helpers, the combined report should move from `963` total cases / `963` passes / `0` unimplemented to `965` total cases / `963` passes / `2` unimplemented while keeping `0` explicit failures and `107` manifests, and the shared `match.grouped_segment` suite should move from `6` total / `6` passed / `0` unimplemented to `8` total / `6` passed / `2` unimplemented.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py tests/conformance/test_correctness_fixture_inventory_contract.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/grouped_segment_workflows.py --report .rebar/tmp/rbr-0475-grouped-segment.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement grouped-segment leading-capture helper behavior, do not touch `benchmarks/workloads/grouped_named_boundary.py`, `tests/benchmarks/`, or `reports/benchmarks/latest.py`, and do not broaden into named grouped-segment, grouped alternation, or backreference support.
- Keep the work anchored to the exact existing benchmark gap pair. This task should make those two helpers visible as honest correctness debt, not rename or replace the benchmark rows that already track them.

## Notes
- `RBR-0473` should land immediately ahead of this task and close the remaining `IGNORECASE|ASCII` literal benchmark gap pair, leaving this grouped-segment publication slice as the concrete surviving follow-on in the ready queue.
- 2026-03-16 planning probe: the tracked benchmark manifest `benchmarks/workloads/grouped_named_boundary.py` already carries the exact gap rows `module-search-grouped-segment-cold-gap` and `pattern-search-grouped-segment-warm-gap`, both pinned to pattern `"(ab)c"`, haystack `"zabcz"`, and flags `0`.
- 2026-03-16 planning probe: in the current checkout, CPython reports that both `re.search("(ab)c", "zabcz")` and `re.compile("(ab)c").search("zabcz")` return a match with span `(1, 4)`, `group(0) == "abc"`, and `group(1) == "ab"`, while `rebar.search("(ab)c", "zabcz")` and `rebar.compile("(ab)c").search("zabcz")` both raise `NotImplementedError: rebar.compile() is a scaffold placeholder; the \`re\`-compatible API is not implemented yet`.
- The immediate follow-on after this publication should stay on the same exact leading-capture pair: first Rust-backed parity for the published `(ab)c` search helpers, then source-tree benchmark catch-up against the already-existing grouped-segment gap rows.

## Completion
- 2026-03-16: Added the exact two numbered `str` leading-capture grouped-segment search cases to `tests/conformance/fixtures/grouped_segment_workflows.py` without introducing named variants, a new manifest, or broader grouped execution shapes.
- 2026-03-16: Updated `tests/conformance/correctness_expectations.py` so both new grouped-segment leading-capture case ids are part of the representative correctness publication surface.
- 2026-03-16: Reworked `tests/python/test_grouped_capture_parity_suite.py` so the grouped-segment bundle publishes the new case ids through the existing fixture/frontier inventory checks while keeping them out of the direct compile, module-helper, pattern-helper, match-group-access, and supplemental-miss parametrizations that still require successful `rebar` grouped-segment behavior.
- 2026-03-16: Republished the tracked combined correctness scorecard at `reports/correctness/latest.py`; the tracked diff includes that file, and the regenerated artifact now reports `965` total cases, `963` passes, `0` explicit failures, `2` unimplemented cases, and `107` manifests overall, while `match.grouped_segment` reports `8` total, `6` passed, `0` failed, and `2` unimplemented.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py` passed (`369 passed, 1055 subtests passed`).
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/grouped_segment_workflows.py --report .rebar/tmp/rbr-0475-grouped-segment.py` passed and reported `8` total cases, `6` passes, `0` failures, and `2` unimplemented.
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` republished the tracked scorecard and reported `965` total cases, `963` passes, `0` failures, and `2` unimplemented.
- The acceptance note still referenced `tests/conformance/test_correctness_fixture_inventory_contract.py`, which no longer exists in this checkout, so the current equivalent inventory gates were run instead: `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py::test_published_full_suite_fixture_selector_matches_tracked_fixture_inventory tests/python/test_fixture_parity_support_contract.py::test_default_fixture_inventory_has_unique_manifest_suite_and_case_ids tests/python/test_fixture_parity_support_contract.py::test_manifest_case_helpers_cover_bundle_manifest_order_and_unselected_rows` (`3 passed`).
