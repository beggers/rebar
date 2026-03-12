# RBR-0033: Publish correctness coverage for literal-only flag behavior

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the correctness harness so bounded literal-only flag-sensitive behavior reaches the published scorecard immediately after `IGNORECASE` support lands.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/literal_flag_workflows.json`
- `tests/conformance/test_correctness_literal_flag_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The correctness runner can execute a literal-flag workflow manifest alongside the existing parser, public-API, match-behavior, exported-symbol, pattern-object, module-workflow, and collection/replacement manifests without breaking the current report schema.
- The new pack covers representative literal-only `IGNORECASE` workflows for module helpers and compiled `Pattern` methods across both `str` and `bytes`, including tiny success and no-match observations plus cache-distinct compile behavior where relevant.
- `reports/correctness/latest.json` distinguishes the new flag-sensitive cases from the earlier workflow packs and keeps unsupported inline-flag, locale, or non-literal flag paths explicit instead of counting them as passes.
- A smoke or unit test regenerates the combined correctness report end to end and validates the expanded scorecard structure.

## Constraints
- Keep this task on tiny literal-only flag-sensitive workflows only; do not broaden into inline-flag parser parity, character-class flag semantics, or general regex-engine coverage.
- Preserve the exact-baseline metadata and the existing multi-manifest scorecard shape rather than inventing a separate reporting branch.
- Do not delegate the flag-sensitive workflows to stdlib `re`; the scorecard must continue to expose real `rebar` behavior and remaining gaps honestly.

## Notes
- Build on `RBR-0032`. This task exists so the first supported flag behavior becomes visible in the published correctness report immediately instead of living only in unit tests.
