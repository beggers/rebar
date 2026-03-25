# RBR-1319: Delete shadow collection-replacement compiled-pattern success selector

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Delete the remaining shadow selector for the compiled-pattern collection/replacement success slice so `tests/benchmarks/benchmark_test_support.py` is the single owner of `_is_collection_replacement_compiled_pattern_success_workload(...)` and the collection-replacement anchor support module stops carrying its own copy.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`

## Acceptance Criteria
- Keep `_is_collection_replacement_compiled_pattern_success_workload(...)` defined only in `tests/benchmarks/benchmark_test_support.py`.
- Update `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` to import and reuse that shared selector instead of defining a local shadow copy.
- Update the affected benchmark-support tests so the ownership contract stays explicit:
  - `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` should prove the collection-replacement owner routes this selector through the shared support owner and no longer defines it locally.
  - `tests/benchmarks/test_benchmark_test_support.py` should keep or add one focused regression check that fails if the selector definition reappears outside the shared owner.
- Do not add a new helper module, alias shim, wrapper surface, or replacement selector abstraction. Reuse the existing shared owner module.
- Keep this cleanup structural:
  - do not change benchmark workload manifests, runtime harness behavior, scorecard contents, README text, or tracked `ops/state/` prose
  - do not move unrelated collection/replacement helper logic out of the current owner modules

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'compiled_pattern_success'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_success or compiled_pattern_contract_consumer_suites_reuse_shared_support_without_local_duplicates'`
- `test "$(rg -c '^def _is_collection_replacement_compiled_pattern_success_workload\\(' tests/benchmarks/benchmark_test_support.py)" = "1"`
- `! rg -n '^def _is_collection_replacement_compiled_pattern_success_workload\\(' tests/benchmarks/collection_replacement_benchmark_anchor_support.py`

## Constraints
- Keep the cleanup bounded to shared ownership of the compiled-pattern collection/replacement success selector.
- Prefer deleting the duplicated selector definition over introducing another indirection layer.

## Notes
- `RBR-1319` is the next available unreserved task id in this checkout:
  - `rg -n 'RBR-1319|RBR-1320|RBR-1321' ops/state/current_status.md ops/state/backlog.md` returned no matches in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f \( -name 'RBR-1319*' -o -name 'RBR-1320*' -o -name 'RBR-1321*' \) | sort` returned no matches before this task was queued.
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
- Queue/runtime state was not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready tasks, no blocked tasks, and no ready `feature-implementation` work
  - the latest runtime dashboard shows the most recent `architecture-implementation` run finishing `done` and no inherited-dirty, refresh, or commit anomaly
- The live simplification target is concrete in the current checkout:
  - `rg -n '^def _is_collection_replacement_compiled_pattern_success_workload\\(' tests/benchmarks/benchmark_test_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py` currently reports two definitions of the same selector, one in each owner module
  - `tests/benchmarks/benchmark_test_support.py` already owns the compiled-pattern module-success contract support that consumes this selector through `_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC`
  - `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` still defines an identical local copy even though that module already imports adjacent shared support helpers from `tests/benchmarks/benchmark_test_support.py`
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'compiled_pattern_success'` passed with `3 passed, 142 deselected in 0.10s`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_success or compiled_pattern_contract_consumer_suites_reuse_shared_support_without_local_duplicates'` passed with `4 passed, 110 deselected in 0.17s`
  - `test "$(rg -c '^def _is_collection_replacement_compiled_pattern_success_workload\\(' tests/benchmarks/benchmark_test_support.py)" = "1"` passed
  - `! rg -n '^def _is_collection_replacement_compiled_pattern_success_workload\\(' tests/benchmarks/collection_replacement_benchmark_anchor_support.py` currently fails because that module still defines the shadow selector locally, and that failure belongs exactly to this cleanup
- A broader `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` run is currently red for unrelated pre-existing failures in `test_collection_replacement_benchmark_anchor_support.py`, so the acceptance is intentionally narrowed to the green selector-focused slices above plus the exact duplicate-definition probe.
