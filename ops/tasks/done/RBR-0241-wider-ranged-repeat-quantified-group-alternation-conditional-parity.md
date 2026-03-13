# RBR-0241: Add bounded wider ranged-repeat quantified-group alternation plus conditional parity

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Convert the first bounded grouped-alternation-plus-conditional `{1,3}` cases from the published correctness pack into real Rust-backed behavior without claiming open-ended grouped-conditionals, replacement workflows, or broader grouped backtracking support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_alternation_conditional_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The wider ranged-repeat grouped-alternation-plus-conditional cases published by `RBR-0240` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded compile, module, and compiled-`Pattern` workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one bounded `{1,3}` envelope around `(bc|de)` wrapped in an optional outer group and followed by `(?(1)d|e)` / `(?(outer)d|e)` is enough, including absent-group `else` behavior, lower-bound successes, mixed-branch successes, upper-bound successes, and explicit no-match observations, but open-ended grouped-conditionals, replacement workflows, nested grouped conditionals, and broader grouped backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded wider ranged-repeat grouped-alternation-plus-conditional cases from `unimplemented` to `pass` without regressing the already-landed wider ranged-repeat grouped alternation slice or the already-published open-ended grouped-alternation benchmark surface.

## Constraints
- Keep this task scoped to the cases published by `RBR-0240`; do not broaden into open-ended grouped-conditionals, replacement workflows, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact grouped-alternation-plus-conditional slice.

## Notes
- Build on `RBR-0240`.
- This task exists so the queue turns one exact grouped-alternation-plus-conditional frontier into real Rust-backed behavior instead of leaving it as publication-only coverage.
- Completed 2026-03-13: extended the Rust compile/match path for the bounded `a((bc|de){1,3})?(?(1)d|e)` and `a(?P<outer>(bc|de){1,3})?(?(outer)d|e)` slice, added focused Rust and Python parity coverage, and republished `reports/correctness/latest.json` to 596 passes / 0 unimplemented.
