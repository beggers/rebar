# RBR-1321: Route manifest-validation imports through benchmark-support owner

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Delete the direct 12-name `benchmark_test_support` owner import wall from `tests/benchmarks/test_benchmark_manifest_validation.py` so the suite reaches that shared benchmark-support surface through the existing `tests.benchmarks.benchmark_test_support` module owner instead of rebinding owner-owned names locally.

## Deliverables
- `tests/benchmarks/test_benchmark_manifest_validation.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- `tests/benchmarks/test_benchmark_manifest_validation.py` must stop using `from tests.benchmarks.benchmark_test_support import ...`.
- The manifest-validation suite must route the currently direct owner surface through the existing `benchmark_test_support` module import instead of binding those names locally:
  - `_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES`
  - `_SourceTreeContractBuilderSpec`
  - `_expected_exception_instance`
  - `_is_pattern_boundary_wrong_text_model_workload`
  - `_source_tree_contract_manifest`
  - `_source_tree_contract_workload`
  - `_write_test_manifest`
  - `CompiledPatternModuleCompileContractCase`
  - `assert_benchmark_workload_matches_expected_result`
  - `run_benchmark_workload_with_cpython`
  - `assert_pattern_helper_wrong_text_model_payload_round_trip`
  - `selected_manifest_workloads`
- Update `tests/benchmarks/test_benchmark_test_support.py` with one focused AST/import ownership check that proves:
  - `tests/benchmarks/test_benchmark_manifest_validation.py` no longer has a direct `ImportFrom` edge to `tests.benchmarks.benchmark_test_support`; and
  - those owner-owned names are no longer present in the manifest-validation suite's top-level definition/assignment namespace.
- Do not add a new helper module, alias shim, re-export layer, or compatibility wrapper. Reuse the existing `tests.benchmarks.benchmark_test_support` owner module already imported by the suite.
- Keep the cleanup structural:
  - do not move definitions out of `tests/benchmarks/benchmark_test_support.py`
  - do not change benchmark manifests, harness behavior, scorecard contents, README text, or tracked `ops/state/` prose

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_benchmark_test_support.py`
- `bash -lc "! rg -n '^from tests\\.benchmarks\\.benchmark_test_support import ' tests/benchmarks/test_benchmark_manifest_validation.py"`

## Constraints
- Keep the cleanup bounded to owner-boundary/import-plumbing simplification between the shared benchmark-support owner and the manifest-validation consumer suite.
- Prefer deleting the direct owner-name bindings over introducing another indirection layer or moving support logic again.

## Notes
- `RBR-1321` is the next available unreserved task id in this checkout:
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f \( -name 'RBR-1321*' -o -name 'RBR-1322*' -o -name 'RBR-1323*' \) | sort` returned no matches before this task was queued; and
  - `rg -n "RBR-1321|RBR-1322|RBR-1323" ops/state/current_status.md ops/state/backlog.md ops/tasks -g '*.md'` matched only historical mentions inside older done-task notes, not a live reservation for `RBR-1321`.
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
- Queue/runtime state was not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready tasks, no blocked tasks, and no ready `feature-implementation` work
  - the latest runtime snapshot shows the most recent `architecture-implementation` run finishing `done` and no inherited-dirty, refresh, or commit anomaly
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/test_benchmark_manifest_validation.py` still contains one direct `ImportFrom` edge to `tests.benchmarks.benchmark_test_support`
  - an AST probe in this run reported `direct-import-count 12` for that edge, covering the owner-owned compile-contract, source-tree contract, payload-round-trip, CPython-runner, and manifest-selection helpers listed above
  - the same suite already imports `tests.benchmarks.benchmark_test_support` as `benchmark_test_support`, so the current direct import block is now shadow owner plumbing rather than a required access path
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_benchmark_test_support.py` passed with `182 passed in 0.55s`
  - `bash -lc "! rg -n '^from tests\\.benchmarks\\.benchmark_test_support import ' tests/benchmarks/test_benchmark_manifest_validation.py"` currently fails because the manifest-validation suite still carries that direct owner import wall, and that failure belongs exactly to this cleanup
