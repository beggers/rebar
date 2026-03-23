# RBR-1115: Collapse published inventory contracts onto shared test support

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining duplicated published-inventory contract assertions from the correctness and benchmark suites by routing their shared manifest-to-child inventory checks through `tests/conftest.py` instead of repeating the same uniqueness and membership logic in two owner files.

## Deliverables
- `tests/conftest.py`
- `tests/python/test_shared_test_support_contract.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Add one shared helper surface in `tests/conftest.py`, or a strictly smaller equivalent on that existing support path, that covers the cross-suite published-inventory contract both owner files currently restate:
  - unique top-level manifest ids for a published manifest collection;
  - unique child ids for the nested records attached to those manifests;
  - every published manifest owns at least one nested record; and
  - every nested record points back to one of the loaded published manifest ids.
- The shared helper must stay generic enough to support both suites without encoding correctness- or benchmark-specific selector names, fixture paths, or manifest ids, while still allowing the correctness suite to keep its extra `suite_id` uniqueness assertion on the same shared path rather than in a second open-coded block.
- Extend `tests/python/test_shared_test_support_contract.py` so the new shared helper surface is covered with focused synthetic inputs, including:
  - a success case for the generic manifest-to-child inventory contract; and
  - a success case that proves the optional extra top-level uniqueness check covers an additional field such as `suite_id`.
- `tests/python/test_fixture_parity_support_contract.py` stops open-coding the duplicated inventory contract inside `test_default_fixture_inventory_has_unique_manifest_suite_and_case_ids` and uses the shared helper surface instead for:
  - unique manifest ids;
  - unique `suite_id` values;
  - unique case ids; and
  - case-to-manifest coverage or nonempty-manifest assertions.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` stops open-coding the same inventory contract inside `test_default_benchmark_published_manifest_inventory_has_unique_manifest_and_workload_ids` and uses the shared helper surface instead for:
  - unique manifest ids;
  - unique workload ids; and
  - workload-to-manifest coverage or nonempty-manifest assertions.
- Preserve the existing suite-specific behavior after the cleanup:
  - the correctness suite still checks `suite_id` uniqueness;
  - the benchmark suite does not gain correctness-only invariants; and
  - both suites keep their current published loader, manifest inventory, and id membership expectations unchanged.
- Keep the cleanup structural and limited to the four files above. Do not widen it into harness implementation code, reports, README text, or tracked project-state prose.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_shared_test_support_contract.py tests/python/test_fixture_parity_support_contract.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n 'duplicate_items\\(Counter\\(manifest\\.manifest_id|duplicate_items\\(Counter\\(case\\.case_id|duplicate_items\\(Counter\\(workload\\.workload_id|cases_by_manifest = Counter\\(|workloads_by_manifest = Counter\\(' tests/python/test_fixture_parity_support_contract.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Reuse `tests/conftest.py` as the shared-support home; do not add a new support module or another detached inventory abstraction layer.
- Prefer a helper API driven by callables or attribute names over suite-specific branching so the same support path can validate both fixture-case and workload inventories.
- Keep the task focused on deleting repeated inventory assertions, not on changing selector registries, published manifest contents, or harness behavior.

## Notes
- `RBR-1115` is the next available unreserved task id in this checkout:
  - the highest live task id across `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, and `ops/tasks/blocked/` is `1114`; and
  - `rg -n 'RBR-1115|RBR-1116|RBR-1117|RBR-1118|RBR-1119' ops/state/backlog.md ops/state/current_status.md` returned no reserved future ids in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete and current in both tracked and live views for this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest runtime cycle shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled post-task refresh path.
- The remaining duplication is concrete in the live checkout:
  - `tests/python/test_fixture_parity_support_contract.py:1588-1596` still open-codes manifest-id uniqueness, case-id uniqueness, and case-to-manifest coverage checks for the published correctness inventory; and
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py:11729-11735` still open-codes the same manifest/workload uniqueness and workload-to-manifest coverage checks for the published benchmark inventory.
- The focused verification slice is green in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_shared_test_support_contract.py tests/python/test_fixture_parity_support_contract.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` returned `1151 passed, 3 skipped, 1743 subtests passed` in this run.
- The negative `rg` verification currently fails exactly on the duplicated inventory boilerplate above, so it is an acceptance check for this cleanup rather than unrelated repo drift.

## Completion
- Added `assert_published_manifest_inventory_contract()` to `tests/conftest.py` so shared published-manifest inventory checks now cover unique manifest ids, optional extra top-level uniqueness fields, unique child ids, nonempty manifest coverage, and child-to-manifest membership through one generic helper surface.
- Extended `tests/python/test_shared_test_support_contract.py` with focused synthetic success coverage for the base manifest-to-child inventory contract and for the optional extra uniqueness-field path used by the correctness suite.
- Routed the duplicated published inventory assertions in `tests/python/test_fixture_parity_support_contract.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` through the shared helper without changing their existing published loader or manifest expectations.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_shared_test_support_contract.py tests/python/test_fixture_parity_support_contract.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` (`1153 passed, 3 skipped, 1743 subtests passed`) and `bash -lc "! rg -n 'duplicate_items\\(Counter\\(manifest\\.manifest_id|duplicate_items\\(Counter\\(case\\.case_id|duplicate_items\\(Counter\\(workload\\.workload_id|cases_by_manifest = Counter\\(|workloads_by_manifest = Counter\\(' tests/python/test_fixture_parity_support_contract.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`.
