# RBR-0314: Replace the parser-through-literal-flag correctness JSON fixtures with Python modules

Status: ready
Owner: architecture-implementation
Created: 2026-03-14

## Goal
- Reduce tracked JSON and simplify the early correctness information flow by replacing the remaining front-of-registry correctness manifests with ordinary Python fixture modules, so the harness and direct scorecard tests stop threading `.json`-specific bootstrap paths through the parser, module-surface, match, and early workflow slices.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/parser_matrix.py`
- `tests/conformance/fixtures/public_api_surface.py`
- `tests/conformance/fixtures/match_behavior_smoke.py`
- `tests/conformance/fixtures/exported_symbol_surface.py`
- `tests/conformance/fixtures/pattern_object_surface.py`
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/conformance/fixtures/collection_replacement_workflows.py`
- `tests/conformance/fixtures/literal_flag_workflows.py`
- `tests/conformance/test_correctness_parser_matrix.py`
- `tests/conformance/test_correctness_public_api_surface.py`
- `tests/conformance/test_correctness_match_behavior.py`
- `tests/conformance/test_correctness_exported_symbol_surface.py`
- `tests/conformance/test_correctness_pattern_object_surface.py`
- `tests/conformance/test_correctness_module_workflow.py`
- `tests/conformance/test_correctness_collection_replacement_workflows.py`
- `tests/conformance/test_correctness_literal_flag_workflows.py`
- `tests/conformance/test_correctness_grouped_match_workflows.py`
- Delete `tests/conformance/fixtures/parser_matrix.json`
- Delete `tests/conformance/fixtures/public_api_surface.json`
- Delete `tests/conformance/fixtures/match_behavior_smoke.json`
- Delete `tests/conformance/fixtures/exported_symbol_surface.json`
- Delete `tests/conformance/fixtures/pattern_object_surface.json`
- Delete `tests/conformance/fixtures/module_workflow_surface.json`
- Delete `tests/conformance/fixtures/collection_replacement_workflows.json`
- Delete `tests/conformance/fixtures/literal_flag_workflows.json`
- `reports/correctness/latest.json`

## Acceptance Criteria
- `python/rebar_harness/correctness.py` continues to load fixture manifests from both `.json` and `.py` paths through the existing shared validation path; do not add a second loader, generator step, or package-discovery layer for this batch.
- Each of the eight targeted manifests becomes a one-manifest-per-file Python module exposing the same manifest ids, suite ids, defaults, case ids, case ordering, and case payloads that the deleted JSON files previously supplied, and no duplicate JSON copy of those eight manifests remains in the tree.
- The converted manifests preserve the current checkout ids and case counts: `parser-matrix` with `15` cases, `public-api-surface` with `7`, `match-behavior-smoke` with `6`, `exported-symbol-surface` with `10`, `pattern-object-surface` with `6`, `module-workflow-surface` with `10`, `collection-replacement-workflows` with `15`, and `literal-flag-workflows` with `11`.
- `DEFAULT_FIXTURE_PATHS` points at the eight new `.py` files while preserving their current ordering at the front of the default registry before `grouped_match_workflows.py`, so the combined scorecard helpers and fixture inventory keep deriving this early surface from one shared path list instead of another family-specific branch.
- The nine direct scorecard tests listed above point at the Python-backed manifests and preserve their current fixture subsets and case-count contracts: `15` cases for parser only, `22` for parser plus public API, `28` for parser plus public API plus match behavior, `38` through exported symbols, `44` through pattern objects, `54` through module workflow, `69` through collection/replacement, `80` through literal flags, and `86` through grouped-match coverage.
- The regenerated `reports/correctness/latest.json` preserves the existing manifest ordering, manifest ids, suite ids, case counts, aggregate totals, and representative coverage for the targeted manifests except for the fixture path extensions changing from `.json` to `.py`; the combined report remains `86` manifests, `779` total cases, `779` passes, `0` explicit failures, and `0` `unimplemented`.
- The existing verification surface still passes with the Python-backed fixtures, including `tests.conformance.test_combined_correctness_scorecards`, `tests.conformance.test_correctness_fixture_inventory_contract`, `tests.conformance.test_python_fixture_manifest_contract`, and the nine direct scorecard tests in this task's deliverables.
- The live JSON count decreases by exactly `8` relative to the current checkout baseline; in this checkout both `git ls-files '*.json' | wc -l` and `rg --files -g '*.json' | wc -l` start at `25` and should finish at `17`, with `rg --files -g '*.json' | wc -l` as the source of truth if the worker runs in a dirty tree where deleted tracked paths linger in `git ls-files`.

## Constraints
- Keep the scope to the eight correctness manifests and the direct fixture-path tests listed above; do not convert `conditional_group_exists_nested_replacement_workflows.json`, `conditional_group_exists_quantified_alternation_workflows.json`, agent/config/report JSON, or benchmark plumbing in the same run.
- Do not change Rust code, `python/rebar` runtime behavior, or the correctness report schema.
- Prefer simple Python `MANIFEST` modules and the existing shared validation path over generators, codegen, or another fixture DSL.

## Notes
- The runtime dashboard is current in this checkout: both the tracked and live filesystem JSON counts are `25`, so size and verify the burn-down against the live counts rather than assuming an older stale snapshot.
- This is the remaining contiguous front block inside `python/rebar_harness/correctness.py::DEFAULT_FIXTURE_PATHS`; after it lands, only the two isolated late conditional correctness JSON fixtures plus harness/report/config JSON should remain tracked.
