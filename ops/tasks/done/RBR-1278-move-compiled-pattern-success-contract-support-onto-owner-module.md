## RBR-1278: Move compiled-pattern success contract support onto owner module

Status: done
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Remove the remaining compiled-pattern success contract helpers that still live inside `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`, so the compiled-pattern benchmark layer keeps those payload-round-trip and measured-row ownership rules in `tests/benchmarks/compiled_pattern_module_success_benchmark_support.py` beside the existing owner-spec surface instead of in the test module.

## Deliverables
- `tests/benchmarks/compiled_pattern_module_success_benchmark_support.py`
- `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`

## Acceptance Criteria
- Extend `tests/benchmarks/compiled_pattern_module_success_benchmark_support.py` so it becomes the single owner of the remaining compiled-pattern success contract support surface currently defined in `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`:
  - `_assert_compiled_pattern_module_success_payload_round_trip(...)`
  - `_assert_compiled_pattern_success_rows_measured_in_combined_manifest(...)`
- Update `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py` to import and use that owner-owned surface instead of defining those helpers locally.
- Preserve current behavior exactly:
  - keep both owner specs using the same source-workload ordering, contract manifest ids, contract filenames, preserved payload fields, and replacement-typing expectations;
  - keep the measured-row helper asserting the same selected workload ids, manifest summary counts, zero-gap expectations, and scorecard contract checks against the live manifests;
  - keep the payload-round-trip helper asserting the same `use_compiled_pattern`, `expected_exception`, `haystack_text_model`, typed pattern/haystack payloads, preserved payload fields, and replacement typing semantics; and
  - keep the cleanup structural and bounded to the two files above, plus `tests/benchmarks/benchmark_test_support.py` only if a tiny shared helper import or move is required to support the ownership shift.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`
- `bash -lc "! rg -n 'def _assert_compiled_pattern_module_success_payload_round_trip\\(|def _assert_compiled_pattern_success_rows_measured_in_combined_manifest\\(' tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py"`

## Constraints
- Prefer consolidating onto the existing `tests/benchmarks/compiled_pattern_module_success_benchmark_support.py` owner module over creating another support file. The point is to finish the ownership move, not to add a parallel helper layer.
- Keep imports direct. Do not leave compatibility aliases or forwarding wrappers in `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`.
- Do not change compiled-pattern callback routing, workload selectors, manifest contents, or benchmark contract semantics in this task.

## Notes
- `RBR-1278` is the next available unreserved task id in this checkout:
  - `rg -n "RBR-1278|RBR-1279|RBR-1280|RBR-1281|RBR-1282" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked -g '*.md'` returned no matches in this run.
- No blocked architecture task exists to reopen or retire first in this run.
- JSON burn-down is complete in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue and runtime state are not currently stalled:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready tasks, no blocked tasks, and no last-cycle anomalies; and
  - the latest recorded cycle finished both `architecture-implementation` and `feature-implementation` tasks as `done`.
- The ownership split is concrete in the live checkout:
  - `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py` is `338` lines in this run and still defines `_assert_compiled_pattern_module_success_payload_round_trip(...)` and `_assert_compiled_pattern_success_rows_measured_in_combined_manifest(...)` locally;
  - `tests/benchmarks/compiled_pattern_module_success_benchmark_support.py` is `162` lines and already owns the adjacent `CompiledPatternModuleSuccessOwnerSpec` model plus the collection-replacement and module-boundary owner specs those helpers depend on; and
  - `rg -n "def _assert_compiled_pattern_module_success_payload_round_trip\\(|def _assert_compiled_pattern_success_rows_measured_in_combined_manifest\\(" tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py tests/benchmarks/compiled_pattern_module_success_benchmark_support.py` matched only the test module in this run.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py` passed with `46 passed`; and
  - the negative `rg` check in `Verification` currently fails because those helpers still live in the test module, and that failure belongs to the exact cleanup queued here.

## Completion
- Moved `_assert_compiled_pattern_module_success_payload_round_trip(...)` and `_assert_compiled_pattern_success_rows_measured_in_combined_manifest(...)` into `tests/benchmarks/compiled_pattern_module_success_benchmark_support.py` so the owner module now carries the remaining compiled-pattern success contract helpers beside the owner specs.
- Updated `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py` to import and use those owner-owned helpers directly, and tightened the local-duplicate guard so the moved helper names are no longer allowed as local test-module definitions.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py` -> `46 passed`
  - `bash -lc "! rg -n 'def _assert_compiled_pattern_module_success_payload_round_trip\\(|def _assert_compiled_pattern_success_rows_measured_in_combined_manifest\\(' tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py"` -> success
