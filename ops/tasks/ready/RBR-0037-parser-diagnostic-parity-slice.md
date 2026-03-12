# RBR-0037: Implement bounded parser diagnostic parity for published error and warning cases

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Convert a narrow set of already-published parser-matrix compile diagnostics from honest `unimplemented` outcomes into real CPython-shaped `re.error` and warning behavior without broadening into general regex execution.

## Deliverables
- `python/rebar/__init__.py`
- `tests/python/test_parser_diagnostic_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- For the existing parser-matrix cases `str-invalid-repeat-error`, `str-invalid-inline-flag-position-error`, `str-inline-locale-flag-error`, `bytes-inline-unicode-flag-error`, `bytes-unicode-escape-error`, and `str-nested-set-warning`, `rebar.compile()` stops returning `NotImplementedError` and instead produces CPython-compatible exception or warning outcomes for the current harness comparisons.
- `reports/correctness/latest.json` flips those published cases from `unimplemented` to `pass` while keeping the remaining parser-matrix cases honest about what is still unsupported.
- Direct unit coverage pins the bounded diagnostic behavior without delegating compile-time parsing to stdlib `re`.

## Constraints
- Keep this task scoped to the already-published compile-time diagnostic cases listed above; do not implement full support for character classes, lookbehind, atomic groups, possessive quantifiers, or broader inline-flag semantics here.
- Do not silently delegate `compile()` to stdlib `re` for supported or unsupported patterns.
- Preserve the current literal-only success behavior, cache semantics, and module-surface behavior outside these exact diagnostic cases.

## Notes
- Build on `RBR-0011`, `RBR-0023`, and the current parser-matrix scorecard. This task exists because once the queued metadata fixes land, the remaining visible correctness debt is concentrated in compile-time parser diagnostics rather than module-surface gaps.
