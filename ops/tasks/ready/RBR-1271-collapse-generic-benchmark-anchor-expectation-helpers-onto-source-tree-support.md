## RBR-1271: Collapse generic benchmark anchor expectation helpers onto source-tree support

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Remove the remaining duplicate generic anchor-expectation helper layer that is still split across `tests/benchmarks/standard_benchmark_anchor_support.py`, `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`, and `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py`, so the benchmark support stack has one shared owner for those tuple/anchor-map transformations instead of three near-identical copies.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/standard_benchmark_anchor_support.py`
- `tests/benchmarks/test_standard_benchmark_anchor_support.py`
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py`
- `tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py`

## Acceptance Criteria
- Extend `tests/benchmarks/source_tree_benchmark_anchor_support.py` so it becomes the single owner of these generic benchmark-anchor helper functions:
  - `_definition_anchor_expectations(...)`
  - `_workload_case_pairs_workload_ids(...)`
  - `_workload_case_pairs_case_ids(...)`
  - `_workload_case_pair_anchor_expectations(...)`
- Update these support modules to import and use that shared source-tree owner surface instead of defining local copies:
  - `tests/benchmarks/standard_benchmark_anchor_support.py`
  - `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
  - `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py`
- Preserve current behavior exactly:
  - keep the current manifest-name expansion shape for anchor expectations;
  - keep workload-id and case-id tuple ordering unchanged;
  - keep every current anchor map, route definition, contract lane, and benchmark selection path using the same helper results as before; and
  - do not add a new generic helper module, registry, manifest loader layer, or another wrapper around the shared source-tree support functions.
- Move the focused generic-helper coverage to the shared owner suite in `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`:
  - cover manifest-name expansion for `_definition_anchor_expectations(...)`;
  - cover tuple-order preservation for `_workload_case_pairs_workload_ids(...)` and `_workload_case_pairs_case_ids(...)`; and
  - cover single-case wrapping for `_workload_case_pair_anchor_expectations(...)`.
- Update the owner-adjacent suites so they follow the shared helper ownership boundary instead of assuming those helpers are still locally defined:
  - `tests/benchmarks/test_standard_benchmark_anchor_support.py`
  - `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
  - `tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py`
- Keep this cleanup structural and bounded to the benchmark support/test files above. Do not widen it into workload manifests, harness implementation code, scorecards, README text, or tracked `ops/state/` prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py`
- `bash -lc "! rg -n 'def _definition_anchor_expectations\\(|def _workload_case_pair_anchor_expectations\\(|def _workload_case_pairs_case_ids\\(|def _workload_case_pairs_workload_ids\\(' tests/benchmarks/standard_benchmark_anchor_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py"`

## Constraints
- Prefer the existing `tests/benchmarks/source_tree_benchmark_anchor_support.py` surface over creating another helper module. The point is to delete duplicate helper ownership, not move it behind a fresh abstraction.
- Do not change route-specific signature logic, compiled-pattern contract behavior, collection-replacement route inventories, standard benchmark definition contents, or anchor expectation values in this task.
- Keep imports direct; do not leave compatibility aliases or forwarding wrappers in the three former owner modules.

## Notes
- `RBR-1271` is the next available unreserved task id in this checkout:
  - `rg -n "RBR-1271|RBR-1272|RBR-1273|RBR-1274|RBR-1275" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked -g '*.md'` returned no matches in this run.
- No blocked architecture task exists to reopen or retire first in this run.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplicate helper ownership is concrete in the live checkout:
  - `rg -n "def _definition_anchor_expectations\\(|def _workload_case_pair_anchor_expectations\\(|def _workload_case_pairs_case_ids\\(|def _workload_case_pairs_workload_ids\\(" tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/standard_benchmark_anchor_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py` matched only the three non-shared support modules in this run;
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` is `662` lines in this run;
  - `tests/benchmarks/standard_benchmark_anchor_support.py` is `1913` lines;
  - `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` is `1424` lines; and
  - `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py` is `1129` lines.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed with `20 passed`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py` passed with `206 passed`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed with `57 passed`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py` passed with `81 passed`; and
  - the negative `rg` check in `Verification` currently fails because those helper definitions still live in the three former owner modules, and that failure belongs to the exact cleanup queued here.
