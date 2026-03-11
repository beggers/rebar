# RBR-0016: Expand the correctness harness into a match-behavior pack

Status: ready
Owner: implementation
Created: 2026-03-11

## Goal
- Grow the correctness harness beyond parser/public-surface checks so it can publish the first match-behavior observations for tiny `re` workflows while keeping `rebar` gaps explicit.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/match_behavior_smoke.json`
- `tests/conformance/test_correctness_match_behavior.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The correctness runner can execute a match-behavior fixture pack in addition to the existing parser and public-API manifests.
- The new pack covers a small set of `search`, `match`, and `fullmatch` cases with both success and no-match outcomes, includes at least one mirrored `bytes` case, and records structured baseline observations such as truthiness, spans, and basic group payloads where CPython exposes them.
- `reports/correctness/latest.json` distinguishes parser, public-API, and match-behavior totals without counting scaffold `NotImplementedError` paths as compatibility passes.
- A smoke or unit test regenerates the combined correctness report end to end and validates the expanded scorecard structure.

## Constraints
- Keep this task on tiny Layer 3 match-result smoke coverage only; do not expand into replacement-template parity, large corpus import, or throughput-oriented workloads.
- Do not paper over missing implementation by delegating helper behavior to stdlib `re`; the scorecard must continue to show `rebar` gaps honestly.
- Keep fixture payloads intentionally small so any measured differences stay about observable API behavior, not engine stress.

## Notes
- Use `docs/testing/correctness-plan.md` as the primary task spec, especially the Phase 3 match behavior pack guidance.
- Build on `RBR-0013` and `RBR-0014`; this task should observe the scaffolded module surface and broaden the report, not restate public-API scaffolding in prose.
