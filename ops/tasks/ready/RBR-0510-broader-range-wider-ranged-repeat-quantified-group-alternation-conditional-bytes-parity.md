# RBR-0510: Convert the broader-range wider-ranged-repeat grouped-conditional bytes pair to real parity

Status: ready
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Convert the exact broader `{1,4}` grouped-alternation-plus-conditional bytes pair published by `RBR-0509` from honest `unimplemented` outcomes into Rust-backed behavior on the existing wider-ranged-repeat parity surface, without widening into new bytes frontiers or benchmark catch-up.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `rebar.compile(rb"a((bc|de){1,4})?(?(1)d|e)")` and `rebar.compile(rb"a(?P<outer>(bc|de){1,4})?(?(outer)d|e)")` no longer raise the scaffold placeholder; compile metadata and named-group details match CPython through the public `rebar` API.
- The existing `BROADER_RANGE_CONDITIONAL_BYTES_CASES` anchor in `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` becomes real parity coverage instead of a `rebar`-only unsupported follow-on:
  - module `search()` matches CPython for the absent else-arm case on `b"zzaezz"`, the present-group lower-bound hits on `b"zzabcdzz"` and `b"zzadedzz"`, and the named upper-bound mixed hit on `b"zzabcdedededzz"`;
  - compiled `Pattern.fullmatch()` matches CPython for the bounded success cases on `b"ae"`, `b"abcded"`, `b"abcbcded"`, and `b"abcdededed"`;
  - the same bounded slice still rejects `b"zzadzz"`, `b"zzabcbcbcbcbcdzz"`, `b"ad"`, `b"abcdede"`, and `b"abcbcbcbcbcd"` where the current supplemental cases say it should.
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` keeps `BROADER_RANGE_CONDITIONAL_BYTES_CASES` as the direct bytes anchor but drops the current `rebar` unsupported gating for these two patterns; do not fork a second bytes-only suite or fixture path.
- Any new parsing or execution semantics live behind `rebar._rebar`; Python changes stay limited to public-surface marshalling, cache/object plumbing, and native result handling.
- `reports/correctness/latest.py` is regenerated honestly. The combined report should move from `997` total / `983` passed / `14` unimplemented across `111` manifests to `997` / `997` / `0`, and `match.broader_range_wider_ranged_repeat_quantified_group_alternation_conditional` should move from `28` total / `14` passed / `14` unimplemented to `28` / `28` / `0`.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py --report .rebar/tmp/rbr-0510-broader-range-conditional-bytes-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the implementation bounded to the published bytes pair. Do not broaden into broader bytes grouped backtracking traces, nested grouped bytes slices, benchmark rows, open-ended repeats, or stdlib delegation.
- Reuse the existing parity suite and correctness fixture. Do not create another bytes-only correctness manifest, another parity suite, or another benchmark family in this run.
- Keep this slice Rust-backed, not Python-only.

## Notes
- Build on `RBR-0509`.
- 2026-03-17 feature-planning probe: `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... rebar.compile(pattern) ... PY` still raises `NotImplementedError: rebar.compile() is a scaffold placeholder; the \`re\`-compatible API is not implemented yet` for both published bytes patterns, so this task is not stale.
- The surviving follow-on after this task is `RBR-0512`, which should add the six bytes mirrors of the current broader-range grouped-conditional source-tree benchmark rows on `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py` before broader bytes follow-ons reopen that family.
