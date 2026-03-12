# RBR-0038: Implement bounded inline-flag compile parity for published parser cases

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the remaining published inline-flag parser-matrix success cases from honest `unimplemented` outcomes into real CPython-shaped `compile()` behavior without broadening into general inline-flag support.

## Deliverables
- `python/rebar/__init__.py`
- `tests/python/test_parser_inline_flag_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- `rebar.compile()` stops returning `NotImplementedError` for the existing parser-matrix cases `str-inline-unicode-flag-success` and `bytes-inline-locale-flag-success`, and instead returns CPython-compatible compile results for those exact cases.
- The parser-matrix report entries for those two cases flip from `unimplemented` to `pass`, while the diagnostic cases covered by `RBR-0037` (`str-invalid-inline-flag-position-error`, `str-inline-locale-flag-error`, and `bytes-inline-unicode-flag-error`) remain aligned with CPython and do not regress.
- Direct unit coverage pins the bounded inline-flag compile behavior without delegating compile-time parsing to stdlib `re`.

## Constraints
- Keep this task scoped to the already-published inline-flag parser cases listed above; do not broaden into general inline-flag parsing, flag scoping semantics, or match-engine behavior.
- Do not silently delegate `compile()` to stdlib `re` for supported or unsupported cases.
- Preserve the existing literal-only success path, cache semantics, and module surface outside these exact cases.

## Notes
- Build on `RBR-0037`. This task exists so inline-flag parser parity continues as a bounded follow-on instead of reopening parser work as one large undifferentiated task.
