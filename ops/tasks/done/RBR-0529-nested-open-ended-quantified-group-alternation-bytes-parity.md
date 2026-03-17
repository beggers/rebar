# RBR-0529: Convert the nested open-ended grouped-alternation bytes pair to real parity

Status: done
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Convert the exact nested open-ended `{1,}` grouped-alternation bytes pair published by `RBR-0528` from honest `unimplemented` outcomes into Rust-backed behavior on the existing open-ended correctness/parity path, without widening into benchmark catch-up or another bytes frontier.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_open_ended_quantified_group_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `rebar.compile(rb"a((bc|de){1,})d")` and `rebar.compile(rb"a(?P<outer>(bc|de){1,})d")` no longer raise the scaffold placeholder; compile metadata and visible outer-capture details match CPython through the public `rebar` API.
- The existing `NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES` anchor in `tests/python/test_open_ended_quantified_group_parity_suite.py` becomes real parity coverage instead of a `rebar`-only unsupported follow-on:
  - numbered `module.search()` matches CPython for the lower-bound hits `b"zzabcdzz"` and `b"zzadedzz"`;
  - numbered compiled `Pattern.fullmatch()` matches CPython for the bounded success cases `b"abcbcded"` and `b"adededed"` plus the bounded misses `b"ae"` and `b"abcbcdede"`;
  - named `module.search()` matches CPython for the lower-bound hits `b"zzabcdzz"` and `b"zzadedzz"`;
  - named compiled `Pattern.fullmatch()` matches CPython for the bounded success cases `b"abcbcded"` and `b"adededed"` plus the bounded misses `b"ae"` and `b"abcbcdede"`.
- `tests/python/test_open_ended_quantified_group_parity_suite.py` keeps `NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES` as the direct bytes anchor but drops the current `rebar` unsupported gating for these two patterns; do not fork a second bytes-only suite or fixture path.
- Any new parsing or execution semantics live behind `rebar._rebar`; Python changes stay limited to public-surface marshalling, cache/object plumbing, and native result handling.
- `reports/correctness/latest.py` is regenerated honestly. The combined report should move from `1067` total / `1053` passed / `14` unimplemented across `111` manifests to `1067` / `1067` / `0`, and `match.nested_open_ended_quantified_group_alternation` should move from `28` total / `14` passed / `14` unimplemented to `28` / `28` / `0`.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_open_ended_quantified_group_alternation_workflows.py --report .rebar/tmp/rbr-0529-nested-open-ended-grouped-alternation-bytes-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the implementation bounded to the published bytes pair. Do not broaden into benchmark rows, grouped-conditionals, grouped backtracking-heavy follow-ons, or another bytes family.
- Reuse the existing correctness fixture and parity suite. Do not create another bytes-only correctness manifest, another parity suite, or another benchmark family in this run.
- Keep this slice Rust-backed, not Python-only.

## Notes
- Build on `RBR-0528`.
- 2026-03-17 feature-planning probes confirm this task is not stale:
  - `reports/correctness/latest.py` currently publishes `match.nested_open_ended_quantified_group_alternation` at `28` total / `14` passed / `14` unimplemented with `['bytes', 'str']` coverage;
  - `tests/python/test_open_ended_quantified_group_parity_suite.py` still marks `NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES` as unsupported for `rebar`; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`.
- The surviving follow-on after this task is `RBR-0530`, which should add the six bytes mirrors of the current nested open-ended grouped-alternation source-tree benchmark rows on `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py` before deeper bytes slices reopen that family.

## Completion Notes
- Landed exact Rust-backed bytes compile/search/fullmatch support for `rb"a((bc|de){1,})d"` and `rb"a(?P<outer>(bc|de){1,})d"` in `crates/rebar-core/src/lib.rs`; the existing native compile/match boundary and Python shim surfaced that support without slice-specific bridge changes.
- Re-enabled the published manifest-backed bytes cases in `tests/python/test_open_ended_quantified_group_parity_suite.py` by removing the queued follow-on placeholder handling and letting the bytes fixture cases run through the normal generic compile/module/pattern coverage.
- Republished `reports/correctness/latest.py`; the tracked combined scorecard now reads `1067` total / `1067` passed / `0` failed / `0` unimplemented, and `match.nested_open_ended_quantified_group_alternation` now reads `28` total / `28` passed / `0` unimplemented across `['bytes', 'str']`.
- Verified with `cargo test -p rebar-core nested_open_ended_quantified_group_alternation`, `cargo build -p rebar-cpython`, `PYTHONPATH=python ./.venv/bin/python -m pytest tests/python/test_open_ended_quantified_group_parity_suite.py`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_open_ended_quantified_group_alternation_workflows.py --report .rebar/runtime/rbr-0529-nested-open-ended-correctness.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.
