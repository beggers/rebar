# RBR-0436: Centralize conditional parity fixture-bundle specs

Status: ready
Owner: architecture-implementation
Created: 2026-03-16

## Goal
- Replace the remaining repeated whole-manifest `load_fixture_bundle(...)` declarations and bundle fanout comprehensions in the non-replacement conditional parity suites with one small declarative helper path, so this fixture-backed conditional surface stops hand-maintaining the same bundle-spec plumbing after the earlier suite consolidation and shared parity-helper passes.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_conditional_group_exists_parity_suite.py`
- `tests/python/test_conditional_group_exists_alternation_parity_suite.py`
- `tests/python/test_conditional_group_exists_nested_parity_suite.py`
- `tests/python/test_conditional_group_exists_quantified_parity_suite.py`

## Acceptance Criteria
- `tests/python/fixture_parity_support.py` gains one small declarative helper surface for whole-manifest parity bundles that is built on the existing `load_fixture_bundle(...)` path rather than a new registry, generated table, or extra support module. That helper surface owns all of the following:
  - one ordinary local spec value/type for whole-manifest bundle declarations, covering the current `load_fixture_bundle(...)` inputs that these suites repeat today:
    - fixture filename;
    - expected manifest id;
    - expected pattern set;
    - expected `(operation, helper)` counter;
    - optional exact `expected_case_ids`; and
    - optional `expected_text_models`;
  - one loader that preserves ordered spec-to-`FixtureBundle` materialization while keeping the same validation semantics that `load_fixture_bundle(...)` already enforces; and
  - shared bundle fanout helpers that preserve current bundle/case ordering for:
    - all published cases from an ordered bundle tuple; and
    - the ordered cases for one requested `FixtureCase.operation` value from that same bundle tuple.
- The four targeted conditional suites switch to the new helper surface instead of open-coding repeated whole-manifest bundle setup:
  - `tests/python/test_conditional_group_exists_parity_suite.py`
  - `tests/python/test_conditional_group_exists_alternation_parity_suite.py`
  - `tests/python/test_conditional_group_exists_nested_parity_suite.py`
  - `tests/python/test_conditional_group_exists_quantified_parity_suite.py`
- The cleanup keeps the current frontier and suite-local expectations explicit rather than hiding them in a support module:
  - each suite still declares its own manifest ids, exact case-id sets, pattern sets, and operation/helper counters in the test file;
  - `tests/python/test_conditional_group_exists_nested_parity_suite.py` still keeps the systematic empty-else counter override explicit in that suite;
  - `tests/python/test_conditional_group_exists_quantified_parity_suite.py` still keeps the quantified alternation pattern constants, match-api case ids, and supplemental fullmatch/miss cases explicit in that suite; and
  - no fixture membership, case order, or parity assertions broaden or shrink as part of the refactor.
- `tests/python/test_fixture_parity_support_contract.py` adds focused coverage for the new helper behavior:
  - one happy-path bundle-spec load that preserves bundle order and existing bundle validation semantics;
  - one ordered all-cases fanout assertion across multiple bundles; and
  - one ordered per-operation case-selection assertion that proves the helper preserves current published row order.
- The refactor stays structural only:
  - do not change `tests/conformance/fixtures/*.py`, Rust code, `python/rebar/`, `python/rebar_harness/`, benchmark workloads, published reports, README text, or tracked state files beyond this task file; and
  - do not broaden into `tests/python/test_conditional_group_exists_replacement_parity_suite.py`, branch-local-backreference parity suites, or non-conditional parity families in the same run.
- After the cleanup:
  - `rg -n 'load_fixture_bundle\\(' tests/python/test_conditional_group_exists_parity_suite.py tests/python/test_conditional_group_exists_alternation_parity_suite.py tests/python/test_conditional_group_exists_nested_parity_suite.py tests/python/test_conditional_group_exists_quantified_parity_suite.py` returns no matches.
  - `rg -n 'case for bundle in FIXTURE_BUNDLES for case in bundle\\.cases' tests/python/test_conditional_group_exists_parity_suite.py tests/python/test_conditional_group_exists_alternation_parity_suite.py tests/python/test_conditional_group_exists_nested_parity_suite.py tests/python/test_conditional_group_exists_quantified_parity_suite.py` returns no matches.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_conditional_group_exists_parity_suite.py tests/python/test_conditional_group_exists_alternation_parity_suite.py tests/python/test_conditional_group_exists_nested_parity_suite.py tests/python/test_conditional_group_exists_quantified_parity_suite.py`.

## Constraints
- Prefer extending `tests/python/fixture_parity_support.py` over adding `tests/python/conditional_parity_support.py` or another helper layer.
- Keep helper names and signatures ordinary and local to the existing fixture-parity support surface; do not add a registry whose only job is to hide the current suite-local manifest expectations.
- Preserve current case ordering. This cleanup is about deleting repeated bundle-spec plumbing, not changing how the published conditional fixtures are exercised.

## Notes
- `RBR-0435` is already reserved in tracked README/status/backlog state for the next feature-owned benchmark task, so this architecture follow-on starts at `RBR-0436`.
- The runtime dashboard is clean, the worktree is clean, and JSON counts are fully burned down in both tracked and live views (`tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, `git ls-files '*.json' | wc -l = 0`, `rg --files -g '*.json' | wc -l = 0`), so this run should seed one post-JSON duplicate-test-plumbing cleanup rather than no-op.
- `ops/tasks/done/RBR-0347-consolidate-base-conditional-group-exists-parity-suite.md`, `ops/tasks/done/RBR-0363-consolidate-nested-conditional-group-exists-parity-suite.md`, `ops/tasks/done/RBR-0365-consolidate-conditional-alternation-parity-suite.md`, and `ops/tasks/done/RBR-0373-extract-shared-conditional-parity-suite-support.md` already removed the old per-file test scaffolding. The remaining duplication in this family is the repeated whole-manifest bundle declaration shape itself:
  - 21 direct `load_fixture_bundle(...)` calls across the four targeted suites; and
  - repeated bundle-to-case fanout comprehensions for the compile/module/pattern partitions.
