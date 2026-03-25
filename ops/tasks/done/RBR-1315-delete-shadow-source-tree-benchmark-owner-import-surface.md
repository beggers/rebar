## RBR-1315: Delete shadow source-tree benchmark owner import surface

Status: done
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Delete the giant shadow import surface in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the suite uses `tests/benchmarks/source_tree_benchmark_anchor_support.py` through one explicit module owner instead of rebinding that owner's exported functions, constants, dataclasses, and expectation tables through five direct `from ... import ...` blocks.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Acceptance Criteria
- Replace the direct `from tests.benchmarks.source_tree_benchmark_anchor_support import ...` import wall in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` with one explicit owner import, for example `from tests.benchmarks import source_tree_benchmark_anchor_support as source_tree_support`.
- Update the combined benchmark suite to reference the moved owner surface through that module import instead of shadowing the owner API locally:
  - source-tree manifest-path constants
  - moved dataclasses and expectation tables
  - helper functions such as `source_tree_scorecard_case(...)`, `source_tree_combined_case(...)`, `select_source_tree_combined_slice_rows(...)`, and the shared benchmark-contract assertions
- Do not replace the removed `from ... import ...` blocks with a second alias layer or compatibility wrapper. The point is to make the support module the single visible owner, not to rename the owner API inside the consumer suite.
- Keep the cleanup structural:
  - do not move definitions out of `tests/benchmarks/source_tree_benchmark_anchor_support.py`
  - do not change benchmark workload manifests, runtime harness behavior, scorecard contents, or tracked `ops/state/` prose
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` to keep the owner boundary explicit after the cleanup:
  - preserve the moved-surface ownership assertions already in that file
  - add or update an AST-level check that `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer contains `ImportFrom` statements targeting `tests.benchmarks.source_tree_benchmark_anchor_support`

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'former_owner_modules_share_source_tree_helpers_without_local_duplicates or source_tree_support_module_exposes_moved_combined_case_surface or source_tree_owner_builders_reference_owner_manifest_path_constants'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n '^from tests\\.benchmarks\\.source_tree_benchmark_anchor_support import ' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep this cleanup bounded to the owner-boundary/import-plumbing layer between the source-tree benchmark support module and the combined benchmark suite.
- Prefer deleting the shadow consumer import surface over adding another indirection helper, local alias table, or re-export shim.

## Notes
- `RBR-1315` is the next available unreserved task id in this checkout:
  - `rg -n 'RBR-1315|RBR-1316|RBR-1317' ops/state/current_status.md ops/state/backlog.md` returned no matches in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f \( -name 'RBR-1315*' -o -name 'RBR-1316*' -o -name 'RBR-1317*' \) | sort` returned no matches before this task was queued.
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
- Queue/runtime state was not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reported a clean worktree, no ready tasks, no blocked tasks, and the most recent `architecture-implementation` run finished `done`
  - the latest runtime dashboard showed no inherited-dirty, refresh, or commit anomaly
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still carries five direct `from tests.benchmarks.source_tree_benchmark_anchor_support import ...` statements at the top of the file
  - those import walls mirror a large owner surface from `tests/benchmarks/source_tree_benchmark_anchor_support.py`, so the consumer suite effectively acts as a second binding layer for the same API
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'former_owner_modules_share_source_tree_helpers_without_local_duplicates or source_tree_support_module_exposes_moved_combined_case_surface or source_tree_owner_builders_reference_owner_manifest_path_constants'` passed with `3 passed, 45 deselected in 0.11s`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed with `279 tests collected in 0.09s`
  - `bash -lc "! rg -n '^from tests\\.benchmarks\\.source_tree_benchmark_anchor_support import ' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently fails because the combined suite still contains the shadow direct-import surface, and that failure belongs exactly to this cleanup.

## Completion Notes
- Replaced the five direct `from tests.benchmarks.source_tree_benchmark_anchor_support import ...` statements in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` with one owner-module import: `from tests.benchmarks import source_tree_benchmark_anchor_support as source_tree_support`.
- Updated the combined benchmark suite to reference source-tree manifest constants, dataclasses, expectation tables, helper builders, and contract assertions through `source_tree_support.*` instead of rebinding the owner surface locally.
- Added an AST-level regression check in `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` that asserts the combined suite no longer contains `ImportFrom` nodes targeting `tests.benchmarks.source_tree_benchmark_anchor_support` and instead imports the owner through `tests.benchmarks`.
- Verification completed in this run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'former_owner_modules_share_source_tree_helpers_without_local_duplicates or source_tree_support_module_exposes_moved_combined_case_surface or source_tree_owner_builders_reference_owner_manifest_path_constants or combined_suite_imports_source_tree_support_through_owner_module_only'` passed with `4 passed, 45 deselected in 0.20s`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed with `279 tests collected in 0.16s`
  - `bash -lc "! rg -n '^from tests\\.benchmarks\\.source_tree_benchmark_anchor_support import ' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` passed
