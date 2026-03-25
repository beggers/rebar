# RBR-1323: Route collection-replacement suite imports through owner modules

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Delete the remaining direct owner import walls from `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` so the collection-replacement benchmark suite reaches shared support only through its existing `benchmark_test_support` and `collection_replacement_benchmark_anchor_support as support` module imports.

## Deliverables
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` must stop using both of these direct owner import forms:
  - `from tests.benchmarks.benchmark_test_support import ...`
  - `from tests.benchmarks.collection_replacement_benchmark_anchor_support import ...`
- The collection-replacement suite must route the currently direct owner surface through the existing module imports it already carries:
  - `from tests.benchmarks import benchmark_test_support`
  - `from tests.benchmarks import collection_replacement_benchmark_anchor_support as support`
- Keep the cleanup structural by converting the current direct owner-bound names to module-attribute access instead of rebinding them locally. This includes the current direct walls that cover:
  - synthetic workload builders, manifest/workload helpers, CPython runner helpers, and keyword/wrong-text-model contract helpers from `benchmark_test_support`
  - manifest-path constants, keyword-error source workload collections, probe helpers, selector helpers, and the keyword-error workload builder from `collection_replacement_benchmark_anchor_support`
- Update `tests/benchmarks/test_benchmark_test_support.py` with one focused AST/import ownership check that proves:
  - `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` no longer has direct `ImportFrom` edges to either owner module
  - the suite still imports `benchmark_test_support` and `collection_replacement_benchmark_anchor_support as support` through `tests.benchmarks`
  - the owner-owned names retired by this cleanup are absent from the collection-replacement suite's top-level definition and assignment namespace
- Do not add a new helper module, alias shim, wrapper layer, or re-export surface. Reuse the existing owner modules already imported by the suite.
- Keep this cleanup structural:
  - do not move support logic out of `tests/benchmarks/benchmark_test_support.py` or `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
  - do not change benchmark manifests, harness behavior, scorecard contents, README text, or tracked `ops/state/` prose

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'keyword_error or support_owned_without_local_duplicates'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'collection_replacement'`
- `python3 -c "import ast,pathlib,sys; mod=ast.parse(pathlib.Path('tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py').read_text()); direct=[n.module for n in mod.body if isinstance(n, ast.ImportFrom) and n.module in {'tests.benchmarks.benchmark_test_support','tests.benchmarks.collection_replacement_benchmark_anchor_support'}]; pkg={(a.name,a.asname) for n in mod.body if isinstance(n, ast.ImportFrom) and n.module=='tests.benchmarks' for a in n.names}; sys.exit(0 if (not direct and ('benchmark_test_support', None) in pkg and ('collection_replacement_benchmark_anchor_support', 'support') in pkg) else 1)"`
- `bash -lc "! rg -n '^from tests\\.benchmarks\\.(benchmark_test_support|collection_replacement_benchmark_anchor_support) import ' tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py"`

## Constraints
- Keep the cleanup bounded to import-ownership simplification in the collection-replacement benchmark suite plus the supporting AST/import contract test.
- Prefer deleting direct owner-name bindings over introducing another indirection layer.

## Notes
- `RBR-1323` is the next available unreserved task id in this checkout:
  - `rg -n 'RBR-1323|RBR-1324|RBR-1325' ops/state/current_status.md ops/state/backlog.md ops/state/decision_log.md ops/tasks -g '*.md'` matched only historical mentions inside already-completed task notes, not a live reservation for `RBR-1323`
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
- Queue/runtime state was not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready tasks, no blocked tasks, and no ready `feature-implementation` work
  - the latest runtime snapshot shows the most recent `architecture-implementation` run finishing `done` and no inherited-dirty, refresh, or commit anomaly
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` still contains two direct owner import walls:
    - one direct `ImportFrom` edge to `tests.benchmarks.benchmark_test_support` with `20` imported names
    - one direct `ImportFrom` edge to `tests.benchmarks.collection_replacement_benchmark_anchor_support` with `9` imported names
  - the same suite already imports both owner modules through `tests.benchmarks`, so the direct owner edges are now shadow access paths rather than required module entry points
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'keyword_error or support_owned_without_local_duplicates'` passed with `64 passed, 82 deselected in 0.15s`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'collection_replacement'` passed with `10 passed, 104 deselected in 0.30s`
  - `python3 -c "import ast,pathlib,sys; mod=ast.parse(pathlib.Path('tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py').read_text()); direct=[n.module for n in mod.body if isinstance(n, ast.ImportFrom) and n.module in {'tests.benchmarks.benchmark_test_support','tests.benchmarks.collection_replacement_benchmark_anchor_support'}]; pkg={(a.name,a.asname) for n in mod.body if isinstance(n, ast.ImportFrom) and n.module=='tests.benchmarks' for a in n.names}; sys.exit(0 if (not direct and ('benchmark_test_support', None) in pkg and ('collection_replacement_benchmark_anchor_support', 'support') in pkg) else 1)"` currently fails because the suite still carries direct owner imports, and that failure belongs exactly to this cleanup
  - `bash -lc "! rg -n '^from tests\\.benchmarks\\.(benchmark_test_support|collection_replacement_benchmark_anchor_support) import ' tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py"` currently fails because both direct owner import forms are still present, and that failure belongs exactly to this cleanup
