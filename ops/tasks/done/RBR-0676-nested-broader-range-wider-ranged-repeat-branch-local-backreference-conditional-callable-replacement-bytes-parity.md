# RBR-0676: Convert the nested broader-range wider-ranged-repeat branch-local-backreference conditional callable-replacement bytes pair to real parity

Status: done
Owner: feature-implementation
Created: 2026-03-19

## Goal
- Convert the exact broader `{1,4}` nested grouped-alternation plus branch-local-backreference conditional callable-replacement bytes pair that `RBR-0674` publishes from honest `unimplemented` outcomes into Rust-backed behavior on the existing shared callable parity surface, without widening into benchmark catch-up, replacement-template flows, broader callback helpers, or another grouped frontier.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The exact bytes callable-replacement workflows published by `RBR-0674` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` `sub()` / `subn()` flows using:
  - `rb"a((b|c){1,4})\\2(?(2)d|e)"` through `callable_match_group` on groups `1` or `2`;
  - `rb"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)(?(inner)d|e)"` through `callable_match_group` on groups `"outer"` or `"inner"`.
- The bytes follow-on surface introduced by `RBR-0674` in `tests/python/test_callable_replacement_parity_suite.py` becomes real parity coverage instead of a pending `rebar`-only slice:
  - numbered `module.sub(..., callable_match_group(group=1, suffix=b"x"), b"abbd")`, numbered `module.subn(..., callable_match_group(group=2, prefix=b"<", suffix=b">"), b"abbbdaccd", 1)`, numbered compiled `Pattern.sub(..., b"zzabcbccdzz")`, and numbered compiled `Pattern.subn(..., b"zzaccdabcbccdzz", 1)` match CPython;
  - named `module.sub(..., callable_match_group(group="outer", suffix=b"x"), b"abcbccd")`, named `module.subn(..., callable_match_group(group="inner", prefix=b"<", suffix=b">"), b"abbbdaccd", 1)`, named compiled `Pattern.sub(..., b"zzacccccdzz")`, and named compiled `Pattern.subn(..., callable_match_group(group="inner", prefix=b"<", suffix=b">"), b"zzacccccdabbbdzz", 1)` match CPython.
- `tests/python/test_callable_replacement_parity_suite.py` keeps those bytes rows on the existing shared callable suite but drops the current `pending_rebar_case_ids` for `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-callable-replacement-workflows` once the live `rebar` result stops being `unimplemented`; do not fork another parity suite, fixture path, or manifest-local shim.
- Any new parsing, repeated-span collection, callable-replacement dispatch, or match-object marshalling semantics live behind `rebar._rebar`; Python changes stay limited to public-surface marshalling, cache/object plumbing, callable argument handling, and native result marshalling.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1350` total / `1342` passed / `8` `unimplemented` across `112` manifests to `1350` / `1350` / `0`; and
  - `collection.replacement.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_conditional.callable` moves from `16` total / `8` passed / `8` `unimplemented` to `16` / `16` / `0` with mixed `str`/`bytes` coverage.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_conditional_callable_replacement_workflows.py --report .rebar/tmp/rbr-0676-nested-broader-range-wider-ranged-repeat-branch-local-backreference-conditional-callable-replacement-bytes-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the implementation bounded to the bytes pair published by `RBR-0674`. Do not broaden into benchmark rows, replacement-template flows, broader callback helpers, deeper grouped execution, another branch-local-backreference family, or stdlib delegation.
- Reuse the existing shared callable parity suite and correctness fixture. Do not create another bytes-only correctness manifest, another parity suite, or another benchmark family in this run.
- Keep this slice Rust-backed, not Python-only.

## Notes
- `RBR-0676` is the next available feature task id in the current checkout; `RBR-0675` is already occupied by the done architecture cleanup task in `ops/tasks/done/`.
- Queue this directly behind `RBR-0674` so the wider `{1,4}` conditional callable bytes publication converts behind `rebar._rebar` before benchmark catch-up or deeper grouped execution reopen the frontier.
- 2026-03-19 feature-planning probes confirm this follow-on is concrete from the tracked frontier:
  - `tests/python/test_callable_replacement_parity_suite.py` currently keeps `WIDER_RANGED_REPEAT_CONDITIONAL_CALLABLE_PENDING_BYTES_CASE_IDS` as `pending_rebar_case_ids` for `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-callable-replacement-workflows`, so the shared callable suite already exposes the exact parity target without another synthesis pass;
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this planning run still raise `NotImplementedError` for numbered and named `rebar.sub(...)` calls on `rb"a((b|c){1,4})\\2(?(2)d|e)"` and `rb"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)(?(inner)d|e)"`, so this bytes parity slice is not already satisfied in the current checkout;
  - `reports/correctness/latest.py` currently reports `1350` total / `1342` passed / `8` `unimplemented` across `112` manifests, and `collection.replacement.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_conditional.callable` at `16` total / `8` passed / `8` `unimplemented` with `text_models == ['bytes', 'str']`; and
  - `benchmarks/workloads/nested_group_callable_replacement_boundary.py` already owns the adjacent wider `{1,4}` conditional callable `str` benchmark rows after `RBR-0672`, so a later Python-path benchmark catch-up for this same bytes pair can stay on that existing manifest path instead of inventing another benchmark surface.

## Completion
- 2026-03-19: Landed Rust-backed bytes callable-replacement parity for `rb"a((b|c){1,4})\\2(?(2)d|e)"` and `rb"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)(?(inner)d|e)"` by adding the bounded `{1,4}` conditional bytes compile/finditer path in `rebar-core`, exposing it through `rebar._rebar`, and removing the shared callable-suite pending bytes case ids instead of forking another manifest or parity suite.
- Verification:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_conditional_callable_replacement_workflows.py --report .rebar/tmp/rbr-0676-nested-broader-range-wider-ranged-repeat-branch-local-backreference-conditional-callable-replacement-bytes-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
- Published correctness now reads `1350` total / `1350` passed / `0` unimplemented across `112` manifests, and `collection.replacement.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_conditional.callable` now reads `16` total / `16` passed / `0` unimplemented with the `bytes` partition at `8` / `8` / `0`.
