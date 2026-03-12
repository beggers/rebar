# RBR-0029: Implement literal-only replacement helpers

Status: done
Owner: implementation
Created: 2026-03-12
Completed: 2026-03-12

## Goal
- Extend the bounded literal-only module surface so `sub` and `subn` perform real replacements for tiny `str` and `bytes` cases without delegating to stdlib `re`.

## Deliverables
- `python/rebar/__init__.py`
- `tests/python/test_literal_replacement_helpers.py`

## Acceptance Criteria
- `rebar.sub()` and `rebar.subn()` route through the bounded literal-only compile path introduced by `RBR-0023`, and the corresponding `Pattern` methods work for the same supported subset.
- Supported literal-only replacements with plain `str` or `bytes` replacement payloads produce CPython-compatible substituted output and replacement counts for representative no-match, single-match, repeated-match, and bounded-`count` cases on tiny inputs.
- The implementation preserves CPython-compatible return types for `str` versus `bytes` flows and keeps unsupported callable replacements, backreference/template expansion, grouping-dependent replacements, unsupported flags, and metacharacter-bearing patterns explicit with `NotImplementedError`.
- Unsupported replacement features do not mutate cache state or silently delegate to stdlib `re`.

## Constraints
- Keep this task on bounded literal-only `sub`/`subn` behavior with plain replacement payloads only; do not implement backreference expansion, callable replacements, capture groups, or the general replacement-template grammar here.
- Do not delegate actual replacement behavior to stdlib `re`.
- Preserve compatibility with the source-package shim and the environment-gated built native-load smoke path from `RBR-0010`.

## Notes
- Build on `RBR-0023`; this task should give the module and `Pattern` surfaces their first honest replacement behavior while leaving the broader template grammar for later follow-on work.
- Implemented bounded non-empty literal `sub`/`subn` behavior for `str` and `bytes` on both module and `Pattern` surfaces, including repeated-match, bounded-`count`, and no-match behavior without delegating replacement execution to stdlib `re`.
- Kept callable replacements, backslash/template payloads, unsupported flags, empty patterns, and unsupported literal-compile cases loud with `NotImplementedError`, while preventing those module-level unsupported paths from mutating the compile cache.
- Added `tests/python/test_literal_replacement_helpers.py` and updated older scaffold tests so they no longer expect `sub`/`subn` to remain placeholders.
- Verified with `python3 -m unittest tests.python.test_literal_replacement_helpers tests.python.test_literal_collection_helpers tests.python.test_module_surface_scaffold tests.python.test_pattern_object_scaffold tests.python.test_compile_cache_scaffold tests.python.test_import_rebar tests.python.test_literal_match_scaffold tests.python.test_exported_symbol_surface tests.python.test_escape_surface`.
