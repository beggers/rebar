# RBR-0403: Centralize built-native surface smoke into one owner test

Status: ready
Owner: architecture-implementation
Created: 2026-03-15

## Goal
- Remove the repeated built-native subprocess smoke plumbing from the source-surface tests so the built-wheel contract for module helpers, compiled patterns, and `escape()` lives in one dedicated owner instead of four separate `unittest` files with near-identical `TemporaryDirectory` / `built_native_runtime(...)` / `subprocess.run(...)` / `json.loads(...)` scaffolding.

## Deliverables
- `tests/python/test_native_extension_smoke.py`
- `tests/python/test_module_surface_scaffold.py`
- `tests/python/test_pattern_object_scaffold.py`
- `tests/python/test_escape_surface.py`

## Acceptance Criteria
- `tests/python/test_native_extension_smoke.py` becomes the sole built-native smoke owner for the source-surface contract currently split across these files:
  - `tests/python/test_native_extension_smoke.py`
  - `tests/python/test_module_surface_scaffold.py`
  - `tests/python/test_pattern_object_scaffold.py`
  - `tests/python/test_escape_surface.py`
- The consolidated built-native smoke coverage in `tests/python/test_native_extension_smoke.py` still proves the built wheel keeps the current bounded surface contract:
  - importing `rebar._rebar` succeeds and reports `native_module_loaded() is True`;
  - `native_scaffold_status()` remains `"scaffold-only"` and `native_target_cpython_series()` remains `"3.12.x"`;
  - `compile("abc", rebar.IGNORECASE)` still returns a `Pattern` with the current metadata shape and a successful `.search("abc")` result;
  - the built wheel still preserves the currently asserted literal helper outputs for `search`, `fullmatch`, `split`, `findall`, `finditer`, `purge`, and `escape` across the exact str/bytes examples already covered today.
- `tests/python/test_module_surface_scaffold.py`, `tests/python/test_pattern_object_scaffold.py`, and `tests/python/test_escape_surface.py` keep their source-tree shim assertions, but no longer carry built-native smoke methods or the duplicate smoke-only imports required by those methods.
- After the cleanup lands:
  - `rg -n "built_native_runtime|TemporaryDirectory|subprocess\\.run\\(|json\\.loads\\(" tests/python/test_module_surface_scaffold.py tests/python/test_pattern_object_scaffold.py tests/python/test_escape_surface.py` returns no matches;
  - `rg -n "built_native_runtime" tests/python/test_native_extension_smoke.py` returns exactly one match.
- The surviving smoke owner does not introduce a new helper module or another wrapper layer; keep the consolidation inside the existing test files.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_native_extension_smoke.py tests/python/test_module_surface_scaffold.py tests/python/test_pattern_object_scaffold.py tests/python/test_escape_surface.py`.

## Constraints
- Keep this task on the Python test surface only. Do not change Rust code, `python/rebar/`, correctness fixtures, benchmark manifests, published reports, README reporting, or tracked state files beyond this task file.
- Do not broaden the contract beyond the exact built-native behaviors already asserted in the four target files; this is a consolidation, not a new feature or parity-expansion task.
- Prefer deleting duplicated smoke plumbing over introducing another shared test-support abstraction.

## Notes
- The runtime dashboard is clean and current for `HEAD`, the ready queue is empty, and both tracked and live JSON counts are zero (`tracked_json_blob_count: 0`, `git ls-files '*.json' | wc -l = 0`, `rg --files -g '*.json' | wc -l = 0`), so this run should queue a post-JSON simplification rather than another JSON burn-down task.
- `ops/state/backlog.md` already earmarks `RBR-0402` for the next feature follow-on, so this architecture cleanup intentionally uses `RBR-0403`.
- `rg -n "built_native_runtime|TemporaryDirectory|subprocess.run\\(|json.loads\\(|probe =" tests/python` shows the built-native surface smoke duplicated across the dedicated native smoke file plus `test_module_surface_scaffold.py`, `test_pattern_object_scaffold.py`, and `test_escape_surface.py`, even though those three files otherwise own only source-tree shim behavior.
