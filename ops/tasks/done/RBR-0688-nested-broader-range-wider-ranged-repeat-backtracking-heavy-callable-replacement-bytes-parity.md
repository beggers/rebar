# RBR-0688: Convert the nested broader-range wider-ranged-repeat backtracking-heavy callable-replacement bytes pair to real parity

Status: ready
Owner: feature-implementation
Created: 2026-03-19

## Goal
- Convert the exact broader `{1,4}` nested grouped backtracking-heavy callable-replacement bytes pair that `RBR-0686` publishes from honest `unimplemented` outcomes into Rust-backed behavior on the existing shared callable parity surface, without widening into benchmark catch-up, replacement-template flows, broader callback helpers, or another grouped frontier.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The exact bytes callable-replacement workflows published by `RBR-0686` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` `sub()` / `subn()` flows using:
  - `rb"a(((bc|b)c){1,4})d"` through `callable_match_group` on groups `1` or `3`;
  - `rb"a(?P<outer>(?:(?P<inner>bc|b)c){1,4})d"` through `callable_match_group` on groups `"outer"` or `"inner"`.
- The bytes follow-on surface introduced by `RBR-0686` in `tests/python/test_callable_replacement_parity_suite.py` becomes real parity coverage instead of a pending `rebar`-only slice:
  - numbered `module.sub(..., callable_match_group(group=1, suffix=b"x"), b"abcd")`, numbered `module.subn(..., callable_match_group(group=3, prefix=b"<", suffix=b">"), b"abccdabcbccd", 1)`, numbered compiled `Pattern.sub(..., b"zzabccbcdzz")`, and numbered compiled `Pattern.subn(..., callable_match_group(group=3, prefix=b"<", suffix=b">"), b"zzabcbccbccbcdabccdzz", 1)` match CPython;
  - named `module.sub(..., callable_match_group(group="outer", suffix=b"x"), b"abccbcd")`, named `module.subn(..., callable_match_group(group="inner", prefix=b"<", suffix=b">"), b"abccdabcbccd", 1)`, named compiled `Pattern.sub(..., callable_match_group(group="outer", suffix=b"x"), b"zzabcbccbccbcdzz")`, and named compiled `Pattern.subn(..., callable_match_group(group="inner", prefix=b"<", suffix=b">"), b"zzabccbcdabccdzz", 1)` match CPython.
- `tests/python/test_callable_replacement_parity_suite.py` keeps those bytes rows on the existing shared callable suite but drops the current `pending_rebar_case_ids` for `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-callable-replacement-workflows` once the live `rebar` result stops being `unimplemented`; do not fork another parity suite, fixture path, or manifest-local shim.
- Any new parsing, repeated-span collection, callable-replacement dispatch, or match-object marshalling semantics live behind `rebar._rebar`; Python changes stay limited to public-surface marshalling, cache/object plumbing, callable argument handling, and native result marshalling.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1366` total / `1358` passed / `8` `unimplemented` across `113` manifests to `1366` / `1366` / `0`;
  - `collection.replacement.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy.callable` moves from `16` total / `8` passed / `8` `unimplemented` to `16` / `16` / `0` with mixed `str`/`bytes` coverage.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_callable_replacement_workflows.py --report .rebar/tmp/rbr-0688-nested-broader-range-wider-ranged-repeat-backtracking-heavy-callable-replacement-bytes-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the implementation bounded to the bytes pair published by `RBR-0686`. Do not broaden into benchmark rows, replacement-template flows, broader callback helpers, deeper grouped execution, another grouped family, or stdlib delegation.
- Reuse the existing shared callable parity suite and correctness fixture. Do not create another bytes-only correctness manifest, another parity suite, or another benchmark family in this run.
- Keep this slice Rust-backed, not Python-only.

## Notes
- `RBR-0688` is the next available feature task id in the current checkout; `RBR-0687` is already occupied by the done architecture cleanup task in `ops/tasks/done/`, and no `RBR-0688*` or `RBR-0689*` task file exists elsewhere under `ops/tasks/`.
- Queue this directly behind `RBR-0686` so the broader `{1,4}` nested backtracking-heavy callable bytes publication converts behind `rebar._rebar` before later Python-path benchmark catch-up or deeper grouped execution reopen the frontier.
- 2026-03-19 feature-planning probes confirm this follow-on is concrete from the tracked frontier:
  - `tests/python/test_callable_replacement_parity_suite.py` currently keeps the eight bytes case ids for `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-callable-replacement-workflows` in `pending_rebar_case_ids`, so the shared callable suite already exposes the exact parity target without another synthesis pass;
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this planning run still raise `NotImplementedError` for numbered and named `rebar.sub(...)` calls on `rb"a(((bc|b)c){1,4})d"` and `rb"a(?P<outer>(?:(?P<inner>bc|b)c){1,4})d"`, so this bytes parity slice is not already satisfied in the current checkout;
  - `reports/correctness/latest.py` currently reports `1366` total / `1358` passed / `8` `unimplemented` across `113` manifests, and `collection.replacement.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy.callable` at `16` total / `8` passed / `8` `unimplemented` with `text_models == ['bytes', 'str']`; and
  - `benchmarks/workloads/nested_group_callable_replacement_boundary.py` already owns the adjacent broader `{1,4}` callable `str` benchmark rows after `RBR-0684`, so a later Python-path benchmark catch-up for this same bytes pair can stay on that existing manifest path instead of inventing another benchmark surface.

## Completion
- 2026-03-19: Added a Rust-backed bytes callable span path for `rb"a(((bc|b)c){1,4})d"` and `rb"a(?P<outer>(?:(?P<inner>bc|b)c){1,4})d"`, including named-bytes compile metadata for `outer`/`inner`, a CPython boundary `finditer` wrapper, Python callable-bytes dispatch, and removal of the eight pending bytes case ids from the shared callable parity suite.
- Verified with `cargo build -p rebar-cpython`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_callable_replacement_workflows.py --report .rebar/tmp/rbr-0688-nested-broader-range-wider-ranged-repeat-backtracking-heavy-callable-replacement-bytes-parity.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.
- Republished `reports/correctness/latest.py` now records `1366` total / `1366` passed / `0` `unimplemented`; `collection.replacement.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy.callable` is `16` total / `16` passed / `0` `unimplemented`.
