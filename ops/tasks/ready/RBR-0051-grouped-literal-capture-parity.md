# RBR-0051: Add bounded grouped-literal numbered-capture parity

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the first grouped-literal numbered-capture match cases from published gaps into real CPython-shaped behavior without claiming general grouped-regex support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_grouped_literal_capture_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact grouped-literal match cases published by `RBR-0050` stop reporting `unimplemented` for numbered-capture metadata and instead match CPython through the public `rebar` API for `group(1)`, `groups()`, `span(1)`, and `lastindex`.
- Module and compiled-`Pattern` flows both consume Rust-backed capture metadata rather than ad hoc Python-only regex semantics; Python changes stay limited to wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: a single grouped-literal capture path is enough, but named groups, nested captures, alternation-driven group semantics, and broader backreference behavior remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded grouped-literal numbered-capture cases from `unimplemented` to `pass` without regressing the already-landed literal-only and replacement-template workflow behavior.

## Constraints
- Keep this task scoped to the numbered-capture cases published by `RBR-0050`; do not broaden into general grouping, named captures, nested groups, or stdlib delegation.
- Implement any new execution or metadata behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Match`/`Pattern` object contracts outside this exact grouped-literal slice.

## Notes
- Build on `RBR-0047`, `RBR-0050`, and the existing Rust-backed compile/match boundary.
- This task exists so the next correctness-pack expansion can turn into real behavior work immediately instead of becoming another reporting-only dead end.
