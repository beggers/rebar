# RBR-0952: Collapse compiled-pattern module-helper keyword contract siblings

Status: done
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the remaining parallel success-versus-keyword-error contract helper families from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the compiled-pattern collection/replacement keyword contract flows through one shared file-local contract surface instead of maintaining two near-identical payload builders, contract-workload builders, manifest builders, payload round-trip assertions, and precompile/probe expectation helpers.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer keeps two parallel helper families for the compiled-pattern collection/replacement keyword contract:
  - success-side helpers:
    - `def _compiled_pattern_module_helper_keyword_manifest_payload(...)`
    - `def _compiled_pattern_module_helper_keyword_workload(...)`
    - `def _compiled_pattern_module_helper_keyword_manifest(...)`
    - `def _assert_compiled_pattern_module_helper_keyword_payload_round_trip(...)`
    - `def _compiled_pattern_module_helper_keyword_expected_build_calls(...)`
    - `def _compiled_pattern_module_helper_keyword_expected_callback_call(...)`
  - keyword-error-side helpers:
    - `def _compiled_pattern_module_helper_keyword_error_manifest_payload(...)`
    - `def _compiled_pattern_module_helper_keyword_error_contract_workload(...)`
    - `def _compiled_pattern_module_helper_keyword_error_manifest(...)`
    - `def _assert_compiled_pattern_module_helper_keyword_error_payload_round_trip(...)`
    - `def _compiled_pattern_module_helper_keyword_error_expected_build_calls(...)`
    - `def _compiled_pattern_module_helper_keyword_error_expected_callback_call(...)`
    - `def _compiled_pattern_module_helper_keyword_error_expected_callback_result(...)`
- Replace those sibling helper stacks with one shared file-local contract surface that is explicit but smaller than the current duplicated structure:
  - it may be a tiny frozen dataclass pair, a tuple of two spec dicts, or equivalent file-local metadata;
  - keep it local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`;
  - do not add a shared helper module, registry, or checked-in data layer; and
  - preserve the existing selector entry points `_compiled_pattern_module_helper_keyword_source_workloads()`, `_compiled_pattern_module_helper_keyword_precompile_anchor_source_workloads()`, and `_compiled_pattern_module_helper_keyword_error_source_workloads()` rather than widening into tracked workload changes.
- The shared contract surface must preserve both live source-workload slices exactly:
  - the success selector still resolves, in order, to:
    - `module-split-maxsplit-keyword-purged-str-compiled-pattern`
    - `module-split-maxsplit-indexlike-keyword-purged-bytes-compiled-pattern`
    - `module-split-maxsplit-bool-keyword-purged-bytes-compiled-pattern`
    - `module-sub-count-keyword-warm-str-compiled-pattern`
    - `module-sub-count-indexlike-keyword-warm-bytes-compiled-pattern`
    - `module-sub-count-bool-keyword-warm-str-compiled-pattern`
    - `module-sub-count-bool-false-keyword-warm-str-compiled-pattern`
    - `module-subn-count-keyword-purged-bytes-compiled-pattern`
    - `module-subn-count-indexlike-keyword-purged-str-compiled-pattern`
    - `module-subn-count-bool-keyword-purged-bytes-compiled-pattern`
    - `module-subn-count-bool-true-keyword-purged-bytes-compiled-pattern`
  - the keyword-error selector still resolves, in order, to:
    - `module-split-duplicate-maxsplit-keyword-purged-str-compiled-pattern`
    - `module-split-unexpected-keyword-purged-bytes-compiled-pattern`
    - `module-sub-duplicate-count-keyword-warm-str-compiled-pattern`
    - `module-sub-unexpected-keyword-purged-str-compiled-pattern`
    - `module-sub-unexpected-keyword-after-positional-count-purged-str-compiled-pattern`
    - `module-subn-duplicate-count-keyword-warm-bytes-compiled-pattern`
    - `module-subn-unexpected-keyword-purged-bytes-compiled-pattern`
    - `module-subn-unexpected-keyword-after-positional-count-purged-bytes-compiled-pattern`
  - both contract manifests still use manifest id `collection-replacement-boundary`;
  - both generated contract surfaces still append `-contract` to the live source workload ids in the same order; and
  - both contract surfaces still keep `use_compiled_pattern is True`, `haystack_text_model is None`, and the same `str` versus `bytes` payload typing for pattern, haystack, and replacement values.
- The shared helper surface must preserve the current semantic split instead of flattening behavior:
  - the success contract path still strips `expected_exception`, keeps the same keyword-carrier `count`/`maxsplit` and `kwargs` payloads, and still drives:
    - `test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_keyword_rows_until_helper_invocation(...)`
    - `test_compiled_pattern_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time(...)`
    - `test_run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_workloads(...)`
    - `test_compiled_pattern_module_helper_keyword_callbacks_precompile_first_argument_before_timing(...)`
  - the keyword-error contract path still preserves `expected_exception`, keeps the same `count`/`maxsplit` and `kwargs` payloads, and still drives:
    - `test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_keyword_error_rows_until_helper_invocation(...)`
    - `test_compiled_pattern_module_helper_keyword_error_callbacks_match_cpython_exceptions(...)`
    - `test_run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_error_workloads(...)`
    - `test_compiled_pattern_module_helper_callbacks_precompile_first_argument_before_timing(...)`
  - the success manifest-preservation path must still compare against `run_benchmark_workload_with_cpython(source_workload)`, while the keyword-error manifest-preservation and callback paths must still compare exact `TypeError` text against `_run_cpython_compiled_pattern_module_helper_keyword_workload(...)` and `run_benchmark_workload_with_cpython(...)`.
- The shared expectation helpers must keep the current precompile-first benchmark contract intact:
  - the success precompile test still anchors to the same three workloads from `_compiled_pattern_module_helper_keyword_precompile_anchor_source_workloads()`;
  - the keyword-error precompile test still covers all eight keyword-error rows;
  - purged rows still append `("purge",)` after the initial `("compile", pattern, flags)` call;
  - split/sub/subn callback-call expectations still preserve the same positional argument order and keyword-carrier values; and
  - the callback result surface remains `"module-result"` for split/sub and `("module-result", 0)` for subn.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword or compiled_pattern_module_helper_keyword_error'`
