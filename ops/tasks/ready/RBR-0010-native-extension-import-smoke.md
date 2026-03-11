# RBR-0010: Exercise the built native-extension import path

Status: ready
Owner: implementation
Created: 2026-03-11

## Goal
- Prove that the scaffolded `rebar._rebar` extension can be built and imported through the package boundary instead of relying only on source-package smoke coverage.

## Deliverables
- `tests/python/test_native_extension_smoke.py`
- `python/rebar/__init__.py`
- `pyproject.toml`

## Acceptance Criteria
- A documented smoke command or test builds the extension through the repo's maturin/PyO3 path and verifies that `import rebar` can load `rebar._rebar`.
- The smoke coverage asserts a true native-module load signal, such as `rebar.native_module_loaded() is True`, and checks scaffold metadata exposed by the extension instead of only the pure-Python shim.
- The native-load smoke fails clearly if the extension is absent or broken; it must not silently pass by falling back to the source-package-only path.
- The scaffold remains honest about missing regex functionality: placeholder compile entry points still raise `NotImplementedError` rather than delegating to stdlib `re`.

## Constraints
- Do not implement broad `re` API compatibility or parser behavior in this task.
- Do not add network-dependent packaging steps; keep the smoke path reproducible from a normal local checkout with the existing toolchain assumptions.
- Keep the existing source-import smoke test working; this task adds built-extension coverage rather than replacing the lighter shim-only test.

## Notes
- Use `pyproject.toml`, `crates/rebar-cpython/src/lib.rs`, and `tests/python/test_import_rebar.py` as the starting point.
- This task is intentionally queued behind `RBR-0007` through `RBR-0009`; harness scaffolds still have higher milestone priority, but the native-load gap should be closed before parser-heavy work begins.
