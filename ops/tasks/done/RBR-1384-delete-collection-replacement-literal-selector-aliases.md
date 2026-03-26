## RBR-1384: Delete collection replacement literal selector aliases

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the two module-level literal-replacement selector alias constants from the shared collection-replacement benchmark owner layer, and route the affected standard-definition and test surfaces through direct `_is_collection_replacement_literal_replacement_workload(...)` predicates instead of storing those fixed `partial(...)` wrappers as owner-level aliases.

## Deliverables
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`

## Acceptance Criteria
- Remove `_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_SELECTOR` and `_COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_SELECTOR` from `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` without replacing them with new registry constants, wrapper functions, or renamed alias layers.
- Rewrite the affected `StandardBenchmarkAnchorContractDefinition(...)` entries in `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` so the module and pattern literal-replacement routes still select the same bounded workload sets by calling `_is_collection_replacement_literal_replacement_workload(...)` directly with the existing route-specific ids, operations, text models, and allowed-count policy:
  - the module route still selects the same 18 workload ids from `_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS`;
  - the direct-`Pattern` route still selects the same 20 workload ids from `_COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS`;
  - `_collection_replacement_literal_replacement_workload_signature(...)` still receives an `include_workload` callable that keeps the same acceptance/rejection boundary for each route.
- Update `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` so the owner/test surface proves the deleted selector aliases are absent and still validates the literal-replacement selection behavior through direct predicate calls or inline `partial(...)` use at the assertion sites.
- Keep the shared `_is_collection_replacement_literal_replacement_workload(...)` predicate and the existing workload-id / operation / text-model constants intact; this task is about deleting the stored alias layer, not changing the live selection contract.
- Do not change benchmark manifests, workload ids, benchmark execution behavior, published row ids, or tracked project-state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `python3 -m py_compile tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `bash -lc "! rg -n '_COLLECTION_REPLACEMENT_(MODULE|PATTERN)_LITERAL_REPLACEMENT_SELECTOR' tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py"`

## Constraints
- Prefer direct calls to `_is_collection_replacement_literal_replacement_workload(...)` or inline `partial(...)` arguments at the actual use sites over another stored selector alias.
- Keep the run bounded to deleting the two literal-replacement selector aliases in the collection-replacement benchmark owner/test surface.

## Notes
- Queue check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
  - `git status --short` was empty, so the runtime JSON count was not lagging a dirty checkout in this run.
- ID and duplicate check in this run:
  - `rg -n 'RBR-1384' ops/state/current_status.md ops/state/backlog.md` returned no matches.
  - `ls -1 ops/tasks/ready` and `ls -1 ops/tasks/blocked` were both empty, so there was no ready/blocked duplicate to refine or reopen first.
  - `rg -n 'RBR-1384|delete-collection-replacement-literal-replacement-selector-aliases|_COLLECTION_REPLACEMENT_(MODULE|PATTERN)_LITERAL_REPLACEMENT_SELECTOR' ops/tasks` only hit historical done-task notes plus the live alias call sites, not a current ready/blocked sibling.
- Candidate selection in this run:
  - I inspected the source-tree contract-builder layer first; `_SourceTreeContractBuilderSpec` is still tied into shared contract-spec objects and cross-module owner metadata, so deleting that stack cleanly would be larger than one bounded architecture-implementation run.
  - The two collection-replacement selector aliases are pure stored `partial(...)` wrappers over `_is_collection_replacement_literal_replacement_workload(...)` and add no owner-specific behavior beyond fixed arguments.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed (`154 passed in 1.71s`).
  - `python3 -m py_compile tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed.
  - `bash -lc "rg -n '_COLLECTION_REPLACEMENT_(MODULE|PATTERN)_LITERAL_REPLACEMENT_SELECTOR' tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py"` currently reports the two alias definitions plus eight owner/test call sites that this task is intended to delete.

## Completion
- Deleted `_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_SELECTOR` and `_COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_SELECTOR` from the collection-replacement benchmark owner layer and rewired the affected standard contract definitions to use direct inline `partial(...)` calls into `_is_collection_replacement_literal_replacement_workload(...)` with the existing workload-id, operation, text-model, and allowed-count arguments.
- Updated the benchmark owner tests to assert the alias layer is absent and to keep the module/pattern literal-replacement measured-row and benchmark-gap checks routed through direct predicate wiring instead of stored selector aliases.
- Verification in this implementation run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed (`155 passed in 1.78s`).
  - `python3 -m py_compile tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed.
  - `bash -lc "! rg -n '_COLLECTION_REPLACEMENT_(MODULE|PATTERN)_LITERAL_REPLACEMENT_SELECTOR' tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py"` passed.
