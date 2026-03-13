# RBR-0217: Add bounded quantified-alternation-plus-conditional parity

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Convert the first quantified-alternation-plus-conditional cases from the published correctness pack into real Rust-backed behavior without claiming branch-local backreferences, replacement semantics, nested conditionals, or broader counted-repeat backtracking-heavy execution.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_quantified_alternation_conditional_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact quantified-alternation-plus-conditional cases published by `RBR-0216` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded compile, module, and compiled-`Pattern` workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one optional capture around one `{1,2}` quantified alternation followed by one group-exists conditional in `a((b|c){1,2})?(?(1)d|e)` / `a(?P<outer>(b|c){1,2})?(?(outer)d|e)` is enough, including `ae`, `abd`, `acd`, `abbd`, `accd`, and `abcd`, plus explicit no-match observations like `abe` and `acce`, but branch-local backreferences, replacement workflows, callable replacements, nested conditionals, wider counted ranges, open-ended repeats, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded quantified-alternation-plus-conditional cases from `unimplemented` to `pass` without regressing the already-landed quantified-alternation baseline, the already-landed conditional group-exists baseline, or the bounded branch-local follow-ons queued ahead of this task.

## Constraints
- Keep this task scoped to the cases published by `RBR-0216`; do not broaden into branch-local backreferences, replacement workflows, nested conditionals, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact combined slice.

## Notes
- Build on `RBR-0216`.
- This task exists so the queue turns the first bounded quantified-alternation-plus-conditional workflows into real Rust-backed behavior instead of leaving them as publication-only coverage.

## Completion
- Added a narrow Rust parser/matcher path for `a((b|c){1,2})?(?(1)d|e)` and `a(?P<outer>(b|c){1,2})?(?(outer)d|e)` with CPython-aligned compile metadata, capture spans, and `lastindex` behavior.
- Added focused Rust regression coverage plus `tests/python/test_quantified_alternation_conditional_parity.py`.
- Rebuilt `rebar._rebar`, ran the targeted parity and fixture-backed correctness tests, and republished `reports/correctness/latest.json` at 494 passed / 0 unimplemented.
