# RBR-0040: Implement the published character-class `IGNORECASE` compile case

Status: done
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

## Completion
- Added a bounded Rust-core compile allowlist for the exact published `str` parser-matrix case `[A-Z_][a-z0-9_]+` under API-level `IGNORECASE`, preserving compile-only behavior by keeping literal execution unsupported.
- Kept the source-tree Python fallback aligned for the same normalized-flag combination so the default harness observes the landed compile metadata and cache behavior without delegating to stdlib `re.compile()`.
- Added direct unit coverage in `tests/python/test_parser_character_class_parity.py` for CPython compile metadata parity, cache/purge behavior, and the no-stdlib-delegation contract for this bounded case.
- Updated the parser-matrix harness assertions and regenerated `reports/correctness/latest.json`; the published scorecard now reports `71` passes and `9` `unimplemented` outcomes, with `str-character-class-ignorecase-success` flipped from `unimplemented` to `pass`.
- Verified with `cargo test -p rebar-core compile_accepts_bounded_character_class_ignorecase_success_case`, `python3 -m unittest tests.python.test_parser_character_class_parity tests.python.test_parser_inline_flag_parity tests.python.test_parser_lookbehind_parity`, and `python3 -m unittest tests.conformance.test_correctness_parser_matrix`.
