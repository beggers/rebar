# RBR-0257: Add broader-range open-ended quantified-group alternation plus conditional parity

Status: done
Owner: feature-implementation
Created: 2026-03-13
Completed: 2026-03-13

## Goal
- Convert the first broader-range open-ended grouped-alternation-plus-conditional cases from the published correctness pack into real Rust-backed behavior without claiming broader grouped backtracking, replacement workflows, or deeper grouped execution support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_broader_range_open_ended_quantified_group_alternation_conditional_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The broader-range open-ended grouped-alternation-plus-conditional cases published by `RBR-0256` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded compile, module, and compiled-`Pattern` workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one open-ended `{2,}` envelope around `(bc|de)` wrapped in an optional outer group and followed by `(?(1)d|e)` / `(?(outer)d|e)` is enough, including absent-group `else` behavior, lower-bound successes, mixed-branch successes, one bounded fourth-repetition success, and explicit no-match observations like `abcd`, but broader grouped backtracking, replacement workflows, nested grouped conditionals, and deeper grouped execution remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded broader-range open-ended grouped-conditional cases from `unimplemented` to `pass` without regressing the already-landed open-ended grouped alternation, open-ended grouped-conditional, or broader-range open-ended grouped-alternation slices queued around this task.

## Constraints
- Keep this task scoped to the cases published by `RBR-0256`; do not broaden into replacement workflows, broader grouped backtracking, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact grouped-alternation-plus-conditional slice.

## Notes
- Build on `RBR-0256`.
- This task exists so the queue turns one exact broader-range open-ended grouped-conditional frontier into real Rust-backed behavior instead of leaving it as publication-only coverage.
- Completed 2026-03-13: widened the shared Rust quantified-alternation-conditional path to carry the `{2,}` lower bound for `a((bc|de){2,})?(?(1)d|e)` and `a(?P<outer>(bc|de){2,})?(?(outer)d|e)`, added focused public parity coverage in `tests/python/test_broader_range_open_ended_quantified_group_alternation_conditional_parity.py`, and republished `reports/correctness/latest.json` at 663 passes and 0 unimplemented cases.
