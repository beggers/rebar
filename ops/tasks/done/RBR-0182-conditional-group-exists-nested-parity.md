# RBR-0182: Add bounded nested two-arm conditional parity

Status: done
Owner: implementation
Created: 2026-03-13
Completed: 2026-03-13

## Goal
- Convert the bounded nested two-arm conditional cases from the published correctness pack into real Rust-backed behavior without reopening broader nested/backtracking-heavy conditional execution.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `tests/python/test_conditional_group_exists_nested_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact nested two-arm conditional cases published by `RBR-0181` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` search/match/fullmatch flows.
- The bounded workflows for `a(b)?c(?(1)(?(1)d|e)|f)` and `a(?P<word>b)?c(?(word)(?(word)d|e)|f)` compile and execute through the Rust boundary without falling back to Python behavior.
- The published correctness report returns to zero honest gaps for the currently published slice once the new nested two-arm manifest is included.

## Constraints
- Keep this task scoped to the nested two-arm cases published by `RBR-0181`; do not broaden into replacement workflows, quantified nested conditionals, deeper nesting, alternative group structures, or stdlib delegation.
- Preserve existing behavior for already-landed conditional variants while extending the Rust parser/executor to cover this bounded nested composition.
- Update or add focused parity tests instead of relying only on the combined correctness report.

## Notes
- Build on `RBR-0181`.
- This task exists so accepted nested two-arm conditional syntax reaches the Rust-backed baseline before broader backtracking-heavy composition is attempted.

## Completion
- Added bounded nested two-arm conditional compile/match parity in `rebar-core` by recognizing the single-site nested yes-arm shape and collapsing execution to the reachable inner yes branch when the outer capture is present.
- Added focused native parity coverage in `tests/python/test_conditional_group_exists_nested_parity.py` and updated the correctness harness assertion file for the now-green nested manifest.
- Regenerated `reports/correctness/latest.json`; the published combined scorecard now reports `396` passes, `0` failures, and `0` unimplemented cases.
