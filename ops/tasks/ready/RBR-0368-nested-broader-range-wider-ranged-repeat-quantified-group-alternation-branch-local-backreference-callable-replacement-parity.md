# RBR-0368: Add broader `{1,4}` nested-group alternation plus branch-local-backreference callable-replacement parity

Status: ready
Owner: feature-implementation
Created: 2026-03-15

## Goal
- Convert the broader `{1,4}` nested-group alternation plus branch-local-backreference callable-replacement cases from `RBR-0366` into real Rust-backed behavior without claiming open-ended counted-repeat grouped callbacks, replacement-template variants, later benchmark rows, or deeper nested grouped execution support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The exact numbered and named cases published by `RBR-0366` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded module and compiled-`Pattern` `sub()` and `subn()` callable-replacement workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, callable marshalling, and native result marshalling.
- The supported slice remains intentionally narrow: one outer capture containing one broader `{1,4}` inner `(b|c)` site immediately replayed by one same-branch backreference feeding callable replacements in `a((b|c){1,4})\\2d` and `a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d` is enough, including one numbered lower-bound same-branch callback success such as `abbd` or `accd`, one numbered broader counted-repeat or mixed-branch callback case such as `abbbd`, `abcbccd`, `abbbdaccd`, or `abcbccdabbd`, one named path that keeps the broader `{1,4}` `outer` capture observable under replacement, and one named first-match-only or doubled-haystack case that keeps the final selected `inner` branch observable under replacement, while open-ended counted repeats like `{1,}`, benchmark rows, replacement-template variants, broader callback semantics, and deeper nested grouped execution remain out of scope.
- The shared `tests/python/test_callable_replacement_parity_suite.py` surface continues to carry callback result and callback `Match` snapshot parity for this slice; do not add a new manifest-specific callable-replacement parity module.
- `reports/correctness/latest.py` flips the bounded broader `{1,4}` nested-group alternation plus branch-local-backreference callable-replacement cases from `unimplemented` to `pass` without regressing the already-landed quantified nested-group alternation plus branch-local-backreference callable-replacement slice, the adjacent broader `{1,4}` nested-group alternation plus branch-local-backreference non-callable slice, or the surrounding callable-replacement and capture-metadata surfaces.

## Constraints
- Keep this task scoped to the cases published by `RBR-0366`; do not broaden into open-ended counted repeats, later benchmark catch-up, replacement-template workflows, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` and callable-replacement contracts outside this exact broader `{1,4}` combined slice.

## Notes
- Build on `RBR-0366`, `RBR-0362`, `RBR-0356`, and `RBR-0338`.
- Keep later benchmark catch-up on the existing `benchmarks/workloads/nested_group_callable_replacement_boundary.py` path instead of forking another benchmark family.
- The shared callable-replacement parity suite already discovers published `*callable_replacement_workflows.py` fixtures, so this task should widen that existing parity coverage rather than creating another manifest-specific test harness.
