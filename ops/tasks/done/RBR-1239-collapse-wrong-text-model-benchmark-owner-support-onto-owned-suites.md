## RBR-1239: Collapse wrong-text-model benchmark owner support onto owned suites

Status: done
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the standalone `tests/benchmarks/wrong_text_model_benchmark_owner_support.py` layer now that it only brokers bounded wrong-text-model contract coverage that is already owned by the dedicated collection-replacement, pattern-boundary, compiled-pattern-helper, and manifest-validation benchmark suites. The benchmark test layer should keep those selectors and expectations on the suites that already own the underlying surfaces instead of routing through a separate owner-spec module plus a second dedicated test file.

## Deliverables
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py`
- `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`
- `tests/benchmarks/wrong_text_model_benchmark_owner_support.py`
- `tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py`

## Acceptance Criteria
- Delete the standalone wrong-text-model owner layer:
  - remove `tests/benchmarks/wrong_text_model_benchmark_owner_support.py`;
  - remove `tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py`; and
  - update benchmark-test imports so no `tests/benchmarks/*.py` file still imports `wrong_text_model_benchmark_owner_support`.
- Rehome the direct `Pattern` wrong-text-model coverage onto the suites that already own those selectors and signatures:
  - move the collection/replacement direct-pattern callback/build/runtime expectations onto `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`; and
  - move the pattern-boundary direct-pattern callback/build/runtime expectations onto `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`.
- Rehome the compiled-pattern module-helper wrong-text-model coverage onto the suite that already owns the shared route helper:
  - move the compiled-pattern callback/build/runtime expectations for the wrong-text-model rows onto `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py`; and
  - keep that suite using the existing `_compiled_pattern_module_helper_route(...)`, `_run_cpython_compiled_pattern_module_helper_workload(...)`, and `_is_module_workflow_compiled_pattern_wrong_text_model_workload(...)` surfaces directly instead of recreating a new broker module.
- Keep the manifest-validation coverage, but stop routing it through the deleted owner-support module:
  - move the wrong-text-model payload round-trip assertion into `tests/benchmarks/test_benchmark_manifest_validation.py` or another already-owned benchmark contract test file; and
  - keep it validating the current wrong-text-model contract shape for the bounded pattern-boundary source workload rows without importing the deleted module.
- Preserve the current bounded source-workload surfaces exactly:
  - the collection-replacement direct-pattern wrong-text-model rows selected via `_is_collection_replacement_pattern_wrong_text_model_workload(...)` from `benchmarks/workloads/collection_replacement_boundary.py` must stay identical and in the same order;
  - the pattern-boundary wrong-text-model rows selected via `_is_pattern_boundary_wrong_text_model_workload(...)` from `benchmarks/workloads/pattern_boundary.py` must stay identical and in the same order;
  - the compiled-pattern collection-replacement wrong-text-model rows selected via `_is_collection_replacement_wrong_text_model_workload(...)` from `benchmarks/workloads/collection_replacement_boundary.py` must stay identical and in the same order; and
  - the compiled-pattern module-boundary wrong-text-model rows selected via `_is_module_workflow_compiled_pattern_wrong_text_model_workload(...)` from `benchmarks/workloads/module_boundary.py` must stay identical and in the same order.
- Preserve current benchmark-contract behavior exactly:
  - keep the existing `TypeError` message comparisons for string/bytes text-model mismatches;
  - keep the current callback-call shapes and pre-build call ordering for warm versus purged workloads; and
  - do not widen this cleanup into workload manifests, `python/rebar_harness/benchmarks.py`, reports, README text, or tracked ops state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_benchmark_manifest_validation.py`
- `bash -lc "! test -e tests/benchmarks/wrong_text_model_benchmark_owner_support.py && ! test -e tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py"`

## Constraints
- Keep the cleanup structural and bounded to the benchmark test/support layer listed above.
- Prefer moving expectations onto existing owner suites over introducing another shared helper module or moving helpers between benchmark test files.
- Preserve workload-id ordering, callback semantics, and exact CPython exception-text assertions.

## Notes
- `RBR-1239` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run; and
  - `rg -n "RBR-1239|RBR-1240|RBR-1241|RBR-1242|RBR-1243|RBR-1244|RBR-1245" ops/state/backlog.md ops/state/current_status.md` returned no reserved follow-on ids in this range.
- No blocked architecture task exists to reopen or retire first in this run.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The live checkout still carries a removable owner-only layer:
  - `tests/benchmarks/wrong_text_model_benchmark_owner_support.py` is `380` lines and `tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py` is `409` lines;
  - `rg -l "wrong_text_model_benchmark_owner_support" tests/benchmarks -g '*.py'` matches only `tests/benchmarks/test_benchmark_manifest_validation.py` and `tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py`; and
  - the underlying wrong-text-model selectors already live on the dedicated owner modules `collection_replacement_benchmark_anchor_support.py`, `pattern_boundary_benchmark_anchor_support.py`, and `compiled_pattern_module_helper_benchmark_support.py`.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_benchmark_manifest_validation.py` passed with `74 passed`.
  - `bash -lc "! test -e tests/benchmarks/wrong_text_model_benchmark_owner_support.py && ! test -e tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py"` currently fails because both files still exist, and that failure belongs to the exact cleanup queued here.

## Completion
- 2026-03-24: Moved the wrong-text-model benchmark owner coverage onto the existing collection-replacement, pattern-boundary, compiled-pattern-module-helper, and manifest-validation suites; deleted `tests/benchmarks/wrong_text_model_benchmark_owner_support.py` and `tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py`; verified `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_benchmark_manifest_validation.py` (`141 passed`), `bash -lc "! test -e tests/benchmarks/wrong_text_model_benchmark_owner_support.py && ! test -e tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py"`, and `git diff --name-status -- tests/benchmarks/wrong_text_model_benchmark_owner_support.py tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py` (both `D`).
