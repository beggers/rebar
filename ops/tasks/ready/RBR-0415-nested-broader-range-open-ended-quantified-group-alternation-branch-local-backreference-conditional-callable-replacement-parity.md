# RBR-0415: Add broader-range open-ended `{2,}` nested-group alternation plus branch-local-backreference conditional callable-replacement parity

Status: ready
Owner: feature-implementation
Created: 2026-03-15

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
