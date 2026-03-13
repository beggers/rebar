# RBR-0229: Add bounded open-ended quantified-alternation parity

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Convert the first open-ended quantified-alternation cases from the published correctness pack into real Rust-backed behavior without claiming nested alternation, branch-local backreferences, conditional combinations, replacement workflows, or broader repeated-backtracking execution.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_quantified_alternation_open_ended_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact open-ended quantified-alternation cases published by `RBR-0228` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded compile, module, and compiled-`Pattern` workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one open-ended `{1,}` envelope around one `b|c` alternation site in `a(b|c){1,}d` / `a(?P<word>b|c){1,}d` is enough, including lower-bound and longer bounded repetitions plus explicit no-match observations like `ad` and `abed`, but nested alternation, branch-local backreferences, conditionals, replacement workflows, and broader repeated-backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded open-ended quantified-alternation cases from `unimplemented` to `pass` without regressing the already-landed `{1,2}` quantified-alternation baseline or the queued backtracking-heavy and broader-range quantified-alternation follow-ons ahead of this task.

## Constraints
- Keep this task scoped to the cases published by `RBR-0228`; do not broaden into nested alternation, branch-local backreferences, conditionals, replacement workflows, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact open-ended slice.

## Notes
- Build on `RBR-0228`.
- This task exists so the queue turns the first bounded open-ended quantified-alternation workflows into real Rust-backed behavior instead of leaving them as publication-only coverage.

## Completion
- Landed narrow Rust-backed `{1,}` quantified-alternation support for the published `a(b|c){1,}d` and `a(?P<word>b|c){1,}d` compile/search/fullmatch workflows, including bounded longer repetitions and the published no-match cases.
- Added focused parity coverage in `tests/python/test_quantified_alternation_open_ended_parity.py` and regenerated `reports/correctness/latest.json`, which now reports the full 548-case published slice as passing with 0 `unimplemented` cases.
- No changes were required in `crates/rebar-cpython/src/lib.rs` or `python/rebar/__init__.py`; the existing generic native compile/match boundary already marshaled the new Rust outcome shape correctly.
