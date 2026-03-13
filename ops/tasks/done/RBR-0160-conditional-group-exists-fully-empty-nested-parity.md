# RBR-0160: Add bounded nested fully-empty conditional parity

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Convert the first nested fully-empty conditional cases from the published correctness pack into real Rust-backed behavior without claiming broader nested empty-arm or backtracking-heavy execution.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_conditional_group_exists_fully_empty_nested_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact nested fully-empty conditional cases published by `RBR-0159` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` `search()`/`match()`/`fullmatch()` flows.
- Any new conditional parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one optional numbered or named capture with one nested fully-empty conditional site inside the outer else-arm of an empty-yes-arm conditional is enough, including capture-present and capture-absent haystacks that both match without a suffix plus a bounded extra-suffix failure, but replacement workflows, broader nested empty-arm spellings, quantified conditionals, deeper nesting, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded nested fully-empty conditional cases from `unimplemented` to `pass` without regressing the already-landed fully-empty baseline, the nested explicit-empty-else slice, or the nested empty-yes-arm slice queued immediately ahead of this task.

## Constraints
- Keep this task scoped to the nested fully-empty cases published by `RBR-0159`; do not broaden into replacement workflows, other nested empty-arm spellings, quantified conditionals, deeper nesting, or stdlib delegation.
- Implement any new execution behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact nested fully-empty slice.

## Notes
- Build on `RBR-0159`.
- This task exists so the queue converts one exact accepted nested fully-empty spelling into real Rust-backed behavior instead of leaving it as publication-only syntax coverage.

## Completion
- Added Rust-backed parsing and bounded match execution for `a(b)?c(?(1)|(?(1)|))` plus `a(?P<word>b)?c(?(word)|(?(word)|))` without widening replacement or other nested empty-arm slices.
- Added dedicated parity coverage in `tests/python/test_conditional_group_exists_fully_empty_nested_parity.py` and refreshed the nested fully-empty correctness expectations.
- Republished `reports/correctness/latest.json`; the combined scorecard now reports 338 passes, 0 explicit failures, and 0 honest gaps across 47 manifests.
