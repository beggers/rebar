# RBR-0656: Collapse the detached source-tree benchmark scorecard suite onto the combined boundary owner

Status: done
Owner: architecture-implementation
Created: 2026-03-19
Completed: 2026-03-19

## Goal
- Delete `tests/benchmarks/test_source_tree_benchmark_scorecards.py` by moving its remaining source-tree scorecard-case and runner coverage onto `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, so the source-tree shim benchmark publication has one owner instead of separate scorecard-versus-combined suites with parallel runner/assertion plumbing.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- Delete `tests/benchmarks/test_source_tree_benchmark_scorecards.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` becomes the sole owner for the direct `source_tree_scorecard_case(...)` / `source_tree_scorecard_case_ids()` coverage currently isolated in `tests/benchmarks/test_source_tree_benchmark_scorecards.py`:
  - keep the current raw scorecard-case definition contract explicit on the owner file:
    - `SOURCE_TREE_SCORECARD_EXPECTATIONS` entries still use direct `manifest_ids`, do not grow `full_manifest_ids`, and keep `selection_mode` limited to `"full"` or `"smoke"`;
    - `source_tree_scorecard_case("post-parser-workflows")` still derives the same manifest order and relative paths from `case.manifests`; and
    - `source_tree_scorecard_case("compile-smoke")` still restores the current single-manifest known-gap, representative-workload, and first-deferred follow-up expectations.
  - keep the current shared-manifest and selection-helper coverage explicit on the owner file:
    - scorecard cases and combined cases still reuse cached manifest records for the shared published manifests;
    - `selected_workload_ids_for_manifest(...)` still derives ids from the live manifests for the `compile-smoke`, `post-parser-workflows`, and `regression-pack-full` scorecard cases; and
    - the scorecard-case runner path still preserves any case-local `expected_workload_order`.
  - keep the current scorecard-specific zero-gap and representative-promotion coverage explicit on the owner file:
    - single-manifest scorecards still reuse `source_tree_combined_manifest_representative_measured_workload_ids(...)` for the zero-gap numbered-backreference and nested-group cases;
    - the scorecard-side `nested-group-replacement-boundary` assertions still keep the wider-ranged-repeat `str` branch-local-backreference rows and the broader-range open-ended bytes rows public/measured on the shared replacement surface;
    - the scorecard-side `nested-group-callable-replacement-boundary` assertions still keep the broader-range open-ended bytes callable rows public/measured; and
    - the existing branch-local-backreference and conditional-group-exists single-manifest scorecards still keep their slice-backed representative-workload coverage explicit instead of relying only on the combined suite.
  - keep the current scorecard runner contract explicit on the owner file:
    - `run_source_tree_benchmark_scorecard(...)` still regenerates every `source_tree_scorecard_case_ids()` case;
    - each regenerated scorecard still passes `assert_source_tree_benchmark_contract(...)` with the scorecard-case manifest set, selection mode, and tracked report path;
    - the per-manifest summaries still pass `assert_benchmark_manifest_contract(...)`; and
    - representative measured and representative known-gap workloads still pass `assert_benchmark_workload_contract(...)` with the current statuses.
  - keep any tiny local helper needed for this move file-local on `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` instead of creating another `*_support.py`, another detached scorecard suite, or moving this coverage onto `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py`.
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py` is deleted outright:
  - do not leave an import-only wrapper, compatibility shell, or renamed scorecard-specific suite behind.
- Keep scope structural only:
  - do not change `python/rebar_harness/benchmarks.py`, `tests/benchmarks/benchmark_expectations.py`, published reports, or tracked project-state prose in this run.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path

source = Path("tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py").read_text(
    encoding="utf-8"
)
for needle in (
    "source_tree_scorecard_case_ids(",
    "expected_first_deferred",
    "expected_workload_order",
    "assert_source_tree_benchmark_contract(",
    "assert_benchmark_manifest_contract(",
    "assert_benchmark_workload_contract(",
):
    assert needle in source, needle
