## RBR-1380: Delete collection-replacement route wrapper methods

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the six thin `workload_ids()`, `case_ids()`, and `anchor_expectations()` wrapper methods from the two collection-replacement route dataclasses, and rewrite the bounded owner/test call sites to derive those values directly from `workload_case_pairs` plus the existing shared anchor helper.

## Deliverables
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`

## Acceptance Criteria
- Delete these methods from `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` without moving them to another shared helper layer or replacing them with another generic route wrapper:
  - `_CollectionReplacementLiteralReplacementRoute.workload_ids`
  - `_CollectionReplacementLiteralReplacementRoute.case_ids`
  - `_CollectionReplacementLiteralReplacementRoute.anchor_expectations`
  - `_CollectionReplacementPatternCollectionRoute.workload_ids`
  - `_CollectionReplacementPatternCollectionRoute.case_ids`
  - `_CollectionReplacementPatternCollectionRoute.anchor_expectations`
- Rewrite the bounded owner logic and tests to use direct tuple projections from `workload_case_pairs` and direct calls to `benchmark_test_support._workload_case_pair_anchor_expectations(...)` at the use sites that still need those derived values. Preserve these boundaries explicitly:
  - the pattern `findall`, `finditer`, and `split` routes still match the same workload ids and case ids as before;
  - the module and pattern literal-replacement selectors still target the same anchored workload ids as before;
  - the standard benchmark definition setup still produces the same anchor expectations for those route-backed slices;
  - `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` no longer treats the deleted route methods as part of the owner surface while still proving the same measured-row and workload-selection contracts.
- Do not change benchmark manifests, benchmark execution behavior, workload selection rules, or tracked project-state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `python3 -m py_compile tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `bash -lc "! rg -n '\\b(def (workload_ids|case_ids|anchor_expectations)|\\.(workload_ids|case_ids|anchor_expectations)\\()' tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py"`

## Constraints
- Prefer direct tuple projections and direct shared-anchor-helper calls at the remaining use sites over introducing another route-level helper.
- Keep the run bounded to this route-wrapper deletion in the collection-replacement benchmark-support owner layer.

## Notes
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1380|RBR-1381|RBR-1382' ops/state/current_status.md ops/state/backlog.md` returned no matches in this run
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate selection in this run:
  - `_CollectionReplacementLiteralReplacementRoute` and `_CollectionReplacementPatternCollectionRoute` still expose six wrapper methods that only project `workload_case_pairs` back into workload-id tuples, case-id tuples, and `_workload_case_pair_anchor_expectations(...)`.
  - The remaining consumers are bounded to the collection-replacement owner module itself plus `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`.
  - Removing those wrappers continues the post-JSON benchmark-support simplification pass without changing any feature boundary or benchmark report surface.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed with `147 passed in 1.75s`
  - `python3 -m py_compile tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed
  - `bash -lc "! rg -n '\\b(def (workload_ids|case_ids|anchor_expectations)|\\.(workload_ids|case_ids|anchor_expectations)\\()' tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py"` currently fails with the exact route methods and call sites this task is intended to delete