- `bash -lc "! rg -n 'def _compiled_pattern_module_helper_keyword_manifest_payload\\(|def _compiled_pattern_module_helper_keyword_workload\\(|def _compiled_pattern_module_helper_keyword_manifest\\(|def _assert_compiled_pattern_module_helper_keyword_payload_round_trip\\(|def _compiled_pattern_module_helper_keyword_expected_build_calls\\(|def _compiled_pattern_module_helper_keyword_expected_callback_call\\(|def _compiled_pattern_module_helper_keyword_error_manifest_payload\\(|def _compiled_pattern_module_helper_keyword_error_contract_workload\\(|def _compiled_pattern_module_helper_keyword_error_manifest\\(|def _assert_compiled_pattern_module_helper_keyword_error_payload_round_trip\\(|def _compiled_pattern_module_helper_keyword_error_expected_build_calls\\(|def _compiled_pattern_module_helper_keyword_error_expected_callback_call\\(|def _compiled_pattern_module_helper_keyword_error_expected_callback_result\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from tests.benchmarks.test_source_tree_combined_boundary_benchmarks import (
    _compiled_pattern_module_helper_keyword_error_source_workloads,
    _compiled_pattern_module_helper_keyword_source_workloads,
)

keyword_ids = tuple(
    workload.workload_id
    for workload in _compiled_pattern_module_helper_keyword_source_workloads()
)
keyword_error_ids = tuple(
    workload.workload_id
    for workload in _compiled_pattern_module_helper_keyword_error_source_workloads()
)

assert keyword_ids == (
    "module-split-maxsplit-keyword-purged-str-compiled-pattern",
    "module-split-maxsplit-indexlike-keyword-purged-bytes-compiled-pattern",
    "module-split-maxsplit-bool-keyword-purged-bytes-compiled-pattern",
    "module-sub-count-keyword-warm-str-compiled-pattern",
    "module-sub-count-indexlike-keyword-warm-bytes-compiled-pattern",
    "module-sub-count-bool-keyword-warm-str-compiled-pattern",
    "module-sub-count-bool-false-keyword-warm-str-compiled-pattern",
    "module-subn-count-keyword-purged-bytes-compiled-pattern",
    "module-subn-count-indexlike-keyword-purged-str-compiled-pattern",
    "module-subn-count-bool-keyword-purged-bytes-compiled-pattern",
    "module-subn-count-bool-true-keyword-purged-bytes-compiled-pattern",
)
assert keyword_error_ids == (
    "module-split-duplicate-maxsplit-keyword-purged-str-compiled-pattern",
    "module-split-unexpected-keyword-purged-bytes-compiled-pattern",
    "module-sub-duplicate-count-keyword-warm-str-compiled-pattern",
    "module-sub-unexpected-keyword-purged-str-compiled-pattern",
    "module-sub-unexpected-keyword-after-positional-count-purged-str-compiled-pattern",
    "module-subn-duplicate-count-keyword-warm-bytes-compiled-pattern",
    "module-subn-unexpected-keyword-purged-bytes-compiled-pattern",
    "module-subn-unexpected-keyword-after-positional-count-purged-bytes-compiled-pattern",
)

print("ok", len(keyword_ids), len(keyword_error_ids))
PY`

## Constraints
- Keep the cleanup structural and file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Do not edit `benchmarks/workloads/collection_replacement_boundary.py`, `python/rebar_harness/benchmarks.py`, reports, README/current-status/backlog prose, or non-benchmark test files in this run.
- Prefer deleting duplicate helpers and test-local plumbing over introducing another detached representation layer.

## Notes
- `RBR-0952` is the next available task id in the current checkout:
  - `rg -n 'RBR-0952|RBR-0953|RBR-0954|RBR-0955|RBR-0956' ops/state/backlog.md ops/state/current_status.md` returned no matches in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 20` currently ends at `RBR-0951-publish-module-workflow-module-replacement-count-alias-keyword-pair.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The shared-ready-queue stall rule does not apply in this run:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword or compiled_pattern_module_helper_keyword_error'` currently passes (`51 passed, 565 deselected, 8 subtests passed`);
  - the selector probe in Verification currently passes (`ok 11 8`), proving both contract surfaces already exist on the live manifest-selected benchmark workload paths; and
  - the negative `rg` check in Verification currently fails only because the duplicated success/error helper families are still present in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, which is the exact cleanup this task queues.

## Completion Note
- Landed a file-local frozen spec plus shared contract helpers in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, preserving the success and keyword-error selector entry points while deleting the duplicated success/error helper families named in this task.
- Verified with the targeted pytest slice (`51 passed, 565 deselected, 8 subtests passed`), the negative helper-name `rg` check, and the selector probe (`ok 11 8`).
