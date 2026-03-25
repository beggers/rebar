# RBR-1320: Route collection owner imports through module alias

Status: done
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Delete the direct 43-name owner import surface from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the combined benchmark suite reaches collection-replacement owner helpers through one `collection_replacement_benchmark_anchor_support` module alias instead of binding those owner-owned names locally.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` must stop using `from tests.benchmarks.collection_replacement_benchmark_anchor_support import ...`.
- The combined benchmark suite must import the owner module through `tests.benchmarks` under a single alias such as `collection_replacement_support` and route the existing collection-replacement owner surfaces through that module object instead of binding them as direct local names.
- Add or update one focused AST/import-contract test in `tests/benchmarks/test_benchmark_test_support.py` that proves:
  - the combined benchmark suite no longer has a direct `ImportFrom` edge to `tests.benchmarks.collection_replacement_benchmark_anchor_support`
  - the suite does import `collection_replacement_benchmark_anchor_support` through `tests.benchmarks`
  - the owner-owned collection-replacement names involved in this cleanup are no longer present in the combined suite's top-level definition or assignment namespace.
- Do not introduce a new helper module, re-export layer, compatibility wrapper, or alias shim inside `tests/benchmarks/benchmark_test_support.py`.
- Keep the cleanup structural:
  - do not change benchmark manifests, harness behavior, scorecard contents, README text, or tracked `ops/state/` prose
  - do not move collection-replacement logic out of `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_success_callbacks_precompile_first_argument_before_timing or compiled_pattern_module_helper_keyword_contract_callbacks_precompile_first_argument_before_timing'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_contract_consumer_suites_reuse_shared_support_without_local_duplicates or compiled_pattern_contract_consumer_suites_do_not_alias_owner_module_surfaces or collection_replacement_support_through_owner_module_only'`
- `python3 -c "import ast,pathlib,sys; mod=ast.parse(pathlib.Path('tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py').read_text()); direct=[n for n in mod.body if isinstance(n, ast.ImportFrom) and n.module=='tests.benchmarks.collection_replacement_benchmark_anchor_support']; aliases=[(a.name,a.asname) for n in mod.body if isinstance(n, ast.ImportFrom) and n.module=='tests.benchmarks' for a in n.names if a.name=='collection_replacement_benchmark_anchor_support' and a.asname=='collection_replacement_support']; sys.exit(0 if (not direct and aliases) else 1)"`

## Constraints
- Keep the cleanup bounded to import ownership in the combined benchmark suite plus the supporting AST/import contract test.
- Prefer deleting direct owner-name bindings over introducing another indirection layer.

## Notes
- `RBR-1320` is the next available unreserved task id in this checkout:
  - `rg -n 'RBR-1320|RBR-1321|RBR-1322' ops/state/current_status.md ops/state/backlog.md` returned no matches in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f \( -name 'RBR-1320*' -o -name 'RBR-1321*' -o -name 'RBR-1322*' \) | sort` returned no matches before this task was queued.
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
- Queue/runtime state was not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready tasks, no blocked tasks, and no ready `feature-implementation` work
  - the latest runtime dashboard shows the most recent `architecture-implementation` run finishing `done` and no inherited-dirty, refresh, or commit anomaly
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently contains one direct `ImportFrom` edge to `tests.benchmarks.collection_replacement_benchmark_anchor_support`
  - a current AST probe reports `direct_name_count: 43` and `owner_aliases: []` for that suite, so the collection-replacement owner surface is still bound locally rather than routed through one owner-module alias
  - the same suite already imports `benchmark_test_support` and `source_tree_benchmark_anchor_support` through `tests.benchmarks`, so this cleanup aligns collection-replacement ownership with the module-alias pattern already used elsewhere in the benchmark support layer
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_success_callbacks_precompile_first_argument_before_timing or compiled_pattern_module_helper_keyword_contract_callbacks_precompile_first_argument_before_timing'` passed with `26 passed, 253 deselected in 0.11s`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_contract_consumer_suites_reuse_shared_support_without_local_duplicates or compiled_pattern_contract_consumer_suites_do_not_alias_owner_module_surfaces'` passed with `4 passed, 111 deselected in 0.17s`
  - `python3 -c "import ast,pathlib,sys; mod=ast.parse(pathlib.Path('tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py').read_text()); direct=[n for n in mod.body if isinstance(n, ast.ImportFrom) and n.module=='tests.benchmarks.collection_replacement_benchmark_anchor_support']; aliases=[(a.name,a.asname) for n in mod.body if isinstance(n, ast.ImportFrom) and n.module=='tests.benchmarks' for a in n.names if a.name=='collection_replacement_benchmark_anchor_support' and a.asname=='collection_replacement_support']; sys.exit(0 if (not direct and aliases) else 1)"` currently fails because the combined suite still imports the owner surface directly and has no owner-module alias yet, and that failure belongs exactly to this cleanup

## Completion
- Routed the combined benchmark suite through `from tests.benchmarks import collection_replacement_benchmark_anchor_support as collection_replacement_support` and converted the former 43 owner-owned direct imports to module-attribute access.
- Added `test_collection_replacement_support_through_owner_module_only` in `tests/benchmarks/test_benchmark_test_support.py` to assert the direct owner `ImportFrom` edge is gone, the `tests.benchmarks` alias import is present, and the retired owner names are absent from the suite's top-level definition/assignment namespace.
- Verification in this implementation run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_success_callbacks_precompile_first_argument_before_timing or compiled_pattern_module_helper_keyword_contract_callbacks_precompile_first_argument_before_timing'` passed with `26 passed, 253 deselected in 0.18s`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_contract_consumer_suites_reuse_shared_support_without_local_duplicates or compiled_pattern_contract_consumer_suites_do_not_alias_owner_module_surfaces or collection_replacement_support_through_owner_module_only'` passed with `5 passed, 111 deselected in 0.27s`
  - `python3 -c "import ast,pathlib,sys; mod=ast.parse(pathlib.Path('tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py').read_text()); direct=[n for n in mod.body if isinstance(n, ast.ImportFrom) and n.module=='tests.benchmarks.collection_replacement_benchmark_anchor_support']; aliases=[(a.name,a.asname) for n in mod.body if isinstance(n, ast.ImportFrom) and n.module=='tests.benchmarks' for a in n.names if a.name=='collection_replacement_benchmark_anchor_support' and a.asname=='collection_replacement_support']; sys.exit(0 if (not direct and aliases) else 1)"` passed
