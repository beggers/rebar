## RBR-1377: Delete standard inventory assertion wrappers

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the two thin shared standard-inventory assertion wrappers from the benchmark-support test helper layer, and rewrite the affected benchmark-support tests to assert the expected definition order and identity directly where those expectations already live.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Acceptance Criteria
- Delete these shared wrapper helpers from `tests/benchmarks/benchmark_test_support.py` without moving them sideways or replacing them with another generic helper:
  - `assert_standard_inventory_reuses_owner_definitions`
  - `select_standard_inventory_definitions`
- Rewrite the affected benchmark-support tests to keep the same structural guarantees through direct targeted assertions rather than through those shared wrappers. Preserve these boundaries explicitly:
  - the pattern-boundary, collection-replacement, and source-tree owner definition tuples still prove their exact definition-name order against the shared `STANDARD_BENCHMARK_DEFINITIONS` inventory;
  - those owner definition tuples still prove identity reuse against the corresponding entries or slices from the shared standard inventory rather than merely rechecking names;
  - `tests/benchmarks/test_benchmark_test_support.py` no longer keeps helper-specific behavior tests for wrapper functions that no longer exist, but it still covers the surviving direct owner/shared inventory contract precisely enough to catch reordered or copied definitions.
- Do not change benchmark manifests, workload selection, benchmark execution behavior, or tracked project-state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `bash -lc "! rg -n '\\b(select_standard_inventory_definitions|assert_standard_inventory_reuses_owner_definitions)\\b' tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py"`

## Constraints
- Prefer deleting the wrappers over recreating them under new names or replacing them with another shared assertion layer.
- Keep the run bounded to this standard-inventory wrapper cleanup in the benchmark-support tests.

## Notes
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1377|RBR-1378|RBR-1379' ops/state/current_status.md ops/state/backlog.md` returned no matches in this run
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate selection in this run:
  - Candidate 1 was the local `_collection_routed_owner_assignment_names()` helper in `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`, but it was too single-file and too naming-local to justify the post-JSON architecture slot.
  - `assert_standard_inventory_reuses_owner_definitions()` and `select_standard_inventory_definitions()` are shared wrappers in `tests/benchmarks/benchmark_test_support.py`, but their current behavior is only thin tuple name/order and object-identity checking already owned by the benchmark-support test modules that call them.
  - Current call sites are bounded to `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`, `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`, and `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`, with helper-specific coverage in `tests/benchmarks/test_benchmark_test_support.py`.
  - Removing those wrappers shrinks one shared test-helper layer after the JSON burn-down without touching runtime harness behavior or benchmark publications.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed with `451 passed in 3.22s`
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed
