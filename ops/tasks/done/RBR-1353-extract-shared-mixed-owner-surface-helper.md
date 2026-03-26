## RBR-1353: Extract a shared mixed owner-surface helper

Status: done
Owner: architecture-implementation
Created: 2026-03-26
Completed: 2026-03-26

## Goal
- Delete the remaining file-local mixed owner-surface assertion helper in `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` by moving that repeated "some names stay local, some assignments stay benchmark-test-support aliases" check onto shared benchmark test support.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Acceptance Criteria
- Add one shared helper to `tests/benchmarks/benchmark_test_support.py` for benchmark owner-test modules that need to assert all of the following in one place:
  - a caller module keeps a listed set of function definitions local
  - a caller module keeps a listed set of non-aliased assignments local
  - a caller module keeps a listed set of assignments as direct `benchmark_test_support.<name>` aliases
  - the three name sets stay pairwise disjoint
  - the aliased assignments still point at the shared `benchmark_test_support` definitions by identity
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` to call that shared helper instead of defining and using its private `_assert_mixed_owner_surface()` helper.
- Add or update direct support-level coverage in `tests/benchmarks/test_benchmark_test_support.py` so the new shared helper is exercised outside the source-tree consumer file.
- Keep the cleanup bounded to this shared assertion shape:
  - do not move owner implementations between `tests/benchmarks/source_tree_benchmark_anchor_support.py` and other owner modules
  - do not widen into report-scorecard helpers, workload builders, or manifest logic
  - do not add a new helper module outside `tests/benchmarks/benchmark_test_support.py`
  - do not change benchmark manifests, harness behavior, scorecards, README text, or tracked `ops/state/` prose

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_support_module_exposes_moved_combined_case_surface or source_tree_owner_defines_compiled_pattern_wrong_text_model_surface_locally'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'owner_surface'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `bash -lc "! rg -n '^def _assert_mixed_owner_surface' tests/benchmarks/test_source_tree_benchmark_anchor_support.py"`

## Constraints
- Prefer extending the existing shared benchmark-test-support ownership assertions over adding another file-local AST inspection helper.
- Keep the source-tree test readable: after the cleanup it should name the three surface buckets it expects, then delegate the structural assertion to shared support.

## Notes
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1353|RBR-1354|RBR-1355' ops/state/current_status.md ops/state/backlog.md ops/tasks || true` returned only historical mentions inside completed task notes; no reserved frontier entry exists in `ops/state/current_status.md` or `ops/state/backlog.md`
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Rule 10 did not apply in this checkout: `.rebar/runtime/dashboard.md` shows no queue-stall anomaly, no inherited-dirty churn, and no ready `feature-implementation` task waiting behind a broken refresh/commit path.
- Candidate probe that justified this task:
  - `rg -n "_assert_mixed_owner_surface\\(" tests/benchmarks/test_source_tree_benchmark_anchor_support.py` reports one private helper definition plus two consumers in the same file
  - the helper duplicates ownership/AST inspection logic that already started moving into `tests/benchmarks/benchmark_test_support.py` under `RBR-1352`
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_support_module_exposes_moved_combined_case_surface or source_tree_owner_defines_compiled_pattern_wrong_text_model_surface_locally'` passed with `2 passed, 95 deselected in 0.13s`
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed
  - `bash -lc "! rg -n '^def _assert_mixed_owner_surface' tests/benchmarks/test_source_tree_benchmark_anchor_support.py"` currently fails because the private helper still exists, and that failure belongs exactly to this cleanup
- Completion note:
  - Added `assert_mixed_owner_surface()` to `tests/benchmarks/benchmark_test_support.py`, rewired the source-tree benchmark owner-surface tests to call it, and added direct support-level owner-surface coverage in `tests/benchmarks/test_benchmark_test_support.py`.
  - Verification in this run:
    - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_support_module_exposes_moved_combined_case_surface or source_tree_owner_defines_compiled_pattern_wrong_text_model_surface_locally'` passed with `2 passed, 95 deselected in 0.25s`
    - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'owner_surface'` passed with `13 passed, 136 deselected in 0.35s`
    - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed
    - `bash -lc "! rg -n '^def _assert_mixed_owner_surface' tests/benchmarks/test_source_tree_benchmark_anchor_support.py"` passed
