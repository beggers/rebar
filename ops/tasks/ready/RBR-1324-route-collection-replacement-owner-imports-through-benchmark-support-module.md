# RBR-1324: Route collection-replacement owner imports through benchmark-support module

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Delete the remaining direct `benchmark_test_support` owner import wall from `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` so the collection-replacement owner module reaches shared benchmark support only through its existing `from tests.benchmarks import benchmark_test_support` package import.

## Deliverables
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` must stop using `from tests.benchmarks.benchmark_test_support import ...`.
- Route the current direct owner surface through the existing `benchmark_test_support` module import instead of binding benchmark-support-owned names locally. This includes the current direct wall that covers:
  - `COLLECTION_REPLACEMENT_MANIFEST_PATH`
  - `MODULE_BOUNDARY_MANIFEST_PATH`
  - `StandardBenchmarkAnchorContractDefinition`
  - `_SourceTreeContractBuilderSpec`
  - `_contract_source_workloads`
  - `_definition_anchor_expectations`
  - `_is_collection_replacement_compiled_pattern_success_workload`
  - `_is_module_workflow_keyword_error_workload`
  - `_workload_case_pair_anchor_expectations`
  - `_workload_case_pairs_case_ids`
  - `_workload_case_pairs_workload_ids`
  - `freeze_signature_value`
- Update `tests/benchmarks/test_benchmark_test_support.py` with one focused AST/import ownership check that proves:
  - `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` no longer has a direct `ImportFrom` edge to `tests.benchmarks.benchmark_test_support`
  - the owner module still imports `benchmark_test_support` through `tests.benchmarks`
  - the retired benchmark-support-owned names listed above are absent from the collection-replacement owner module's top-level definition and assignment namespace
- Do not add a wrapper, alias shim, re-export surface, or new helper module. Reuse the existing `tests.benchmarks import benchmark_test_support` import already present in the owner module.
- Keep the cleanup structural:
  - do not move support logic out of `tests/benchmarks/benchmark_test_support.py`
  - do not change benchmark manifests, harness behavior, scorecard contents, README text, or tracked `ops/state/` prose

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'owner_module_owned_without_local_duplicates or keyword_error or grouped_callable_anchor_contract_in_combined_suite_uses_owner_helpers'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'collection_replacement_support or non_owner_collection_replacement_benchmark_support_routes_shared_classifiers_through_support_alias or collection_replacement_compiled_pattern_success_selector_stays_owned_by_shared_support'`
- `python3 -c "import ast,pathlib,sys; mod=ast.parse(pathlib.Path('tests/benchmarks/collection_replacement_benchmark_anchor_support.py').read_text()); direct=[n for n in mod.body if isinstance(n, ast.ImportFrom) and n.module=='tests.benchmarks.benchmark_test_support']; pkg={(a.name,a.asname) for n in mod.body if isinstance(n, ast.ImportFrom) and n.module=='tests.benchmarks' for a in n.names}; sys.exit(0 if (not direct and ('benchmark_test_support', None) in pkg) else 1)"`
- `bash -lc "! rg -n '^from tests\\.benchmarks\\.benchmark_test_support import ' tests/benchmarks/collection_replacement_benchmark_anchor_support.py"`

## Constraints
- Keep the cleanup bounded to owner-boundary/import-plumbing simplification between `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` and `tests/benchmarks/benchmark_test_support.py`, plus the supporting AST/import contract test.
- Prefer deleting direct owner-name bindings over introducing another indirection layer.

## Notes
- `RBR-1324` is the next available unreserved task id in this checkout:
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f | sed 's#.*/##' | sort | tail -n 10` ended at `RBR-1323-...`
  - `rg -n "RBR-1324|RBR-1325|RBR-1326" ops/state/current_status.md ops/state/backlog.md ops/state/decision_log.md ops/tasks -g '*.md'` matched only historical mentions inside completed task notes, not a live reservation for `RBR-1324`
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
- Queue/runtime state was not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready `feature-implementation` work, no blocked tasks, and the most recent `architecture-implementation` run finishing `done`
  - the latest runtime dashboard reports no inherited-dirty, refresh, or commit anomaly
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` still contains one direct `ImportFrom` edge to `tests.benchmarks.benchmark_test_support`
  - an AST probe in this run reported `12` directly imported owner names on that edge
  - the same owner module already imports `benchmark_test_support` through `tests.benchmarks`, so the direct owner import block is now duplicate access plumbing rather than a required module entry point
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'owner_module_owned_without_local_duplicates or keyword_error or grouped_callable_anchor_contract_in_combined_suite_uses_owner_helpers'` passed with `65 passed, 81 deselected in 0.16s`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'collection_replacement_support or non_owner_collection_replacement_benchmark_support_routes_shared_classifiers_through_support_alias or collection_replacement_compiled_pattern_success_selector_stays_owned_by_shared_support'` passed with `3 passed, 112 deselected in 0.20s`
  - `python3 -c "import ast,pathlib,sys; mod=ast.parse(pathlib.Path('tests/benchmarks/collection_replacement_benchmark_anchor_support.py').read_text()); direct=[n for n in mod.body if isinstance(n, ast.ImportFrom) and n.module=='tests.benchmarks.benchmark_test_support']; pkg={(a.name,a.asname) for n in mod.body if isinstance(n, ast.ImportFrom) and n.module=='tests.benchmarks' for a in n.names}; sys.exit(0 if (not direct and ('benchmark_test_support', None) in pkg) else 1)"` currently fails because the owner module still carries the direct import wall, and that failure belongs exactly to this cleanup
  - `bash -lc "! rg -n '^from tests\\.benchmarks\\.benchmark_test_support import ' tests/benchmarks/collection_replacement_benchmark_anchor_support.py"` currently fails because that direct import wall is still present, and that failure belongs exactly to this cleanup
