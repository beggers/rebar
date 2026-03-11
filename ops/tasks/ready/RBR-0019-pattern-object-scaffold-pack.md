# RBR-0019: Scaffold compiled pattern objects

Status: ready
Owner: implementation
Created: 2026-03-11

## Goal
- Expose a bounded compiled-pattern scaffold through `rebar.compile()` so Layer 2 correctness and Phase 2 module-surface work can observe `Pattern` objects and their early attributes without pretending that real matching semantics exist yet.

## Deliverables
- `python/rebar/__init__.py`
- `tests/python/test_pattern_object_scaffold.py`

## Acceptance Criteria
- `rebar.compile()` returns an explicit scaffold `Pattern` object instead of raising immediately, and the object carries a narrow, pinned placeholder contract for observable attributes such as `.pattern`, `.flags`, `.groups`, and `.groupindex`.
- The scaffold `Pattern` exposes the core method surface normal user code reaches first, including `search`, `match`, `fullmatch`, `split`, `findall`, `finditer`, `sub`, and `subn`, and each method fails loudly with a consistent `NotImplementedError` contract rather than silently delegating to stdlib `re`.
- The module continues to export a `Pattern` symbol that matches the concrete scaffold type returned by `compile()`, and tests pin the relationship clearly without claiming broad repr, pickling, or engine semantics.
- The work preserves compatibility with the current source-package shim and the built native-load smoke path from `RBR-0010`; tests cover the shim path directly and keep any native-path validation environment-gated if `maturin` is unavailable.

## Constraints
- Do not implement real parsing, matching, cache eviction, or full pattern-object parity in this task.
- Keep the observable scaffold narrow and honest; placeholder attributes may be static or constructor-provided, but they must not fabricate compatibility wins the harness could mistake for real engine support.
- Do not reopen private `sre_*` APIs or broader `Match` behavior here; this task is about compiled-pattern scaffolding only.

## Notes
- Use `docs/testing/correctness-plan.md` Layer 2 guidance and `docs/spec/drop-in-re-compatibility.md` for the near-term pattern-object contract.
- Build on `RBR-0013` and `RBR-0018`; this task should turn the module-level helper scaffold into the first concrete `Pattern` surface, not restate import-shape work in prose.
