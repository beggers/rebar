# RBR-0232: Add bounded exact-repeat quantified-group alternation parity

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Convert the first exact-repeat quantified-group alternation cases from the published correctness pack into real Rust-backed behavior without claiming ranged-repeat, open-ended-repeat, conditional, replacement, or broader backtracking support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_exact_repeat_quantified_group_alternation_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact-repeat quantified-group alternation cases published by `RBR-0231` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded compile, module, and compiled-`Pattern` workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one exact `{2}` envelope around one `bc|de` alternation site in `a(bc|de){2}d` / `a(?P<word>bc|de){2}d` is enough, including all-`bc`, mixed-branch, all-`de`, and explicit no-match observations, but ranged repeats, open-ended repeats, conditionals, replacement workflows, nested alternation, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded exact-repeat quantified-group alternation cases from `unimplemented` to `pass` without regressing the already-landed exact-repeat quantified-group baseline or the queued broader-range/open-ended quantified-alternation follow-ons ahead of this task.

## Constraints
- Keep this task scoped to the cases published by `RBR-0231`; do not broaden into ranged repeats, open-ended repeats, conditionals, replacement workflows, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact counted-repeat alternation slice.

## Notes
- Build on `RBR-0231`.
- This task exists so the queue turns the first exact-repeat quantified-group alternation workflows into real Rust-backed behavior instead of leaving them as publication-only coverage.
- Completed 2026-03-13: added a narrow Rust-backed parser/matcher for `a(bc|de){2}d` and `a(?P<word>bc|de){2}d`, added focused parity coverage in `tests/python/test_exact_repeat_quantified_group_alternation_parity.py`, and republished `reports/correctness/latest.json` at 558 passes / 0 unimplemented.