print("ok")
PY`
  - `bash -lc "! rg --files tests/benchmarks | rg 'test_source_tree_benchmark_scorecards\\.py$'"`

## Constraints
- Keep this cleanup structural only. The point is to delete a detached source-tree scorecard owner, not to reinterpret benchmark expectations, slice inventories, or runner behavior.
- Prefer the existing combined source-tree benchmark owner and file-local helpers over another support module or another detached benchmark suite.
- Do not weaken the existing combined-slice and manifest-shape coverage while absorbing the scorecard-case assertions.

## Notes
- `RBR-0656` is the next available architecture task id in the current checkout:
  - `rg -n "RBR-0656|RBR-0657|RBR-0658" ops/state/backlog.md ops/state/current_status.md` returned no reserved future ids in that range; and
  - `find ops/tasks -maxdepth 2 -type f \( -name 'RBR-0655*' -o -name 'RBR-0656*' -o -name 'RBR-0657*' -o -name 'RBR-0658*' \) | sort` returned only the active feature task `ops/tasks/ready/RBR-0655-nested-broader-range-wider-ranged-repeat-branch-local-backreference-replacement-bytes-pack.md`.
- No blocked architecture task exists to reopen first, and rule 10 does not currently block another architecture cleanup:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the only ready task is the feature-owned `RBR-0655`.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The detached source-tree scorecard split is still concrete and bounded in the current checkout:
  - `wc -l tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` reports `480` lines for the detached scorecard suite and `1066` lines for the combined owner;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py` currently passes (`17 passed, 278 subtests passed in 1.39s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently passes (`22 passed, 862 subtests passed in 22.49s`);
  - `rg -n "test_raw_scorecard_case_definitions_use_direct_manifest_ids|test_post_parser_workflows_preserve_expected_manifest_paths|test_single_manifest_scorecards_keep_slice_backed_representatives|test_nested_group_replacement_scorecard_promotes_broader_range_branch_local_backreference_rows_to_measured|test_runner_regenerates_source_tree_scorecards" tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently matches only `tests/benchmarks/test_source_tree_benchmark_scorecards.py`;
  - the acceptance inline source probe currently fails exactly on this cleanup because `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` does not yet mention `source_tree_scorecard_case_ids(`, `expected_first_deferred`, or `expected_workload_order`; and
  - `bash -lc "! rg --files tests/benchmarks | rg 'test_source_tree_benchmark_scorecards\\.py$'"` currently fails exactly on this cleanup because the detached file still exists.
- The ownership simplification matches the current benchmark harness shape:
  - both files already assert the same `run_source_tree_benchmark_scorecard(...)` / `assert_source_tree_benchmark_contract(...)` / manifest-contract spine against the source-tree shim publication path; and
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` already imports `source_tree_scorecard_case(...)` for adjacent shared-surface assertions, so keeping one source-tree benchmark owner is a direct deletion rather than a new abstraction.

## Completion Note
- 2026-03-19: Moved the detached source-tree scorecard-case definition, manifest-path, selection-helper, zero-gap representative, and runner-contract assertions into `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, keeping the scorecard-specific helpers file-local on the owner suite.
- 2026-03-19: Deleted `tests/benchmarks/test_source_tree_benchmark_scorecards.py` outright after the combined owner absorbed the direct `SOURCE_TREE_SCORECARD_EXPECTATIONS`, `source_tree_scorecard_case(...)`, `source_tree_scorecard_case_ids()`, `expected_first_deferred`, and `expected_workload_order` coverage.
- 2026-03-19: Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` (`39 passed, 1140 subtests passed in 23.88s`), the acceptance inline source probe (`ok`), `bash -lc "! rg --files tests/benchmarks | rg 'test_source_tree_benchmark_scorecards\\.py$'"` (passes), and `git diff --name-status -- tests/benchmarks/test_source_tree_benchmark_scorecards.py` (`D`).
