## RBR-1381: Delete literal replacement route registry

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the `_CollectionReplacementLiteralReplacementRoute` dataclass and `_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_ROUTES` registry from the collection-replacement benchmark owner layer, and rewire the bounded owner/test call sites to use plain workload-case-pair tuples plus explicit literal-replacement metadata instead of the bespoke route object layer.

## Deliverables
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`

## Acceptance Criteria
- Remove `_CollectionReplacementLiteralReplacementRoute` and `_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_ROUTES` from `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` without replacing them with another generic registry or wrapper class.
- Replace that route-object layer with ordinary module-owned metadata that keeps the two bounded literal-replacement slices explicit:
  - one plain workload/case-pair tuple for the module literal-replacement slice;
  - one plain workload/case-pair tuple for the direct-`Pattern` literal-replacement slice;
  - direct workload-id tuples and explicit operation metadata for selectors and correctness-signature wiring.
- Rewrite the owner call sites that still depend on the removed registry so they use the new plain metadata directly. Keep these boundaries unchanged:
  - `_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_SELECTOR` still selects the same 18 module workload ids;
  - `_COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_SELECTOR` still selects the same 20 direct-`Pattern` workload ids;
  - the two `StandardBenchmarkAnchorContractDefinition(...)` entries for literal replacement still publish the same anchor expectations and workload signatures;
  - `_collection_replacement_literal_replacement_correctness_case_signature(...)` still matches the same module and direct-`Pattern` correctness rows as before.
- Rewrite `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` so it stops treating the deleted dataclass/registry as part of the owner surface and instead asserts against the new plain literal-replacement metadata while preserving the same workload-order, measured-row, and zero-gap contracts.
- Do not change benchmark manifests, benchmark execution behavior, workload ids, published case ids, or tracked project-state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `python3 -m py_compile tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `bash -lc \"! rg -n '_CollectionReplacementLiteralReplacementRoute|_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_ROUTES' tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py\"`

## Constraints
- Prefer plain tuple constants and direct explicit metadata over another dataclass, registry, or route wrapper layer.
- Keep the run bounded to the literal-replacement route-registry deletion in the collection-replacement benchmark-support owner layer.

## Notes
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1381|RBR-1382|RBR-1383' ops/state/current_status.md ops/state/backlog.md ops/tasks ops/state/decision_log.md` returned no reserved or existing matches in this run
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate selection in this run:
  - `_CollectionReplacementLiteralReplacementRoute` no longer carries behavior; it is only a stored metadata wrapper around workload/case pairs plus a few explicit literal-replacement fields.
  - The owner module already exposes `_collection_replacement_literal_replacement_correctness_case_signature(...)` with explicit `case_ids`, `expected_operation`, `operation_prefix`, and `args_offset` parameters, so the route registry is no longer required to express the bounded module and direct-`Pattern` slices.
  - The remaining registry consumers are bounded to the two literal-replacement benchmark definitions, the two literal-replacement selectors, and the focused test assertions in `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed with `153 passed in 1.75s`
  - `python3 -m py_compile tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed
  - `bash -lc \"rg -n '_CollectionReplacementLiteralReplacementRoute|_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_ROUTES' tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py\"` currently fails with the exact class and registry references this task is intended to delete
