## RBR-1263: Move collection-replacement grouped-callable signature ownership onto dedicated support suite

Status: done
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Remove the remaining collection-replacement grouped-callable signature ownership that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, so the giant combined benchmark broker stops owning helper logic that belongs to the existing dedicated collection-replacement support surfaces.

## Deliverables
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Move these two inline grouped-callable signature helpers out of `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and rehome them into `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`:
  - `_collection_replacement_grouped_callable_correctness_case_signature(...)`
  - `_collection_replacement_grouped_callable_workload_signature(...)`
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to import those helpers from `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` and delete the local helper definitions.
- Add focused owner-suite coverage in `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` that pins the moved grouped-callable helper behavior directly:
  - keep the correctness-case helper restricted to the existing `_COLLECTION_REPLACEMENT_GROUPED_CALLABLE_WORKLOAD_CASE_PAIRS` surface;
  - keep callable replacement matching routed through `callable_match_group_signature(...)`;
  - keep the operation, pattern, replacement, args, flags, and text-model signature shapes unchanged for the current `sub()` / `subn()` grouped-callable rows; and
  - keep non-matching helpers or non-callable replacements rejected.
- Preserve the current bounded standard benchmark anchor behavior exactly:
  - the `collection-replacement-grouped-callable-replacement` `StandardBenchmarkAnchorContractDefinition` in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` must keep the same manifest path, workload-case pairs, include-workload selector, callback-parity flag, and anchored workload ordering; and
  - do not introduce copied workload-id inventories, a new broker module, or a second grouped-callable ownership layer.
- Do not widen this cleanup into workload manifests, `python/rebar_harness/benchmarks.py`, reports, README text, or tracked `ops/state/` prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `bash -lc "! rg -n 'def _collection_replacement_grouped_callable_(correctness_case_signature|workload_signature)\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep the cleanup structural and bounded to the three benchmark files listed above.
- Prefer the existing collection-replacement support module and dedicated support suite over adding another broker test file, wrapper helper, or ownership layer.
- Preserve the live grouped-callable workload-pair ordering, signature normalization, and standard-anchor contract behavior exactly.

## Notes
- `RBR-1263` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run; and
  - `rg -n "RBR-1263|RBR-1264|RBR-1265|RBR-1266" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -g '*.md'` found no reserved follow-on ids in tracked state or live queue files outside a historical note in an older done-task file.
- No blocked architecture task exists to reopen or retire first in this run.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The simplification is concrete in the live checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `10261` lines in this run;
  - `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` is `1391` lines; and
  - `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` is `948` lines.
- The grouped-callable signature ownership is still uniquely inline in the combined broker in this run:
  - `rg -n "_collection_replacement_grouped_callable_(correctness_case_signature|workload_signature)" tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` matched only `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`; and
  - the only live call sites are the `collection-replacement-grouped-callable-replacement` standard-anchor definition in the combined broker.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed with `40 passed`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed with `128 tests collected`.
  - `bash -lc "! rg -n 'def _collection_replacement_grouped_callable_(correctness_case_signature|workload_signature)\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently fails because those two grouped-callable signature helpers still live inline in the combined suite, and that failure belongs to the exact cleanup queued here.

## Completion
- Moved `_collection_replacement_grouped_callable_correctness_case_signature(...)` and `_collection_replacement_grouped_callable_workload_signature(...)` into `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` and rewired `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to import them from the owner support module.
- Added direct owner-suite coverage in `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` for the four live grouped-callable workload/case pairs, callable-match-group routing, unchanged signature shapes, and rejection of unpaired rows, wrong helpers, and non-callable replacements.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` -> `44 passed`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` -> `132 tests collected`
  - `bash -lc "! rg -n 'def _collection_replacement_grouped_callable_(correctness_case_signature|workload_signature)\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` -> success
