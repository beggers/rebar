# RBR-0131: Add bounded omitted-no-arm conditional replacement parity

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the first omitted-no-arm conditional replacement cases from the published correctness pack into real Rust-backed behavior without claiming broader conditional composition or general replacement-template support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_conditional_group_exists_no_else_replacement_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact omitted-no-arm conditional replacement cases published by `RBR-0130` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded `sub()` and `subn()` flows.
- Module and compiled-`Pattern` flows both consume Rust-backed conditional replacement behavior rather than ad hoc Python-only regex semantics; Python changes stay limited to wrapper construction, cache/object plumbing, replacement marshalling, and native result marshalling.
- The supported slice remains intentionally narrow: one omitted-no-arm conditional site inside literal prefix/suffix text feeding constant replacement text is enough, but explicit-empty-else or fully-empty variants, replacement templates that read capture groups, callable replacement semantics, alternation-heavy conditional arms, nested conditionals, quantified conditionals, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded omitted-no-arm conditional replacement cases from `unimplemented` to `pass` without regressing the already-landed omitted-no-arm conditional search/fullmatch behavior or the broader literal-only replacement helper surface.

## Constraints
- Keep this task scoped to the omitted-no-arm conditional replacement cases published by `RBR-0130`; do not broaden into explicit-empty-else variants, nested conditionals, quantified conditionals, replacement-template capture expansion, callable replacement semantics, or stdlib delegation.
- Implement any new replacement behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` and replacement object contracts outside this exact omitted-no-arm conditional replacement slice.

## Notes
- Build on `RBR-0108`, `RBR-0130`, and the already-landed literal replacement helper boundary.
- This task exists so the queue converts the first bounded conditional replacement workflow into real Rust-backed behavior instead of leaving it as publication-only coverage.

## Completion
- Added a Rust-backed repeated-match finder for the bounded omitted-no-arm conditional `str` replacement slice and wired `rebar._rebar` `sub()`/`subn()` through it for constant replacement text.
- Added module and compiled-pattern parity tests for numbered and named omitted-no-arm conditional replacement workflows.
- Republished `reports/correctness/latest.json`; the published correctness scorecard is now `248` passes, `0` failures, and `0` unimplemented cases across the current default fixture set.
