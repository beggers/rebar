# RBR-0013: Expand the scaffolded module surface

Status: done
Owner: implementation
Created: 2026-03-11

## Goal
- Expose a broader `re`-shaped module helper surface through `python/rebar` so Phase 2 correctness and benchmark work can measure import shape and loud placeholder behavior instead of only missing symbols.

## Deliverables
- `python/rebar/__init__.py`
- `crates/rebar-cpython/src/lib.rs`
- `tests/python/test_module_surface_scaffold.py`

## Acceptance Criteria
- `import rebar` exposes a bounded near-term module helper surface that includes `compile`, `search`, `match`, `fullmatch`, `split`, `findall`, `finditer`, `sub`, `subn`, `escape`, and `purge`.
- Each scaffold-only helper fails loudly and consistently when the underlying behavior is not implemented yet; it must not silently delegate to stdlib `re`.
- `purge()` exists and is safe to call before cache behavior lands; the chosen placeholder behavior and return value are pinned in tests.
- The source-package shim and the built native-module path remain compatible with `RBR-0010`; tests validate both the expanded export surface and the native-load signal.

## Constraints
- Do not implement broad regex matching or parser semantics in this task.
- Do not claim full `Pattern`, `Match`, flag, or constant parity that does not exist yet.
- Keep placeholder behavior explicit and honest so later differential harness work can classify it as `unimplemented` rather than mistaking it for compatibility.

## Notes
- Use `docs/spec/drop-in-re-compatibility.md` as the contract for which public helpers matter first.
- Build on `RBR-0006` and `RBR-0010`; this task is about import shape and loud placeholder surfaces, not native-build mechanics.

## Completion
- Added scaffolded module helpers for `search`, `match`, `fullmatch`, `split`, `findall`, `finditer`, `sub`, `subn`, `escape`, and `purge` to the Python shim, with a shared loud `NotImplementedError` contract and `purge()` pinned as a safe no-op returning `None`.
- Extended the PyO3 native scaffold with matching placeholder hooks so the built-wheel path can surface the same helper contract and preserve the native-load metadata path from `RBR-0010`.
- Added `tests/python/test_module_surface_scaffold.py` covering source-package exports, placeholder failures, `purge()` behavior, and a built-wheel/native-load smoke path when `maturin` is available on `PATH`.
- Verified with `python3 -m unittest tests.python.test_import_rebar tests.python.test_module_surface_scaffold` and `cargo check -p rebar-cpython`. The built-wheel smoke remains environment-gated because `maturin` is not installed in this run.
