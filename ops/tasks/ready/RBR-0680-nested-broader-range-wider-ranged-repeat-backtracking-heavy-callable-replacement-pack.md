# RBR-0680: Publish a nested broader-range wider-ranged-repeat backtracking-heavy callable-replacement correctness pack

Status: ready
Owner: feature-implementation
Created: 2026-03-19

## Goal
- Extend the published correctness scorecard with one bounded broader `{1,4}` nested grouped backtracking-heavy callable-replacement manifest so the frontier reopens on correctness publication now that `RBR-0678` closed the adjacent broader `{1,4}` conditional callable bytes benchmark gap on the shared callable owner path.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_callable_replacement_workflows.py`
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated broader `{1,4}` nested grouped backtracking-heavy callable-replacement manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded `module.sub()`, `module.subn()`, compiled-`Pattern.sub()`, and compiled-`Pattern.subn()` callable-replacement observations through the public `rebar` API for the exact numbered and named workflows:
  - `a(((bc|b)c){1,4})d`;
  - `a(?P<outer>(?:(?P<inner>bc|b)c){1,4})d`.
- The published rows stay pinned to the same bounded owner shape already established by the adjacent broader `{1,4}` backtracking-heavy match frontier and the existing shared callable workflow surface:
  - include one numbered lower-bound outer-capture callback case such as `module.sub(..., callable_match_group(group=1, suffix="x"), "abcd")`;
  - include one numbered first-match-only final-inner callback case such as `module.subn(..., callable_match_group(group=3, prefix="<", suffix=">"), "abccdabcbccd", 1)` or a compiled-`Pattern` equivalent that keeps the overlapping long-branch site explicit;
  - include one named outer-capture callback case such as `module.sub(..., callable_match_group(group="outer", suffix="x"), "abccbcd")` or a compiled-`Pattern` equivalent on a mixed-branch haystack; and
  - include one named first-match-only final-inner callback case such as `module.subn(..., callable_match_group(group="inner", prefix="<", suffix=">"), "abccdabcbccd", 1)` or a compiled-`Pattern` equivalent that keeps the bounded overlapping-branch choice observable.
- The callable replacements stay bounded to the existing `callable_match_group` helper shape by reading `match.group(1)` or `match.group(3)` for numbered workflows and `match.group("outer")` or `match.group("inner")` for named workflows; the task does not broaden into arbitrary callback behavior.
- `python/rebar_harness/correctness.py` and `tests/python/test_fixture_parity_support_contract.py` register the new manifest on the shared `CALLABLE_REPLACEMENT_FIXTURE_SELECTOR` surface instead of adding another manifest-local selector or parity module.
- `tests/python/test_callable_replacement_parity_suite.py` keeps the new manifest on the existing shared callable surface and leaves it explicitly pending until later parity lands; do not add another manifest-specific callable-replacement parity module.
- `tests/conformance/correctness_expectations.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1350` total / `1350` passed / `0` `unimplemented` across `112` manifests to `1358` / `1350` / `8` across `113` manifests; and
  - the new suite `collection.replacement.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy.callable` publishes `8` total `str` cases with honest `unimplemented` outcomes rather than disappearing from the scorecard.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_callable_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_callable_replacement_workflows.py --report .rebar/tmp/rbr-0680-nested-broader-range-wider-ranged-repeat-backtracking-heavy-callable-replacement.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement new callable-replacement behavior just to make the new cases pass.
- Do not broaden into bytes, Rust-backed parity, benchmark rows, replacement-template variants, general callback behavior, another branch-local-backreference family, or deeper grouped slices beyond this exact broader `{1,4}` backtracking-heavy pair.
- Reuse the existing shared callable parity surface and keep the later benchmark follow-on on the existing `benchmarks/workloads/nested_group_callable_replacement_boundary.py` path instead of inventing another benchmark family.

## Notes
- `RBR-0680` is the next available feature task id in the current checkout; `RBR-0679` is already occupied by the done architecture cleanup task in `ops/tasks/done/`.
- Queue this directly after the drained `RBR-0678` head so the next broader `{1,4}` nested grouped callable slice reopens through one exact correctness pack on the same owner surface instead of pausing for another synthesis pass.
- 2026-03-19 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py` already pins the adjacent broader `{1,4}` numbered and named backtracking-heavy grouped owner shape for `a(((bc|b)c){1,4})d` and `a(?P<outer>((bc|b)c){1,4})d`;
  - `tests/conformance/fixtures/quantified_nested_group_alternation_callable_replacement_workflows.py` already pins the shared callable owner shape with bounded `module` and compiled-`Pattern` `sub()` / `subn()` rows using `callable_match_group` on outer and inner captures, so this broader `{1,4}` follow-on can stay on the existing callable surface without another harness design pass;
  - direct `rg` probes in this planning run confirmed that no `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-callable-replacement-workflows` manifest id or backtracking-heavy callable rows currently exist in `python/rebar_harness/correctness.py`, `tests/python/test_callable_replacement_parity_suite.py`, `benchmarks/workloads/nested_group_callable_replacement_boundary.py`, `reports/correctness/latest.py`, or `reports/benchmarks/latest.py`; and
  - direct public-API probes from this planning run still raise `NotImplementedError` for `rebar.sub(...)` on numbered `a(((bc|b)c){1,4})d` and named `a(?P<outer>(?:(?P<inner>bc|b)c){1,4})d`, so this publication pack is not a stale no-op.
