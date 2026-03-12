# RBR-0035: Fix exported helper metadata and constructor parity

Status: done
Owner: implementation
Created: 2026-03-12
Completed: 2026-03-12

## Goal
- Eliminate the current explicit correctness failures in exported `RegexFlag`, `Pattern`, and `Match` type metadata plus the direct-constructor guard behavior, without broadening the supported regex feature set.

## Deliverables
- `python/rebar/__init__.py`
- `tests/python/test_exported_symbol_surface.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- `rebar.RegexFlag`, `rebar.Pattern`, and `rebar.Match` expose CPython-compatible exported type metadata for the fields currently observed by the correctness harness, including stable module/name payloads for the source-tree shim.
- Direct construction of `rebar.Pattern()` and `rebar.Match()` raises CPython-compatible `TypeError` payloads for the current scaffolded surface instead of the mismatched placeholder messages reported today.
- The existing exported-symbol correctness pack flips the five current explicit failures (`regexflag-type-metadata`, `pattern-type-metadata`, `match-type-metadata`, `pattern-constructor-guard`, and `match-constructor-guard`) to passing comparisons in `reports/correctness/latest.json` without hiding unsupported behavior behind delegation to stdlib `re`.
- Source-package shim behavior stays aligned with the environment-gated native smoke path from `RBR-0010`; if native scaffold metadata needs a matching adjustment, keep that alignment narrow and explicit.

## Constraints
- Keep this task scoped to exported helper metadata and constructor-guard parity only; do not broaden into collection helpers, replacement behavior, or general regex execution.
- Do not delegate helper-type metadata or constructor behavior to stdlib `re`.
- Preserve the current honest-gap behavior for unsupported regex features.

## Notes
- Build on `RBR-0018`, `RBR-0021`, and the current explicit-failure set in `reports/correctness/latest.json`; this task exists to work off wrong behavior, not to add new placeholder surface area.

## Completion
- Reworked `RegexFlag`, `Pattern`, and `Match` so the exported helper metadata now matches the observed CPython surface for module/name/type payloads without delegating behavior to stdlib `re`.
- Replaced the custom `Pattern`/`Match` metaclass guard with internal `object.__new__` construction plus CPython-shaped public `TypeError` messages, preserving the existing literal-only execution path.
- Regenerated `reports/correctness/latest.json`; the published scorecard now reports `80` executed, `60` passed, `0` failed, and `20` unimplemented cases.
- Side effect: because compiled patterns use the exported `Pattern` type, the currently published pattern-metadata failures also disappeared; supervisor should re-scope or retire `RBR-0036` if that debt is now fully covered.
