# RBR-0468: Publish the IGNORECASE|ASCII literal helper pair on the shared literal-flag correctness surface

Status: ready
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Extend the published correctness scorecard with the exact `IGNORECASE|ASCII` literal helper pair already exposed as `module-search-ignorecase-ascii-cold-gap` and `pattern-search-ignorecase-ascii-warm-gap` on `literal-flag-boundary`, while keeping the work on the ordinary `literal-flag-workflows` correctness path before Rust-backed parity or source-tree benchmark catch-up revisit that flag-combination slice.

## Deliverables
- `tests/conformance/fixtures/literal_flag_workflows.py`
- `tests/conformance/correctness_expectations.py`
- `tests/python/test_literal_flag_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/literal_flag_workflows.py` grows only by the minimal two `str`-valued workflow cases needed to publish the exact helper pair:
  - `flag-module-search-ignorecase-ascii-str-hit` for `rebar.search("abc", "ABC", rebar.IGNORECASE | rebar.ASCII)`
  - `flag-pattern-search-ignorecase-ascii-str-hit` for `rebar.compile("abc", rebar.IGNORECASE | rebar.ASCII).search("ABC")`
- Keep both new cases pinned to the existing literal-only `search` helper path on the shared `literal-flag-workflows` manifest. Do not create a new correctness manifest, do not add bytes variants, and do not broaden into inline-flag or non-literal flag-combination work in this run.
- `tests/python/test_literal_flag_parity_suite.py` keeps the published frontier contract honest for the new ASCII pair without pretending that direct parity already exists:
  - the new case ids are visible through the existing fixture/frontier inventory checks; and
  - until real support lands, they stay out of the direct parity parametrizations that currently require successful `rebar` helper behavior for the bounded `IGNORECASE` slice.
- `tests/conformance/correctness_expectations.py` updates the `literal-flag-workflows` representative-case set so both new ASCII case ids stay visible in the combined publication instead of landing as unpublished tail cases.
- `reports/correctness/latest.py` is regenerated honestly. With the current checkout still raising the scaffold placeholders on both exact `IGNORECASE|ASCII` helpers, the combined report should move from `961` total cases / `961` passes / `0` unimplemented to `963` total cases / `961` passes / `2` unimplemented while keeping `0` explicit failures and `107` manifests, and the shared `literal.flag.workflow` suite should move from `11` total / `11` passed / `0` unimplemented to `13` total / `11` passed / `2` unimplemented.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_literal_flag_parity_suite.py tests/conformance/test_correctness_fixture_inventory_contract.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/literal_flag_workflows.py --report .rebar/tmp/rbr-0468-literal-flags.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement `IGNORECASE|ASCII` helper behavior, do not touch `benchmarks/workloads/literal_flag_boundary.py`, `tests/benchmarks/`, or `reports/benchmarks/latest.py`, and do not broaden into general flag-combination support.
- Keep the work anchored to the exact existing benchmark gap pair. This task should make those two helpers visible as honest correctness debt, not rename or replace the benchmark rows that already track them.

## Notes
- 2026-03-16 planning probe: the tracked benchmark manifest `benchmarks/workloads/literal_flag_boundary.py` already carries the exact gap rows `module-search-ignorecase-ascii-cold-gap` and `pattern-search-ignorecase-ascii-warm-gap`, both pinned to pattern `"abc"`, haystack `"ABC"`, and flags `258` (`IGNORECASE | ASCII`).
- 2026-03-16 planning probe: in the current checkout, `re.search("abc", "ABC", re.IGNORECASE | re.ASCII)` and `re.compile("abc", re.IGNORECASE | re.ASCII).search("ABC")` both return a match with span `(0, 3)`, while `rebar.search("abc", "ABC", rebar.IGNORECASE | rebar.ASCII)` raises `NotImplementedError: rebar.search() is a scaffold placeholder; the \`re\`-compatible API is not implemented yet` and `rebar.compile("abc", rebar.IGNORECASE | rebar.ASCII).search("ABC")` raises `NotImplementedError: rebar.Pattern.search() is a scaffold placeholder; compiled pattern semantics are not implemented yet`.
- 2026-03-16 planning probe: the tracked `reports/correctness/latest.py` artifact currently reports `961` total cases with `961` passes and `0` unimplemented outcomes, and the existing `literal.flag.workflow` suite reports `11` total cases with `11` passes, so this task should make the two existing `IGNORECASE|ASCII` helper gaps visible as honest correctness debt instead of leaving them unpublished.
- The immediate follow-on after this publication should stay on the same exact helper pair: first Rust-backed parity for the published `IGNORECASE|ASCII` cases, then source-tree benchmark catch-up against the already-existing gap rows.
