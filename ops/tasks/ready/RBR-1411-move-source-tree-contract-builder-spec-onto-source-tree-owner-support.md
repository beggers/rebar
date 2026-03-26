## RBR-1411: Move the source-tree contract builder spec onto source-tree owner support

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove one remaining source-tree-only contract-builder seam from `tests/benchmarks/benchmark_test_support.py`.
- `tests/benchmarks/source_tree_benchmark_anchor_support.py` already owns the source-tree contract manifest/workload builders and the owner-facing scorecard contract assertions, but the `_SourceTreeContractBuilderSpec` dataclass still lives in shared benchmark support and is threaded back into source-tree and pattern-boundary owner modules through `benchmark_test_support`.
- Move that dataclass onto `tests/benchmarks/source_tree_benchmark_anchor_support.py` so source-tree owner support owns its full contract-builder surface and shared benchmark support keeps only generic helpers that are not tied to that owner lane.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`

## Acceptance Criteria
- Delete `_SourceTreeContractBuilderSpec` from `tests/benchmarks/benchmark_test_support.py`.
- Recreate `_SourceTreeContractBuilderSpec` on `tests/benchmarks/source_tree_benchmark_anchor_support.py` with the same field names, defaults, and frozen/slotted dataclass behavior:
  - `manifest_id`
  - `excluded_fields`
  - `manifest_timed_samples=2`
  - `timing_scope=None`
  - `notes=()`
- Update `tests/benchmarks/source_tree_benchmark_anchor_support.py` so its type annotations, spec constants, and owner methods build and return `source_tree_benchmark_anchor_support._SourceTreeContractBuilderSpec` instead of routing that type through `benchmark_test_support`.
- Update `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py` so its wrong-text-model contract spec is built through `tests/benchmarks/source_tree_benchmark_anchor_support.py` rather than importing the spec type from `benchmark_test_support`.
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`, `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`, `tests/benchmarks/test_benchmark_manifest_validation.py`, and `tests/benchmarks/test_benchmark_test_support.py` so ownership assertions and type references treat `_SourceTreeContractBuilderSpec` as source-tree-owned instead of shared-support-owned.
- Keep the moved dataclass compatible with the existing source-tree contract helpers without changing:
  - source-tree contract manifest ids,
  - excluded-field sets,
  - timed-sample defaults,
  - timing-scope values,
  - contract notes payloads,
  - generated contract workload ids.
- Keep genuinely shared helpers in `tests/benchmarks/benchmark_test_support.py`, including `StandardBenchmarkAnchorContractDefinition`, `_CompiledPatternModuleHelperKeywordContractSpec`, workload selectors/signature helpers, CPython dispatch helpers, and generic payload/assertion utilities.
- Do not widen into the collection/replacement helper-keyword contract lane, compiled-pattern compile owner cases, benchmark manifests, reports, or tracked project-state docs in the same task.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'source_tree_contract or contract_builder_spec' tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'SourceTreeContractBuilderSpec or source_tree_contract' tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py -k 'source_tree_contract' tests/benchmarks/test_benchmark_manifest_validation.py -k 'source_tree_contract'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_benchmark_manifest_validation.py`
- `bash -lc "! rg -n '^class _SourceTreeContractBuilderSpec\\b' tests/benchmarks/benchmark_test_support.py"`
- `bash -lc "! rg -n 'benchmark_test_support\\._SourceTreeContractBuilderSpec' tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_benchmark_manifest_validation.py"`

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the dashboard JSON counts were not obviously stale.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and duplicate check in this run:
  - `ops/tasks/blocked/` only contained `.gitkeep`, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1411|RBR-1412|RBR-1413" ops/state/current_status.md ops/state/backlog.md ops/tasks ops/state/decision_log.md` found no reserved future-id use for `RBR-1411`.
- Candidate selection in this run:
  - The first viable post-JSON simplification was `_SourceTreeContractBuilderSpec` because the source-tree owner module already owns `_source_tree_contract_manifest(...)`, `_source_tree_contract_workload(...)`, and `assert_source_tree_benchmark_contract(...)`, while the spec dataclass still sits in `tests/benchmarks/benchmark_test_support.py`.
  - `rg -n "^class _SourceTreeContractBuilderSpec\\b|benchmark_test_support\\._SourceTreeContractBuilderSpec" ...` in this run showed the remaining direct spec references are confined to `tests/benchmarks/source_tree_benchmark_anchor_support.py`, `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py`, and the scoped benchmark-owner tests, which makes this a bounded owner-boundary cleanup rather than a repo-wide refactor.
  - I stopped after this first viable candidate because it removes one remaining shared-to-owner routing layer without depending on feature work or broader benchmark-manifest changes.
- Verification in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'source_tree_contract or contract_builder_spec' tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'SourceTreeContractBuilderSpec or source_tree_contract' tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py -k 'source_tree_contract' tests/benchmarks/test_benchmark_manifest_validation.py -k 'source_tree_contract'` -> `16 passed, 381 deselected`
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_benchmark_manifest_validation.py` succeeded.
  - `bash -lc "! rg -n '^class _SourceTreeContractBuilderSpec\\b' tests/benchmarks/benchmark_test_support.py"` currently fails only because the class is still defined there, which is the cleanup this task queues.
  - `bash -lc "! rg -n 'benchmark_test_support\\._SourceTreeContractBuilderSpec' tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_benchmark_manifest_validation.py"` currently fails only because those files still route the spec through `benchmark_test_support`, which is the exact ownership cleanup this task queues.
