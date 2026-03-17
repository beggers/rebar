# RBR-0525: Convert the nested broader-range wider-ranged-repeat grouped-conditional bytes pair to real parity

Status: done
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Convert the exact nested broader `{1,4}` grouped-conditional bytes pair published by `RBR-0524` from honest `unimplemented` outcomes into Rust-backed behavior on the existing wider-ranged-repeat parity surface, without widening into benchmark catch-up or another bytes frontier.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `rebar.compile(rb"a(((bc|de){1,4})d)?(?(1)e|f)")` and `rebar.compile(rb"a(?P<outer>((bc|de){1,4})d)?(?(outer)e|f)")` no longer raise the scaffold placeholder; compile metadata and visible outer-capture details match CPython through the public `rebar` API.
- The existing `NESTED_BROADER_RANGE_CONDITIONAL_BYTES_CASES` anchor in `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` becomes real parity coverage instead of a `rebar`-only unsupported follow-on:
  - numbered `module.search()` matches CPython for the absent `b"zzafzz"` branch and the present-group lower-bound hits `b"zzabcdezz"` and `b"zzadedezz"`;
  - numbered compiled `Pattern.fullmatch()` matches CPython for the bounded success case `b"abcbcdede"` and the bounded misses `b"abcbcded"` and `b"ae"`;
  - named `module.search()` matches CPython for the absent `b"zzafzz"` branch, the lower-bound `de` hit `b"zzadedezz"`, and the upper-bound all-`de` hit `b"zzadededededezz"`;
  - named compiled `Pattern.fullmatch()` matches CPython for the bounded success case `b"abcbcdede"` and the bounded misses `b"ae"` and `b"abcbcbcbcbcde"`.
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` keeps `NESTED_BROADER_RANGE_CONDITIONAL_BYTES_CASES` as the direct bytes anchor but drops the current `rebar` unsupported gating for these two patterns; do not fork a second bytes-only suite or fixture path.
- Any new parsing or execution semantics live behind `rebar._rebar`; Python changes stay limited to public-surface marshalling, cache/object plumbing, and native result handling.
- `reports/correctness/latest.py` is regenerated honestly. The combined report should move from `1053` total / `1039` passed / `14` unimplemented across `111` manifests to `1053` / `1053` / `0`, and `match.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional` should move from `28` total / `14` passed / `14` unimplemented to `28` / `28` / `0`.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py --report .rebar/tmp/rbr-0525-nested-broader-range-grouped-conditional-bytes-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the implementation bounded to the published bytes pair. Do not broaden into benchmark rows, nested broader grouped backtracking-heavy follow-ons, open-ended repeats, or stdlib delegation.
- Reuse the existing parity suite and correctness fixture. Do not create another bytes-only correctness manifest, another parity suite, or another benchmark family in this run.
- Keep this slice Rust-backed, not Python-only.

## Notes
- Build on `RBR-0524`.
- 2026-03-17 feature-planning probes confirm this task is not stale:
  - `reports/correctness/latest.py` currently publishes `match.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional` at `28` total / `14` passed / `14` unimplemented, with the bytes subset still at `14` total / `0` passed / `14` unimplemented;
  - `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` still marks `NESTED_BROADER_RANGE_CONDITIONAL_BYTES_CASES` as unsupported for `rebar`; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`.
- 2026-03-17 completion:
  - Landed the bounded bytes parser and match path in `crates/rebar-core/src/lib.rs` for `rb"a(((bc|de){1,4})d)?(?(1)e|f)"` and `rb"a(?P<outer>((bc|de){1,4})d)?(?(outer)e|f)"`, including compile metadata, search/fullmatch execution, capture spans, and `lastindex` parity through the existing native boundary.
  - Dropped the temporary `rebar` unsupported gating from `NESTED_BROADER_RANGE_CONDITIONAL_BYTES_CASES` in `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`; no `crates/rebar-cpython/src/lib.rs` or `python/rebar/__init__.py` change was needed because the generic native compile/match paths already forward bytes patterns through `core_compile()` and `core_literal_match()`.
  - Verified with `cargo build -p rebar-cpython`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py --report .rebar/tmp/rbr-0525-nested-broader-range-grouped-conditional-bytes-parity.py` (`28` total / `28` passed / `0` unimplemented), and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.
  - Republished `reports/correctness/latest.py`; the tracked report now reads `1053` total / `1053` passed / `0` unimplemented overall, and `match.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional` now reads `28` total / `28` passed / `0` unimplemented.
- The surviving follow-on after this task is `RBR-0527`, which should add the six bytes mirrors of the current nested broader grouped-conditional source-tree benchmark rows on `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py` before nested broader grouped backtracking-heavy or deeper bytes slices reopen that family.
