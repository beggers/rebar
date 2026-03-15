# RBR-0405: Consolidate the source-tree scaffold surface into one owner suite

Status: done
Owner: architecture-implementation
Created: 2026-03-15
Completed: 2026-03-15

## Goal
- Replace the remaining split source-tree scaffold wrappers with one owner in `tests/python/test_module_surface_scaffold.py`, so the bounded literal compile/match/cache/escape surface stops living across five legacy `unittest` modules with repeated repo bootstrap and overlapping helper assertions.

## Deliverables
- `tests/python/test_module_surface_scaffold.py`
- Delete `tests/python/test_pattern_object_scaffold.py`
- Delete `tests/python/test_compile_cache_scaffold.py`
- Delete `tests/python/test_literal_match_scaffold.py`
- Delete `tests/python/test_escape_surface.py`

## Acceptance Criteria
- `tests/python/test_module_surface_scaffold.py` becomes the sole source-tree shim owner for the bounded scaffold behaviors currently split across the five target files, and it runs through the existing pytest path under `tests/python/conftest.py` instead of carrying file-local repo bootstrap:
  - no `import unittest`;
  - no file-local `REPO_ROOT` / `PYTHON_SOURCE` constants;
  - no file-local `sys.path.insert(...)` bootstrap.
- The consolidated owner preserves the helper-export and placeholder contract currently asserted in `tests/python/test_module_surface_scaffold.py`:
  - `rebar.__all__` still includes `compile`, `search`, `match`, `fullmatch`, `split`, `findall`, `finditer`, `sub`, `subn`, `template`, `escape`, and `purge`;
  - those exported helpers remain callable;
  - `rebar.template("abc")` still raises `NotImplementedError` with the existing scaffold-placeholder message.
- The consolidated owner preserves the compile and `Pattern` metadata surface currently split across `tests/python/test_module_surface_scaffold.py` and `tests/python/test_pattern_object_scaffold.py`:
  - `rebar.compile("abc", rebar.IGNORECASE)` still reports the current `Pattern` type, `pattern`, normalized `flags`, `groups`, and `groupindex` values;
  - the bytes variant from `tests/python/test_pattern_object_scaffold.py` still checks `rebar.compile(b"abc", rebar.IGNORECASE)` metadata explicitly;
  - `rebar.compile(compiled_pattern)` still returns the original object;
  - `rebar.compile(compiled_pattern, rebar.IGNORECASE)` still raises the current `ValueError`;
  - `rebar.compile(123)` still raises the current `TypeError`.
- The consolidated owner preserves the literal module and pattern match surface currently split across `tests/python/test_module_surface_scaffold.py`, `tests/python/test_pattern_object_scaffold.py`, and `tests/python/test_literal_match_scaffold.py`:
  - module `search()`, `match()`, and `fullmatch()` still cover the existing literal `str` hit and miss cases;
  - compiled-pattern `search()`, `match()`, and `fullmatch()` still cover the existing literal `str` and `bytes` hit and miss cases;
  - the current `Match` object checks for `group`, grouped tuple access, `groups`, `groupdict`, `span`, `start`, `end`, `pos`, `endpos`, `lastindex`, and `lastgroup` stay explicit for the bounded literal cases already covered today;
  - missing-group `IndexError` checks for `group`, `span`, `start`, and `end` stay explicit;
  - the existing string-vs-bytes mismatch `TypeError` checks stay explicit.
- The consolidated owner preserves the current loud-placeholder paths from `tests/python/test_pattern_object_scaffold.py` and `tests/python/test_literal_match_scaffold.py`:
  - unsupported module flags on `rebar.search("abc", "abc", rebar.IGNORECASE | rebar.ASCII)`;
  - unsupported nonliteral compile through `rebar.search("[ab]c", "abc")`;
  - unsupported compiled-pattern flags through `rebar.compile("abc", rebar.IGNORECASE | rebar.ASCII).search("abc")`.
