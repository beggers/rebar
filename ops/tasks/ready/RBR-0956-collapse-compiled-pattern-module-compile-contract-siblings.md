## RBR-0956: Collapse compiled-pattern module.compile contract siblings

Status: ready
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the remaining parallel compile-success versus compile-keyword contract helper/test stacks from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the compiled-pattern-first-argument `module.compile` benchmark contract runs through one file-local shared compile-contract surface instead of maintaining two near-identical manifest/workload builders, payload round-trip helpers, CPython expectation helpers, build-call helpers, and repeated manifest/probe/anchor/callback test bodies.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines or relies on these duplicated compile-success versus compile-keyword helper families:
  - `def _compiled_pattern_module_compile_success_manifest_payload(...)`
  - `def _compiled_pattern_module_compile_success_workload(...)`
  - `def _compiled_pattern_module_compile_success_manifest(...)`
  - `def _assert_compiled_pattern_module_compile_success_payload_round_trip(...)`
  - `def _run_cpython_compiled_pattern_module_compile_success_workload(...)`
  - `def _compiled_pattern_module_compile_success_expected_build_calls(...)`
  - `def _compiled_pattern_module_compile_keyword_manifest_payload(...)`
  - `def _compiled_pattern_module_compile_keyword_workload(...)`
  - `def _compiled_pattern_module_compile_keyword_manifest(...)`
  - `def _assert_compiled_pattern_module_compile_keyword_payload_round_trip(...)`
  - `def _run_cpython_compiled_pattern_module_compile_keyword_workload(...)`
  - `def _compiled_pattern_module_compile_keyword_expected_build_calls(...)`
