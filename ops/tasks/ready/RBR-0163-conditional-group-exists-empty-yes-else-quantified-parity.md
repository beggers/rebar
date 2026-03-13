# RBR-0163: Add bounded quantified empty-yes-arm conditional parity

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Convert the first quantified empty-yes-arm conditional cases from the published correctness pack into real Rust-backed behavior without claiming broader quantified or backtracking-heavy empty-arm execution.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_conditional_group_exists_empty_yes_else_quantified_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact quantified empty-yes-arm conditional cases published by `RBR-0162` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded workflows under test.
- Module and compiled-`Pattern` flows both consume Rust-backed quantified empty-yes-arm behavior rather than ad hoc Python-only regex semantics; Python changes stay limited to wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one exact-repeat `{2}` quantifier over `(a(b)?c(?(1)|e)){2}` / `(a(?P<word>b)?c(?(word)|e)){2}` is enough, including repeated capture-present, repeated capture-absent, and mixed present/absent cases, but fully-empty quantified variants, replacement helpers, alternation-heavy repeated arms, nested conditionals inside the repeated site, deeper nesting, ranged/open-ended repeats, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded quantified empty-yes-arm cases from `unimplemented` to `pass` without regressing the already-landed empty-yes-arm baseline, the nested empty-yes-arm slice queued immediately ahead of this task, or the broader quantified-conditional frontier.

## Constraints
- Keep this task scoped to the quantified empty-yes-arm cases published by `RBR-0162`; do not broaden into fully-empty quantified variants, replacement semantics, nested repeated conditionals, alternation-heavy repeated arms, ranged/open-ended repeats, or stdlib delegation.
- Any new regex behavior must live behind `rebar._rebar`; `python/rebar/__init__.py` stays limited to export, wrapper, cache, and FFI responsibilities.
- Preserve the current `Pattern`/`Match` contracts outside this exact quantified empty-yes-arm slice.

## Notes
- Build on `RBR-0162`.
- This task exists so the queue converts one exact repeated empty-yes-arm spelling into real Rust-backed behavior instead of leaving it as publication-only coverage.
