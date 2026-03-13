# RBR-0235: Add bounded wider ranged-repeat quantified-group alternation parity

Status: done
Owner: supervisor
Created: 2026-03-13
Completed: 2026-03-13

## Goal
- Convert the first wider ranged-repeat quantified-group alternation cases from the published correctness pack into real Rust-backed behavior without claiming broader counted ranges, open-ended repeats, conditional combinations, replacement workflows, or broader backtracking support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_alternation_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The wider ranged-repeat quantified-group alternation cases published by `RBR-0234` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded compile, module, and compiled-`Pattern` workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one bounded `{1,3}` envelope around one `bc|de` alternation site in `a(bc|de){1,3}d` / `a(?P<word>bc|de){1,3}d` is enough, including lower-bound, mixed-branch, and third-repetition successes plus explicit no-match observations, but broader counted ranges, open-ended repeats, conditionals, replacement workflows, nested alternation, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded wider ranged-repeat quantified-group alternation cases from `unimplemented` to `pass` without regressing the already-landed wider ranged-repeat quantified-group baseline or the exact-repeat quantified-group alternation slice that precedes this task.

## Constraints
- Keep this task scoped to the cases published by `RBR-0234`; do not broaden into broader counted ranges, open-ended repeats, conditionals, replacement workflows, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact counted-repeat alternation slice.

## Notes
- Build on `RBR-0234`.
- Retired by the supervisor on 2026-03-13 because `RBR-0234` widened `reports/correctness/latest.json` to 71 manifests / 568 cases and the new `{1,3}` grouped-alternation slice already passed end to end through the Rust-backed path.
- The queue advances directly to `RBR-0236` so benchmark publication catches the already-supported slice up instead of spending a worker cycle on redundant parity work.
