# RBR-0475: Publish the grouped-segment leading-capture search pair on the shared grouped-segment correctness surface

Status: ready
Owner: feature-implementation
Created: 2026-03-16

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
