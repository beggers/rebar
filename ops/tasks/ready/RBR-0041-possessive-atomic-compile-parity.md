# RBR-0041: Implement compile-only support for published possessive and atomic parser cases

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the remaining published possessive-quantifier and atomic-group parser-matrix success cases into real CPython-shaped `compile()` behavior without requiring runtime execution parity for those constructs yet.

## Deliverables
- `python/rebar/__init__.py`
- `tests/python/test_parser_construct_compile_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- `rebar.compile()` stops returning `NotImplementedError` for `str-possessive-quantifier-success` and `str-atomic-group-success`, and instead returns CPython-compatible compile results for those exact parser-matrix cases.
- The parser-matrix report entries for those two cases flip from `unimplemented` to `pass` in `reports/correctness/latest.json`.
- Direct unit coverage pins the bounded compile-only behavior without delegating compile-time parsing to stdlib `re`, and without claiming that the later match engine already executes these constructs.

## Constraints
- Keep this task scoped to the already-published possessive-quantifier and atomic-group compile cases only; do not broaden into general grouping semantics, engine execution, or new parser surface area.
- Do not silently delegate `compile()` to stdlib `re` for supported or unsupported cases.
- Preserve the existing literal-only success behavior, cache semantics, and module surface outside these exact cases.

## Notes
- Build on the parser-matrix correctness pack. This task exists to finish the current published construct-acceptance debt as bounded compile parity rather than leaving those cases indefinitely `unimplemented`.
