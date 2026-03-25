## RBR-1334: Route remaining collection-owner surface through source-tree owner

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Delete the remaining direct `collection_replacement_benchmark_anchor_support` dependency from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the source-tree combined suite routes its collection-replacement-owned benchmark surface through `tests/benchmarks/source_tree_benchmark_anchor_support.py` instead of reaching across owner modules directly.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Extend `tests/benchmarks/source_tree_benchmark_anchor_support.py` so it owns the remaining collection-replacement-driven source-tree suite surface currently consumed directly from `collection_replacement_support` in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`. Keep this bounded to the live direct-reference set in that suite:
  - the remaining `CONDITIONAL_GROUP_EXISTS_*` workload-id tuples used by the source-tree combined suite
  - the nested and quantified callable correctness/workload signature helpers still read from `collection_replacement_support`
  - the compiled-pattern collection-replacement success workload filter currently reached through `collection_replacement_support.benchmark_test_support`
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to consume that surface only through `source_tree_support` and delete the direct `collection_replacement_benchmark_anchor_support as collection_replacement_support` import.
- Add or update focused coverage in `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so the cleanup stays pinned:
  - prove the moved surface is available from `source_tree_benchmark_anchor_support`
  - fail if `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` reintroduces a direct `collection_replacement_support` import or direct `collection_replacement_support.` attribute reads
- Keep the cleanup structural only:
  - do not change benchmark manifests, correctness fixtures, harness behavior, README text, or tracked `ops/state/` prose
  - do not add a new support module, alias shim, or another bounce layer between `source_tree_benchmark_anchor_support` and the combined suite
  - do not widen into unrelated `benchmark_test_support` routing in the same task

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `bash -lc "! rg -n 'collection_replacement_support\\.' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
- `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Constraints
- Keep the task bounded to removing the last direct collection-owner dependency from the source-tree combined benchmark suite.
- Prefer moving or deriving owner-scoped surface on `source_tree_benchmark_anchor_support.py` over inventing another helper layer.

## Notes
- `RBR-1334` is the next available unreserved task id in this checkout:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n "RBR-1334|RBR-1335|RBR-1336|RBR-1337" ops/state/current_status.md ops/state/backlog.md` returned no matches in this run
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still contains direct `collection_replacement_support.` reads for conditional-callable workload-id tuples, nested/quantified callable signature helpers, and one compiled-pattern success filter routed through `collection_replacement_support.benchmark_test_support`
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` already owns the adjacent source-tree conditional-callable and compiled-pattern owner surface consumed by the same suite, so this direct cross-owner import is now the remaining structural outlier on that boundary
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed with `349 passed, 1821 subtests passed in 13.11s`
  - `bash -lc "! rg -n 'collection_replacement_support\\.' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently fails because the suite still reads `collection_replacement_support.` directly, and that failure belongs exactly to this cleanup
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed
