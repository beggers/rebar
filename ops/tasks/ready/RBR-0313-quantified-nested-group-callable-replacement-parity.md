# RBR-0313: Add quantified nested-group callable-replacement parity

Status: ready
Owner: feature-implementation
Created: 2026-03-14

## Goal
- Convert the quantified nested-group callable-replacement cases from `RBR-0309` into real CPython-shaped behavior without claiming broader quantified grouped callback semantics, alternation inside the repeated site, or deeper nested grouped execution support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_quantified_nested_group_callable_replacement_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact quantified nested-group callable-replacement cases published by `RBR-0309` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded `sub()` and `subn()` flows.
- Module and compiled-`Pattern` flows both consume Rust-backed quantified nested-group callable-replacement behavior rather than ad hoc Python-only regex semantics; Python changes stay limited to wrapper construction, cache/object plumbing, callable marshalling, and native result marshalling.
- The supported slice remains intentionally narrow: one outer capturing group containing one `+`-quantified inner numbered or named capturing group inside literal prefix/suffix text feeding callable replacements that inspect the published outer or inner capture values is enough, including a lower-bound one-repetition path on `abcd`, a repeated-inner-capture path on `abcbcd`, and one bounded first-match-only path on `abcbcdabcbcd`, but alternation inside the repeated site, broader counted repeats like `{1,4}` or `{1,}`, replacement-template broadening beyond the already-landed slice, broader match-object callback semantics, branch-local backreferences, and deeper nested grouped execution remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded quantified nested-group callable-replacement cases from `unimplemented` to `pass` without regressing the already-landed quantified nested-group replacement-template behavior, nested-group callable-replacement behavior, grouped-alternation callable-replacement behavior, or the surrounding grouped replacement surfaces.

## Constraints
- Keep this task scoped to the quantified nested-group callable-replacement cases published by `RBR-0309`; do not broaden into alternation inside the repeated site, broader counted repeats, general callback semantics, or stdlib delegation.
- Implement any new execution or callback behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match`/replacement object contracts outside this exact quantified nested-group callable-replacement slice.

## Notes
- Build on `RBR-0309`, `RBR-0084`, and the existing quantified nested-group replacement support.
- Keep later benchmark catch-up on the existing `benchmarks/workloads/nested_group_callable_replacement_boundary.py` path, which already carries the quantified named `Pattern.subn()` gap row; do not fork another benchmark family when that follow-on is seeded.
