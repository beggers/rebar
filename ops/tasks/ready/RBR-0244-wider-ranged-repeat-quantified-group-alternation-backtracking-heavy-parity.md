# RBR-0244: Add bounded wider ranged-repeat quantified-group alternation backtracking-heavy parity

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Convert the first bounded wider ranged-repeat grouped backtracking-heavy cases from the published correctness pack into real Rust-backed behavior without claiming open-ended grouped-conditionals, replacement workflows, or broader grouped backtracking support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The wider ranged-repeat grouped backtracking-heavy cases published by `RBR-0243` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded compile, module, and compiled-`Pattern` workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one bounded `{1,3}` envelope around one overlapping `(bc|b)c` site in `a((bc|b)c){1,3}d` / `a(?P<word>(bc|b)c){1,3}d` is enough, including lower-bound successes, mixed-branch successes, one bounded third-repetition success, and explicit no-match observations like `abcccd`, but open-ended grouped-conditionals, replacement workflows, nested grouped conditionals, and broader grouped backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded wider ranged-repeat grouped backtracking-heavy cases from `unimplemented` to `pass` without regressing the already-landed wider ranged-repeat grouped alternation slice or the grouped-alternation-plus-conditional slice queued ahead of this task.

## Constraints
- Keep this task scoped to the cases published by `RBR-0243`; do not broaden into open-ended grouped-conditionals, replacement workflows, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact grouped backtracking-heavy slice.

## Notes
- Build on `RBR-0243`.
- This task exists so the queue turns one exact wider ranged-repeat grouped backtracking-heavy frontier into real Rust-backed behavior instead of leaving it as publication-only coverage.
