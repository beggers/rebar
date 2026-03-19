# RBR-0670: Convert the nested broader-range wider-ranged-repeat branch-local-backreference conditional callable-replacement pair to real parity

Status: ready
Owner: feature-implementation
Created: 2026-03-19

## Goal
- Convert the exact broader `{1,4}` nested grouped-alternation plus branch-local-backreference conditional callable-replacement `str` pair that `RBR-0668` publishes from honest `unimplemented` outcomes into Rust-backed behavior on the existing shared callable parity surface, without widening into bytes, benchmark catch-up, replacement-template flows, broader callback helpers, or another grouped frontier.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The exact `str` callable-replacement workflows published by `RBR-0668` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` `sub()` / `subn()` flows using:
  - `a((b|c){1,4})\2(?(2)d|e)` through `callable_match_group` on groups `1` or `2`;
  - `a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)(?(inner)d|e)` through `callable_match_group` on groups `"outer"` or `"inner"`.
- `tests/python/test_callable_replacement_parity_suite.py` keeps those eight rows on the existing shared callable suite but drops the current `pending_rebar_case_ids` for `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-callable-replacement-workflows` once live `rebar` behavior stops being `unimplemented`; do not fork another parity suite, fixture path, or manifest-local shim.
- Any new parsing, repeated-span collection, callable-replacement dispatch, or match-object marshalling semantics live behind `rebar._rebar`; Python changes stay limited to public-surface marshalling, cache/object plumbing, callable argument handling, and native result marshalling.
- `reports/correctness/latest.py` is regenerated honestly:
  - the combined report moves from `1342` total / `1334` passed / `8` `unimplemented` across `112` manifests to `1342` / `1342` / `0`; and
  - `collection.replacement.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_conditional.callable` moves from `8` total / `0` passed / `8` `unimplemented` to `8` / `8` / `0`.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_conditional_callable_replacement_workflows.py --report .rebar/tmp/rbr-0670-nested-broader-range-wider-ranged-repeat-branch-local-backreference-conditional-callable-replacement-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the implementation bounded to the `str` pair published by `RBR-0668`. Do not broaden into bytes, benchmark rows, replacement-template flows, broader callback helpers, deeper grouped execution, or stdlib delegation.
- Reuse the existing shared callable parity suite and correctness fixture. Do not create another correctness manifest, another parity suite, or another benchmark family in this run.
- Keep this slice Rust-backed, not Python-only.

## Notes
- `RBR-0670` is the next available feature task id in the current checkout; `RBR-0669` is already occupied by the done architecture cleanup task in `ops/tasks/done/`.
- Queue this directly behind `RBR-0668` so the wider `{1,4}` conditional callable publication converts behind `rebar._rebar` before benchmark catch-up or broader callable follow-ons reopen the frontier.
- 2026-03-19 feature-planning probes confirm this follow-on is concrete from the tracked frontier:
  - `tests/python/test_callable_replacement_parity_suite.py` currently carries all eight case ids for `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-callable-replacement-workflows` in `pending_rebar_case_ids`, so the shared callable suite already exposes the exact parity target without another synthesis pass;
  - `reports/correctness/latest.py` currently reports `collection.replacement.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_conditional.callable` at `8` total / `0` passed / `8` `unimplemented`, so the published frontier is still a real gap rather than a stale no-op;
  - `benchmarks/workloads/nested_group_callable_replacement_boundary.py` already owns the adjacent callable benchmark family for this grouped frontier, so a later Python-path benchmark catch-up can stay on that existing manifest path instead of inventing another benchmark surface; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this planning run still raise `NotImplementedError` for numbered and named `rebar.sub(...)` calls on `a((b|c){1,4})\2(?(2)d|e)` and `a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)(?(inner)d|e)`, so this parity slice is not already satisfied in the current checkout.
