# RBR-0037A: Move the supported compile and match slice behind the Rust boundary

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Stop deepening `python/rebar/__init__.py` by moving the currently supported compile, parser-diagnostic, literal-match, API-level `IGNORECASE`, cache-visible compile metadata, and `escape()` behavior behind Rust-backed entrypoints in `rebar._rebar`.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_rust_compile_match_boundary.py`

## Acceptance Criteria
- The currently published passing compile, parser-diagnostic, literal `search`/`match`/`fullmatch`, API-level `IGNORECASE`, cache/purge-visible compile metadata, and `escape()` cases still pass through the public `rebar` API, but the underlying behavior decisions come from Rust-backed functions rather than hand-written Python matching or parser logic.
- `python/rebar/__init__.py` remains responsible only for symbol export, wrapper construction, object/cache plumbing, and calling the extension boundary for this supported slice; it should not gain new regex semantics while completing this task.
- Direct unit coverage proves the supported slice still works through the public module surface without delegating to stdlib `re`, and exercises the new Rust boundary explicitly enough that a Python-only fallback would fail the tests.
- Any required correctness-report regeneration keeps the published `66` pass / `14` unimplemented split unchanged or improves it honestly; this task is an architectural port, not a new compatibility-breadth task.

## Constraints
- Keep the scope to behavior that is already supported today; do not broaden into inline-flag success cases, lookbehind, character classes, possessive quantifiers, atomic groups, or new non-literal execution.
- Do not silently delegate supported or unsupported behavior to stdlib `re`.
- Do not replace the Python surface with raw native objects; the CPython-facing module still needs `re`-shaped wrappers and exported symbols.

## Notes
- Triggered by `USER-ASK-2`.
- Build on `RBR-0023`, `RBR-0024`, `RBR-0025`, `RBR-0032`, and `RBR-0037`.
- This task exists so the next parser parity work extends a Rust-owned path instead of adding more permanent logic to the Python shim.

## Completion
- Added bounded Rust compile classification, parser-diagnostic parity cases, literal `search`/`match`/`fullmatch`, and `escape()` logic in `rebar-core`, then surfaced that slice through new `rebar._rebar` boundary functions.
- Refactored `python/rebar/__init__.py` so compile/match/escape semantics now call the native boundary while preserving the existing `Pattern`/`Match` wrappers, cache behavior, and placeholder handling.
- Added `tests/python/test_rust_compile_match_boundary.py` to prove the public module surface depends on the boundary hooks strongly enough that the old Python-only implementation path would fail.
- Verified with `cargo test -p rebar-core`, `cargo test -p rebar-cpython`, and `python3 -m unittest tests.python.test_rust_compile_match_boundary tests.python.test_literal_match_scaffold tests.python.test_literal_ignorecase_behavior tests.python.test_parser_diagnostic_parity tests.python.test_escape_surface tests.python.test_pattern_object_scaffold`.
