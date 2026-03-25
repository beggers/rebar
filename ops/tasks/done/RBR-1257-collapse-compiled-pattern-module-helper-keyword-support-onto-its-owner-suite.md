## RBR-1257: Collapse compiled-pattern module-helper keyword support onto its owner suite

Status: done
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Delete the now-single-consumer support layer in `tests/benchmarks/compiled_pattern_module_helper_keyword_benchmark_support.py` by moving its owned contract definitions into `tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py`, so this benchmark slice stops paying for an extra wrapper module that only forwards data to one owner suite.

## Deliverables
- `tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py`
- `tests/benchmarks/compiled_pattern_module_helper_keyword_benchmark_support.py`

## Acceptance Criteria
- Move the compiled-pattern module-helper keyword contract ownership into `tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py`:
  - rehome `_CompiledPatternModuleHelperKeywordContractSpec` and `_CompiledPatternModuleHelperKeywordContractSurface`;
  - rehome the two selector helpers `_is_collection_replacement_compiled_pattern_keyword_error_workload(...)` and `_is_collection_replacement_compiled_pattern_module_helper_keyword_workload(...)`; and
  - rehome the owned spec/source-workload/param registries now published as `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_*`.
- Preserve the current bounded surface exactly after the move:
  - the success lane must keep the same 11 source workload ids in the same order;
  - the keyword-error lane must keep the same 10 source workload ids in the same order;
  - the precompile-anchor subset must keep the same 3 workload ids in the same order; and
  - the owner suite must keep the same `86` passing tests without widening to other manifests or benchmark families.
- Delete `tests/benchmarks/compiled_pattern_module_helper_keyword_benchmark_support.py` once its owned definitions live in the owner suite, and remove the now-unused `support` import alias from the test file.
- Do not widen this cleanup into workload manifests, `python/rebar_harness/benchmarks.py`, reports, README text, or tracked `ops/state/` prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py`
- `bash -lc "test ! -e tests/benchmarks/compiled_pattern_module_helper_keyword_benchmark_support.py"`
- `bash -lc "! rg -n 'compiled_pattern_module_helper_keyword_benchmark_support' -g '*.py' tests/benchmarks"`

## Constraints
- Keep the cleanup structural and bounded to the compiled-pattern module-helper keyword owner suite and its single-consumer support file.
- Prefer deleting the extra support layer over introducing another shared helper, broker test, or replacement wrapper module.
- Preserve the existing workload-id ordering, contract-builder behavior, callback expectations, and measured probe coverage exactly.

## Notes
- `RBR-1257` is the next available unreserved task id in this checkout:
  - `rg -n "RBR-1257|RBR-1258|RBR-1259|RBR-1260" ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` found no reserved follow-on ids in this range outside historical note references.
- No blocked architecture task exists to reopen or retire first in this run.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The simplification is concrete in the live checkout:
  - `tests/benchmarks/compiled_pattern_module_helper_keyword_benchmark_support.py` is `427` lines in this run;
  - `tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py` is `445` lines; and
  - `rg -n "compiled_pattern_module_helper_keyword_benchmark_support" -g '*.py' tests/benchmarks` matched only the owner suite import in `tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py`.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py` passed with `86 passed`.
  - `bash -lc "test ! -e tests/benchmarks/compiled_pattern_module_helper_keyword_benchmark_support.py"` currently fails because the single-consumer support module still exists, and that failure belongs to the exact cleanup queued here.
  - `bash -lc "! rg -n 'compiled_pattern_module_helper_keyword_benchmark_support' -g '*.py' tests/benchmarks"` currently fails because the owner suite still imports the single-consumer support module, and that failure belongs to the exact cleanup queued here.

## Completion
- Inlined `_CompiledPatternModuleHelperKeywordContractSpec`, `_CompiledPatternModuleHelperKeywordContractSurface`, the compiled-pattern selector helpers, and all owned workload/surface registries directly into `tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py`.
- Deleted `tests/benchmarks/compiled_pattern_module_helper_keyword_benchmark_support.py` after the owner suite became self-contained.
- Verified the owner suite stays bounded to the same `86` passing tests and that no `tests/benchmarks/*.py` file still references `compiled_pattern_module_helper_keyword_benchmark_support`.
