## RBR-1298: Delete lazy standard-definition owner exports

Status: done
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Remove the remaining lazy `__getattr__` wrapper layer that benchmark support modules use only to expose their standard-definition tuples, so those modules publish ordinary constants instead of bespoke attribute indirection.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`
- `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_standard_benchmark_anchor_support.py`
- `tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py`

## Acceptance Criteria
- Replace the lazy owner-export pattern with ordinary module globals for these exact public names:
  - `tests/benchmarks/benchmark_test_support.py`: `COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS`
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py`: `MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS`
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py`: `SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS`
  - `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`: `COLLECTION_REPLACEMENT_STANDARD_BENCHMARK_DEFINITIONS`
  - `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py`: `PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS`
  - `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`: `COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS`
  - `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py`: `COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS`
- Delete the `__getattr__` functions from those six support modules once the constants are bound directly. Do not replace them with another custom export broker, registry, alias layer, or compatibility shim.
- Preserve behavior exactly:
  - keep every exported tuple name, tuple order, tuple contents, and definition-object identity unchanged;
  - keep the existing private cached builder functions available where current tests or support code still use them; and
  - ensure each exported constant is still the exact same object returned by its corresponding cached builder function.
- Update `tests/benchmarks/test_standard_benchmark_anchor_support.py` so it stops asserting that owner exports are absent from `vars(module)` and instead asserts the exports are direct module globals that still reuse the builder-returned tuple objects.
- Keep the missing-attribute coverage in `tests/benchmarks/test_standard_benchmark_anchor_support.py`, but retarget it away from the lazy-export implementation detail: the module should still raise ordinary `AttributeError` for unknown names without a custom `__getattr__`.
- Update `tests/benchmarks/test_benchmark_test_support.py` and `tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py` so their focused owner-export checks pin the direct-global shape rather than the lazy `__getattr__` path.
- Keep the cleanup structural and bounded to the nine files above. Do not change benchmark manifests, harness runners, scorecards, README text, or tracked `ops/state/` prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n '^def __getattr__' tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/pattern_boundary_benchmark_anchor_support.py tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py"`

## Constraints
- Prefer direct constant binding over another layer of indirection. The point is to delete export plumbing now that the owner tuples already exist, not to move that plumbing elsewhere.
- Do not change the cross-file ownership split landed in `RBR-1280` through `RBR-1297`; each benchmark family should keep owning its own definition tuple beside its existing selectors and signatures.
- Do not widen this into cache-policy changes. If a private builder stays `@cache`-decorated, that is fine; just stop routing public access through `__getattr__`.

## Notes
- `RBR-1298` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run;
  - the newest live task file before this change was `ops/tasks/done/RBR-1297-delete-compile-proxy-owner-module.md`; and
  - `rg -o "RBR-[0-9]{4}" ops/state/backlog.md ops/state/current_status.md | sort -u | tail -n 30` did not reserve any id above `RBR-0399`.
- No blocked architecture task exists to reopen or retire first in this run.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue/runtime state is not in the rule-10 stall case:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready tasks, no blocked tasks, and the most recent `architecture-implementation` run finished `done`; and
  - there is no inherited-dirty or commit-refresh anomaly in the latest dashboard snapshot.
- The live simplification target is concrete in the current checkout:
  - `bash -lc "! rg -n '^def __getattr__' tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/pattern_boundary_benchmark_anchor_support.py tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py"` currently fails exactly on the wrapper functions this task deletes; and
  - `PYTHONPATH=python:. ./.venv/bin/python - <<'PY' ...` probe work in this planning run showed each public owner-export tuple resolves today only through `__getattr__`, with the export name absent from `vars(module)`.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py` passed with `355 passed`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed with `443 tests collected`; and
  - the negative `rg` command in `Verification` currently fails because those six `__getattr__` wrappers still exist, and that failure belongs exactly to this cleanup.

## Completion
- Bound all seven owner-export tuples as direct module globals, deleted the six `__getattr__` wrappers, and kept each exported constant identical to its cached builder return value.
- Updated the focused benchmark support tests to assert direct-global exports plus ordinary missing-name `AttributeError` behavior without a lazy export path.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `bash -lc "! rg -n '^def __getattr__' tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/pattern_boundary_benchmark_anchor_support.py tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py"`
