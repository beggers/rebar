# RBR-1113: Collapse published selector contract checks onto shared test support

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining duplicated published-selector contract assertions from the correctness and benchmark test suites by routing the shared selector-registry and published-subset checks through `tests/conftest.py` instead of repeating the same assertion blocks in two large owner files.

## Deliverables
- `tests/conftest.py`
- `tests/python/test_shared_test_support_contract.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Add one or more shared helper surfaces in `tests/conftest.py`, or a strictly smaller equivalent on that existing support path, that cover both of these cross-suite contracts without creating a new support module:
  - validating that declared string selector constants on a module match a selector-registry mapping and do not duplicate values; and
  - validating that a selector-backed published subset resolves to existing `.py` paths under a published full-suite selector in published order, with an optional exact-filename membership check for selectors that intentionally pin a specific subset.
- Extend `tests/python/test_shared_test_support_contract.py` so the new shared helper surface is covered with focused synthetic inputs, including:
  - a success case for the selector-registry alignment contract; and
  - a success case for the published-subset path-order contract that proves published-order filtering is preserved.
- `tests/python/test_fixture_parity_support_contract.py` stops open-coding the duplicated selector-contract blocks and uses the shared helper surface instead for:
  - `test_shared_correctness_fixture_selectors_resolve_published_paths`;
  - `test_canonical_published_subset_selectors_keep_explicit_membership_contract`; and
  - `test_declared_correctness_fixture_selectors_match_registry_keys`.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` stops open-coding the same selector-contract blocks and uses the shared helper surface instead for:
  - `test_shared_benchmark_manifest_selectors_resolve_published_subset_invariants`;
  - `test_built_native_smoke_manifest_selector_keeps_membership_contract`; and
  - `test_declared_benchmark_manifest_selectors_match_registry_keys`.
- Preserve the existing suite-specific behavior after the cleanup:
  - correctness-specific and benchmark-specific unknown-selector tests stay local and still assert their current error text;
  - full-suite inventory/order tests stay local and still cover their current roots and tracked path inventories; and
  - selector-parametrization coverage does not narrow or change membership.
- Keep the cleanup structural and limited to the four files above. Do not widen it into harness implementation code, reports, README text, or tracked project-state prose.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_shared_test_support_contract.py tests/python/test_fixture_parity_support_contract.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n 'declared_selectors = declared_string_constants_by_suffix\\(|expected_ordered_subset = tuple\\(|published_ordered_subset = tuple\\(' tests/python/test_fixture_parity_support_contract.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Reuse `tests/conftest.py` as the shared-support home; do not add a new helper module or another selector abstraction layer.
- Prefer parameterized helper inputs over registry-specific branching so the same support path can serve correctness and benchmark selector checks without encoding harness-specific knowledge.
- Keep the task focused on deleting repeated contract assertions, not on changing selector registries, file inventories, or harness behavior.

## Notes
- `RBR-1113` is the next available unreserved task id in this checkout:
  - the highest live task id across `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, and `ops/tasks/blocked/` is `1112`; and
  - `rg -n 'RBR-1113|RBR-1114|RBR-1115|RBR-1116|RBR-1117' ops/state/backlog.md ops/state/current_status.md` returned no reserved future ids in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete and current in both tracked and live views for this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest runtime cycle shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled post-task refresh path.
- The remaining duplication is concrete in the live checkout:
  - `tests/python/test_fixture_parity_support_contract.py:1268-1293` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py:11266-11282` still open-code the published-subset path-order assertions;
  - `tests/python/test_fixture_parity_support_contract.py:1311-1325` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py:11292-11302` still open-code the explicit selector-membership checks; and
  - `tests/python/test_fixture_parity_support_contract.py:1353-1362` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py:11325-11334` still open-code the declared-selector-registry alignment assertions.
- The focused verification slice is green in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_shared_test_support_contract.py tests/python/test_fixture_parity_support_contract.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` returned `1144 passed, 3 skipped, 1743 subtests passed` in this run.
- The negative `rg` verification currently fails exactly on the duplicated selector-contract boilerplate above, so it is an acceptance check for this cleanup rather than unrelated repo drift.
