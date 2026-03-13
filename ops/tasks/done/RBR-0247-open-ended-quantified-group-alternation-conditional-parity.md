# RBR-0247: Add open-ended quantified-group alternation plus conditional parity

Status: done
Owner: implementation
Created: 2026-03-13
Completed: 2026-03-13

## Goal
- Convert the first open-ended grouped-alternation-plus-conditional `{1,}` cases from the published correctness pack into real Rust-backed behavior without claiming broader grouped backtracking, replacement workflows, or wider counted-range support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_open_ended_quantified_group_alternation_conditional_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The open-ended grouped-alternation-plus-conditional cases published by `RBR-0246` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded compile, module, and compiled-`Pattern` workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one open-ended `{1,}` envelope around `(bc|de)` wrapped in an optional outer group and followed by `(?(1)d|e)` / `(?(outer)d|e)` is enough, including absent-group `else` behavior, lower-bound successes, repeated and mixed-branch successes, fourth-repetition successes, and explicit no-match observations, but broader grouped backtracking, replacement workflows, nested grouped conditionals, and wider counted ranges remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded open-ended grouped-alternation-plus-conditional cases from `unimplemented` to `pass` without regressing the already-landed open-ended grouped alternation slice or the queued bounded grouped backtracking-heavy follow-on.

## Constraints
- Keep this task scoped to the cases published by `RBR-0246`; do not broaden into replacement workflows, broader grouped backtracking, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact grouped-alternation-plus-conditional slice.

## Notes
- Build on `RBR-0246`.
- This task exists so the queue turns one exact open-ended grouped-conditional frontier into real Rust-backed behavior instead of leaving it as publication-only coverage.
- Completed with a Rust-side parser/matcher extension for `a((bc|de){1,})?(?(1)d|e)` and `a(?P<outer>(bc|de){1,})?(?(outer)d|e)`, focused public parity coverage in `tests/python/test_open_ended_quantified_group_alternation_conditional_parity.py`, and a republished `reports/correctness/latest.json` showing the combined published scorecard at 621 passes and 0 unimplemented cases.
