# RBR-1204: Collapse synthetic benchmark workload builders onto shared test support

Status: done
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining file-local synthetic benchmark workload payload builders that are duplicated across the small benchmark support suites by consolidating them onto `tests/benchmarks/benchmark_test_support.py`, so these support tests share one ordinary Python helper path instead of hand-maintaining near-identical `workload_from_payload(...)` wrappers in each file.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_module_pattern_keyword_benchmark_anchor_support.py`
- `tests/benchmarks/test_wrong_text_model_benchmark_anchor_support.py`
- `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py`
- `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/test_recording_benchmark_module_support.py`
- `tests/benchmarks/test_grouped_alternation_benchmark_anchor_support.py`

## Acceptance Criteria
- Extend `tests/benchmarks/benchmark_test_support.py` with one shared synthetic workload builder that can express the current support-test workload shapes without adding another support module:
  - it must keep the current default benchmark payload fields used by these tests (`bucket`, `family`, `flags`, `use_compiled_pattern`, `count`, `maxsplit`, `kwargs`, `text_model`, `haystack_text_model`, `cache_mode`, `timing_scope`, warmup/sample/timed-sample fields, notes/categories/syntax_features, and smoke);
  - it must still allow the current per-test overrides for replacement, expected exceptions, positional windows, manifest id, categories, and compiled-pattern routing; and
  - it must return ordinary benchmark workload objects through `workload_from_payload(...)`, not invent a new intermediate representation.
- Refactor the listed benchmark support tests to use that shared helper and delete their local synthetic payload-builder wrappers instead of leaving thin aliases behind:
  - `test_collection_replacement_benchmark_anchor_support.py`: `_collection_replacement_workload`
  - `test_module_pattern_keyword_benchmark_anchor_support.py`: `_module_pattern_workload`
  - `test_wrong_text_model_benchmark_anchor_support.py`: `_workload`
  - `test_compiled_pattern_module_helper_benchmark_support.py`: `_workload`
  - `test_pattern_boundary_benchmark_anchor_support.py`: `_pattern_workload`
  - `test_recording_benchmark_module_support.py`: `_module_compile_contract_workload` and `_pattern_search_contract_workload`
  - `test_grouped_alternation_benchmark_anchor_support.py`: `_synthetic_workload`
- Keep scope bounded to payload construction only:
  - leave file-local case-object helpers in place when they encode assertion-specific shapes;
  - do not change benchmark anchor support modules, benchmark manifests, harness code, correctness fixtures, reports, README text, or tracked ops/state prose; and
  - do not widen this into a second refactor for live-manifest lookup helpers or broader `test_source_tree_combined_boundary_benchmarks.py` extraction work.
- Preserve the current assertions exactly:
  - the refactor must keep the current manifest ids, timing scopes, kwargs encoding, replacement/count/maxsplit handling, category handling, and text-model behavior intact in every touched test file; and
  - the current test names, parameter ids, and asserted workload signatures must stay the same apart from using the shared builder.
- Reuse the existing `tests/benchmarks/benchmark_test_support.py` owner instead of adding a new `*_support.py` layer.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_module_pattern_keyword_benchmark_anchor_support.py tests/benchmarks/test_wrong_text_model_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_recording_benchmark_module_support.py tests/benchmarks/test_grouped_alternation_benchmark_anchor_support.py`
- `bash -lc "! rg -n 'def _collection_replacement_workload\\(|def _module_pattern_workload\\(|def _pattern_workload\\(|def _module_compile_contract_workload\\(|def _pattern_search_contract_workload\\(|def _synthetic_workload\\(|^def _workload\\(' tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_module_pattern_keyword_benchmark_anchor_support.py tests/benchmarks/test_wrong_text_model_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_recording_benchmark_module_support.py tests/benchmarks/test_grouped_alternation_benchmark_anchor_support.py"`

## Notes
- `RBR-1204` is the next available unreserved task id in this checkout:
  - a repo-local id scan over `ops/tasks/**/*.md`, `ops/state/current_status.md`, and `ops/state/backlog.md` reported `1203` as the current maximum referenced id in this run; and
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this checkout, so this task does not collide with an existing live queue item.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Rule 10 does not block another architecture cleanup in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `Dirty worktree: false`, and `Last Cycle Anomalies: none`; and
  - the most recent cycle completed both an architecture cleanup and a feature task through the normal done path with no inherited-dirty or refresh/commit anomaly recorded.
- This simplification is concrete and still unfinished in the current checkout:
  - `bash -lc "! rg -n 'def _collection_replacement_workload\\(|def _module_pattern_workload\\(|def _pattern_workload\\(|def _module_compile_contract_workload\\(|def _pattern_search_contract_workload\\(|def _synthetic_workload\\(|^def _workload\\(' tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_module_pattern_keyword_benchmark_anchor_support.py tests/benchmarks/test_wrong_text_model_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_recording_benchmark_module_support.py tests/benchmarks/test_grouped_alternation_benchmark_anchor_support.py"` currently fails exactly on the duplicated builders this task targets; and
  - those wrappers all still feed `workload_from_payload(...)` with near-identical default payload scaffolding rather than using the existing shared benchmark test support owner.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_module_pattern_keyword_benchmark_anchor_support.py tests/benchmarks/test_wrong_text_model_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_recording_benchmark_module_support.py tests/benchmarks/test_grouped_alternation_benchmark_anchor_support.py` returned `41 passed in 0.13s`; and
  - the negative `rg` check named above currently fails exactly because the duplicated local builders are still present in this checkout.
- Completion note:
  - Added `synthetic_workload(...)` to `tests/benchmarks/benchmark_test_support.py` and switched the seven listed benchmark support tests over to it, preserving their existing manifest ids, timing scopes, kwargs handling, replacement/count/maxsplit behavior, category handling, and compiled-pattern routing without leaving local wrapper aliases behind.
  - Verification in this run: `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_module_pattern_keyword_benchmark_anchor_support.py tests/benchmarks/test_wrong_text_model_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_recording_benchmark_module_support.py tests/benchmarks/test_grouped_alternation_benchmark_anchor_support.py` returned `39 passed in 0.13s`, and the negative `rg` check from this task now succeeds.