- Replace those sibling helper stacks with one shared file-local compile-contract surface that is explicit but smaller than the current duplicated structure:
  - it may extend `CompiledPatternModuleCompileKeywordCaseGroup` or introduce a tiny adjacent frozen spec/helper surface;
  - keep it local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`;
  - do not add a shared helper module, registry, or checked-in data layer; and
  - preserve `_compiled_pattern_module_compile_success_source_workloads()`, `COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CASE_GROUPS`, and `_compiled_pattern_module_compile_keyword_source_workloads()` as the live selector entry points unless a tiny file-local successor preserves the same verification surface.
- Preserve the current bounded source-workload surfaces exactly:
  - the compile-success selector still resolves, in order, to:
    - `module-compile-literal-warm-str-compiled-pattern`
    - `module-compile-literal-purged-bytes-compiled-pattern`
    - `module-compile-named-group-warm-str-compiled-pattern`
    - `module-compile-named-group-purged-bytes-compiled-pattern`
  - the compile-keyword case groups still resolve, in order, to:
    - `int-zero`
      - `module-compile-flags-int-zero-warm-str-compiled-pattern`
      - `module-compile-flags-int-zero-purged-bytes-compiled-pattern`
    - `int-zero-named-group`
      - `module-compile-flags-int-zero-warm-str-compiled-pattern-named-group`
      - `module-compile-flags-int-zero-purged-bytes-compiled-pattern-named-group`
    - `bool-false`
      - `module-compile-flags-bool-false-warm-str-compiled-pattern`
      - `module-compile-flags-bool-false-purged-bytes-compiled-pattern`
    - `bool-false-named-group`
      - `module-compile-flags-bool-false-warm-str-compiled-pattern-named-group`
      - `module-compile-flags-bool-false-purged-bytes-compiled-pattern-named-group`
    - `ignorecase`
      - `module-compile-flags-ignorecase-warm-str-compiled-pattern`
      - `module-compile-flags-ignorecase-purged-bytes-compiled-pattern`
    - `ignorecase-named-group`
      - `module-compile-flags-ignorecase-warm-str-compiled-pattern-named-group`
      - `module-compile-flags-ignorecase-purged-bytes-compiled-pattern-named-group`
  - both contract surfaces still use manifest id `module-boundary`;
  - both contract surfaces still append `-contract` to the live source workload ids in the same order; and
  - both contract surfaces still keep `use_compiled_pattern is True`, `timing_scope == "module-helper-call"`, and `haystack_text_model is None`.
- Collapse the duplicate test bodies onto one shared compile-contract structure while preserving behavior:
  - `test_standard_benchmark_manifest_preserves_compiled_pattern_module_compile_success_rows_until_helper_invocation(...)` and `test_standard_benchmark_manifest_preserves_compiled_pattern_module_compile_keyword_rows_until_helper_invocation(...)` become one parametrized or equivalently shared compile-contract test body;
  - `test_compiled_pattern_module_compile_success_rows_stay_anchored_to_published_correctness_cases(...)` and `test_compiled_pattern_module_compile_keyword_rows_stay_anchored_to_published_correctness_cases(...)` become one parametrized or equivalently shared compile-contract test body;
  - `test_run_internal_workload_probe_measures_compiled_pattern_module_compile_success_workloads(...)` and `test_run_internal_workload_probe_measures_compiled_pattern_module_compile_keyword_workloads(...)` become one parametrized or equivalently shared compile-contract test body; and
  - `test_compiled_pattern_module_compile_success_callbacks_precompile_first_argument_before_timing(...)` and `test_compiled_pattern_module_compile_keyword_callbacks_precompile_first_argument_before_timing(...)` become one parametrized or equivalently shared compile-contract test body.
- The shared compile-contract surface must preserve the current success-versus-keyword semantic split instead of flattening behavior:
  - success rows still compare against `re.compile(compiled_pattern, workload.flags)`, return the precompiled pattern object from the callback path, and keep the current four literal/named-group anchor pairs:
    - `module-compile-literal-warm-str-compiled-pattern-contract` -> `workflow-module-compile-str-compiled-pattern`
    - `module-compile-literal-purged-bytes-compiled-pattern-contract` -> `workflow-module-compile-bytes-compiled-pattern`
    - `module-compile-named-group-warm-str-compiled-pattern-contract` -> `workflow-module-compile-str-compiled-pattern-named-group`
    - `module-compile-named-group-purged-bytes-compiled-pattern-contract` -> `workflow-module-compile-bytes-compiled-pattern-named-group`
  - keyword rows still compare against `re.compile(compiled_pattern, **workload.keyword_arguments())`, still preserve the type of `kwargs["flags"]`, still keep `kwargs.flags` materialization deferred until callback time, and still keep the current six keyword group anchor-pair sets exactly as declared on `COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CASE_GROUPS`;
  - ignorecase keyword rows still preserve the same `TypeError` behavior and exact message-substring matching against CPython;
  - warm rows still build exactly `[("compile", pattern, flags)]`;
  - purged rows still build exactly `[("compile", pattern, flags), ("purge",)]`; and
  - the callback path still makes the final recorded `compile` call against the precompiled pattern object, passing positional `flags` for success rows and the keyword-carrier `flags` value for keyword rows.
- Keep the remaining keyword-only coverage explicit:
  - `test_compiled_pattern_module_compile_keyword_kwargs_materialize_at_callback_time(...)` stays present or is replaced by an equivalent keyword-only shared assertion that still proves `kwargs.flags` is the only numeric field materialized at callback time; and
  - do not broaden into the surrounding compiled-pattern validation section except for minimal mechanical renames needed to keep the shared compile-contract helpers wired up.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile_success or compiled_pattern_module_compile_keyword'`
