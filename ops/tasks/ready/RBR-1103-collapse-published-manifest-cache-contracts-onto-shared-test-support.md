# RBR-1103: Collapse published manifest cache contracts onto shared test support

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the duplicated published-manifest cache/order contract logic currently embedded in `tests/python/test_fixture_parity_support_contract.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving that shared assertion flow onto the existing repo-wide test support surface instead of keeping two owner-local copies of the same harness-publication behavior.

## Deliverables
- `tests/conftest.py`
- `tests/python/test_shared_test_support_contract.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Add one shared helper surface in `tests/conftest.py`, or a strictly smaller equivalent on the existing shared test-support path, that covers the common published-helper contract both owners currently restate:
  - the published helper returns a cached object on repeated calls;
  - the returned manifest/fixture path order matches the current requested default order; and
  - clearing the cache forces one reload from the current default path or selector source.
- `tests/python/test_fixture_parity_support_contract.py` stops carrying bespoke cache-reload/order assertion plumbing for:
  - `published_fixture_manifests()` preserving `DEFAULT_FIXTURE_PATHS`; and
  - `published_fixture_manifests.cache_clear()` reloading the current `DEFAULT_FIXTURE_PATHS`.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` stops carrying bespoke cache-reload/order assertion plumbing for:
  - `published_benchmark_manifests()` preserving `select_benchmark_manifest_paths(PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR)` order; and
  - `published_benchmark_manifests.cache_clear()` reloading the current selector result.
- Keep the owner-specific checks that are not actually shared in their current owner files:
  - correctness-side manifest/suite/case uniqueness assertions remain in `tests/python/test_fixture_parity_support_contract.py`; and
  - benchmark-side manifest/workload uniqueness assertions remain in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Cover the new shared helper behavior in `tests/python/test_shared_test_support_contract.py`.
- Keep the cleanup structural and limited to test support plus the two test owners above. Do not edit `python/rebar_harness/`, benchmark workload modules, correctness fixture modules, reports, README copy, or tracked state prose.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_shared_test_support_contract.py tests/python/test_fixture_parity_support_contract.py::test_default_fixture_inventory_has_unique_manifest_suite_and_case_ids tests/python/test_fixture_parity_support_contract.py::test_published_fixture_manifests_cache_clear_reloads_current_default_fixture_paths tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::test_default_benchmark_published_manifest_helper_is_cached_and_preserves_selector_order tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::test_published_benchmark_manifests_cache_clear_reloads_current_default_selector`

## Constraints
- Prefer extending the existing shared test-support surface in `tests/conftest.py` over adding a new support module, registry, or detached abstraction tier.
- Preserve the current public-helper coverage surface and exact default-order semantics for both harnesses.
- Do not redesign selector names, published subset membership, cache decorators, or manifest-loading behavior in `python/rebar_harness/correctness.py` or `python/rebar_harness/benchmarks.py`.

## Notes
- `RBR-1103` is the next available unreserved task id in this checkout:
  - the highest live task id across `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, and `ops/tasks/blocked/` is `1102`; and
  - `rg -n 'RBR-1103|RBR-1104|RBR-1105|RBR-1106|RBR-1107' ops/state/current_status.md ops/state/backlog.md` returned no reserved future ids in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete and current in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest runtime cycle shows both task workers completing `done`, with no inherited-dirty checkpoint churn or stalled refresh path.
- The simplification target is concrete in the live checkout:
  - `tests/python/test_fixture_parity_support_contract.py:1571` and `tests/python/test_fixture_parity_support_contract.py:2198` encode correctness-side published-helper cache/order assertions today; and
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py:11281` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py:11291` encode the benchmark-side copy of the same contract today.
- The focused verification slice is green in the live checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py::test_default_fixture_inventory_has_unique_manifest_suite_and_case_ids tests/python/test_fixture_parity_support_contract.py::test_published_fixture_manifests_cache_clear_reloads_current_default_fixture_paths tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::test_default_benchmark_published_manifest_helper_is_cached_and_preserves_selector_order tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::test_published_benchmark_manifests_cache_clear_reloads_current_default_selector` returned `4 passed` in this run.
