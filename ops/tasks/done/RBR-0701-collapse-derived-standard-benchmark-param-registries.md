# RBR-0701: Collapse derived standard benchmark param registries onto definition-driven queries

Status: done
Owner: architecture-implementation
Created: 2026-03-19

## Goal
- Remove the mirrored `STANDARD_BENCHMARK_*` parameter-registry block from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the standard benchmark owner keeps one canonical `STANDARD_BENCHMARK_DEFINITIONS` registry instead of a second layer of prefiltered tuples/lists that exist only to feed pytest parametrization.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` stops keeping these detached derived registries:
  - delete `STANDARD_BENCHMARK_MANIFEST_DEFINITIONS`;
  - delete `STANDARD_BENCHMARK_MANIFEST_IDS`;
  - delete `STANDARD_BENCHMARK_LEGACY_DEFINITIONS`;
  - delete `STANDARD_BENCHMARK_CALLBACK_PARITY_DEFINITIONS`;
  - delete `STANDARD_BENCHMARK_SPECIAL_UNANCHORED_DEFINITIONS`;
  - delete `STANDARD_BENCHMARK_SPECIAL_UNANCHORED_DIRECT_PARITY_DEFINITIONS`;
  - delete `STANDARD_BENCHMARK_SPECIAL_UNANCHORED_RESULT_PARITY_CASES`; and
  - delete `STANDARD_BENCHMARK_SPECIAL_UNANCHORED_RESULT_PARITY_IDS`.
- The parametrized standard-benchmark tests derive their parameter sets directly from `STANDARD_BENCHMARK_DEFINITIONS` instead of those detached registries:
  - `test_standard_benchmark_manifest_keeps_expected_workloads_in_scope` and `test_standard_benchmark_workloads_stay_anchored_to_published_correctness_cases` no longer read `STANDARD_BENCHMARK_MANIFEST_DEFINITIONS` / `STANDARD_BENCHMARK_MANIFEST_IDS`;
  - `test_standard_benchmark_special_unanchored_workloads_stay_explicit`, `test_standard_benchmark_special_unanchored_bytes_workloads_stay_covered_by_direct_parity_cases`, `test_standard_benchmark_legacy_workloads_stay_pinned_to_expected_case_ids`, and `test_standard_benchmark_workload_callbacks_match_anchor_case_results` no longer read detached filtered-definition tuples; and
  - `test_standard_benchmark_special_unanchored_workloads_match_manual_cpython_dispatch` no longer reads detached `(definition, workload_id)` pair or id tables.
- Preserve the current effective membership and ordering exactly:
  - the manifest-path parametrized tests still iterate the same `(definition, manifest_path)` pairs in the same order as the current `STANDARD_BENCHMARK_DEFINITIONS x manifest_paths` expansion;
  - the legacy, callback, special-unanchored, and direct-parity parametrized tests still cover the same definition subsets in the same definition order as today;
  - the manual-result parity test still iterates the same `(definition, workload_id)` pairs in the same order as the current `run_special_unanchored_result_parity` plus `expected_special_unanchored_workload_ids` expansion; and
  - the manifest-pair ids and special-unanchored result-parity ids stay identical to the current `"{definition.name}:{manifest_path.name}"` and `"{definition.name}:{workload_id}"` strings.
- Keep the canonical ownership boundary unchanged:
  - do not edit `STANDARD_BENCHMARK_DEFINITIONS` membership, anchored case ids, filters, supplemental direct-parity cases, or workload-id expectations except as needed to route the deleted derived registries through definition-driven parameter builders;
  - if a tiny file-local helper is still useful, keep it definition-driven and local to this file instead of adding another detached top-level registry block.
- Keep scope structural only:
  - do not change `python/rebar_harness/benchmarks.py`, workload modules under `benchmarks/workloads/`, tracked benchmark reports, or tracked project-state prose; and
  - do not broaden into removing `OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID`, `OPEN_ENDED_DIRECT_PARITY_BYTES_CASES`, `BASE_SOURCE_TREE_MANIFEST_IDS`, or `ZERO_GAP_PROMOTION_MANIFEST_IDS` in this task.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path

source = Path("tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py").read_text(
    encoding="utf-8"
)
for needle in (
    "STANDARD_BENCHMARK_MANIFEST_DEFINITIONS",
    "STANDARD_BENCHMARK_MANIFEST_IDS",
    "STANDARD_BENCHMARK_LEGACY_DEFINITIONS",
    "STANDARD_BENCHMARK_CALLBACK_PARITY_DEFINITIONS",
    "STANDARD_BENCHMARK_SPECIAL_UNANCHORED_DEFINITIONS",
    "STANDARD_BENCHMARK_SPECIAL_UNANCHORED_DIRECT_PARITY_DEFINITIONS",
    "STANDARD_BENCHMARK_SPECIAL_UNANCHORED_RESULT_PARITY_CASES",
    "STANDARD_BENCHMARK_SPECIAL_UNANCHORED_RESULT_PARITY_IDS",
):
    assert needle not in source, needle
print("ok")
PY`
  - `bash -lc "! rg -n 'STANDARD_BENCHMARK_MANIFEST_DEFINITIONS|STANDARD_BENCHMARK_MANIFEST_IDS|STANDARD_BENCHMARK_LEGACY_DEFINITIONS|STANDARD_BENCHMARK_CALLBACK_PARITY_DEFINITIONS|STANDARD_BENCHMARK_SPECIAL_UNANCHORED_DEFINITIONS|STANDARD_BENCHMARK_SPECIAL_UNANCHORED_DIRECT_PARITY_DEFINITIONS|STANDARD_BENCHMARK_SPECIAL_UNANCHORED_RESULT_PARITY_CASES|STANDARD_BENCHMARK_SPECIAL_UNANCHORED_RESULT_PARITY_IDS' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete one more mirrored parameter-registry layer inside the standard benchmark owner, not to reinterpret benchmark anchoring, change which workloads are intentionally special or legacy, or alter parity expectations.
- Prefer direct definition-driven parameter builders or inline filtered comprehensions over another detached constant block or another helper registry.

## Notes
- `RBR-0701` is the next available architecture-task id in the current checkout:
  - `python3 - <<'PY'
import pathlib, re
existing=set()
for base in ['ops/tasks/ready','ops/tasks/in_progress','ops/tasks/done','ops/tasks/blocked']:
    for path in pathlib.Path(base).glob('RBR-*.md'):
        m=re.match(r'(RBR-\\d+[A-Z]?)', path.name)
        if m:
            existing.add(m.group(1))
text='\\n'.join(pathlib.Path(p).read_text(encoding='utf-8') for p in ['ops/state/backlog.md','ops/state/current_status.md'])
mentioned=set(re.findall(r'RBR-\\d+[A-Z]?', text))
reserved=sorted(mentioned-existing, key=lambda s:(int(re.search(r'\\d+', s).group()), s))
existing_sorted=sorted(existing, key=lambda s:(int(re.search(r'\\d+', s).group()), s))
print('highest_existing_tail:', existing_sorted[-12:])
print('reserved_missing_tail:', reserved[-20:])
print('next_available:', 'RBR-0701')
PY` reported `RBR-0700` as the highest existing numeric task and no reserved missing ids at the tail.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the last recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The detached param-registry layer is concrete and bounded in the current checkout:
  - `rg -n 'STANDARD_BENCHMARK_MANIFEST_DEFINITIONS|STANDARD_BENCHMARK_MANIFEST_IDS|STANDARD_BENCHMARK_LEGACY_DEFINITIONS|STANDARD_BENCHMARK_CALLBACK_PARITY_DEFINITIONS|STANDARD_BENCHMARK_SPECIAL_UNANCHORED_DEFINITIONS|STANDARD_BENCHMARK_SPECIAL_UNANCHORED_DIRECT_PARITY_DEFINITIONS|STANDARD_BENCHMARK_SPECIAL_UNANCHORED_RESULT_PARITY_CASES|STANDARD_BENCHMARK_SPECIAL_UNANCHORED_RESULT_PARITY_IDS' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` shows the eight derived registries are declared once and consumed only by the standard benchmark parametrized tests in the same file;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently passes (`163 passed, 3 skipped, 1310 subtests passed in 26.15s`);
  - the inline source probe in Acceptance currently fails exactly on this cleanup with `AssertionError: STANDARD_BENCHMARK_MANIFEST_DEFINITIONS`; and
  - the final `rg` absence check in Acceptance currently fails exactly on this cleanup because all eight target names still exist.
- This simplification matches the current benchmark information flow:
  - `STANDARD_BENCHMARK_DEFINITIONS` already acts as the canonical registry for standard benchmark anchor contracts; and
  - deleting the mirrored filtered/pair/id registries removes one more parallel owner layer without changing the published benchmark surface.

## Completion Notes
- 2026-03-19: Replaced the detached standard benchmark manifest-pair, filtered-definition, and `(definition, workload_id)` parity registries with small file-local parameter builders that derive directly from `STANDARD_BENCHMARK_DEFINITIONS`.
- 2026-03-19: Repointed the affected `@pytest.mark.parametrize` decorators in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to those builders while preserving the existing subset membership, expansion order, and id strings.
- 2026-03-19: Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, the inline source probe from Acceptance, and `bash -lc "! rg -n 'STANDARD_BENCHMARK_MANIFEST_DEFINITIONS|STANDARD_BENCHMARK_MANIFEST_IDS|STANDARD_BENCHMARK_LEGACY_DEFINITIONS|STANDARD_BENCHMARK_CALLBACK_PARITY_DEFINITIONS|STANDARD_BENCHMARK_SPECIAL_UNANCHORED_DEFINITIONS|STANDARD_BENCHMARK_SPECIAL_UNANCHORED_DIRECT_PARITY_DEFINITIONS|STANDARD_BENCHMARK_SPECIAL_UNANCHORED_RESULT_PARITY_CASES|STANDARD_BENCHMARK_SPECIAL_UNANCHORED_RESULT_PARITY_IDS' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`.
