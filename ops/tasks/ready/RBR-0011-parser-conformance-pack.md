# RBR-0011: Expand the correctness harness into a parser conformance pack

Status: ready
Owner: implementation
Created: 2026-03-11

## Goal
- Grow the Phase 0 correctness scaffold into the first Phase 1 parser conformance pack with broader compile-path coverage and richer parser diagnostics reporting.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/parser_matrix.json`
- `tests/conformance/test_correctness_parser_matrix.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The correctness runner can load and execute a larger parser-focused fixture pack in addition to the Phase 0 smoke manifest.
- The new fixture pack covers multiple syntax-scope construct families, including at least valid compile cases, invalid compile cases, and mirrored `bytes` coverage where parser-visible behavior differs from `str`.
- `reports/correctness/latest.json` publishes parser-focused suite totals beyond the two smoke cases and distinguishes `pass`, `fail`, and `unimplemented` outcomes without overstating current `rebar` support.
- A smoke or unit test regenerates the parser-matrix report path end to end and validates the expanded scorecard shape.

## Constraints
- Keep this task on Layer 1 parser acceptance and diagnostics only; do not expand into pattern-object parity, matching behavior, or broad module helpers.
- Do not hand-wave away diagnostic differences; warning/exception capture should stay explicit and conservative.
- Keep the fixture corpus intentionally small and representative rather than trying to ingest a large upstream suite in one run.

## Notes
- Use `docs/testing/correctness-plan.md` as the primary task spec, especially the Phase 1 parser conformance pack guidance.
- Use `docs/spec/syntax-scope.md` to choose the first construct families and `bytes` deltas to cover.
- Build directly on `RBR-0007`; preserve the existing smoke fixture path and placeholder honesty for unimplemented `rebar` behavior.
