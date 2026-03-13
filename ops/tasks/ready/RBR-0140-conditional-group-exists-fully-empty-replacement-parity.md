# RBR-0140: Add bounded fully-empty conditional replacement parity

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Convert the first fully-empty conditional replacement cases from the published correctness pack into real Rust-backed behavior without claiming broader conditional composition or general replacement-template support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_conditional_group_exists_fully_empty_replacement_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact fully-empty conditional replacement cases published by `RBR-0139` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded `sub()` and `subn()` flows.
- Module and compiled-`Pattern` flows both consume Rust-backed conditional replacement behavior rather than ad hoc Python-only regex semantics; Python changes stay limited to wrapper construction, cache/object plumbing, replacement marshalling, and native result marshalling.
- The supported slice remains intentionally narrow: one fully-empty conditional site inside literal prefix/suffix text feeding constant replacement text is enough, but omitted-no-arm, explicit-empty-else, or empty-yes-arm variants, replacement templates that read capture groups, callable replacement semantics, alternation-heavy conditional arms, nested conditionals, quantified conditionals, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded fully-empty conditional replacement cases from `unimplemented` to `pass` without regressing the already-landed fully-empty conditional search/fullmatch behavior or the broader literal-only replacement helper surface.

## Constraints
- Keep this task scoped to the fully-empty conditional replacement cases published by `RBR-0139`; do not broaden into omitted-no-arm, explicit-empty-else, or empty-yes-arm variants, nested conditionals, quantified conditionals, replacement-template capture expansion, callable replacement semantics, or stdlib delegation.
- Any new regex behavior must live behind `rebar._rebar`; `python/rebar/__init__.py` stays limited to export, wrapper, cache, and FFI responsibilities.
- Preserve the current `Pattern`/`Match` and replacement object contracts outside this exact fully-empty conditional replacement slice.

## Notes
- Build on `RBR-0117` and `RBR-0139`.
- This task exists so the queue converts the next accepted conditional replacement workflow into real Rust-backed behavior instead of leaving it as publication-only coverage.
