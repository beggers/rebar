# RBR-0018: Expand the exported symbol surface

Status: done
Owner: implementation
Created: 2026-03-11
Completed: 2026-03-12

## Goal
- Expose more of the CPython-shaped import surface through `python/rebar` so user code can import core flags, exceptions, and public helper types without falling through to stdlib `re`.

## Deliverables
- `python/rebar/__init__.py`
- `tests/python/test_exported_symbol_surface.py`

## Acceptance Criteria
- `import rebar` exposes a bounded but useful exported-symbol surface that includes `RegexFlag`, `error`, `Pattern`, `Match`, and the primary flag/constants user code imports directly from `re`.
- Flag and constant names use CPython-compatible numeric values for the pinned `3.12.x` target where those values are part of the observable API; tests compare the exported names and values against stdlib `re`.
- `Pattern` and `Match` exports exist as explicit scaffold symbols without pretending that full compiled-pattern or match-object behavior already exists; tests pin the placeholder contract clearly.
- The task does not silently delegate matching or compilation behavior to stdlib `re`; it only broadens the import surface and keeps unimplemented behavior loud.

## Constraints
- Do not implement the matching engine, broad pattern-object behavior, or real match-result semantics in this task.
- Keep the symbol set explicit and scoped to names normal `re` consumers import directly; avoid reopening private `sre_*` compatibility questions here.
- Preserve compatibility with the source-package shim and the built native-module smoke path from `RBR-0010`.

## Notes
- Use `docs/spec/drop-in-re-compatibility.md` as the compatibility contract for flags, exported helper types, and public constants.
- Build on `RBR-0013`; this task is about import-shape parity, not about claiming broader execution compatibility.

## Completion Note
- Landed a CPython-shaped exported symbol scaffold in `python/rebar/__init__.py` with explicit `RegexFlag` values, `error`, non-instantiable `Pattern`/`Match` placeholders, and a `template()` placeholder while keeping compile/match behavior loudly unimplemented.
- Added `tests/python/test_exported_symbol_surface.py` and extended the helper-surface smoke test so exported names, flag values, alias pairs, and placeholder contracts are pinned against stdlib `re`.
