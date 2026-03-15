# RBR-0408: Add broader-range open-ended `{2,}` nested-group alternation plus branch-local-backreference conditional replacement-template parity

Status: ready
Owner: feature-implementation
Created: 2026-03-15

## Goal
- Convert the broader-range open-ended `{2,}` nested-group alternation plus branch-local-backreference conditional replacement-template cases published by `RBR-0406` into real CPython-shaped behavior without claiming benchmark catch-up, callable replacement, broader template parsing, or deeper nested grouped execution support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_open_ended_quantified_group_replacement_template_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The exact broader-range open-ended `{2,}` conditional replacement-template cases published by `RBR-0406` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` `sub()` / `subn()` flows using `\1x`, `\2x`, `\g<outer>x`, and `\g<inner>x`.
- Backend-parameterized Python parity coverage for this slice stays on the ordinary pytest path in `tests/python/test_open_ended_quantified_group_replacement_template_parity_suite.py`, driven directly from the published fixture instead of another file-local scenario table, bespoke manifest layer, or native-only gate.
- Module and compiled-`Pattern` flows both consume Rust-backed broader-range open-ended counted-repeat branch-local-backreference conditional replacement behavior rather than ad hoc Python-only regex semantics; Python changes stay limited to wrapper construction, cache/object plumbing, template marshalling, and native result marshalling.
- The supported slice remains intentionally narrow: one outer capture around one broader-range open-ended `{2,}` inner `(b|c)` site immediately replayed by one same-branch backreference and one later group-exists conditional feeding numbered or named replacement templates is enough, including one numbered lower-bound same-branch path such as `abbbd` or `acccd`, one numbered mixed-branch or doubled-haystack path such as `abcbccd`, `abbbdabcbccd`, or `abcbccdaccccd`, one named path that keeps the shifted `{2,}` `outer` capture observable under template replacement, and one named first-match-only or doubled-haystack path that keeps the final selected `inner` branch observable, while benchmark rows, callable replacements, broader template parsing, broader callback semantics, and deeper nested grouped execution remain out of scope.
- `reports/correctness/latest.py` flips the bounded broader-range open-ended `{2,}` conditional replacement-template cases from `unimplemented` to `pass` without regressing the already-landed broader-range open-ended `{2,}` replacement-template parity, the adjacent compile/search/fullmatch conditional slice, or other published nested replacement behavior.

## Constraints
- Keep this task scoped to the cases published by `RBR-0406`; do not broaden into benchmark work, callable replacement semantics, general template parsing, or stdlib delegation.
- Implement any new execution or template-expansion behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern` / `Match` / replacement object contracts outside this exact broader-range open-ended `{2,}` nested-group branch-local-backreference conditional replacement slice.
- Reuse ordinary pytest parameterization plus the published fixture-loading path and the existing open-ended replacement parity suite instead of adding JSON manifests, generators, or another manifest-specific harness layer.

## Notes
- Build on `RBR-0406`, `RBR-0404`, `RBR-0388`, and the existing nested-group replacement parity surface.
- Keep later benchmark catch-up on the existing `benchmarks/workloads/nested_group_replacement_boundary.py` path; do not fork another benchmark family when that follow-on is queued.
