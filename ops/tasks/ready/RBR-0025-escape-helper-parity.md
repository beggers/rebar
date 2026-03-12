# RBR-0025: Implement `escape()` parity for `str` and `bytes`

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Land one fully implemented public helper by making `rebar.escape()` behave like CPython for representative `str` and `bytes` inputs, independent of the broader regex engine work.

## Deliverables
- `python/rebar/__init__.py`
- `tests/python/test_escape_surface.py`

## Acceptance Criteria
- `rebar.escape()` returns CPython-compatible escaped output for a representative set of `str` and `bytes` inputs that covers regex metacharacters, punctuation, whitespace, and already-safe alphanumeric/underscore characters.
- The helper preserves CPython-compatible return types for `str` versus `bytes` inputs and no longer raises the scaffold placeholder error.
- The implementation lives in `rebar`'s own surface rather than proxying through stdlib `re.escape()` at call time.
- Existing source-shim imports and the environment-gated built native-load smoke path continue to work after the helper lands.

## Constraints
- Keep this task on the public `escape()` helper only; do not broaden into replacement-template semantics, parser work, or private `sre_*` compatibility.
- Do not mask unsupported regex-engine behavior by routing general helper families through stdlib `re`.
- Keep the parity corpus intentionally small and explicit so future changes can extend it incrementally.

## Notes
- Use `docs/spec/drop-in-re-compatibility.md` for the public helper contract. This task should give the module surface one honest implemented helper while the general engine is still scaffolded.
