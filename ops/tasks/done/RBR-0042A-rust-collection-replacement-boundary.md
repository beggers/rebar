# RBR-0042A: Move the supported collection and replacement slice behind the Rust boundary

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Stop deepening `python/rebar/__init__.py` by moving the currently supported literal-only `split`/`findall`/`finditer`/`sub`/`subn` behavior behind Rust-backed entrypoints in `rebar._rebar` before more workflow breadth lands.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_rust_collection_replacement_boundary.py`

## Acceptance Criteria
- The currently published passing literal-only collection and replacement cases still pass through the public `rebar` API, but the underlying workflow execution and replacement decisions come from Rust-backed functions rather than hand-written Python helper logic.
- `python/rebar/__init__.py` remains responsible only for symbol export, wrapper construction, object/cache plumbing, replacement-callable marshalling, and calling the extension boundary for this supported slice; it should not gain new regex semantics while completing this task.
- Direct unit coverage proves the supported collection and replacement helpers still work through the public module and `Pattern` surfaces without delegating to stdlib `re`, and exercises the new Rust boundary explicitly enough that a Python-only fallback would fail the tests.
- Any required correctness-report regeneration keeps the published pass/gap split unchanged or improves it honestly; this task is an architectural port, not a new compatibility-breadth task.

## Constraints
- Keep the scope to literal-only workflow behavior that is already supported today; do not broaden into replacement templates, callable replacement parity, grouped templates, single-dot matching, inline-flag execution, `LOCALE`, or other new workflow breadth.
- Do not silently delegate supported or unsupported behavior to stdlib `re`.
- Do not replace the Python surface with raw native objects; the CPython-facing module still needs `re`-shaped wrappers and exported symbols.

## Notes
- Triggered by `USER-ASK-2`.
- Build on `RBR-0028`, `RBR-0029`, `RBR-0030`, and `RBR-0031`.
- This task exists so the queued workflow follow-ons extend a Rust-owned path instead of adding more permanent logic to the Python shim.

## Completion
- 2026-03-12: Moved the supported literal-only collection/replacement execution path into Rust by adding repeated-span discovery in `rebar-core`, exposing split/findall/finditer/subn entrypoints from `rebar._rebar`, and keeping `python/rebar/__init__.py` limited to wrapper construction, placeholder translation, and replacement payload marshalling.
- 2026-03-12: Added `tests/python/test_rust_collection_replacement_boundary.py` to prove module and `Pattern` collection/replacement helpers consume native-only outputs and spans when `_native` is present, updated the collection/replacement correctness harness expectation to the current `69`-case `65 pass / 4 unimplemented` summary, and republished the combined tracked correctness report (`80` cases, `73` pass, `7` unimplemented).
- 2026-03-12: Verification: `python3 -m unittest tests.python.test_rust_collection_replacement_boundary tests.python.test_rust_compile_match_boundary tests.python.test_literal_collection_helpers tests.python.test_literal_replacement_helpers tests.conformance.test_correctness_collection_replacement_workflows`; `cargo test -p rebar-core --lib`; `cargo test -p rebar-cpython --lib`; republished `reports/correctness/latest.json` via `python3 -m rebar_harness.correctness ...`.
