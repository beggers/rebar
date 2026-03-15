# RBR-0415: Add broader-range open-ended `{2,}` nested-group alternation plus branch-local-backreference conditional callable-replacement parity

Status: done
Owner: feature-implementation
Created: 2026-03-15
Completed: 2026-03-15

## Goal
- Convert the broader-range open-ended `{2,}` nested-group alternation plus branch-local-backreference conditional callable-replacement cases published by `RBR-0414` into real Rust-backed behavior without claiming later benchmark rows, replacement-template variants, broader callback semantics, or deeper nested grouped execution.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The exact numbered and named cases published by `RBR-0414` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded module and compiled-`Pattern` `sub()` and `subn()` callable-replacement workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, callable marshalling, and native result marshalling.
- The supported slice remains intentionally narrow: one outer capture containing one broader-range open-ended `{2,}` inner `(b|c)` site immediately replayed by one same-branch backreference and one later group-exists conditional feeding callable replacements in `a((b|c){2,})\2(?(2)d|e)` and `a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)` is enough, including one numbered lower-bound same-branch callback success such as `abbbd` or `acccd`, one numbered mixed-branch or doubled-haystack callback case such as `abcbccd`, `abbbdabcbccd`, or `abcbccdaccccd`, one named path that keeps the shifted `{2,}` `outer` capture observable under replacement, and one named first-match-only or doubled-haystack path that keeps the final selected `inner` branch observable under replacement, while later benchmark catch-up, replacement-template variants, broader callback helpers, and deeper nested grouped execution remain out of scope.
- The shared `tests/python/test_callable_replacement_parity_suite.py` surface continues to carry callback result and callback `Match` snapshot parity for this slice, and the pending-manifest bookkeeping drops this manifest once the live `rebar` result stops being `unimplemented`; do not add a new manifest-specific callable-replacement parity module.
- `reports/correctness/latest.py` flips the bounded broader-range open-ended `{2,}` nested-group alternation plus branch-local-backreference conditional callable-replacement cases from `unimplemented` to `pass` without regressing the already-landed broader-range open-ended `{2,}` callable-replacement and replacement-template slices, the adjacent conditional replacement-template slice, or the surrounding callable-replacement and capture-metadata surfaces.

## Constraints
- Keep this task scoped to the cases published by `RBR-0414`; do not broaden into later benchmark catch-up, replacement-template variants, broader callback helpers, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern` / `Match` and callable-replacement contracts outside this exact broader-range open-ended `{2,}` conditional slice.

## Notes
- Build on `RBR-0414`, `RBR-0408`, `RBR-0395`, and the existing shared callable-replacement fixture path.
- Keep later benchmark catch-up on the existing `benchmarks/workloads/nested_group_callable_replacement_boundary.py` path instead of forking another benchmark family.
- The shared callable-replacement parity suite already discovers published `*callable_replacement_workflows.py` fixtures, so this task should widen that existing parity coverage rather than creating another manifest-specific test harness.

## Completion
- 2026-03-15: Exposed the existing Rust broader-range open-ended `{2,}` nested-group alternation plus branch-local-backreference conditional span finder through a dedicated `_rebar` `finditer` boundary and routed native callable-replacement marshalling through it.
- 2026-03-15: Dropped the last pending-manifest skip from `tests/python/test_callable_replacement_parity_suite.py`, so the shared callable parity surface now runs this published manifest live instead of treating it as queued follow-on work.
- 2026-03-15: Republished `reports/correctness/latest.py`; the tracked combined scorecard now reports `933` total cases, `933` passing cases, `0` explicit failures, and `0` unimplemented cases, and the task-local conditional callable suite now reports `8` executed, `8` passed, and `0` unimplemented cases.

## Verification
- 2026-03-15: `cargo build -p rebar-cpython`
- 2026-03-15: `PYTHONPATH=python ./.venv/bin/python -m pytest tests/python/test_callable_replacement_parity_suite.py` (`821 passed`)
- 2026-03-15: `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_callable_replacement_workflows.py --report .rebar/tmp/rbr-0415-conditional-callable.py` (`{"executed_cases": 8, "failed_cases": 0, "passed_cases": 8, "skipped_cases": 0, "total_cases": 8, "unimplemented_cases": 0}`)
- 2026-03-15: `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` (`{"executed_cases": 933, "failed_cases": 0, "passed_cases": 933, "skipped_cases": 0, "total_cases": 933, "unimplemented_cases": 0}`)
- 2026-03-15: `PYTHONPATH=python ./.venv/bin/python -m pytest tests/conformance/test_combined_correctness_scorecards.py` (`9 passed`)
