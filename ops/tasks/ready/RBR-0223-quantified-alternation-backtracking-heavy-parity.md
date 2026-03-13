# RBR-0223: Add bounded quantified-alternation backtracking-heavy parity

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Convert the first quantified-alternation backtracking-heavy cases from the published correctness pack into real Rust-backed behavior without claiming wider counted ranges, open-ended repeats, branch-local backreferences, conditional combinations, or broader repeated-backtracking execution.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_quantified_alternation_backtracking_heavy_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact quantified-alternation backtracking-heavy cases published by `RBR-0222` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded compile, module, and compiled-`Pattern` workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one bounded `{1,2}` envelope around one overlapping `b|bc` alternation site in `a(b|bc){1,2}d` / `a(?P<word>b|bc){1,2}d` is enough, including lower-bound and second-repetition successes plus explicit no-match observations like `abccd`, but wider counted ranges, open-ended repeats, branch-local backreferences, conditionals, replacement workflows, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded quantified-alternation backtracking-heavy cases from `unimplemented` to `pass` without regressing the already-landed quantified-alternation baseline or the bounded branch-local, conditional, and nested-branch quantified-alternation follow-ons queued ahead of this task.

## Constraints
- Keep this task scoped to the cases published by `RBR-0222`; do not broaden into wider counted ranges, open-ended repeats, branch-local backreferences, conditional combinations, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact combined slice.

## Notes
- Build on `RBR-0222`.
- This task exists so the queue turns the first bounded quantified-alternation backtracking-heavy workflows into real Rust-backed behavior instead of leaving them as publication-only coverage.
