# RBR-0514: Convert the broader-range wider-ranged-repeat grouped backtracking-heavy bytes pair to real parity

Status: done
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Convert the exact broader `{1,4}` grouped-alternation-backtracking-heavy bytes pair published by `RBR-0513` from honest `unimplemented` outcomes into Rust-backed behavior on the existing wider-ranged-repeat parity surface, without widening into new bytes frontiers or benchmark catch-up.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `rebar.compile(rb"a((bc|b)c){1,4}d")` and `rebar.compile(rb"a(?P<word>(bc|b)c){1,4}d")` no longer raise the scaffold placeholder; compile metadata and named-group details match CPython through the public `rebar` API.
- The existing `BROADER_RANGE_BACKTRACKING_HEAVY_BYTES_CASES` anchor in `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` becomes real parity coverage instead of a `rebar`-only unsupported follow-on:
  - module `search()` matches CPython for the numbered lower-bound hits on `b"zzabcdzz"` and `b"zzabccdzz"`, the named second-repetition short-then-long hit on `b"zzabcbccdzz"`, and the named fourth-repetition mixed hit on `b"zzabcbccbccbcdzz"`;
  - compiled `Pattern.fullmatch()` matches CPython for the bounded success cases on `b"abcbccd"`, `b"abccbcd"`, and `b"abcbccbccbcd"`;
  - the same bounded slice still rejects `b"zzabccbdzz"`, `b"zzabcbcbcbcbcdzz"`, `b"abccbd"`, and `b"abcbcbcbcbcd"` where the current supplemental cases say it should.
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` keeps `BROADER_RANGE_BACKTRACKING_HEAVY_BYTES_CASES` as the direct bytes anchor but drops the current `rebar` unsupported gating for these two patterns; do not fork a second bytes-only suite or fixture path.
- Any new parsing or execution semantics live behind `rebar._rebar`; Python changes stay limited to public-surface marshalling, cache/object plumbing, and native result handling.
- `reports/correctness/latest.py` is regenerated honestly. The combined report should move from `1011` total / `997` passed / `14` unimplemented across `111` manifests to `1011` / `1011` / `0`, and `match.broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy` should move from `28` total / `14` passed / `14` unimplemented to `28` / `28` / `0`.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py --report .rebar/tmp/rbr-0514-broader-range-backtracking-heavy-bytes-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the implementation bounded to the published bytes pair. Do not broaden into broader bytes grouped-conditionals already closed, nested broader grouped bytes slices, benchmark rows, open-ended repeats, or stdlib delegation.
- Reuse the existing parity suite and correctness fixture. Do not create another bytes-only correctness manifest, another parity suite, or another benchmark family in this run.
- Keep this slice Rust-backed, not Python-only.

## Notes
- Build on `RBR-0513`.
- 2026-03-17 feature-planning probes confirm this task is not stale:
  - `reports/correctness/latest.py` currently publishes `match.broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy` at `28` total / `14` passed / `14` unimplemented;
  - `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` still marks `BROADER_RANGE_BACKTRACKING_HEAVY_BYTES_CASES` as unsupported for `rebar`, with the reason text pinned to `RBR-0514`; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`.
- The surviving follow-on after this task is `RBR-0515`, which should add only the six bytes mirrors of the current broader-range grouped backtracking-heavy source-tree benchmark rows on `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py` before nested broader bytes follow-ons reopen that family.
- 2026-03-17 feature-implementation completed this bounded bytes-parity slice by adding exact Rust-core compile/match support for `rb"a((bc|b)c){1,4}d"` and `rb"a(?P<word>(bc|b)c){1,4}d"`, removing the old `rebar` skip gating from `BROADER_RANGE_BACKTRACKING_HEAVY_BYTES_CASES`, and republishing `reports/correctness/latest.py` to `1011` total / `1011` passed / `0` unimplemented overall with `match.broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy` at `28` total / `28` passed / `0` unimplemented. The existing `rebar._rebar` boundary and `python/rebar/__init__.py` marshalling paths already carried the new core behavior, so no Python-side runtime expansion was needed.
- Verification:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py --report .rebar/tmp/rbr-0514-broader-range-backtracking-heavy-bytes-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
