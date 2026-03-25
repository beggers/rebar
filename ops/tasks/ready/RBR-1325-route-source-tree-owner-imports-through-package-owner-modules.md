# RBR-1325: Route source-tree owner imports through package owner modules

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Delete the remaining direct owner import walls from `tests/benchmarks/source_tree_benchmark_anchor_support.py` so the source-tree benchmark owner reaches shared benchmark support only through package-level owner-module imports.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- `tests/benchmarks/source_tree_benchmark_anchor_support.py` must stop using both of these direct owner import forms:
  - `from tests.benchmarks.benchmark_test_support import ...`
  - `from tests.benchmarks.collection_replacement_benchmark_anchor_support import ...`
- Route the current owner-owned surface through package-level module imports instead:
  - `from tests.benchmarks import benchmark_test_support`
  - `from tests.benchmarks import collection_replacement_benchmark_anchor_support as collection_replacement_support`
- Keep the cleanup structural by converting the current direct owner-bound names to module-attribute access instead of rebinding them locally. This includes the current direct walls that cover:
  - manifest-path constants and the standard-definition contract type from `benchmark_test_support`
  - shared anchor expectation helpers, signature helpers, live-manifest loaders, and published-case lookup helpers from `benchmark_test_support`
  - `CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_BYTES_WORKLOAD_IDS` from `collection_replacement_benchmark_anchor_support`
- Update the benchmark-support tests so the ownership contract stays explicit:
  - add or update one focused AST/import ownership check proving `tests/benchmarks/source_tree_benchmark_anchor_support.py` no longer has direct `ImportFrom` edges to either owner module and instead imports both owner modules through `tests.benchmarks`
  - keep or add one focused regression check proving the retired owner-bound names from this cleanup are absent from the source-tree owner module's top-level definition and assignment namespace
- Do not add a wrapper, alias shim, re-export surface, or new helper module. Reuse the existing owner modules directly.
- Keep this cleanup structural:
  - do not move support logic out of `tests/benchmarks/benchmark_test_support.py` or `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
  - do not change benchmark manifests, harness behavior, scorecard contents, README text, or tracked `ops/state/` prose

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_owner_manifest_path_constants_point_to_current_workload_files or source_tree_standard_definitions_export_stays_owned_by_source_tree or source_tree_owner_definition_exports_reuse_owner_manifest_path_constants or source_tree_owner_builders_reference_owner_manifest_path_constants'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'standard_benchmark_definitions_keep_owner_blocks_in_order or source_tree_anchor_contract_suite_imports_benchmark_support_without_shadow_alias or source_tree_combined_suite_imports_standard_benchmark_definitions_from_support'`
- `bash -lc "! rg -n '^from tests\\.benchmarks\\.(benchmark_test_support|collection_replacement_benchmark_anchor_support) import ' tests/benchmarks/source_tree_benchmark_anchor_support.py"`
- `python3 -c "import ast,pathlib,sys; mod=ast.parse(pathlib.Path('tests/benchmarks/source_tree_benchmark_anchor_support.py').read_text()); direct=[n.module for n in mod.body if isinstance(n, ast.ImportFrom) and n.module in {'tests.benchmarks.benchmark_test_support','tests.benchmarks.collection_replacement_benchmark_anchor_support'}]; pkg={(a.name,a.asname) for n in mod.body if isinstance(n, ast.ImportFrom) and n.module=='tests.benchmarks' for a in n.names}; sys.exit(0 if (not direct and ('benchmark_test_support', None) in pkg and ('collection_replacement_benchmark_anchor_support', 'collection_replacement_support') in pkg) else 1)"`

## Constraints
- Keep the cleanup bounded to owner-boundary/import-plumbing simplification inside `tests/benchmarks/source_tree_benchmark_anchor_support.py` plus the supporting ownership tests.
- Prefer deleting direct owner-name bindings over introducing another indirection layer.

## Notes
- `RBR-1325` is the next available unreserved task id in this checkout:
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f \( -name 'RBR-1325*' -o -name 'RBR-1326*' -o -name 'RBR-1327*' \) | sort` returned no matches before this task was queued
  - `rg -n 'RBR-1325|RBR-1326|RBR-1327' ops/state/current_status.md ops/state/backlog.md ops/state/decision_log.md ops/tasks -g '*.md'` matched only historical mentions inside completed task notes, not a live reservation for `RBR-1325`
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
- Queue/runtime state was not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready tasks, no blocked tasks, and no ready `feature-implementation` work
  - the latest runtime dashboard shows the most recent `architecture-implementation` run finishing `done` and no inherited-dirty, refresh, or commit anomaly
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` still contains two direct owner import walls:
    - one direct `ImportFrom` edge to `tests.benchmarks.benchmark_test_support` with `18` imported names
    - one direct `ImportFrom` edge to `tests.benchmarks.collection_replacement_benchmark_anchor_support` with `1` imported name
  - the same module currently has no `from tests.benchmarks import ...` package-level owner-module import, so its shared support access still depends on direct owner bindings
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_owner_manifest_path_constants_point_to_current_workload_files or source_tree_standard_definitions_export_stays_owned_by_source_tree or source_tree_owner_definition_exports_reuse_owner_manifest_path_constants or source_tree_owner_builders_reference_owner_manifest_path_constants'` passed with `4 passed, 47 deselected in 0.11s`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'standard_benchmark_definitions_keep_owner_blocks_in_order or source_tree_anchor_contract_suite_imports_benchmark_support_without_shadow_alias or source_tree_combined_suite_imports_standard_benchmark_definitions_from_support'` passed with `9 passed, 106 deselected in 0.17s`
  - `bash -lc "! rg -n '^from tests\\.benchmarks\\.(benchmark_test_support|collection_replacement_benchmark_anchor_support) import ' tests/benchmarks/source_tree_benchmark_anchor_support.py"` currently fails because both direct owner import walls are still present, and that failure belongs exactly to this cleanup
  - `python3 -c "import ast,pathlib,sys; mod=ast.parse(pathlib.Path('tests/benchmarks/source_tree_benchmark_anchor_support.py').read_text()); direct=[n.module for n in mod.body if isinstance(n, ast.ImportFrom) and n.module in {'tests.benchmarks.benchmark_test_support','tests.benchmarks.collection_replacement_benchmark_anchor_support'}]; pkg={(a.name,a.asname) for n in mod.body if isinstance(n, ast.ImportFrom) and n.module=='tests.benchmarks' for a in n.names}; sys.exit(0 if (not direct and ('benchmark_test_support', None) in pkg and ('collection_replacement_benchmark_anchor_support', 'collection_replacement_support') in pkg) else 1)"` currently fails because the source-tree owner module still uses direct owner imports and has no package-level owner-module imports yet
- A broader `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'former_owner_modules_share_source_tree_helpers_without_local_duplicates or source_tree_owner_manifest_path_constants_point_to_current_workload_files or source_tree_standard_definitions_export_stays_owned_by_source_tree'` slice is already red in this checkout for unrelated drift (`collection_replacement_benchmark_anchor_support` no longer exports `freeze_signature_value`), so the acceptance is intentionally narrowed to the exact green ownership checks above plus the direct-import probes that belong to this cleanup.
