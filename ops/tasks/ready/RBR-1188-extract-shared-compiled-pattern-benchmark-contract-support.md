# RBR-1188: Extract shared compiled-pattern benchmark contract support

Status: ready
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining duplicated compiled-pattern benchmark-contract plumbing that still lives in multiple benchmark support modules by moving it onto one shared support module, so the compiled-pattern benchmark owner files stop each carrying their own copy of the same cache-build-call helper and identical contract excluded-field set.

## Deliverables
- `tests/benchmarks/compiled_pattern_contract_benchmark_support.py`
- `tests/benchmarks/test_compiled_pattern_contract_benchmark_support.py`
- `tests/benchmarks/compiled_pattern_module_helper_keyword_benchmark_support.py`
- `tests/benchmarks/compiled_pattern_module_success_benchmark_support.py`
- `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py`
- `tests/benchmarks/wrong_text_model_benchmark_owner_support.py`

## Acceptance Criteria
- Add one bounded shared support module at `tests/benchmarks/compiled_pattern_contract_benchmark_support.py` for the duplicated compiled-pattern benchmark-contract behavior that is currently split across the compiled-pattern support files:
  - move the shared cache-build-call helper that currently lives in `tests/benchmarks/compiled_pattern_module_helper_keyword_benchmark_support.py` into that module;
  - expose one shared excluded-fields constant for the compiled-pattern module-helper contract payload shape that currently appears as identical `frozenset(...)` literals in `tests/benchmarks/compiled_pattern_module_success_benchmark_support.py`, `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py`, and `tests/benchmarks/wrong_text_model_benchmark_owner_support.py`; and
  - keep the moved helper behavior pinned to the current `warm` and `purged` cache modes only, still returning `[("compile", ...)]` for warm workloads and `[("compile", ...), ("purge",)]` for purged workloads while rejecting any other cache mode with the current assertion surface.
- Update the affected benchmark support modules to import the shared support directly instead of carrying local copies:
  - remove the local `_compiled_pattern_contract_expected_build_calls(...)` definition from `tests/benchmarks/compiled_pattern_module_helper_keyword_benchmark_support.py`;
  - replace the local identical compiled-pattern contract excluded-field literals in `tests/benchmarks/compiled_pattern_module_success_benchmark_support.py`, `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py`, and `tests/benchmarks/wrong_text_model_benchmark_owner_support.py` with the shared constant;
  - keep `tests/benchmarks/compiled_pattern_module_success_benchmark_support.py` on the same successful compiled-pattern module-boundary and collection/replacement contract behavior after the extraction;
  - keep `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py` on the same compiled-pattern `module.compile` success and keyword contract behavior after the extraction; and
  - keep `tests/benchmarks/wrong_text_model_benchmark_owner_support.py` on the same compiled-pattern wrong-text-model contract payload shape after the extraction.
- Add one focused support test file at `tests/benchmarks/test_compiled_pattern_contract_benchmark_support.py` that pins the new shared helper module without reintroducing another owner-file dependency:
  - cover the shared excluded-fields constant shape directly; and
  - cover the shared build-call helper for one `warm` workload, one `purged` workload, and one rejecting cache-mode case.
- Delete the duplicated local support definitions instead of leaving aliases or wrapper passthroughs behind.
- Do not widen this cleanup into benchmark manifest edits, `python/rebar_harness/benchmarks.py`, correctness fixtures, reports, README text, or tracked ops state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_contract_benchmark_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py`

## Constraints
- Keep this cleanup structural and limited to the compiled-pattern benchmark-contract support layer above.
- Prefer one ordinary shared support module over more owner-to-owner imports or another duplicate local copy.
- Do not turn this into a broader breakup of the benchmark owner files; this task is only the bounded shared compiled-pattern contract-support extraction above.

## Notes
- `RBR-1188` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contain no live `RBR-1188` file; and
  - `rg -n "RBR-118[89]|RBR-119[0-9]|RBR-12[0-9]{2}" ops/state/current_status.md ops/state/backlog.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done` matched only stale completion-note mentions for `RBR-1188`, not a live reservation.
- No blocked architecture task exists to reopen or retire first in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication is still present in the current checkout:
  - `rg -n "_COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS|_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SHARED_EXCLUDED_FIELDS|_compiled_pattern_contract_expected_build_calls" tests/benchmarks` shows the shared excluded-field literal duplicated across `tests/benchmarks/compiled_pattern_module_success_benchmark_support.py`, `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py`, and `tests/benchmarks/wrong_text_model_benchmark_owner_support.py`, while `_compiled_pattern_contract_expected_build_calls(...)` still lives in `tests/benchmarks/compiled_pattern_module_helper_keyword_benchmark_support.py` and is imported back into the other compiled-pattern owner files;
  - `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py` is still `1112` lines in this run and still carries compiled-pattern contract route wiring that imports the helper back from the helper-keyword module; and
  - no shared benchmark-support module currently owns this exact compiled-pattern contract support surface.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_contract_benchmark_support.py` is expected to fail right now because that focused support test file does not exist yet, and that failure belongs to the exact cleanup queued here.
  - `.venv/bin/python -m pytest tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py` returned `125 passed in 0.19s` in this run.
