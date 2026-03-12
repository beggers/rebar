# RBR-0027: Expand correctness into a module-workflow pack

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the correctness harness beyond helper presence and isolated match observations so it can publish the first end-to-end module workflow checks for the bounded literal-only surface.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/module_workflow_surface.json`
- `tests/conformance/test_correctness_module_workflow.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The correctness runner can execute a module-workflow fixture pack alongside the existing parser, public-API, exported-symbol, pattern-object, and match-behavior manifests.
- The new pack covers tiny literal-only `compile`/`search`/`match`/`fullmatch` workflows, repeated `compile()` cache-hit observations, `purge()` reset behavior, and `escape()` parity across representative `str` and `bytes` cases where the implementation supports them.
- `reports/correctness/latest.json` distinguishes module-workflow cases from the earlier module-surface and match-behavior packs, and it keeps unsupported or placeholder paths explicit instead of counting them as passes.
- A smoke or unit test regenerates the combined correctness report end to end and validates the expanded scorecard structure.

## Constraints
- Keep this task on tiny literal-only workflows and public helper behavior; do not broaden into replacement-template parity, full regex matching semantics, or imported upstream corpora yet.
- Preserve the exact-baseline metadata and the existing multi-manifest scorecard shape rather than inventing a separate workflow-only schema branch.
- Do not delegate the workflow operations to stdlib `re`; the scorecard must continue to expose real `rebar` behavior and remaining gaps honestly.

## Notes
- Build on `RBR-0016`, `RBR-0022`, `RBR-0023`, `RBR-0024`, and `RBR-0025`; this task exists so new bounded behavior reaches the published correctness scorecard immediately instead of living only in unit tests.
