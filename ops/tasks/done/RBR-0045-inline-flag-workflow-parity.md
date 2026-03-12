# RBR-0045: Carry inline `(?i)` literal support through the module workflow surface

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the published inline-flag search workflow from an honest `unimplemented` outcome into real CPython-shaped behavior once the compile-only inline-flag slice exists.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_inline_flag_literal_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- `rebar.search("(?i)abc", "ABC")` stops returning `NotImplementedError` and instead matches CPython for the published case `flag-unsupported-inline-flag-search`.
- The compile path for that exact case stays aligned with the bounded inline-flag acceptance work from `RBR-0038`; this task should carry the flag state through execution rather than reintroducing a parser-only versus workflow mismatch.
- The new workflow semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, and cache/object integration.
- `reports/correctness/latest.json` flips `flag-unsupported-inline-flag-search` from `unimplemented` to `pass` without regressing the diagnostic and compile-only inline-flag cases already covered by the parser scorecard.

## Constraints
- Keep this task scoped to the already-published inline `(?i)` literal workflow case only; do not broaden into general inline-flag scoping, multi-flag parsing, or stdlib delegation.
- Implement the new workflow behavior in Rust, not in ad hoc Python execution helpers.
- Preserve the current literal-only behavior contract outside this exact case.
- Do not silently route inline-flag execution through stdlib `re`.

## Notes
- Build on `RBR-0038` and `RBR-0042A`. This task exists so the published workflow surface catches up with the bounded inline-flag compile work without leaving new behavior in Python.
- Completed 2026-03-12: the Rust core now compiles the bounded `(?i)abc` case with CPython-shaped normalized flags and executes the published `search()` workflow through `rebar._rebar`, the source package can load a locally built native artifact from `target/` for scorecard runs, focused Python/Rust tests cover the new path, and the combined correctness report now publishes `flag-unsupported-inline-flag-search` as `pass` with an 80-case summary of 78 pass / 2 unimplemented.
