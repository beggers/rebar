# RBR-0226: Add bounded broader-range quantified-alternation parity

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Convert the first broader-range quantified-alternation cases from the published correctness pack into real Rust-backed behavior without claiming open-ended repeats, nested alternation, branch-local backreferences, conditional combinations, or broader repeated-backtracking execution.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_quantified_alternation_broader_range_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact broader-range quantified-alternation cases published by `RBR-0225` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded compile, module, and compiled-`Pattern` workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one bounded `{1,3}` envelope around one `b|c` alternation site in `a(b|c){1,3}d` / `a(?P<word>b|c){1,3}d` is enough, including lower-bound successes, third-repetition successes, and explicit no-match observations like `ad` or `abbbcd`, but wider counted ranges, open-ended repeats, nested alternation, branch-local backreferences, conditionals, replacement workflows, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded broader-range quantified-alternation cases from `unimplemented` to `pass` without regressing the already-landed `{1,2}` quantified-alternation baseline or the bounded nested-branch and backtracking-heavy quantified-alternation follow-ons queued ahead of this task.

## Constraints
- Keep this task scoped to the cases published by `RBR-0225`; do not broaden into wider counted ranges, open-ended repeats, nested alternation, branch-local backreferences, conditional combinations, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact counted-range slice.

## Notes
- Build on `RBR-0225`.
- This task exists so the queue turns the first broader-range quantified-alternation workflows into real Rust-backed behavior instead of leaving them as publication-only coverage.
