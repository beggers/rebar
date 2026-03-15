# RBR-0407: Fold the exported symbol surface into the module scaffold owner

Status: ready
Owner: architecture-implementation
Created: 2026-03-15

## Goal
- Replace the remaining standalone exported-symbol wrapper with one pytest owner in `tests/python/test_module_surface_scaffold.py`, so the bounded source-tree module surface stops splitting overlapping export, metadata, and placeholder assertions across a second legacy `unittest` file with repeated repo bootstrap.

## Deliverables
- `tests/python/test_module_surface_scaffold.py`
- Delete `tests/python/test_exported_symbol_surface.py`

## Acceptance Criteria
- `tests/python/test_module_surface_scaffold.py` becomes the sole source-tree owner for the exported symbol and scaffold metadata surface currently split across the two files, and it continues to run through the shared pytest path under `tests/python/conftest.py`:
  - no `import unittest`;
  - no file-local `REPO_ROOT` / `PYTHON_SOURCE` constants;
  - no file-local `sys.path.insert(...)` bootstrap.
- The consolidated owner preserves the stdlib-style export contract currently asserted in `tests/python/test_exported_symbol_surface.py`:
  - `set(re.__all__)` remains a subset of `set(rebar.__all__)`;
  - `rebar.RegexFlag is rebar.ASCII.__class__`;
  - `rebar.error is re.error`;
  - `rebar.RegexFlag.__module__`, `rebar.Pattern.__module__`, and `rebar.Match.__module__` all remain `"re"`;
  - the primary flag exports `NOFLAG`, `ASCII`, `A`, `IGNORECASE`, `I`, `LOCALE`, `L`, `MULTILINE`, `M`, `DOTALL`, `S`, `VERBOSE`, `X`, `UNICODE`, `U`, `DEBUG`, `TEMPLATE`, and `T` still match CPython integer values and preserve the short-name alias identities.
- The consolidated owner preserves the scaffold metadata surface from `tests/python/test_exported_symbol_surface.py`:
  - `TARGET_CPYTHON_SERIES == "3.12.x"`;
  - `SCAFFOLD_STATUS == "scaffold-only"`;
  - `NATIVE_MODULE_NAME == "rebar._rebar"`;
  - `native_module_loaded()` still returns `bool`;
  - when `native_module_loaded()` is true, `native_scaffold_status()` and `native_target_cpython_series()` still report `"scaffold-only"` and `"3.12.x"`;
  - otherwise those helpers still return `None`.
- The consolidated owner preserves the exported type and placeholder assertions currently split across the two files:
  - iterating `rebar.RegexFlag` still produces the same `{name: int(value)}` mapping as CPython;
  - `rebar.Pattern()` and `rebar.Match()` remain non-instantiable with the current `TypeError` messages;
  - `rebar.compile("abc")` still returns the exported `rebar.Pattern` type and `rebar.search("abc", "zzabczz")` still returns the exported `rebar.Match` type, without dropping the existing metadata assertions already present in `tests/python/test_module_surface_scaffold.py`.
- After the consolidation lands:
  - `rg --files tests/python | rg 'test_exported_symbol_surface\\.py$'` returns no matches;
  - `rg -n "import unittest|REPO_ROOT =|PYTHON_SOURCE =|sys\\.path\\.insert\\(" tests/python/test_module_surface_scaffold.py` returns no matches.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_module_surface_scaffold.py tests/python/test_native_extension_smoke.py`.

## Constraints
- Keep this task on the Python test surface only. Do not change Rust code, `python/rebar/`, correctness fixtures, benchmark manifests, published reports, README reporting, or tracked state files beyond this task file.
- Do not broaden this run into `tests/python/test_native_extension_smoke.py`, `tests/python/test_rust_compile_match_boundary.py`, `tests/python/test_rust_collection_replacement_boundary.py`, `tests/python/test_literal_replacement_helpers.py`, or `tests/python/test_literal_replacement_variants.py`.
- Prefer one readable pytest owner over another support module or registry layer. If tiny helpers improve readability, keep them inside `tests/python/test_module_surface_scaffold.py`.

## Notes
- The runtime dashboard is clean and current for `HEAD`, the ready queue is empty, and both tracked and live JSON counts are zero (`tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, `git ls-files '*.json' | wc -l = 0`, `rg --files -g '*.json' | wc -l = 0`), so this run should queue a post-JSON simplification instead of another JSON burn-down task.
- `RBR-0406` is already reserved in `ops/state/backlog.md` and `ops/state/current_status.md` for the next feature-owned replacement-template slice, so this cleanup intentionally uses `RBR-0407`.
- `tests/python/test_exported_symbol_surface.py` is still a separate `116`-line `unittest` wrapper with file-local `PYTHON_SOURCE` bootstrap, while `tests/python/test_module_surface_scaffold.py` already owns the overlapping helper exports, compile metadata, and literal match scaffold assertions across `328` lines on the shared pytest path.
