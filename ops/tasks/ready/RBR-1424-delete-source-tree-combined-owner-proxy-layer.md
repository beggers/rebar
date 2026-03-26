## RBR-1424: Delete the source-tree-combined owner proxy layer

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the suite-local `_SourceTreeSupportProxy` wrapper from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- The combined benchmark suite still routes both suite-owned names and shared `benchmark_test_support` names through a synthetic `source_tree_support` namespace, and `tests/benchmarks/benchmark_test_support.py` plus `tests/benchmarks/test_benchmark_test_support.py` still carry helper/test plumbing that exists only to validate that proxy.
- Keep the suite on one explicit boundary instead: shared helpers stay on the `benchmark_test_support` module alias, and suite-owned definitions stay local module names.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/benchmark_test_support.py`

## Acceptance Criteria
- Remove `_SourceTreeSupportProxy` and the `source_tree_support = _SourceTreeSupportProxy()` assignment from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Rewrite the combined suite so it no longer depends on the synthetic `source_tree_support` namespace:
  - suite-owned dataclasses, expectation registries, and helper functions should be referenced directly as local names
  - genuinely shared helpers and constants should be referenced through the existing `benchmark_test_support` module alias
- Delete the shared-support route checker that exists only for the proxy boundary:
  - `_assert_source_tree_combined_routes_owner_names_through_module_alias(...)` should be removed from `tests/benchmarks/benchmark_test_support.py`
- Replace the proxy-specific tests in `tests/benchmarks/test_benchmark_test_support.py` with direct-boundary assertions that verify:
  - the combined suite no longer defines `_SourceTreeSupportProxy` or `source_tree_support`
  - proxy-specific route-helper tests are gone
  - the combined suite still imports shared support through `benchmark_test_support`
  - the combined suite still owns the rehomed source-tree-combined expectation/contract surface locally
- Keep the task bounded to deleting this wrapper/routing layer only; do not reopen workload manifests, `python/rebar_harness/benchmarks.py`, reporting/state files, or unrelated benchmark-owner cleanup.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'source_tree_combined or source_tree_support_proxy'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n 'class _SourceTreeSupportProxy|^source_tree_support = _SourceTreeSupportProxy\\(|^def _assert_source_tree_combined_routes_owner_names_through_module_alias\\(|test_source_tree_support_proxy_|test_source_tree_combined_routing_helpers_live_on_shared_support|test_source_tree_combined_route_helper_' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py"`
- `bash -lc "! rg -n '\\bsource_tree_support\\.' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Notes
- Queue and JSON check in this planning run:
  - `.rebar/runtime/dashboard.md` reported `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the runtime JSON counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1424|RBR-1425|RBR-1426" ops/state/current_status.md ops/state/backlog.md ops/tasks || true` returned only historical done-task mentions; there was no planning-owned reservation for `RBR-1424`.
- Candidate selection in this run:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still defines `_SourceTreeSupportProxy` and then references hundreds of local and shared names through `source_tree_support.*`, even though the suite already imports `benchmark_test_support` directly and now owns its private `_SourceTree*` surface locally.
  - `tests/benchmarks/benchmark_test_support.py` still carries `_assert_source_tree_combined_routes_owner_names_through_module_alias(...)` only to validate that synthetic proxy boundary.
  - `tests/benchmarks/test_benchmark_test_support.py` still spends dedicated tests on the proxy and route helper instead of the simpler direct module boundary.
  - That makes this a bounded post-JSON architectural deletion with shared payoff: remove one entire wrapper/routing layer rather than continuing to preserve a bespoke owner-support namespace.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'source_tree_combined or source_tree_support_proxy'` passed with `320 passed, 169 deselected, 1573 subtests passed in 13.19s`.
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'source_tree_support_proxy or source_tree_combined_routes_owner_names_through_module_alias or source_tree_combined_suite_owns_rehomed_manifest_expectation_surface'` passed with `3 passed, 486 deselected in 0.25s`.
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed.
  - `bash -lc "rg -n 'class _SourceTreeSupportProxy|^source_tree_support = _SourceTreeSupportProxy\\(|_assert_source_tree_combined_routes_owner_names_through_module_alias|source_tree_support_proxy' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py"` currently finds the exact proxy/routing layer this task deletes.
