# RBR-0024: Add observable compile-cache and purge behavior

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Make the literal-only `compile()` scaffold observable through repeated-call cache hits and `purge()` resets so the public cache surface and cache-aware benchmarks stop being placeholder-only.

## Deliverables
- `python/rebar/__init__.py`
- `tests/python/test_compile_cache_scaffold.py`

## Acceptance Criteria
- Successful literal-only `rebar.compile()` calls are cached by the observable inputs needed to distinguish `str` versus `bytes`, pattern text, and flags, and repeated calls with the same supported inputs return the same `Pattern` object until the cache is cleared.
- `rebar.purge()` clears the compile cache, keeps returning `None`, and leaves subsequent supported `compile()` calls free to create fresh scaffold objects.
- Unsupported compile requests still raise loudly and do not create partial cache entries or mutate cache state in misleading ways.
- Tests pin the source-tree shim behavior directly and keep any built-wheel/native-path validation environment-gated if `maturin` is unavailable.

## Constraints
- Keep this task on bounded cache and purge observability only; do not introduce cache-size tuning, eviction-policy work, or speculative performance optimizations.
- Do not delegate cache semantics to stdlib `re`.
- Preserve the literal-only honesty contract from `RBR-0023`; unsupported regex features must remain explicit gaps.

## Notes
- Build on `RBR-0019` and `RBR-0023`; this task exists so both the correctness and benchmark harnesses can observe real cache-state behavior instead of only placeholder `purge()` results.

## Completion Notes
- Added a bounded source-package compile cache in `python/rebar/__init__.py` keyed by pattern type, pattern value, and normalized flags so repeated supported literal-only `compile()` calls now reuse the same `Pattern` scaffold.
- Updated `purge()` to clear that cache before returning `None`, while keeping the optional native scaffold hook in place.
- Added `tests/python/test_compile_cache_scaffold.py` to pin cache hits, `purge()` resets, normalized-flag behavior, and the requirement that unsupported compile requests leave the cache unchanged.
