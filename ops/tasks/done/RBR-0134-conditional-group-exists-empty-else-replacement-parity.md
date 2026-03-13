# RBR-0134: Add bounded explicit-empty-else conditional replacement parity

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the first explicit-empty-else conditional replacement cases from the published correctness pack into real Rust-backed behavior without claiming broader conditional composition or general replacement-template support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_conditional_group_exists_empty_else_replacement_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact explicit-empty-else conditional replacement cases published by `RBR-0133` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded `sub()` and `subn()` flows.
- Module and compiled-`Pattern` flows both consume Rust-backed conditional replacement behavior rather than ad hoc Python-only regex semantics; Python changes stay limited to wrapper construction, cache/object plumbing, replacement marshalling, and native result marshalling.
- The supported slice remains intentionally narrow: one explicit-empty-else conditional site inside literal prefix/suffix text feeding constant replacement text is enough, but empty-yes-arm or fully-empty variants, replacement templates that read capture groups, callable replacement semantics, alternation-heavy conditional arms, nested conditionals, quantified conditionals, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded explicit-empty-else conditional replacement cases from `unimplemented` to `pass` without regressing the already-landed explicit-empty-else conditional search/fullmatch behavior or the broader literal-only replacement helper surface.

## Constraints
- Keep this task scoped to the explicit-empty-else conditional replacement cases published by `RBR-0133`; do not broaden into empty-yes-arm or fully-empty variants, nested conditionals, quantified conditionals, replacement-template capture expansion, callable replacement semantics, or stdlib delegation.
- Any new regex behavior must live behind `rebar._rebar`; `python/rebar/__init__.py` stays limited to export, wrapper, cache, and FFI responsibilities.
- Preserve the current `Pattern`/`Match` and replacement object contracts outside this exact explicit-empty-else conditional replacement slice.

## Notes
- Build on `RBR-0111` and `RBR-0133`.
- This task exists so the queue converts the next accepted conditional replacement workflow into real Rust-backed behavior instead of leaving it as publication-only coverage.

## Completion
- Added a dedicated Rust span-discovery helper for bounded explicit-empty-else conditional replacements and wired the native `sub()`/`subn()` boundary to use it after the existing omitted-no-arm replacement path.
- Added focused Python parity coverage for module and compiled-pattern numbered/named `a(b)?c(?(1)d|)` / `a(?P<word>b)?c(?(word)d|)` replacement flows.
- Republished `reports/correctness/latest.json`; the combined scorecard now reports 256 passed cases and 0 unimplemented cases, with the eight explicit-empty-else replacement cases flipped from `unimplemented` to `pass`.