- `bash -lc "! rg -n 'def _compiled_pattern_module_compile_success_manifest_payload\\(|def _compiled_pattern_module_compile_success_workload\\(|def _compiled_pattern_module_compile_success_manifest\\(|def _assert_compiled_pattern_module_compile_success_payload_round_trip\\(|def _run_cpython_compiled_pattern_module_compile_success_workload\\(|def _compiled_pattern_module_compile_success_expected_build_calls\\(|def _compiled_pattern_module_compile_keyword_manifest_payload\\(|def _compiled_pattern_module_compile_keyword_workload\\(|def _compiled_pattern_module_compile_keyword_manifest\\(|def _assert_compiled_pattern_module_compile_keyword_payload_round_trip\\(|def _run_cpython_compiled_pattern_module_compile_keyword_workload\\(|def _compiled_pattern_module_compile_keyword_expected_build_calls\\(|test_standard_benchmark_manifest_preserves_compiled_pattern_module_compile_success_rows_until_helper_invocation|test_standard_benchmark_manifest_preserves_compiled_pattern_module_compile_keyword_rows_until_helper_invocation|test_compiled_pattern_module_compile_success_rows_stay_anchored_to_published_correctness_cases|test_compiled_pattern_module_compile_keyword_rows_stay_anchored_to_published_correctness_cases|test_run_internal_workload_probe_measures_compiled_pattern_module_compile_success_workloads|test_run_internal_workload_probe_measures_compiled_pattern_module_compile_keyword_workloads|test_compiled_pattern_module_compile_success_callbacks_precompile_first_argument_before_timing|test_compiled_pattern_module_compile_keyword_callbacks_precompile_first_argument_before_timing' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from tests.benchmarks.test_source_tree_combined_boundary_benchmarks import (
    COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CASE_GROUPS,
    MODULE_BOUNDARY_MANIFEST_PATH,
    _compiled_pattern_module_compile_success_source_workloads,
    _selected_manifest_workloads,
)

success_ids = tuple(
    workload.workload_id
    for workload in _compiled_pattern_module_compile_success_source_workloads()
)
assert success_ids == (
    "module-compile-literal-warm-str-compiled-pattern",
    "module-compile-literal-purged-bytes-compiled-pattern",
    "module-compile-named-group-warm-str-compiled-pattern",
    "module-compile-named-group-purged-bytes-compiled-pattern",
)

observed_groups = {
    group.group_id: tuple(
        workload.workload_id
        for workload in _selected_manifest_workloads(
            MODULE_BOUNDARY_MANIFEST_PATH,
            include_workload=group.selector,
        )
    )
    for group in COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CASE_GROUPS
}
assert observed_groups == {
    "int-zero": (
        "module-compile-flags-int-zero-warm-str-compiled-pattern",
        "module-compile-flags-int-zero-purged-bytes-compiled-pattern",
    ),
    "int-zero-named-group": (
        "module-compile-flags-int-zero-warm-str-compiled-pattern-named-group",
        "module-compile-flags-int-zero-purged-bytes-compiled-pattern-named-group",
    ),
    "bool-false": (
        "module-compile-flags-bool-false-warm-str-compiled-pattern",
        "module-compile-flags-bool-false-purged-bytes-compiled-pattern",
    ),
    "bool-false-named-group": (
        "module-compile-flags-bool-false-warm-str-compiled-pattern-named-group",
        "module-compile-flags-bool-false-purged-bytes-compiled-pattern-named-group",
    ),
    "ignorecase": (
        "module-compile-flags-ignorecase-warm-str-compiled-pattern",
        "module-compile-flags-ignorecase-purged-bytes-compiled-pattern",
    ),
    "ignorecase-named-group": (
        "module-compile-flags-ignorecase-warm-str-compiled-pattern-named-group",
        "module-compile-flags-ignorecase-purged-bytes-compiled-pattern-named-group",
    ),
}

print("ok", len(success_ids), len(observed_groups))
PY`

## Constraints
- Keep the cleanup structural and file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Do not edit `benchmarks/workloads/module_boundary.py`, `python/rebar_harness/benchmarks.py`, reports, README/current-status/backlog prose, or non-benchmark test files in this run.
- Prefer deleting duplicate helper/test plumbing over introducing another detached representation layer.

## Notes
- `RBR-0956` is the next available task id in the current checkout:
  - `rg -n 'RBR-0956|RBR-0957|RBR-0958|RBR-0959|RBR-0960' ops/state/backlog.md ops/state/current_status.md` returned no matches in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 12` currently ends at `RBR-0955-publish-compiled-pattern-module-replacement-count-alias-keyword-pair.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The shared-ready-queue stall rule does not apply in this run:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile_success or compiled_pattern_module_compile_keyword'` currently passes (`75 passed, 549 deselected, 18 subtests passed`);
  - the selector probe in Verification currently passes (`ok 4 6`), proving the live compile-success surface plus the six keyword case groups already exist directly on the tracked manifest-selected workload path; and
  - the negative `rg` check in Verification currently fails only because the duplicate compile-success and compile-keyword helper/test names called out in this task are still present in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
