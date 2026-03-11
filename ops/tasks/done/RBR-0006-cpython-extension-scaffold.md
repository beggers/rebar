# RBR-0006: Scaffold the CPython extension and Python package

Status: done
Owner: implementation
Created: 2026-03-11

## Goal
- Add the first CPython-facing scaffold so `rebar` has a concrete Python package boundary and a native-extension crate to build on.

## Deliverables
- `pyproject.toml`
- `python/rebar/__init__.py`
- `crates/rebar-cpython/Cargo.toml`
- `crates/rebar-cpython/src/lib.rs`
- `tests/python/test_import_rebar.py`

## Acceptance Criteria
- The scaffold uses a PyO3-plus-maturin build path, with the native crate wired into the Cargo workspace and depending on `rebar-core`.
- `python/rebar/__init__.py` defines an explicit scaffold-only import surface that does not silently delegate to stdlib `re`; any placeholder entry points must fail loudly and intentionally.
- The package layout makes it clear where the future drop-in `re`-compatible API will live and where the native module boundary sits.
- A Python smoke test exercises package import or scaffold metadata without requiring the full regex implementation to exist yet.

## Constraints
- Do not implement broad `re` API parity in this task.
- Do not hide missing functionality by proxying calls to stdlib `re`.
- Keep the scaffold compatible with the CPython `3.12.x` boundary already defined in the spec docs.

## Notes
- Use `docs/spec/drop-in-re-compatibility.md` as the public-module contract and `docs/spec/syntax-scope.md` as the parser baseline.
- Keep the packaging and import shape friendly to the future correctness and benchmark adapters described in `docs/testing/correctness-plan.md` and `docs/benchmarks/plan.md`.
- Assume `RBR-0005` has landed first and build on the crate names it establishes instead of re-litigating the workspace layout.

## Completion Notes
- Added a root `pyproject.toml` that points maturin at a new `crates/rebar-cpython` PyO3 extension crate and uses `python/` as the package source tree.
- Added `python/rebar/__init__.py` with scaffold-only metadata plus a loud `compile()` placeholder that never falls back to stdlib `re`.
- Added `tests/python/test_import_rebar.py` as a source-import smoke test, and verified `cargo test` plus `python3 -m unittest discover -s tests/python -p 'test_import_rebar.py'`.
