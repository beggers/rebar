# RBR-0032: Implement literal-only `IGNORECASE` behavior

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the bounded literal-only execution slice so module and `Pattern` match helpers honor API-level `IGNORECASE` for representative `str` and `bytes` inputs without broadening into general regex parsing.

## Deliverables
- `python/rebar/__init__.py`
- `tests/python/test_literal_ignorecase_behavior.py`

## Acceptance Criteria
- Supported literal-only `compile()`, `search()`, `match()`, and `fullmatch()` flows honor API-level `IGNORECASE` for representative `str` and `bytes` cases on both the module surface and compiled `Pattern` methods.
- The implementation keeps cache identity honest by distinguishing `IGNORECASE`-compiled patterns from default-flag patterns and by preserving the existing `str` versus `bytes` flag normalization rules.
- Unsupported flag combinations, inline flag syntax, metacharacter-bearing patterns, and broader locale/character-class semantics remain explicit with `NotImplementedError` instead of silently delegating to stdlib `re`.
- Tests pin both positive and negative tiny-case behavior directly against the source-tree shim, while leaving any built-wheel/native-path validation environment-gated if `maturin` is unavailable.

## Constraints
- Keep this task on API-level literal-only `IGNORECASE` behavior only; do not broaden into inline-flag parsing, capture groups, locale handling, or general regex engine work.
- Do not delegate actual case-insensitive matching behavior to stdlib `re`.
- Preserve the bounded honesty contract from `RBR-0023` and `RBR-0024`; unsupported regex features must remain loud gaps.

## Notes
- Build on `RBR-0023` and `RBR-0024`. This task exists to turn one high-value flag path into real observable behavior before the roadmap reopens broader parser/engine work.
