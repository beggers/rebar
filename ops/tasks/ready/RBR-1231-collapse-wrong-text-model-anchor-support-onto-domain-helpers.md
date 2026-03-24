## RBR-1231: Collapse wrong-text-model anchor support onto domain helpers

Status: ready
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the standalone `tests/benchmarks/wrong_text_model_benchmark_anchor_support.py` layer now that its four helpers are only a thin bridge between richer benchmark-support owners, so wrong-text-model benchmark wiring lives on the existing pattern-boundary and compiled-pattern module helper support surfaces instead of on a dedicated extra module plus a dedicated extra test file.

## Deliverables
- `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`
- `tests/benchmarks/wrong_text_model_benchmark_owner_support.py`
- `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Delete the standalone wrong-text-model anchor helper layer:
  - remove `tests/benchmarks/wrong_text_model_benchmark_anchor_support.py`; and
  - remove `tests/benchmarks/test_wrong_text_model_benchmark_anchor_support.py`.
- Fold the direct-`Pattern` wrong-text-model helper trio onto the existing pattern-boundary support owner in `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py`:
  - move `_pattern_boundary_wrong_text_model_correctness_case_signature(...)`;
  - move `_pattern_boundary_wrong_text_model_workload_signature(...)`; and
  - move `_is_pattern_boundary_wrong_text_model_workload(...)`.
- Fold the compiled-pattern-first-argument module wrong-text-model selector onto the existing compiled-pattern helper owner in `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`:
  - move `_is_module_workflow_compiled_pattern_wrong_text_model_workload(...)`.
- Rehome the focused test coverage from the deleted dedicated test file onto the existing owner test files instead of recreating another wrapper surface:
  - put the direct-`Pattern` wrong-text-model selector/signature assertions into `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`;
  - put the compiled-pattern module wrong-text-model selector assertions into `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py`; and
  - keep the current wrong-text-model payload-round-trip validation reachable from `tests/benchmarks/test_benchmark_manifest_validation.py` and `tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py` without introducing a new `*_support.py` file.
- Update downstream imports to use the domain helpers directly:
  - `tests/benchmarks/wrong_text_model_benchmark_owner_support.py`;
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`; and
  - any touched benchmark-support tests.
- Preserve the current bounded benchmark behavior exactly:
  - the compiled-pattern-first-argument module-helper wrong-text-model trio on `benchmarks/workloads/module_boundary.py` stays on the existing `module-workflow-compiled-pattern-wrong-text-model` contract path;
  - the direct-`Pattern` wrong-text-model trio on `benchmarks/workloads/pattern_boundary.py` stays on the existing `pattern-boundary-wrong-text-model` contract path; and
  - do not widen this cleanup into collection-replacement wrong-text-model helpers, benchmark manifests, scorecards, harness implementation code, or new abstraction layers.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py -k 'wrong_text_model or compiled_pattern_module_boundary_validation_matches_manifest_and_payload_entry_points'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! test -e tests/benchmarks/wrong_text_model_benchmark_anchor_support.py && ! test -e tests/benchmarks/test_wrong_text_model_benchmark_anchor_support.py"`

## Constraints
- Keep the cleanup structural and bounded to the benchmark-support/test layer listed above. Do not modify workload manifests, `python/rebar_harness/benchmarks.py`, reports, README text, or tracked ops state prose.
- Prefer moving the existing helper bodies directly onto the domain support owners over leaving compatibility aliases that only forward to another module.
- Preserve the current wrong-text-model selector rules, signature tuple shapes, owner-spec contract behavior, and combined-suite contract definitions exactly.

## Notes
- `RBR-1231` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run;
  - the highest filed task is `RBR-1230`; and
  - `rg -n "RBR-1231|RBR-1232|RBR-1233|RBR-1234|RBR-1235" ops/state/backlog.md ops/state/current_status.md` returned no reserved follow-on ids in this range.
- No blocked architecture task exists to reopen or retire first in this run.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The simplification is concrete in the live checkout:
  - `tests/benchmarks/wrong_text_model_benchmark_anchor_support.py` is only `85` lines and exports exactly four helpers;
  - those helpers are imported only by `tests/benchmarks/wrong_text_model_benchmark_owner_support.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `tests/benchmarks/test_wrong_text_model_benchmark_anchor_support.py`; and
  - the destination owner modules already exist at `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py` and `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`.
- Verification status in this run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py -k 'wrong_text_model or compiled_pattern_module_boundary_validation_matches_manifest_and_payload_entry_points'` passed with `73 passed, 42 deselected`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_wrong_text_model_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py` also passed with `77 passed`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently succeeds, while the full combined suite is red for unrelated alternation-heavy callable replacement expectation drift, so this task uses collection-only coverage there to validate import rewiring without inheriting that separate failure.
