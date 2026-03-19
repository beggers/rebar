# RBR-0694: Convert the nested broader-range open-ended backtracking-heavy callable-replacement pair to real parity

Status: done
Owner: feature-implementation
Created: 2026-03-19

## Goal
- Convert the exact broader-range open-ended `{2,}` nested grouped backtracking-heavy callable-replacement `str` pair published by `RBR-0692` from honest `unimplemented` outcomes into Rust-backed behavior on the existing shared callable parity surface, without widening into benchmark catch-up, replacement-template flows, bytes mirrors, broader callback helpers, or another grouped frontier.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The exact `str` callable-replacement workflows published by `RBR-0692` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` `sub()` / `subn()` flows using:
  - `a(((bc|b)c){2,})d` through `callable_match_group` on groups `1` or `3`;
  - `a(?P<outer>(?:(?P<inner>bc|b)c){2,})d` through `callable_match_group` on groups `"outer"` or `"inner"`.
- The shared callable parity surface in `tests/python/test_callable_replacement_parity_suite.py` becomes real parity coverage instead of a pending `rebar`-only slice for these exact eight published case ids:
  - `module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-str`
  - `module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-str`
  - `pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-mixed-branches-str`
  - `pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-fourth-repetition-b-branch-first-match-only-str`
  - `module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-mixed-branches-str`
  - `module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-first-match-only-long-branch-str`
  - `pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-fourth-repetition-short-only-str`
  - `pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-str`
- `tests/python/test_callable_replacement_parity_suite.py` keeps this slice on the existing shared callable suite but drops the current `pending_rebar_case_ids` for `nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-callable-replacement-workflows` once the live `rebar` result stops being `unimplemented`; do not fork another parity suite, manifest-local shim, or bytes-only owner path.
- Any new parsing, repeated-span collection, callable-replacement dispatch, or match-object marshalling semantics live behind `rebar._rebar`; Python changes stay limited to public-surface marshalling, cache/object plumbing, callable argument handling, and native result marshalling.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1374` total / `1366` passed / `8` `unimplemented` across `114` manifests to `1374` / `1374` / `0`;
  - `collection.replacement.nested_broader_range_open_ended_quantified_group_alternation_backtracking_heavy.callable` moves from `8` total / `0` passed / `8` `unimplemented` to `8` / `8` / `0`;
  - the same suite remains `str`-only in the published report.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_backtracking_heavy_callable_replacement_workflows.py --report .rebar/tmp/rbr-0694-nested-broader-range-open-ended-backtracking-heavy-callable-replacement-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the implementation bounded to the `str` pair published by `RBR-0692`. Do not broaden into benchmark rows, replacement-template flows, bytes mirrors, broader callback helpers, deeper grouped execution, another grouped family, or stdlib delegation.
- Reuse the existing shared callable parity suite and the published correctness fixture. Do not create another correctness manifest, another parity suite, or another benchmark family in this run.
- Keep this slice Rust-backed, not Python-only.

## Notes
- `RBR-0694` is the next available feature task id in the current checkout; `RBR-0693` is already occupied by the done architecture cleanup task in `ops/tasks/done/`.
- Queue this directly behind the drained `RBR-0692` head so the nested broader-range open-ended backtracking-heavy callable slice reaches Rust-backed parity before later Python-path benchmark catch-up or bytes mirrors reopen that family.
- 2026-03-19 feature-planning probes confirm this follow-on is concrete from the tracked frontier:
  - `tests/python/test_callable_replacement_parity_suite.py` currently keeps all eight `str` case ids for `nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-callable-replacement-workflows` in `pending_rebar_case_ids`, so the shared callable suite already exposes the exact parity target without another synthesis pass;
  - `reports/correctness/latest.py` currently reports `1374` total / `1366` passed / `8` `unimplemented` across `114` manifests, and `collection.replacement.nested_broader_range_open_ended_quantified_group_alternation_backtracking_heavy.callable` at `8` total / `0` passed / `8` `unimplemented`;
  - direct report probes in this planning run confirmed those eight honest gaps are the only remaining `unimplemented` cases in the current published correctness slice; and
  - `benchmarks/workloads/nested_group_callable_replacement_boundary.py` remains the adjacent Python-path benchmark home for this family, so a later benchmark catch-up can stay on that existing manifest path instead of inventing another benchmark surface.

## Completion
- 2026-03-19: Added a Rust-backed compile and callable span path for `a(((bc|b)c){2,})d` and `a(?P<outer>(?:(?P<inner>bc|b)c){2,})d`, exposed it through the CPython boundary, and wired the shared Python callable dispatcher to use it for module and compiled-`Pattern` `sub()` / `subn()` parity.
- Removed the eight case ids for `nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-callable-replacement-workflows` from `pending_rebar_case_ids` and updated the shared callable-suite manifest bookkeeping so those rows now run as ordinary parity coverage.
- Republished `reports/correctness/latest.py`; the tracked combined report is now `1374` total / `1374` passed / `0` `unimplemented`, and `collection.replacement.nested_broader_range_open_ended_quantified_group_alternation_backtracking_heavy.callable` is `8` total / `8` passed / `0` `unimplemented`.
- Verified with `cargo build -p rebar-cpython`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_backtracking_heavy_callable_replacement_workflows.py --report .rebar/tmp/rbr-0694-nested-broader-range-open-ended-backtracking-heavy-callable-replacement-parity.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.
