# RBR-0044: Add a bounded single-dot non-literal workflow slice

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the remaining published `a.c` workflow cases from honest `unimplemented` outcomes into real CPython-shaped behavior without reopening general regex parsing or execution.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_bounded_wildcard_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- `rebar.findall("a.c", "abc")` stops returning `NotImplementedError` and instead matches CPython for the published case `module-findall-nonliteral-str`.
- `rebar.search("a.c", "ABC", rebar.IGNORECASE)` stops returning `NotImplementedError` and instead matches CPython for the published case `flag-unsupported-nonliteral-ignorecase-search`.
- The new workflow semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, and cache/object integration.
- `reports/correctness/latest.json` flips those two published workflow cases from `unimplemented` to `pass`.
- The supported slice stays narrow and explicit: this task should only add the bounded single-dot wildcard form needed by the published cases, not general metacharacter handling, character classes, or broader regex-engine behavior.

## Constraints
- Keep this task scoped to the already-published single-dot wildcard workflow cases; do not silently broaden support to arbitrary regex syntax or delegate matching to stdlib `re`.
- Implement the new workflow behavior in Rust, not in ad hoc Python execution helpers.
- Preserve the current literal-only behavior and cache semantics outside these exact cases.
- Keep any new compile acceptance or execution support honest and narrow enough that later parser tasks still have real work left to do.

## Notes
- Build on `RBR-0032`, `RBR-0038`, `RBR-0042`, and `RBR-0042A`. This task exists so the next published non-literal workflow debt is addressed as a bounded Rust-backed compatibility slice instead of another broad parser rewrite.
