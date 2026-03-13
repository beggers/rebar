# RBR-0238: Add bounded open-ended quantified-group alternation parity

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Convert the first bounded open-ended quantified-group alternation cases from the published correctness pack into real Rust-backed behavior without claiming conditional combinations, replacement workflows, or broader grouped backtracking support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_open_ended_quantified_group_alternation_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The open-ended quantified-group alternation cases published by `RBR-0237` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded compile, module, and compiled-`Pattern` workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one bounded `{1,}` envelope around one `bc|de` alternation site in `a(bc|de){1,}d` / `a(?P<word>bc|de){1,}d` is enough, including lower-bound, mixed-branch, third/fourth-repetition successes plus explicit no-match observations, but broader counted-repeat families, conditionals, replacement workflows, nested alternation, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded open-ended quantified-group alternation cases from `unimplemented` to `pass` without regressing the already-landed exact-repeat and wider ranged-repeat quantified-group alternation slices that precede this task.

## Constraints
- Keep this task scoped to the cases published by `RBR-0237`; do not broaden into broader counted-repeat families, conditionals, replacement workflows, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact counted-repeat alternation slice.

## Notes
- Build on `RBR-0237`.
- This task exists so the queue turns the first bounded open-ended quantified-group alternation workflows into real Rust-backed behavior instead of leaving them as publication-only coverage.

## Completion
- Extended the Rust-backed open-ended quantified-alternation parser path so the bounded `a(bc|de){1,}d` and `a(?P<word>bc|de){1,}d` grouped-alternation slice now compiles and executes through the existing native `compile`/`search`/`fullmatch` boundary without widening into other open-ended families.
- Added focused Rust assertions in `crates/rebar-core/src/lib.rs` plus a new Python parity suite in `tests/python/test_open_ended_quantified_group_alternation_parity.py` covering lower-bound matches, bounded second/third/fourth repetition paths, and explicit no-match observations.
- Republished `reports/correctness/latest.json`; the combined scorecard now reports 584 executed cases with 584 passes, 0 failures, and 0 remaining `unimplemented` outcomes.
