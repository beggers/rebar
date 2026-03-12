# RBR-0125: Add bounded quantified-alternation parity

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the first bounded quantified-alternation cases from the published correctness pack into real CPython-shaped behavior without claiming wider alternation-heavy repetition, open-ended repeats, or broad backtracking support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_quantified_alternation_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact quantified-alternation cases published by `RBR-0124` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` `search()`/`match()`/`fullmatch()` flows.
- Any new quantified-alternation parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one bounded `{1,2}` capturing group containing one literal alternation site inside literal prefix/suffix text is enough, including the observable final capture values after the second repetition completes, but wider counted ranges, open-ended repeats, nested alternation inside quantified branches, replacement workflows, branch-local backreferences inside quantified alternation, conditionals, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded quantified-alternation cases from `unimplemented` to `pass` without regressing the already-landed grouped alternation, ranged-repeat quantified-group, optional-group alternation, or conditional behavior.

## Constraints
- Keep this task scoped to the quantified-alternation cases published by `RBR-0124`; do not broaden into wider counted ranges, open-ended repeats, replacement workflows, conditionals, or stdlib delegation.
- Implement any new execution behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact quantified-alternation slice.

## Notes
- Build on `RBR-0124`.
- This task exists so the queue turns the first combined alternation-plus-bounded-repetition workflows into real Rust-backed behavior instead of leaving them as publication-only coverage.
- Completed 2026-03-12: added a narrow Rust-backed quantified-alternation parser/executor for the published `a(b|c){1,2}d` / `a(?P<word>b|c){1,2}d` slice, including final-capture reporting from the last repetition.
- Added `tests/python/test_quantified_alternation_parity.py` plus updated `tests/conformance/test_correctness_quantified_alternation_workflows.py` so the six published quantified-alternation cases now assert `pass` instead of `unimplemented`.
- Republished `reports/correctness/latest.json`; the combined scorecard now reports `232/232` passing cases with `0` unimplemented outcomes.
- No Python shim or CPython-boundary code changes were required beyond the already-landed generic native compile/match wiring; the new behavior stayed inside `rebar-core`.
