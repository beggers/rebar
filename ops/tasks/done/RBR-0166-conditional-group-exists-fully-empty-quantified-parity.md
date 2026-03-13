# RBR-0166: Add bounded quantified fully-empty conditional parity

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Convert the first quantified fully-empty conditional cases from the published correctness pack into real Rust-backed behavior without claiming broader quantified or backtracking-heavy empty-arm execution.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_conditional_group_exists_fully_empty_quantified_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact quantified fully-empty conditional cases published by `RBR-0165` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded workflows under test.
- Module and compiled-`Pattern` flows both consume Rust-backed quantified fully-empty behavior rather than ad hoc Python-only regex semantics; Python changes stay limited to wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one exact-repeat `{2}` quantifier over `(a(b)?c(?(1)|)){2}` / `(a(?P<word>b)?c(?(word)|)){2}` is enough, including repeated capture-present, repeated capture-absent, and mixed present/absent cases, but empty-yes-arm quantified variants, replacement helpers, alternation-heavy repeated arms, nested conditionals inside the repeated site, deeper nesting, ranged/open-ended repeats, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded quantified fully-empty cases from `unimplemented` to `pass` without regressing the already-landed fully-empty baseline, the nested fully-empty slice queued immediately ahead of this task, or the broader quantified-conditional frontier.

## Constraints
- Keep this task scoped to the quantified fully-empty cases published by `RBR-0165`; do not broaden into empty-yes-arm quantified variants, replacement semantics, nested repeated conditionals, alternation-heavy repeated arms, ranged/open-ended repeats, or stdlib delegation.
- Any new regex behavior must live behind `rebar._rebar`; `python/rebar/__init__.py` stays limited to export, wrapper, cache, and FFI responsibilities.
- Preserve the current `Pattern`/`Match` contracts outside this exact quantified fully-empty slice.

## Notes
- Build on `RBR-0165`.
- This task exists so the queue converts one exact repeated fully-empty spelling into real Rust-backed behavior instead of leaving it as publication-only coverage.

## Completion
- Landed narrow Rust-backed support for `(?:a(b)?c(?(1)|)){2}` and `(?:a(?P<word>b)?c(?(word)|)){2}` by opening the existing quantified whole-conditional parser gate to the fully-empty no-branch spelling without broadening nested or alternation-heavy cases.
- Added Rust and Python parity coverage for compile metadata plus present, absent, mixed, and extra-suffix fullmatch workflows.
- Republished `reports/correctness/latest.json`; the combined scorecard now reports `356/356` passing cases with `0` `unimplemented`.
