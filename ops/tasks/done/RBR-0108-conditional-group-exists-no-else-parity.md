# RBR-0108: Add bounded conditional no-else parity

Status: done
Owner: implementation
Created: 2026-03-12
Completed: 2026-03-12

## Goal
- Convert the first bounded omitted-no-arm conditional group-exists cases from the published correctness pack into real CPython-shaped behavior without claiming explicit empty-else forms, assertion-conditioned branches, nested conditionals, or broad backtracking support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_conditional_group_exists_no_else_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact omitted-no-arm conditional group-exists cases published by `RBR-0107` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` match flows.
- Any new conditional parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one conditional site keyed by an already-open optional numbered or named capture inside literal prefix/suffix text with no explicit else arm is enough, but explicit empty-else variants, assertion-conditioned branches, nested conditionals, replacement semantics, branch-local backreferences inside conditional arms, quantified conditionals, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded conditional no-else cases from `unimplemented` to `pass` without regressing the already-landed optional-group, optional-group alternation, or two-arm conditional group-exists behavior.

## Constraints
- Keep this task scoped to the omitted-no-arm conditional group-exists cases published by `RBR-0107`; do not broaden into explicit empty-else variants, assertion-conditioned branches, replacement workflows, broader quantified execution, or stdlib delegation.
- Implement any new execution behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact conditional slice.

## Notes
- Build on `RBR-0107`.
- This task exists so the queue turns the next accepted conditional shape into real Rust-backed behavior instead of leaving it as publication-only coverage.
- Landed by extending the Rust conditional parser/executor to treat omitted-no-arm forms as an empty false branch while still rejecting explicit-empty-else, empty-yes-arm, and fully empty variants.
- Added bounded Rust and Python parity coverage for numbered and named no-else conditionals, updated the no-else correctness expectation test, and republished `reports/correctness/latest.json` at `200/200` passes with `0` unimplemented cases.
