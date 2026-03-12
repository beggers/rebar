# RBR-0028: Implement literal-only collection helpers

Status: done
Owner: implementation
Created: 2026-03-12
Completed: 2026-03-12

## Goal
- Extend the first honest literal-only execution slice so `split`, `findall`, and `finditer` work for tiny `str` and `bytes` cases without delegating to stdlib `re`.

## Deliverables
- `python/rebar/__init__.py`
- `tests/python/test_literal_collection_helpers.py`

## Acceptance Criteria
- `rebar.split()`, `rebar.findall()`, and `rebar.finditer()` route through the same bounded literal-only compile path introduced by `RBR-0023`, and the corresponding `Pattern` methods work for the same supported subset.
- Supported literal-only `findall()` calls return CPython-shaped whole-match results for representative `str` and `bytes` cases, and `finditer()` yields `rebar.Match` objects with stable ordering and normal iterator exhaustion on tiny examples.
- Supported literal-only `split()` calls produce CPython-compatible list shapes for representative no-match, single-match, repeated-match, leading-match, trailing-match, and `maxsplit` cases on tiny inputs.
- Unsupported flags, metacharacter-bearing patterns, and broader iterator or grouping semantics still fail loudly with `NotImplementedError` instead of silently delegating to stdlib `re`.

## Constraints
- Keep this task strictly to literal-only `split`/`findall`/`finditer` behavior and the iterator surface required to expose whole-match results; do not broaden into capture groups, general regex parsing, replacement handling, or throughput work.
- Do not delegate actual collection-helper behavior to stdlib `re`.
- Preserve compatibility with the source-package shim and the environment-gated built native-load smoke path from `RBR-0010`.

## Notes
- Build on `RBR-0023`; this task should turn the remaining placeholder collection helpers into honest bounded behavior before the queue moves on to replacement helpers.
- Implemented bounded non-empty literal `split`/`findall`/`finditer` behavior on both module and `Pattern` surfaces, preserving loud `NotImplementedError` results for unsupported flags, metacharacter patterns, and zero-width collection cases.
- Added `tests/python/test_literal_collection_helpers.py` and updated scaffold/native-surface tests to reflect the newly supported helper subset.
- Verified with `python3 -m unittest tests.python.test_literal_collection_helpers tests.python.test_literal_match_scaffold tests.python.test_module_surface_scaffold tests.python.test_pattern_object_scaffold tests.python.test_compile_cache_scaffold`.
