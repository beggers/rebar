## RBR-1372: Delete source-tree combined retired owner registry

Status: done
Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the test-only `SOURCE_TREE_COMBINED_RETIRED_OWNER_NAMES` export from `tests/benchmarks/source_tree_benchmark_anchor_support.py` so the source-tree owner module stops carrying bookkeeping that exists only to satisfy benchmark-support ownership assertions and does not participate in runtime benchmark behavior.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- Delete `SOURCE_TREE_COMBINED_RETIRED_OWNER_NAMES` from `tests/benchmarks/source_tree_benchmark_anchor_support.py`.
- Update `tests/benchmarks/test_benchmark_test_support.py` so the source-tree combined ownership assertions no longer read an exported retired-name registry from `tests.benchmarks.source_tree_benchmark_anchor_support`.
- Replace the registry-based assertions with direct checks that keep the same architectural contract narrow:
  - `tests.benchmarks.test_source_tree_combined_boundary_benchmarks` still routes through `tests.benchmarks.benchmark_test_support`;
  - it still does not define or alias the specific compiled-pattern helper keyword shared-surface names that matter to that route; and
  - benchmark manifest validation keeps its own explicit owner-surface contract without reusing a source-tree combined registry.
- Do not add a replacement registry, forwarding alias, or another exported bookkeeping constant elsewhere.
- Keep the cleanup structural only; do not change benchmark workload data, benchmark execution behavior, scorecard logic, or tracked project-state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_contract_consumer_suites_reuse_shared_support_without_local_duplicates or compiled_pattern_contract_consumer_suites_do_not_alias_owner_module_surfaces or compiled_pattern_module_helper_keyword_shared_surface_stays_listed_in_source_tree_retired_owner_registries'`
- `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py`
- `bash -lc "! rg -n '^SOURCE_TREE_COMBINED_RETIRED_OWNER_NAMES\\s*=' tests/benchmarks/source_tree_benchmark_anchor_support.py"`
- `bash -lc "! rg -n 'SOURCE_TREE_COMBINED_RETIRED_OWNER_NAMES' tests/benchmarks/test_benchmark_test_support.py"`

## Constraints
- Prefer deleting the exported retired-name registry over moving it sideways or recreating it under another module.
- Keep the run bounded to this single test-only registry cleanup and the ownership assertions that currently depend on it.

## Notes
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1372|RBR-1373|RBR-1374' ops/state/current_status.md ops/state/backlog.md ops/tasks` returned no future-ID reservations in this run
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate selection in this run:
  - Post-JSON cleanup stayed in the benchmark-support ownership layer because the live and tracked JSON counts are both zero.
  - `SOURCE_TREE_COMBINED_RETIRED_OWNER_NAMES` is defined only in `tests/benchmarks/source_tree_benchmark_anchor_support.py` and referenced only by `tests/benchmarks/test_benchmark_test_support.py`, so it is still a bounded bookkeeping-only export rather than runtime support surface.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_contract_consumer_suites_reuse_shared_support_without_local_duplicates or compiled_pattern_contract_consumer_suites_do_not_alias_owner_module_surfaces or compiled_pattern_module_helper_keyword_shared_surface_stays_listed_in_source_tree_retired_owner_registries'` passed with `4 passed, 166 deselected in 0.19s`
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py` passed
  - `bash -lc "! rg -n '^SOURCE_TREE_COMBINED_RETIRED_OWNER_NAMES\\s*=' tests/benchmarks/source_tree_benchmark_anchor_support.py"` currently fails because the exported registry constant still exists, and that failure belongs exactly to this cleanup
  - `bash -lc "! rg -n 'SOURCE_TREE_COMBINED_RETIRED_OWNER_NAMES' tests/benchmarks/test_benchmark_test_support.py"` currently fails because the benchmark-support tests still depend on that registry, and that failure belongs exactly to this cleanup

## Completion
- Deleted `SOURCE_TREE_COMBINED_RETIRED_OWNER_NAMES` from `tests/benchmarks/source_tree_benchmark_anchor_support.py`.
- Replaced the combined-suite ownership assertions in `tests/benchmarks/test_benchmark_test_support.py` with direct checks against `COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SHARED_SURFACE_NAMES`, while keeping benchmark manifest validation on its explicit owner-only surface set.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_contract_consumer_suites_reuse_shared_support_without_local_duplicates or compiled_pattern_contract_consumer_suites_do_not_alias_owner_module_surfaces or compiled_pattern_module_helper_keyword_shared_surface_stays_listed_in_source_tree_retired_owner_registries'` -> `3 passed, 166 deselected`
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py`
  - `bash -lc "! rg -n '^SOURCE_TREE_COMBINED_RETIRED_OWNER_NAMES\\s*=' tests/benchmarks/source_tree_benchmark_anchor_support.py"`
  - `bash -lc "! rg -n 'SOURCE_TREE_COMBINED_RETIRED_OWNER_NAMES' tests/benchmarks/test_benchmark_test_support.py"`
