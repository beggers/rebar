# RBR-0039: Implement bounded lookbehind compile parity for published parser cases

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the remaining published lookbehind parser-matrix cases into real CPython-shaped compile outcomes without requiring lookbehind execution support.

## Deliverables
- `python/rebar/__init__.py`
- `tests/python/test_parser_lookbehind_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- `rebar.compile()` stops returning `NotImplementedError` for `str-fixed-width-lookbehind-success` and `str-variable-width-lookbehind-error`, and instead produces CPython-compatible success versus `re.error` outcomes for those exact parser-matrix cases.
- The parser-matrix report entries for those two lookbehind cases flip from `unimplemented` to `pass` in `reports/correctness/latest.json`.
- Direct unit coverage pins the bounded compile-only lookbehind behavior without delegating compile-time parsing to stdlib `re`, and without implying that later match execution semantics are implemented.

## Constraints
- Keep this task scoped to the already-published fixed-width success and variable-width error cases only; do not broaden into general lookbehind parsing, execution, or capture semantics.
- Do not silently delegate `compile()` to stdlib `re` for supported or unsupported cases.
- Preserve the current literal-only success behavior, cache semantics, and module surface outside these exact cases.

## Notes
- Build on `RBR-0037`. This task exists so the remaining published lookbehind debt becomes explicit compile-parity work instead of waiting for a broad parser rewrite.
