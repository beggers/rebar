# RBR-0522: Convert the nested broader-range wider-ranged-repeat grouped-alternation bytes pair to real parity

Status: done
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Convert the exact nested broader `{1,4}` grouped-alternation bytes pair published by `RBR-0520` from honest `unimplemented` outcomes into Rust-backed behavior on the existing wider-ranged-repeat parity surface, without widening into new bytes frontiers or benchmark catch-up.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `rebar.compile(rb"a((bc|de){1,4})d")` and `rebar.compile(rb"a(?P<outer>(bc|de){1,4})d")` no longer raise the scaffold placeholder; compile metadata and visible outer-capture details match CPython through the public `rebar` API.
- The existing `NESTED_BROADER_RANGE_ALTERNATION_BYTES_CASES` anchor in `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` becomes real parity coverage instead of a `rebar`-only unsupported follow-on:
  - module `search()` matches CPython for the lower-bound hits on `b"zzabcdzz"` and `b"zzadedzz"`;
  - compiled `Pattern.fullmatch()` matches CPython for the bounded success cases on `b"abcbcded"` and `b"adedededed"`;
  - the same bounded slice still rejects `b"ae"`, `b"abcbcdede"`, and `b"abcbcbcbcbcd"` where the current supplemental cases say it should.
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` keeps `NESTED_BROADER_RANGE_ALTERNATION_BYTES_CASES` as the direct bytes anchor but drops the current `rebar` unsupported gating for these two patterns; do not fork a second bytes-only suite or fixture path.
- Any new parsing or execution semantics live behind `rebar._rebar`; Python changes stay limited to public-surface marshalling, cache/object plumbing, and native result handling.
- `reports/correctness/latest.py` is regenerated honestly. The combined report should move from `1039` total / `1025` passed / `14` unimplemented across `111` manifests to `1039` / `1039` / `0`, and `match.nested_broader_range_wider_ranged_repeat_quantified_group_alternation` should move from `28` total / `14` passed / `14` unimplemented to `28` / `28` / `0`.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_workflows.py --report .rebar/tmp/rbr-0522-nested-broader-range-grouped-alternation-bytes-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the implementation bounded to the published bytes pair. Do not broaden into nested broader grouped-conditional bytes follow-ons, benchmark rows, open-ended repeats, or stdlib delegation.
- Reuse the existing parity suite and correctness fixture. Do not create another bytes-only correctness manifest, another parity suite, or another benchmark family in this run.
- Keep this slice Rust-backed, not Python-only.

## Notes
- Build on `RBR-0520`.
- 2026-03-17 feature-planning probes confirm this task is not stale:
  - `reports/correctness/latest.py` currently publishes `match.nested_broader_range_wider_ranged_repeat_quantified_group_alternation` at `28` total / `14` passed / `14` unimplemented, with the bytes subset still at `14` total / `0` passed / `14` unimplemented;
  - `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` still marks `NESTED_BROADER_RANGE_ALTERNATION_BYTES_CASES` as unsupported for `rebar`, with the reason text pinned to `RBR-0522`.
- The surviving follow-on after this task is `RBR-0523`, which should add the six bytes mirrors of the current nested broader grouped-alternation source-tree benchmark rows on `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py` before nested broader grouped-conditionals reopen correctness work.
- 2026-03-17 completion: added bounded Rust-backed bytes compile/match support for `rb"a((bc|de){1,4})d"` and `rb"a(?P<outer>(bc|de){1,4})d"` in `rebar-core`, removed the parity-suite `rebar` unsupported gating for `NESTED_BROADER_RANGE_ALTERNATION_BYTES_CASES`, and republished `reports/correctness/latest.py`.
- Verification:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_workflows.py --report .rebar/tmp/rbr-0522-nested-broader-range-grouped-alternation-bytes-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
- Published scorecard check from the tracked artifact:
  - combined totals now read `1039` total / `1039` passed / `0` unimplemented;
  - `match.nested_broader_range_wider_ranged_repeat_quantified_group_alternation` now reads `28` total / `28` passed / `0` unimplemented, with the bytes subset at `14` / `14` / `0`.
