# RBR-0682: Convert the nested broader-range wider-ranged-repeat backtracking-heavy callable-replacement slice to real parity

Status: done
Owner: feature-implementation
Created: 2026-03-19

## Goal
- Convert the exact broader `{1,4}` nested grouped backtracking-heavy callable-replacement workflows published by `RBR-0680` from honest `unimplemented` outcomes into Rust-backed behavior on the existing shared callable parity surface, without widening into benchmark catch-up, bytes coverage, replacement-template flows, broader callback helpers, or another grouped frontier.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The exact eight callable-replacement workflows published by `RBR-0680` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` `sub()` / `subn()` flows using:
  - `a(((bc|b)c){1,4})d` through `callable_match_group` on groups `1` or `3`;
  - `a(?P<outer>(?:(?P<inner>bc|b)c){1,4})d` through `callable_match_group` on groups `"outer"` or `"inner"`.
- The shared `tests/python/test_callable_replacement_parity_suite.py` surface becomes real parity coverage for this manifest instead of a pending `rebar`-only slice:
  - numbered `module.sub(..., callable_match_group(group=1, suffix="x"), "abcd")`, numbered `module.subn(..., callable_match_group(group=3, prefix="<", suffix=">"), "abccdabcbccd", 1)`, numbered compiled `Pattern.sub(..., "zzabccbcdzz")`, and numbered compiled `Pattern.subn(..., "zzabcbccbccbcdabccdzz", 1)` match CPython;
  - named `module.sub(..., callable_match_group(group="outer", suffix="x"), "abccbcd")`, named `module.subn(..., callable_match_group(group="inner", prefix="<", suffix=">"), "abccdabcbccd", 1)`, named compiled `Pattern.sub(..., "zzabcbccbccbcdzz")`, and named compiled `Pattern.subn(..., "zzabccbcdabccdzz", 1)` match CPython.
- `tests/python/test_callable_replacement_parity_suite.py` keeps those eight rows on the existing shared callable suite but drops the current `pending_rebar_case_ids` for `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-callable-replacement-workflows` once the live `rebar` result stops being `unimplemented`; do not fork another parity suite, fixture path, or manifest-local shim.
- Any new parsing, repeated-span collection, callable-replacement dispatch, or match-object marshalling semantics live behind `rebar._rebar`; Python changes stay limited to public-surface marshalling, cache/object plumbing, callable argument handling, and native result marshalling.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1358` total / `1350` passed / `8` `unimplemented` across `113` manifests to `1358` / `1358` / `0`; and
  - `collection.replacement.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy.callable` moves from `8` total / `0` passed / `8` `unimplemented` to `8` / `8` / `0` with `str` coverage.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_callable_replacement_workflows.py --report .rebar/tmp/rbr-0682-nested-broader-range-wider-ranged-repeat-backtracking-heavy-callable-replacement-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the implementation bounded to the eight `str` cases published by `RBR-0680`. Do not broaden into benchmark rows, bytes coverage, replacement-template flows, broader callback helpers, deeper grouped execution, another grouped family, or stdlib delegation.
- Reuse the existing shared callable parity suite and correctness fixture. Do not create another correctness manifest, another parity suite, or another benchmark family in this run.
- Keep this slice Rust-backed, not Python-only.

## Notes
- `RBR-0682` is the next available feature task id in the current checkout; `RBR-0681` is already occupied by the done architecture cleanup task in `ops/tasks/done/`.
- Queue this directly behind `RBR-0680` so the broader `{1,4}` nested backtracking-heavy callable slice converts behind `rebar._rebar` before benchmark catch-up or deeper grouped execution reopens the frontier.
- 2026-03-19 feature-planning probes confirm this follow-on is concrete from the tracked frontier:
  - `tests/python/test_callable_replacement_parity_suite.py` currently keeps all eight `RBR-0680` case ids in `pending_rebar_case_ids` for `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-callable-replacement-workflows`, so the shared callable suite already exposes the exact parity target without another synthesis pass;
  - `reports/correctness/latest.py` currently reports `1358` total / `1350` passed / `8` `unimplemented` across `113` manifests, and `collection.replacement.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy.callable` at `8` total / `0` passed / `8` `unimplemented`;
  - direct public-API probes from this planning run still raise `NotImplementedError` for numbered and named `rebar.sub(...)` calls on `a(((bc|b)c){1,4})d` and `a(?P<outer>(?:(?P<inner>bc|b)c){1,4})d`, so this parity slice is not already satisfied in the current checkout; and
  - a later benchmark follow-on should catch the same slice up on the existing `benchmarks/workloads/nested_group_callable_replacement_boundary.py` path instead of inventing another benchmark surface.

## Completion
- 2026-03-19: Landed Rust-backed compile and captured-span support for the numbered outer-capture form, the existing named-outer backtracking-heavy match form, and the new named outer-plus-inner callable form behind `rebar._rebar`, then wired the shared callable replacement path through the new native `finditer` boundary.
- Dropped the manifest’s `pending_rebar_case_ids` from `tests/python/test_callable_replacement_parity_suite.py` and updated the shared pattern return-type-error frontier expectation so the newly landed slice stays inside the existing shared callable suite.
- Verified with `cargo build -p rebar-cpython`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`, the task-local correctness rerun at `.rebar/tmp/rbr-0682-nested-broader-range-wider-ranged-repeat-backtracking-heavy-callable-replacement-parity.py`, and the published combined rerun at `reports/correctness/latest.py`.
- Republished `reports/correctness/latest.py` at `1358` total / `1358` passed / `0` `unimplemented` across `113` manifests, with `collection.replacement.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy.callable` now at `8` total / `8` passed / `0` `unimplemented` on `str`.
