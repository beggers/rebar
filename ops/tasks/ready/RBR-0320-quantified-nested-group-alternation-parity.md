# RBR-0320: Add quantified nested-group alternation parity

Status: ready
Owner: feature-implementation
Created: 2026-03-14

## Goal
- Convert the quantified nested-group alternation cases from `RBR-0318` into real CPython-shaped behavior without claiming broader counted-repeat grouped alternation, replacement semantics on this alternation shape, branch-local backreferences, or deeper nested grouped execution support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_quantified_nested_group_alternation_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact quantified nested-group alternation cases published by `RBR-0318` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded compile, `search()`, and compiled-`Pattern.fullmatch()` flows.
- Module and compiled-`Pattern` flows both consume Rust-backed quantified nested-group alternation behavior rather than ad hoc Python-only regex semantics; Python changes stay limited to wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one outer capturing group containing one `+`-quantified inner numbered or named capturing group with one literal alternation site is enough, including a lower-bound one-branch path on `abd`, a repeated-branch path on `abccd` or `acbbd`, and one named path that keeps the quantified outer capture plus final inner branch observable under repetition, but broader counted repeats like `{1,4}` or `{1,}`, replacement-template or callable-replacement behavior on this alternation shape, branch-local backreferences, and deeper nested grouped execution remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded quantified nested-group alternation cases from `unimplemented` to `pass` without regressing the already-landed nested-group alternation, quantified nested-group replacement-template, quantified nested-group callable-replacement, or surrounding grouped capture metadata surfaces.

## Constraints
- Keep this task scoped to the quantified nested-group alternation cases published by `RBR-0318`; do not broaden into wider counted repeats, replacement workflows on this alternation shape, branch-local backreferences, or stdlib delegation.
- Implement any new execution behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact quantified nested-group alternation slice.

## Notes
- Build on `RBR-0318`, `RBR-0313`, and the existing nested-group alternation execution support.
- Keep later benchmark catch-up on the existing `benchmarks/workloads/nested_group_alternation_boundary.py` path, which already carries the quantified nested-group alternation gap anchor; do not fork another benchmark family when that follow-on is seeded.
