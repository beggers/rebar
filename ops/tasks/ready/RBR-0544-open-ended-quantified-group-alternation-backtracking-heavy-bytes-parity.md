# RBR-0544: Convert the open-ended grouped backtracking-heavy bytes pair to real parity

Status: ready
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Convert the exact open-ended `{1,}` grouped backtracking-heavy bytes pair published by `RBR-0543` from honest `unimplemented` outcomes into Rust-backed behavior on the existing open-ended parity surface, without widening into benchmark catch-up or another bytes frontier.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_open_ended_quantified_group_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `rebar.compile(rb"a((bc|b)c){1,}d")` and `rebar.compile(rb"a(?P<word>(bc|b)c){1,}d")` no longer raise the scaffold placeholder; compile metadata and visible `word` capture details match CPython through the public `rebar` API.
- The existing `OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES` anchor in `tests/python/test_open_ended_quantified_group_parity_suite.py` becomes real parity coverage instead of a `rebar`-only unsupported follow-on:
  - numbered `module.search()` matches CPython for the lower-bound short-branch hit `b"zzabcdzz"`;
  - numbered compiled `Pattern.fullmatch()` matches CPython for the bounded success cases `b"abccd"`, `b"abcbcd"`, and `b"abcbccd"` plus the bounded miss `b"abcccd"`;
  - named `module.search()` matches CPython for the lower-bound long-branch hit `b"zzabccdzz"`, the second-repetition long-then-short hit `b"zzabccbcdzz"`, the third-repetition mixed hit `b"zzabcbccbcdzz"`, and the invalid-tail miss `b"zzabccbdzz"`;
  - named compiled `Pattern.fullmatch()` matches CPython for the bounded success case `b"abcbcbcbcd"`.
- `tests/python/test_open_ended_quantified_group_parity_suite.py` keeps `OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES` as the direct bytes anchor but drops the current `rebar` unsupported gating for these two patterns; do not fork a second bytes-only suite or fixture path.
- Any new parsing or execution semantics live behind `rebar._rebar`; Python changes stay limited to public-surface marshalling, cache/object plumbing, and native result handling.
- `reports/correctness/latest.py` is regenerated honestly. The combined report should move from `1120` total / `1108` passed / `12` `unimplemented` across `111` manifests to `1120` / `1120` / `0`, and `match.open_ended_quantified_group_alternation_backtracking_heavy` should move from `24` total / `12` passed / `12` `unimplemented` to `24` / `24` / `0`.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/open_ended_quantified_group_alternation_backtracking_heavy_workflows.py --report .rebar/tmp/rbr-0544-open-ended-grouped-backtracking-heavy-bytes-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the implementation bounded to the published bytes pair. Do not broaden into benchmark rows, deeper grouped follow-ons, or another bytes family.
- Reuse the existing parity suite and correctness fixture. Do not create another bytes-only correctness manifest, another parity suite, or another benchmark family in this run.
- Keep this slice Rust-backed, not Python-only.

## Notes
- Build on `RBR-0543`.
- 2026-03-17 feature-planning probes confirm this task is not stale:
  - `reports/correctness/latest.py` currently publishes `match.open_ended_quantified_group_alternation_backtracking_heavy` at `24` total / `12` passed / `12` `unimplemented` with `['bytes', 'str']` coverage;
  - `tests/python/test_open_ended_quantified_group_parity_suite.py` still marks `OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES` as unsupported for `rebar`;
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`; and
  - `benchmarks/workloads/open_ended_quantified_group_boundary.py` already publishes the six adjacent measured `str` backtracking-heavy rows for this exact `{1,}` slice, so the surviving benchmark follow-on should reuse that existing Python-path manifest instead of inventing another benchmark family.
- The surviving follow-on after this task is `RBR-0546`, which should add the six adjacent bytes benchmark mirrors for the same open-ended grouped backtracking-heavy pair on `benchmarks/workloads/open_ended_quantified_group_boundary.py`.
