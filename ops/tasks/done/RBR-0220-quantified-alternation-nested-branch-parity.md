# RBR-0220: Add bounded quantified-alternation nested-branch parity

Status: done
Owner: implementation
Created: 2026-03-13
Completed: 2026-03-13

## Goal
- Convert the first quantified-alternation nested-branch cases from the published correctness pack into real Rust-backed behavior without claiming wider counted ranges, open-ended repeats, branch-local backreferences, or broader backtracking-heavy grouped execution.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_quantified_alternation_nested_branch_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact quantified-alternation nested-branch cases published by `RBR-0219` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded compile, module, and compiled-`Pattern` workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one bounded `{1,2}` outer capture whose alternation chooses either one nested `b|c` site or one literal `de` branch in `a((b|c)|de){1,2}d` / `a(?P<word>(b|c)|de){1,2}d` is enough, including lower-bound successes, second-repetition successes that mix branch selections, and explicit no-match observations that keep the trailing literal outside the quantified group, but wider counted ranges, open-ended repeats, branch-local backreferences, conditionals, replacement workflows, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded quantified-alternation nested-branch cases from `unimplemented` to `pass` without regressing the already-landed quantified-alternation baseline, the already-landed nested-group alternation baseline, or the bounded branch-local and conditional quantified-alternation follow-ons queued ahead of this task.

## Constraints
- Keep this task scoped to the cases published by `RBR-0219`; do not broaden into wider counted ranges, open-ended repeats, branch-local backreferences, conditional combinations, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact combined slice.

## Notes
- Build on `RBR-0219`.
- This task exists so the queue turns the first bounded quantified-alternation nested-branch workflows into real Rust-backed behavior instead of leaving them as publication-only coverage.
- Landed a narrow Rust-backed parser/matcher for `a((b|c)|de){1,2}d` and `a(?P<word>(b|c)|de){1,2}d`, added Python parity coverage, and republished `reports/correctness/latest.json` at 504 passing cases with 0 `unimplemented` gaps.
