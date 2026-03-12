# RBR-0023: Implement a literal-only match slice

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Turn the placeholder-only module surface into the first honest execution slice by supporting literal-only `compile`, `search`, `match`, and `fullmatch` behavior for tiny `str` and `bytes` cases without delegating to stdlib `re`.

## Deliverables
- `python/rebar/__init__.py`
- `tests/python/test_literal_match_scaffold.py`

## Acceptance Criteria
- `rebar.compile()` returns a concrete `Pattern` scaffold for the bounded subset where `flags == 0` and the pattern contains no regex metacharacters, and the module-level `search`, `match`, and `fullmatch` helpers route through that same literal-only path.
- `rebar.Pattern` and `rebar.Match` are concrete exported scaffold types for that subset, and successful literal-only calls expose a pinned minimal `Match` contract covering truthiness, `group(0)`, `groups()`, `groupdict()`, `span()`, `start()`, `end()`, `pos`, `endpos`, `lastindex`, and `lastgroup`.
- The implementation supports both `str` and `bytes` literal-only cases with CPython-compatible return-type shape for successful and unsuccessful matches on tiny examples; no-match results return `None`.
- Unsupported flags, metacharacter-bearing patterns, and broader helper families still fail loudly with `NotImplementedError` instead of pretending to implement the general regex engine.

## Constraints
- Keep this task strictly to literal-only semantics and the `compile`/`search`/`match`/`fullmatch` surface; do not implement character classes, quantifiers, alternation, replacement handling, iterators, or full regex parsing here.
- Do not delegate actual compilation or matching behavior to stdlib `re`.
- Preserve compatibility with the source-package shim and the built native-load smoke path from `RBR-0010`.

## Notes
- Build on `RBR-0018` and `RBR-0019`; this task is the first bounded behavior slice that should make the match-behavior harness from `RBR-0016` capable of recording real `rebar` passes.
