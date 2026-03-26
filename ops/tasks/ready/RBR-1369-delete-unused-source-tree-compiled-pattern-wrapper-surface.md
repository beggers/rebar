# RBR-1369: Delete unused source-tree compiled-pattern wrapper surface

Status: ready
Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the remaining unused source-tree compiled-pattern wrapper surface from `tests/benchmarks/source_tree_benchmark_anchor_support.py` so the benchmark support layer stops carrying owner-local helpers that no benchmark suite consumes and that only restate behavior already available from `tests/benchmarks/benchmark_test_support.py`.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- Delete these unused source-tree wrapper helpers from `tests/benchmarks/source_tree_benchmark_anchor_support.py`:
  - `build_compiled_pattern_module_contract_anchor_lanes(...)`
  - `live_compiled_pattern_module_success_surface_ids(...)`
- Keep the real shared builder on `tests/benchmarks/benchmark_test_support.py`; do not move it again, duplicate it again, or leave a forwarding alias on the source-tree owner module.
- Update the touched benchmark support tests so they stop asserting that `tests/benchmarks/source_tree_benchmark_anchor_support.py` owns those two helper names and instead pin the leaner split:
  - the shared builder stays on `tests/benchmarks/benchmark_test_support.py`;
  - the source-tree owner no longer defines the dead wrapper surface; and
  - no benchmark support test file keeps a local ownership expectation for those two deleted names.
- Keep the cleanup structural only:
  - do not change benchmark manifests, runtime benchmark behavior, scorecard logic, or tracked project-state prose;
  - do not widen into other source-tree support moves in the same run.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'compiled_pattern_module_compile_standard_definition_surface_moves_to_shared_support or source_tree_owner_retires_compiled_pattern_module_compile_surface_to_shared_support'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'benchmark_test_support_owns_compiled_pattern_module_compile_standard_definitions or shared_compiled_pattern_helper_contract_tests_import_from_support'`
- `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py`
- `rg -n '^def build_compiled_pattern_module_contract_anchor_lanes\\b' tests/benchmarks/benchmark_test_support.py`
- `bash -lc "! rg -n '^def (build_compiled_pattern_module_contract_anchor_lanes|live_compiled_pattern_module_success_surface_ids)\\b' tests/benchmarks/source_tree_benchmark_anchor_support.py"`
- `bash -lc "! rg -n 'build_compiled_pattern_module_contract_anchor_lanes|live_compiled_pattern_module_success_surface_ids' tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py"`

## Constraints
- Prefer deleting these dead wrappers over relocating them sideways. The point is to remove unused owner-local surface, not to restage it behind another alias or helper broker.
- Keep `tests/benchmarks/source_tree_benchmark_anchor_support.py` focused on source-tree benchmark expectations and owner-specific support that still has live consumers after this cleanup.

## Notes
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1369|RBR-1370|RBR-1371' ops/state/current_status.md ops/state/backlog.md` returned no matches in this run
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate probe that justified this task:
  - `rg -n 'build_compiled_pattern_module_contract_anchor_lanes\\(|live_compiled_pattern_module_success_surface_ids' tests/benchmarks` shows repo-local references only in `tests/benchmarks/source_tree_benchmark_anchor_support.py`, `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`, and `tests/benchmarks/test_benchmark_test_support.py`
  - `rg -n '^def build_compiled_pattern_module_contract_anchor_lanes\\b' tests/benchmarks/benchmark_test_support.py` shows the shared builder already exists on the generic support module
  - the source-tree copies are therefore dead ownership residue rather than live support surface
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'compiled_pattern_module_compile_standard_definition_surface_moves_to_shared_support or source_tree_owner_retires_compiled_pattern_module_compile_surface_to_shared_support'` passed with `2 passed, 104 deselected in 0.16s`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'benchmark_test_support_owns_compiled_pattern_module_compile_standard_definitions or shared_compiled_pattern_helper_contract_tests_import_from_support'` passed with `2 passed, 168 deselected in 0.21s`
  - `rg -n '^def build_compiled_pattern_module_contract_anchor_lanes\\b' tests/benchmarks/benchmark_test_support.py` passed and reported the shared builder at line `2310`
  - `bash -lc "! rg -n '^def (build_compiled_pattern_module_contract_anchor_lanes|live_compiled_pattern_module_success_surface_ids)\\b' tests/benchmarks/source_tree_benchmark_anchor_support.py"` currently fails because both dead wrappers still live on the source-tree owner, and that failure belongs exactly to this cleanup
  - `bash -lc "! rg -n 'build_compiled_pattern_module_contract_anchor_lanes|live_compiled_pattern_module_success_surface_ids' tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py"` currently fails because the ownership tests still pin those deleted names, and that failure belongs exactly to this cleanup
