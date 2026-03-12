# RBR-0040: Implement the published character-class `IGNORECASE` compile case

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the published parser-matrix case `str-character-class-ignorecase-success` from `unimplemented` to a real CPython-shaped compile success without broadening into general character-class or engine support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_parser_character_class_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- `rebar.compile()` stops returning `NotImplementedError` for the existing parser-matrix case `str-character-class-ignorecase-success`, and instead produces a CPython-compatible compile result for that exact pattern plus API-level `IGNORECASE` combination.
- The new compile semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, and cache integration for the returned compile metadata.
- The parser-matrix report entry for that case flips from `unimplemented` to `pass` in `reports/correctness/latest.json`.
- Direct unit coverage pins the bounded compile-only character-class behavior without delegating compile-time parsing to stdlib `re`, and without claiming general character-class execution support.

## Constraints
- Keep this task scoped to the already-published `str-character-class-ignorecase-success` case only; do not broaden into arbitrary bracket-class parsing, class-set operations, or general regex-engine behavior.
- Implement the new compile behavior in Rust, not in ad hoc Python parsing helpers.
- Do not silently delegate `compile()` to stdlib `re` for supported or unsupported cases.
- Preserve the existing literal-only success behavior, cache semantics, and module surface outside this exact case.

## Notes
- Build on `RBR-0032`, `RBR-0037`, and `RBR-0037A`. This task exists so one high-value published character-class compile case becomes real Rust-backed behavior before the roadmap broadens again.
