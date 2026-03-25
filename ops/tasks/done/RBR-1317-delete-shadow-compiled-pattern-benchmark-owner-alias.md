# RBR-1317: Delete shadow compiled-pattern benchmark owner alias

Status: done
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Delete the shadow `compiled_pattern_module_helper_support` alias layer from the benchmark contract consumers so they reference `tests/benchmarks/benchmark_test_support.py` through one explicit owner import instead of rebinding the same owner module under a fake sub-owner name.

## Deliverables
- `tests/benchmarks/test_benchmark_manifest_validation.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Replace `from tests.benchmarks import benchmark_test_support as compiled_pattern_module_helper_support` in these consumer suites with one explicit owner import that matches the real module boundary:
  - `tests/benchmarks/test_benchmark_manifest_validation.py`
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `tests/benchmarks/test_benchmark_test_support.py`
- Update those suites to reference the compiled-pattern helper surface through the chosen owner module import instead of the shadow alias name, including the compiled-pattern success owner specs, wrong-text-model helpers, keyword-contract helpers, and shared manifest-path constants they already consume from `tests/benchmarks/benchmark_test_support.py`.
- Keep the owner boundary explicit in `tests/benchmarks/test_benchmark_test_support.py`:
  - rewrite the consumer-ownership assertions so they prove the consumer suites import `tests.benchmarks.benchmark_test_support` without binding a local `compiled_pattern_module_helper_support` alias
  - preserve the deleted-wrapper/import-absence coverage for the removed historical helper modules
- Do not add a replacement compatibility alias, helper module, or re-export shim. The point is to make `tests/benchmarks/benchmark_test_support.py` the only visible owner, not to rename it again inside the consumer layer.
- Keep this cleanup structural:
  - do not move compiled-pattern helper definitions out of `tests/benchmarks/benchmark_test_support.py`
  - do not change benchmark workload manifests, runtime harness behavior, scorecard contents, README text, or tracked `ops/state/` prose

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_contract_consumer_suites_reuse_shared_support_without_local_duplicates or benchmark_test_support_owns_compiled_pattern_module_success_surface or deleted_compiled_pattern_module_helper_support_stays_unimportable_and_unreferenced'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n 'benchmark_test_support as compiled_pattern_module_helper_support' tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep the cleanup bounded to owner-boundary/import-plumbing simplification in the benchmark contract suites.
- Prefer deleting the shadow alias over broad renaming or another support-layer reshuffle.

## Notes
- `RBR-1317` is the next available unreserved task id in this checkout:
  - `rg -n 'RBR-1317|RBR-1318|RBR-1319' ops/state/current_status.md ops/state/backlog.md` returned no matches in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f \( -name 'RBR-1317*' -o -name 'RBR-1318*' -o -name 'RBR-1319*' \) | sort` returned no matches before this task was queued.
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
- Queue/runtime state was not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready tasks, no blocked tasks, and no ready `feature-implementation` work
  - the latest runtime dashboard shows the most recent `architecture-implementation` run finishing `done` and no inherited-dirty, refresh, or commit anomaly
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/test_benchmark_manifest_validation.py`
  - `tests/benchmarks/test_benchmark_test_support.py`
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - each still imports `tests.benchmarks.benchmark_test_support` as `compiled_pattern_module_helper_support`, creating a consumer-local shadow owner name for symbols that already live directly on `tests/benchmarks/benchmark_test_support.py`
  - `tests/benchmarks/test_benchmark_test_support.py` currently encodes that alias as part of the ownership contract, so the alias boundary is now durable architecture drift rather than a one-off local style issue
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_contract_consumer_suites_reuse_shared_support_without_local_duplicates or benchmark_test_support_owns_compiled_pattern_module_success_surface or deleted_compiled_pattern_module_helper_support_stays_unimportable_and_unreferenced'` passed with `4 passed, 104 deselected in 0.28s`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed with `343 tests collected in 0.10s`
  - `bash -lc "! rg -n 'benchmark_test_support as compiled_pattern_module_helper_support' tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently fails because all three consumer suites still bind that shadow alias, and that failure belongs exactly to this cleanup.
- 2026-03-25T16:44:00+00:00: landed by deleting the consumer-local `compiled_pattern_module_helper_support` alias from the three benchmark suites, switching the two consumer modules to import `tests.benchmarks.benchmark_test_support` under its real owner name, and tightening `tests/benchmarks/test_benchmark_test_support.py` so it now requires `benchmark_test_support` to be imported from `tests.benchmarks` and rejects any reintroduced `compiled_pattern_module_helper_support` binding.
- Verification:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_contract_consumer_suites_reuse_shared_support_without_local_duplicates or benchmark_test_support_owns_compiled_pattern_module_success_surface or deleted_compiled_pattern_module_helper_support_stays_unimportable_and_unreferenced'` -> `4 passed, 104 deselected in 0.38s`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` -> `343 tests collected in 0.20s`
  - `bash -lc "! rg -n 'benchmark_test_support as compiled_pattern_module_helper_support' tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` -> passed
