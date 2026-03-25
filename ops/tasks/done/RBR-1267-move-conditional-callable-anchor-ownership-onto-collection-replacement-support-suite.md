## RBR-1267: Move conditional callable anchor ownership onto collection-replacement support suite

Status: done
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Remove the remaining nested and quantified conditional callable anchor ownership that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, so the giant combined benchmark broker stops owning collection/replacement-specific callable signature logic and workload-id inventories that belong beside the existing `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` support surface.

## Deliverables
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Move these four inline helper definitions out of `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and rehome them into `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`:
  - `_conditional_group_exists_nested_callable_correctness_case_signature(...)`
  - `_conditional_group_exists_nested_callable_workload_signature(...)`
  - `_conditional_group_exists_quantified_callable_correctness_case_signature(...)`
  - `_conditional_group_exists_quantified_callable_workload_signature(...)`
- Move the exact workload-id ownership those helpers rely on into the same support module so the combined suite no longer owns the conditional callable inventory:
  - `CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS`
  - `CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS`
  - `CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_NEGATIVE_COUNT_BYTES_WORKLOAD_IDS`
  - `_CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_WORKLOAD_STEMS`
  - `CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS`
  - `CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS`
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to import the moved helpers and workload-id tuples from `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`, and delete the local copies.
- Add focused owner-suite coverage in `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` that pins the moved behavior directly:
  - nested conditional callable signature helpers must keep the current numbered and named `module.sub`, `module.subn`, `pattern.sub`, and `pattern.subn` tuple shapes for both `str` and `bytes`;
  - quantified conditional callable signature helpers must keep the current omitted-`count` versus explicit-`count` handling, plus the existing `exception` and `no-match` category bits;
  - the moved workload-signature helpers must accept only the live nested or quantified conditional callable workload ids and must continue rejecting non-callable replacements or non-owned rows; and
  - the owner suite must assert that the combined broker imports these helpers from the support module instead of redefining them locally.
- Preserve the current combined-suite behavior exactly:
  - the nested and quantified conditional callable anchor-to-published-case tests in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` must keep using the same workload ordering, workload ids, callable replacement signatures, and anchored published-case uniqueness checks; and
  - do not introduce a new support module, wrapper helper layer, copied workload-id inventory, or fallback local definitions in the combined broker.
- Do not widen this cleanup into workload manifests, `python/rebar_harness/benchmarks.py`, reports, README text, or tracked `ops/state/` prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `bash -lc "! rg -n 'def _conditional_group_exists_(quantified|nested)_callable_(correctness_case_signature|workload_signature)\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
- `bash -lc "! rg -n '^(CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_(STR|BYTES|NEGATIVE_COUNT_BYTES)_WORKLOAD_IDS|_CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_WORKLOAD_STEMS|CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_(STR|BYTES)_WORKLOAD_IDS)\\s*=' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep the cleanup structural and bounded to the three benchmark support files listed above.
- Prefer the existing `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` owner surface over creating another broker file, another support module, or another layer of imported aliases.
- Preserve the current conditional callable workload ordering, signature tuple shapes, exception/no-match bits, and published-case anchoring behavior exactly.

## Notes
- `RBR-1267` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run; and
  - `rg -n "RBR-1267|RBR-1268|RBR-1269|RBR-1270" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -g '*.md'` found no reserved follow-on ids in tracked state or live queue files outside historical notes in older done-task files.
- No blocked architecture task exists to reopen or retire first in this run.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The simplification is concrete in the live checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `9997` lines in this run;
  - `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` is `1017` lines; and
  - `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` is `1686` lines.
- The conditional callable anchor ownership is still uniquely inline in the combined broker in this run:
  - `rg -n "_conditional_group_exists_(quantified|nested)_callable_(correctness_case_signature|workload_signature)" tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` matched only `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`; and
  - `rg -n "CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_(STR|BYTES|NEGATIVE_COUNT_BYTES)_WORKLOAD_IDS|_CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_WORKLOAD_STEMS|CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_(STR|BYTES)_WORKLOAD_IDS" tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` also matched only `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed with `45 passed`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed with `133 tests collected`.
  - `bash -lc "! rg -n 'def _conditional_group_exists_(quantified|nested)_callable_(correctness_case_signature|workload_signature)\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently fails because those four helpers still live inline in the combined suite, and that failure belongs to the exact cleanup queued here.
  - `bash -lc "! rg -n '^(CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_(STR|BYTES|NEGATIVE_COUNT_BYTES)_WORKLOAD_IDS|_CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_WORKLOAD_STEMS|CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_(STR|BYTES)_WORKLOAD_IDS)\\s*=' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently fails because the conditional callable workload-id inventories still live inline in the combined suite, and that failure belongs to the exact cleanup queued here.

## Completion
- Moved the nested and quantified conditional callable workload-id inventories plus their correctness/workload signature helpers into `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`, and updated `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to import them instead of owning local copies.
- Added focused owner-suite coverage in `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` for the moved nested/quantified callable signature shapes, exception/no-match bits, workload-id rejection paths, and the no-local-definition/imported-from-support contract in the combined broker.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` -> `52 passed`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` -> `140 tests collected`
  - `bash -lc "! rg -n 'def _conditional_group_exists_(quantified|nested)_callable_(correctness_case_signature|workload_signature)\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` -> passed
  - `bash -lc "! rg -n '^(CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_(STR|BYTES|NEGATIVE_COUNT_BYTES)_WORKLOAD_IDS|_CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_WORKLOAD_STEMS|CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_(STR|BYTES)_WORKLOAD_IDS)\\s*=' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` -> passed
