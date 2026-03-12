# RBR-0038: Implement bounded inline-flag compile parity for published parser cases

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the remaining published inline-flag parser-matrix success cases from honest `unimplemented` outcomes into real CPython-shaped `compile()` behavior without broadening into general inline-flag support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_parser_inline_flag_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- `rebar.compile()` stops returning `NotImplementedError` for the existing parser-matrix cases `str-inline-unicode-flag-success` and `bytes-inline-locale-flag-success`, and instead returns CPython-compatible compile results for those exact cases.
- The new compile semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, and cache integration for the returned compile metadata.
- The parser-matrix report entries for those two cases flip from `unimplemented` to `pass`, while the diagnostic cases covered by `RBR-0037` (`str-invalid-inline-flag-position-error`, `str-inline-locale-flag-error`, and `bytes-inline-unicode-flag-error`) remain aligned with CPython and do not regress.
- Direct unit coverage pins the bounded inline-flag compile behavior without delegating compile-time parsing to stdlib `re`.

## Constraints
- Keep this task scoped to the already-published inline-flag parser cases listed above; do not broaden into general inline-flag parsing, flag scoping semantics, or match-engine behavior.
- Implement the new compile behavior in Rust, not in ad hoc Python parsing helpers.
- Do not silently delegate `compile()` to stdlib `re` for supported or unsupported cases.
- Preserve the existing literal-only success path, cache semantics, and module surface outside these exact cases.

## Notes
- Build on `RBR-0037` and `RBR-0037A`. This task exists so inline-flag parser parity continues as a bounded follow-on without deepening the Python shim.

## Completion
- Added a bounded Rust-core compile allowlist for `(?u:a)` on `str` and `(?L:a)` on `bytes`, preserving the existing diagnostic cases and marking both new successes as compile-only rather than literal-execution-capable.
- Kept the source-tree Python fallback in sync for those exact cases so the non-wheel correctness harness still observes the same compile metadata and cache behavior while the primary behavior definition remains in Rust.
- Added direct unit coverage in `tests/python/test_parser_inline_flag_parity.py` for CPython metadata parity, cache/purge behavior, and the no-stdlib-delegation contract for these supported cases.
- Regenerated `reports/correctness/latest.json`; the published scorecard now reports `68` passes and `12` `unimplemented` outcomes, with both inline-flag parser-matrix cases flipped to `pass`.
- Verified with `cargo test -p rebar-core` and `python3 -m unittest tests.conformance.test_correctness_parser_matrix tests.conformance.test_correctness_public_api_surface tests.conformance.test_correctness_match_behavior tests.conformance.test_correctness_exported_symbol_surface tests.conformance.test_correctness_pattern_object_surface tests.conformance.test_correctness_module_workflow tests.conformance.test_correctness_collection_replacement_workflows tests.conformance.test_correctness_literal_flag_workflows tests.python.test_parser_inline_flag_parity tests.python.test_parser_diagnostic_parity tests.python.test_rust_compile_match_boundary`.
