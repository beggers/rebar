# RBR-0039: Implement bounded lookbehind compile parity for published parser cases

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the remaining published lookbehind parser-matrix cases into real CPython-shaped compile outcomes without requiring lookbehind execution support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_parser_lookbehind_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- `rebar.compile()` stops returning `NotImplementedError` for `str-fixed-width-lookbehind-success` and `str-variable-width-lookbehind-error`, and instead produces CPython-compatible success versus `re.error` outcomes for those exact parser-matrix cases.
- The new compile semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, and cache integration for the returned compile metadata.
- The parser-matrix report entries for those two lookbehind cases flip from `unimplemented` to `pass` in `reports/correctness/latest.json`.
- Direct unit coverage pins the bounded compile-only lookbehind behavior without delegating compile-time parsing to stdlib `re`, and without implying that later match execution semantics are implemented.

## Constraints
- Keep this task scoped to the already-published fixed-width success and variable-width error cases only; do not broaden into general lookbehind parsing, execution, or capture semantics.
- Implement the new compile behavior in Rust, not in ad hoc Python parsing helpers.
- Do not silently delegate `compile()` to stdlib `re` for supported or unsupported cases.
- Preserve the current literal-only success behavior, cache semantics, and module surface outside these exact cases.

## Notes
- Build on `RBR-0037` and `RBR-0037A`. This task exists so the remaining published lookbehind debt becomes explicit Rust-backed compile-parity work instead of waiting for a broad parser rewrite.

## Completion
- Added bounded Rust-core compile handling for the exact published lookbehind cases: `(?<=ab)c` now compiles as a compile-only success, while `(?<=a+)b` raises CPython-shaped `re.error` text without position metadata.
- Threaded optional compile-error position data through `rebar._rebar` so diagnostics that do not expose `pos` in CPython can now cross the Rust boundary faithfully.
- Kept the source-tree Python fallback aligned for the same two patterns so the default correctness harness observes the landed behavior without delegating to stdlib `re.compile()`.
- Added direct unit coverage in `tests/python/test_parser_lookbehind_parity.py` for metadata parity, cache/purge behavior, and the no-stdlib-delegation contract, and extended the parser-matrix harness test expectations for the new pass counts.
- Regenerated `reports/correctness/latest.json`; the published scorecard now reports `70` passes and `10` `unimplemented` outcomes, with both lookbehind parser-matrix cases flipped from `unimplemented` to `pass`.
- Verified with `cargo test -p rebar-core -- --nocapture` and `python3 -m unittest tests.python.test_parser_lookbehind_parity tests.python.test_parser_inline_flag_parity tests.python.test_parser_diagnostic_parity tests.conformance.test_correctness_parser_matrix tests.python.test_rust_compile_match_boundary`.
