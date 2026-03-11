# RBR-0014: Expand the correctness harness into a public-API surface pack

Status: done
Owner: implementation
Created: 2026-03-11

## Goal
- Grow the correctness harness beyond parser acceptance so it can measure the first public `re` module-surface behaviors and report that progress separately from parser-only coverage.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/public_api_surface.json`
- `tests/conformance/test_correctness_public_api_surface.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The correctness runner can execute a public-API surface fixture pack in addition to the existing parser-focused manifests.
- The new pack covers import/module-surface checks such as helper presence, loud placeholder exception behavior, and early cache-surface smoke like `purge()` without pretending that matching semantics already exist.
- `reports/correctness/latest.json` distinguishes parser-focused totals from public-API surface totals and preserves honest `pass`, `fail`, and `unimplemented` accounting for each suite.
- A smoke or unit test regenerates the combined correctness report and validates the expanded scorecard structure end to end.

## Constraints
- Keep this task on Layer 2 public-surface behavior only; do not expand into real match-result parity or broad replacement semantics.
- Do not silently treat missing features as passing compatibility; placeholder behavior must stay visible in the report.
- Reuse the exact-baseline metadata path from `RBR-0009` instead of inventing a correctness-only provenance schema.

## Notes
- Use `docs/testing/correctness-plan.md` as the primary task spec, especially the Phase 2 public API surface pack guidance.
- Build on `RBR-0010`, `RBR-0011`, and `RBR-0013`; the public-API pack should observe the scaffold that exists rather than restating it in prose.

## Completion Note
- 2026-03-11: Expanded `python/rebar_harness/correctness.py` to load multiple manifests, added `tests/conformance/fixtures/public_api_surface.json`, regenerated `reports/correctness/latest.json` with separate parser/module-surface layer totals, and verified the combined scorecard with `python3 -m unittest tests.conformance.test_correctness_smoke tests.conformance.test_correctness_parser_matrix tests.conformance.test_correctness_public_api_surface tests.python.test_readme_reporting`.
