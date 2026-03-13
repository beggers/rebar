# RBR-0137: Add bounded empty-yes-arm conditional replacement parity

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the first empty-yes-arm conditional replacement cases from the published correctness pack into real Rust-backed behavior without claiming broader conditional composition or general replacement-template support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_conditional_group_exists_empty_yes_else_replacement_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact empty-yes-arm conditional replacement cases published by `RBR-0136` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded `sub()` and `subn()` flows.
- Module and compiled-`Pattern` flows both consume Rust-backed conditional replacement behavior rather than ad hoc Python-only regex semantics; Python changes stay limited to wrapper construction, cache/object plumbing, replacement marshalling, and native result marshalling.
- The supported slice remains intentionally narrow: one empty-yes-arm conditional site inside literal prefix/suffix text feeding constant replacement text is enough, but explicit-empty-else or fully-empty variants, replacement templates that read capture groups, callable replacement semantics, alternation-heavy conditional arms, nested conditionals, quantified conditionals, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded empty-yes-arm conditional replacement cases from `unimplemented` to `pass` without regressing the already-landed empty-yes-arm conditional search/fullmatch behavior or the broader literal-only replacement helper surface.

## Constraints
- Keep this task scoped to the empty-yes-arm conditional replacement cases published by `RBR-0136`; do not broaden into explicit-empty-else or fully-empty variants, nested conditionals, quantified conditionals, replacement-template capture expansion, callable replacement semantics, or stdlib delegation.
- Any new regex behavior must live behind `rebar._rebar`; `python/rebar/__init__.py` stays limited to export, wrapper, cache, and FFI responsibilities.
- Preserve the current `Pattern`/`Match` and replacement object contracts outside this exact empty-yes-arm conditional replacement slice.

## Notes
- Build on `RBR-0114` and `RBR-0136`.
- This task exists so the queue converts the next accepted conditional replacement workflow into real Rust-backed behavior instead of leaving it as publication-only coverage.

## Completion
- Added a bounded Rust-core repeated-span collector for `a(b)?c(?(1)|e)` / `a(?P<word>b)?c(?(word)|e)` replacement workflows and wired the CPython boundary `boundary_literal_subn()` fallback chain through it.
- Added focused Python parity coverage for module and compiled-`Pattern` `sub()` / `subn()` flows, plus Rust-core span-discovery tests for the new empty-yes-arm replacement slice.
- Regenerated `reports/correctness/latest.json`; the published combined scorecard now reports `264` passed cases and `0` unimplemented cases.

## Verification
- `cargo test -p rebar-core conditional_group_exists_empty_yes_else`
- `cargo build -p rebar-cpython`
- `PYTHONPATH=python python3 -m unittest tests.python.test_conditional_group_exists_empty_yes_else_replacement_parity`
- `PYTHONPATH=python python3 -m unittest tests.conformance.test_correctness_conditional_group_exists_empty_yes_else_replacement_workflows tests.conformance.test_correctness_conditional_group_exists_no_else_replacement_workflows tests.conformance.test_correctness_conditional_group_exists_empty_else_replacement_workflows tests.conformance.test_correctness_conditional_group_exists_empty_else_alternation_workflows`
- `PYTHONPATH=python python3 -m rebar_harness.correctness --report reports/correctness/latest.json`
