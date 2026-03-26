## RBR-1393: Delete the global standard benchmark definition aggregate

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove the remaining cross-owner aggregate in `tests/benchmarks/benchmark_test_support.py` where the module imports `collection_replacement_benchmark_anchor_support` and `source_tree_benchmark_anchor_support` only to concatenate owner-owned tuples into `STANDARD_BENCHMARK_DEFINITIONS`. The owner modules already expose their own `*_STANDARD_BENCHMARK_DEFINITIONS`, so shared benchmark support should stop routing a repo-wide benchmark-definition inventory through one global tuple.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Acceptance Criteria
- Delete `STANDARD_BENCHMARK_DEFINITIONS` from `tests/benchmarks/benchmark_test_support.py` and remove the owner-module imports at the bottom of that file that exist only to feed the deleted aggregate.
- Delete or rewrite `_standard_benchmark_manifest_params`, `_standard_benchmark_definition_params`, and `_standard_benchmark_special_unanchored_result_parity_params` so they no longer close over a shared cross-owner definition inventory inside `tests/benchmarks/benchmark_test_support.py`. If any replacement helper remains, it must take an explicit caller-owned definition tuple rather than rebuilding another hidden global aggregate.
- Rewrite the consuming tests so owner-local assertions stay owner-local: `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`, `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`, and `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` should assemble any needed combined definition inventory explicitly from the owner exports and the benchmark-test-support-owned definition tuples instead of reading `benchmark_test_support.STANDARD_BENCHMARK_DEFINITIONS`.
- Rewrite `tests/benchmarks/test_benchmark_test_support.py` so it no longer asserts the existence or AST shape of `STANDARD_BENCHMARK_DEFINITIONS`, and instead verifies the post-cleanup explicit inventory shape without reintroducing another benchmark-support-global aggregator.
- Do not replace the deleted tuple with another owner-neutral wrapper such as `_build_standard_benchmark_definitions()`, `ALL_STANDARD_BENCHMARK_DEFINITIONS`, or another cross-owner inventory exported from `tests/benchmarks/benchmark_test_support.py`.
- Do not change benchmark workload definitions, manifest contents, benchmark execution behavior, generated reports, or tracked project-state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'grouped_callable_anchor_contract_in_combined_suite_uses_owner_helpers or collection_replacement_standard_definitions_are_reused_by_standard_inventory'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py -k 'pattern_boundary_standard_definitions_are_owner_owned_in_exact_order or pattern_boundary_standard_definitions_are_reused_by_standard_inventory'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_standard_definitions_export_stays_owned_by_source_tree'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `bash -lc "! rg -n 'STANDARD_BENCHMARK_DEFINITIONS|collection_replacement_support\\.COLLECTION_REPLACEMENT_STANDARD_BENCHMARK_DEFINITIONS|source_tree_support\\.SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS' tests/benchmarks/benchmark_test_support.py"`

## Constraints
- Prefer deleting the shared aggregate layer outright over moving it to another helper or another support module.
- Keep the run bounded to this definition-inventory cleanup. Do not widen into source-tree combined-slice expectation refactors, benchmark workload reshaping, or feature work.

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`.
  - `git status --short` was empty in this run, so the runtime counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- ID and duplicate check in this run:
  - `rg -n 'RBR-1393|RBR-1394|RBR-1395' ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done` returned only historical mentions inside completed task notes, with no reserved future-id hit and no ready/in-progress/blocked duplicate for `RBR-1393`.
  - No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate selection in this run:
  - First I checked the remaining `tests/benchmarks/source_tree_benchmark_anchor_support.py` surface after `RBR-1392`; the live cross-file references there are now mostly owner-local suite builders and tests, which is below the post-JSON bar for seeding another architecture task.
  - I then checked `tests/benchmarks/benchmark_test_support.py` and found one remaining shared layer: the module imports `collection_replacement_benchmark_anchor_support` and `source_tree_benchmark_anchor_support` only to build `STANDARD_BENCHMARK_DEFINITIONS`, and the only live references to those imported modules in that file are the two tuple splices at lines 5038 and 5043.
  - That central aggregate still forces multiple owner tests to validate their inventories through a benchmark-support-global router, which is a clearer cross-file simplification target than another local helper deletion inside a single support file.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py` passed with `176 passed in 0.57s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'grouped_callable_anchor_contract_in_combined_suite_uses_owner_helpers or collection_replacement_standard_definitions_are_reused_by_standard_inventory'` passed with `2 passed, 153 deselected in 0.13s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py -k 'pattern_boundary_standard_definitions_are_owner_owned_in_exact_order or pattern_boundary_standard_definitions_are_reused_by_standard_inventory'` passed with `2 passed, 25 deselected in 0.12s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_standard_definitions_export_stays_owned_by_source_tree'` passed with `1 passed, 115 deselected in 0.12s`.
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed.
  - `bash -lc "rg -n 'STANDARD_BENCHMARK_DEFINITIONS|collection_replacement_support\\.COLLECTION_REPLACEMENT_STANDARD_BENCHMARK_DEFINITIONS|source_tree_support\\.SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS' tests/benchmarks/benchmark_test_support.py"` currently reports the global aggregate assignment, the two owner-module tuple splices, and the helper comprehensions that this task is intended to delete or rewrite.
