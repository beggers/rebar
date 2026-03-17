# RBR-0537: Convert the broader-range open-ended grouped-alternation-plus-conditional bytes pair to real parity

Status: ready
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Convert the exact broader-range open-ended `{2,}` grouped-alternation-plus-conditional bytes pair published by `RBR-0535` from honest `unimplemented` outcomes into Rust-backed behavior on the existing open-ended parity surface, without widening into benchmark catch-up or another bytes frontier.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_open_ended_quantified_group_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `rebar.compile(rb"a((bc|de){2,})?(?(1)d|e)")` and `rebar.compile(rb"a(?P<outer>(bc|de){2,})?(?(outer)d|e)")` no longer raise the scaffold placeholder; compile metadata and visible outer-capture details match CPython through the public `rebar` API.
- The existing `BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES` anchor in `tests/python/test_open_ended_quantified_group_parity_suite.py` becomes real parity coverage instead of a `rebar`-only unsupported follow-on:
  - numbered `module.search()` matches CPython for the absent `b"zzaezz"` branch and the present-group lower-bound hits `b"zzabcbcdzz"` and `b"zzadededzz"`;
  - numbered compiled `Pattern.fullmatch()` matches CPython for the bounded success cases `b"abcded"` and `b"abcbcded"` plus the bounded misses `b"abcdede"` and `b"abcd"`;
  - named `module.search()` matches CPython for the absent `b"zzaezz"` branch, the lower-bound `de` hit `b"zzadededzz"`, and the fourth-repetition `de` hit `b"zzadedededzz"`;
  - named compiled `Pattern.fullmatch()` matches CPython for the bounded success case `b"abcbcded"` and the bounded miss `b"ad"`.
- `tests/python/test_open_ended_quantified_group_parity_suite.py` keeps `BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES` as the direct bytes anchor but drops the current `rebar` unsupported gating for these two patterns; do not fork a second bytes-only suite or fixture path.
- Any new parsing or execution semantics live behind `rebar._rebar`; Python changes stay limited to public-surface marshalling, cache/object plumbing, and native result handling.
- `reports/correctness/latest.py` is regenerated honestly. The combined report should move from `1094` total / `1080` passed / `14` unimplemented across `111` manifests to `1094` / `1094` / `0`, and `match.broader_range_open_ended_quantified_group_alternation_conditional` should move from `28` total / `14` passed / `14` unimplemented to `28` / `28` / `0`.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/broader_range_open_ended_quantified_group_alternation_conditional_workflows.py --report .rebar/tmp/rbr-0537-broader-range-open-ended-grouped-conditional-bytes-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the implementation bounded to the published bytes pair. Do not broaden into benchmark rows, broader-range open-ended grouped backtracking-heavy bytes work, or another bytes family.
- Reuse the existing parity suite and correctness fixture. Do not create another bytes-only correctness manifest, another parity suite, or another benchmark family in this run.
- Keep this slice Rust-backed, not Python-only.

## Notes
- Build on `RBR-0535`.
- 2026-03-17 feature-planning probes confirm this task is not stale:
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`;
  - `tests/python/test_open_ended_quantified_group_parity_suite.py` still marks `BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES` as unsupported for `rebar`; and
  - `reports/correctness/latest.py` currently publishes `match.broader_range_open_ended_quantified_group_alternation_conditional` at `28` total / `14` passed / `14` unimplemented while the combined report stays at `1094` total / `1080` passed / `14` unimplemented.
- The surviving follow-on after this task is `RBR-0538`, which should add the six adjacent bytes benchmark mirrors for the same broader-range open-ended grouped-conditional pair on `benchmarks/workloads/open_ended_quantified_group_boundary.py`.