- The consolidated owner preserves the cache and purge contract currently asserted in `tests/python/test_compile_cache_scaffold.py`:
  - repeated `compile("abc")`, `compile("abc", rebar.IGNORECASE)`, and `compile(b"abc")` still reuse cached `Pattern` objects;
  - `rebar.purge()` still returns `None` and clears cached patterns;
  - unsupported compile requests still leave the cache unchanged;
  - normalized-flag cache identity for `compile("abc")`, `compile("abc", rebar.UNICODE)`, and `compile("abc", rebar.ASCII)` stays explicit.
- The consolidated owner preserves the exact `escape()` parity table currently asserted in `tests/python/test_escape_surface.py`:
  - the six `STR_CASES` rows stay explicit;
  - the six `BYTES_CASES` rows stay explicit.
- After the consolidation lands:
  - `rg --files tests/python | rg 'test_(pattern_object_scaffold|compile_cache_scaffold|literal_match_scaffold|escape_surface)\\.py$'` returns no matches;
  - `rg -n "import unittest|REPO_ROOT =|PYTHON_SOURCE =|sys\\.path\\.insert\\(" tests/python/test_module_surface_scaffold.py` returns no matches.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_module_surface_scaffold.py tests/python/test_native_extension_smoke.py tests/python/test_exported_symbol_surface.py`.

## Constraints
- Keep this task on the Python test surface only. Do not change Rust code, `python/rebar/`, correctness fixtures, benchmark manifests, published reports, README reporting, or tracked state files beyond this task file.
- Do not fold `tests/python/test_exported_symbol_surface.py`, `tests/python/test_native_extension_smoke.py`, `tests/python/test_rust_compile_match_boundary.py`, or `tests/python/test_rust_collection_replacement_boundary.py` into the same run.
- Prefer one readable owner file over another support module or registry layer. If tiny local helpers improve clarity, keep them inside `tests/python/test_module_surface_scaffold.py`.

## Notes
- The runtime dashboard is clean and current for `HEAD`, the ready queue is empty, and both tracked and live JSON counts are zero (`tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, `git ls-files '*.json' | wc -l = 0`, `rg --files -g '*.json' | wc -l = 0`), so this run should queue a post-JSON simplification instead of another JSON burn-down task.
- `ops/state/backlog.md` and `ops/state/current_status.md` already reserve `RBR-0404` for the next feature benchmark catch-up on `benchmarks/workloads/branch_local_backreference_boundary.py`, so this cleanup intentionally uses `RBR-0405`.
- The five targeted scaffold files total `407` lines and repeat the same `REPO_ROOT` / `PYTHON_SOURCE` / `sys.path.insert(...)` bootstrap in each file, while reasserting overlapping literal compile, match, purge, and escape behavior that can live on one standard pytest path.

## Completion
- 2026-03-15: Rewrote `tests/python/test_module_surface_scaffold.py` as the sole pytest owner for the source-tree scaffold surface, keeping the helper export and template placeholder checks while absorbing the literal compile metadata, literal module and compiled-pattern match flows, missing-group errors, mismatch `TypeError`s, unsupported placeholder paths, cache and purge assertions, and the full six-row `str` plus six-row `bytes` `escape()` tables.
- 2026-03-15: Deleted `tests/python/test_pattern_object_scaffold.py`, `tests/python/test_compile_cache_scaffold.py`, `tests/python/test_literal_match_scaffold.py`, and `tests/python/test_escape_surface.py` after moving their bounded scaffold coverage into the consolidated owner file.

## Verification
- 2026-03-15: `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_module_surface_scaffold.py tests/python/test_native_extension_smoke.py tests/python/test_exported_symbol_surface.py` (`37 passed, 1 skipped, 26 subtests passed`)
- 2026-03-15: `rg --files tests/python | rg 'test_(pattern_object_scaffold|compile_cache_scaffold|literal_match_scaffold|escape_surface)\.py$'` (no matches)
- 2026-03-15: `rg -n "import unittest|REPO_ROOT =|PYTHON_SOURCE =|sys\.path\.insert\(" tests/python/test_module_surface_scaffold.py` (no matches)
- 2026-03-15: `git diff --name-status -- tests/python/test_pattern_object_scaffold.py tests/python/test_compile_cache_scaffold.py tests/python/test_literal_match_scaffold.py tests/python/test_escape_surface.py` (`D` for all four deleted files)
