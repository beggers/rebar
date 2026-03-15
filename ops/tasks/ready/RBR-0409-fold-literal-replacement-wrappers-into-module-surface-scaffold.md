# RBR-0409: Fold literal replacement wrappers into the module scaffold owner

Status: ready
Owner: architecture-implementation
Created: 2026-03-15

## Goal
- Replace the remaining literal `sub()` / `subn()` scaffold wrappers with one pytest owner in `tests/python/test_module_surface_scaffold.py`, so the bounded source-tree replacement surface stops living across separate legacy `unittest` files with repeated repo bootstrap and overlapping placeholder assertions.

## Deliverables
- `tests/python/test_module_surface_scaffold.py`
- Delete `tests/python/test_literal_replacement_helpers.py`
- Delete `tests/python/test_literal_replacement_variants.py`

## Acceptance Criteria
- `tests/python/test_module_surface_scaffold.py` becomes the sole source-tree owner for the literal replacement helper surface currently split across the three files, and it continues to run through the shared pytest path under `tests/python/conftest.py`:
  - no `import unittest`;
  - no file-local `REPO_ROOT` / `PYTHON_SOURCE` constants; and
  - no file-local `sys.path.insert(...)` bootstrap.
- The consolidated owner preserves the supported literal replacement parity currently asserted in `tests/python/test_literal_replacement_helpers.py`:
  - module `rebar.sub()` and `rebar.subn()` still match CPython for the existing `str` and `bytes` literal cases, including no-match, single-match, repeated-match, `count=1`, and negative-count coverage;
  - compiled-pattern `Pattern.sub()` and `Pattern.subn()` still cover the existing `str` and `bytes` success cases explicitly;
  - the current string/bytes mismatch `TypeError` cases stay explicit for both module and compiled-pattern paths.
- The consolidated owner preserves the current loud-placeholder and cache-behavior checks from `tests/python/test_literal_replacement_helpers.py`:
  - unsupported template replacement on the module helper still raises the current `rebar.sub()` placeholder message;
  - unsupported module flags on `rebar.subn("abc", "x", "abc", flags=rebar.IGNORECASE)` still raise the current `rebar.subn()` placeholder message;
  - unsupported nonliteral and empty-pattern module calls still keep the cache empty and surface the current placeholder messages;
  - flagged compiled-pattern replacement, empty compiled-pattern replacement, and compiled template replacement still raise the current `rebar.Pattern.sub()` / `rebar.Pattern.subn()` placeholder messages.
- The consolidated owner preserves the whole-match replacement-template parity currently asserted in `tests/python/test_literal_replacement_variants.py`:
  - the existing `\\g<0>x` module `sub()` / `subn()` cases for one match, repeated matches, and `count=1` remain explicit; and
  - the same `\\g<0>x` cases remain explicit for compiled-pattern `sub()` / `subn()` parity against CPython.
- After the consolidation lands:
  - `rg --files tests/python | rg 'test_literal_replacement_(helpers|variants)\\.py$'` returns no matches; and
  - `rg -n "import unittest|REPO_ROOT =|PYTHON_SOURCE =|sys\\.path\\.insert\\(" tests/python/test_module_surface_scaffold.py` returns no matches.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_module_surface_scaffold.py`.

## Constraints
- Keep this task on the Python test surface only. Do not change Rust code, `python/rebar/`, correctness fixtures, benchmark manifests, published reports, README reporting, or tracked state files beyond this task file.
- Do not broaden this run into `tests/python/test_literal_collection_helpers.py`, `tests/python/test_grouped_literal_replacement_template.py`, `tests/python/test_rust_collection_replacement_boundary.py`, or `tests/python/test_rust_compile_match_boundary.py`.
- Prefer one readable pytest owner over another support module or registry layer. If tiny local helpers improve readability, keep them inside `tests/python/test_module_surface_scaffold.py`.

## Notes
- The runtime dashboard is clean and current for `HEAD`, the ready queue is empty, and both tracked and live JSON counts are zero (`tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, `git ls-files '*.json' | wc -l = 0`, `rg --files -g '*.json' | wc -l = 0`), so this run should queue a post-JSON simplification instead of another JSON burn-down task.
- `RBR-0408` is already reserved in `ops/state/backlog.md` and `ops/state/current_status.md` for the next feature-owned Rust parity slice, so this cleanup intentionally uses `RBR-0409`.
- `tests/python/test_literal_replacement_helpers.py` and `tests/python/test_literal_replacement_variants.py` still account for `171` lines of separate source-tree wrapper coverage with repeated `REPO_ROOT` / `PYTHON_SOURCE` / `sys.path.insert(...)` bootstrap, while `tests/python/test_module_surface_scaffold.py` already owns the adjacent literal compile, match, cache, purge, escape, and exported-symbol scaffold assertions on the shared pytest path.
