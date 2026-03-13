# RBR-0214: Add bounded quantified-alternation-plus-branch-local-backreference parity

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Convert the first quantified-alternation-plus-branch-local-backreference cases from the published correctness pack into real Rust-backed behavior without claiming broader counted-repeat, replacement, conditional, or backtracking-heavy grouped execution.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_quantified_alternation_branch_local_backreference_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact quantified-alternation-plus-branch-local-backreference cases published by `RBR-0213` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded compile, module, and compiled-`Pattern` workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one `{1,2}` quantified envelope around one literal alternation site followed by one same-branch backreference in `a((b|c)\\2){1,2}d` / `a(?P<outer>(?P<inner>b|c)(?P=inner)){1,2}d` is enough, including lower-bound and second-repetition successes plus explicit no-match observations, but broader counted repeats, replacement workflows, conditional combinations, nested alternations, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded quantified-alternation-plus-branch-local-backreference cases from `unimplemented` to `pass` without regressing the already-landed quantified-alternation baseline, the already-landed branch-local backreference baseline, or the optional-group-alternation-plus-branch-local-backreference slice.

## Constraints
- Keep this task scoped to the cases published by `RBR-0213`; do not broaden into wider counted repeats, replacement workflows, conditional combinations, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact combined slice.

## Notes
- Build on `RBR-0213`.
- This task exists so the queue turns the first bounded quantified-alternation-plus-branch-local-backreference workflows into real Rust-backed behavior instead of leaving them as publication-only coverage.
