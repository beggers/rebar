## RBR-1270: Move standard benchmark definition ownership onto standard support suite

Status: done
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Remove the remaining import-cycle-style ownership split where `tests/benchmarks/standard_benchmark_anchor_support.py` imports `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` just to fetch `_STANDARD_BENCHMARK_DEFINITIONS`, so the standard benchmark support layer becomes the single owner of those definitions and the giant combined benchmark suite stops acting as a hidden data registry for another support module.

## Deliverables
- `tests/benchmarks/standard_benchmark_anchor_support.py`
- `tests/benchmarks/test_standard_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`

## Acceptance Criteria
- Move the `_STANDARD_BENCHMARK_DEFINITIONS` tuple out of `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and make `tests/benchmarks/standard_benchmark_anchor_support.py` the single owner of the standard benchmark definition inventory.
- Delete the combined-suite import shim and proxy wrapper from `tests/benchmarks/standard_benchmark_anchor_support.py`:
  - `from tests.benchmarks import test_source_tree_combined_boundary_benchmarks as combined_suite`
  - `_standard_benchmark_definitions(...)`
  - `_StandardBenchmarkDefinitionsProxy`
  - `STANDARD_BENCHMARK_DEFINITIONS = _StandardBenchmarkDefinitionsProxy()`
- Replace that wrapper path with an ordinary support-owned tuple surface in `tests/benchmarks/standard_benchmark_anchor_support.py`, and update the existing helpers there to iterate over the direct tuple owner instead of lazily reaching back into the combined benchmark suite.
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to import and use the support-owned standard benchmark definitions instead of defining a local `_STANDARD_BENCHMARK_DEFINITIONS` block.
- Keep the current standard benchmark definition set behavior exactly the same:
  - preserve the current definition order, names, manifest paths, expected anchor case ids, include-workload selectors, workload signatures, callback-result parity flags, legacy-workload ids, and special-unanchored workload metadata;
  - do not introduce a new benchmark-definition registry, builder abstraction, generated data file, or another proxy/re-export wrapper to replace the deleted cycle; and
  - do not widen this cleanup into scorecard expectations, slice expectation helpers, workload manifests, `python/rebar_harness/benchmarks.py`, reports, README text, or tracked `ops/state/` prose.
- Add focused owner-suite coverage in `tests/benchmarks/test_standard_benchmark_anchor_support.py` that pins the new ownership boundary directly:
  - assert that `STANDARD_BENCHMARK_DEFINITIONS` is the direct support-owned tuple used by the standard benchmark helper parametrization path;
  - assert that the combined benchmark suite imports that support-owned definition tuple instead of defining its own local `_STANDARD_BENCHMARK_DEFINITIONS`; and
  - assert that `tests/benchmarks/standard_benchmark_anchor_support.py` no longer contains the combined-suite import/proxy path listed above.
- Update `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` wherever it still inspects `combined_suite._STANDARD_BENCHMARK_DEFINITIONS`, so its owner-contract coverage follows the support-owned definition surface instead of depending on the deleted private combined-suite alias.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `bash -lc "! rg -n 'test_source_tree_combined_boundary_benchmarks as combined_suite|return combined_suite\\._STANDARD_BENCHMARK_DEFINITIONS|class _StandardBenchmarkDefinitionsProxy|STANDARD_BENCHMARK_DEFINITIONS = _StandardBenchmarkDefinitionsProxy\\(\\)' tests/benchmarks/standard_benchmark_anchor_support.py"`
- `bash -lc "! rg -n '^_STANDARD_BENCHMARK_DEFINITIONS\\s*=\\s*\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep the cleanup structural and bounded to the four files above.
- Prefer deleting the hidden owner split over preserving compatibility aliases; the point of this task is to remove the support-module dependency on the combined test suite, not to move the same cycle behind another name.
- Preserve the current benchmark definition contents and parametrized test coverage exactly; this task changes ownership and information flow, not benchmark scope.

## Notes
- `RBR-1270` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contain no live task files in this run; and
  - `rg -n "RBR-1270|RBR-1271|RBR-1272|RBR-1273" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -g '*.md'` found no live reservation outside historical mentions inside older done-task notes.
- No blocked architecture task exists to reopen or retire first in this run.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining ownership split is concrete in the live checkout:
  - `tests/benchmarks/standard_benchmark_anchor_support.py` is `452` lines in this run;
  - `tests/benchmarks/test_standard_benchmark_anchor_support.py` is `419` lines in this run;
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `9551` lines in this run; and
  - `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` is `2873` lines in this run.
- The coupling this task removes is still present right now:
  - `rg -n 'test_source_tree_combined_boundary_benchmarks as combined_suite|return combined_suite\\._STANDARD_BENCHMARK_DEFINITIONS|class _StandardBenchmarkDefinitionsProxy|STANDARD_BENCHMARK_DEFINITIONS = _StandardBenchmarkDefinitionsProxy\\(\\)' tests/benchmarks/standard_benchmark_anchor_support.py` matched lines `366`, `369`, `372`, and `383`;
  - `rg -n '^_STANDARD_BENCHMARK_DEFINITIONS\\s*=\\s*\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` matched line `8209`; and
  - `rg -n 'combined_suite\\._STANDARD_BENCHMARK_DEFINITIONS' tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` still matched line `720`.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py` passed with `203 passed`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed with `348 tests collected`;
  - the first negative `rg` check in `Verification` currently fails because the support module still imports the combined suite and exposes the proxy wrapper, and that failure belongs to the exact cleanup queued here; and
  - the second negative `rg` check in `Verification` currently fails because the combined suite still owns a local `_STANDARD_BENCHMARK_DEFINITIONS` tuple, and that failure belongs to the exact cleanup queued here.

## Completion
- Moved the standard benchmark definition tuple into `tests/benchmarks/standard_benchmark_anchor_support.py` as the direct `STANDARD_BENCHMARK_DEFINITIONS` owner, using local builder imports to avoid recreating the old support-to-combined-suite dependency.
- Removed the combined-suite import shim, `_standard_benchmark_definitions(...)`, `_StandardBenchmarkDefinitionsProxy`, and the proxy-backed export from the support module.
- Updated `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to import the support-owned `STANDARD_BENCHMARK_DEFINITIONS` instead of defining a local `_STANDARD_BENCHMARK_DEFINITIONS` block.
- Updated owner-contract coverage in `tests/benchmarks/test_standard_benchmark_anchor_support.py` and switched the grouped callable collection-replacement check to the support-owned tuple surface in `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py` -> `206 passed`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` -> `351 tests collected`
  - `bash -lc "! rg -n 'test_source_tree_combined_boundary_benchmarks as combined_suite|return combined_suite\\._STANDARD_BENCHMARK_DEFINITIONS|class _StandardBenchmarkDefinitionsProxy|STANDARD_BENCHMARK_DEFINITIONS = _StandardBenchmarkDefinitionsProxy\\(\\)' tests/benchmarks/standard_benchmark_anchor_support.py"` -> passed
  - `bash -lc "! rg -n '^_STANDARD_BENCHMARK_DEFINITIONS\\s*=\\s*\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` -> passed
