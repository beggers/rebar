## RBR-1386: Delete source-tree path and case-id wrappers

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the two thin source-tree utility wrappers from the shared benchmark support layer, and have the combined source-tree benchmark suite use the existing underlying manifest paths and scorecard expectation registry directly instead of routing those reads through helper functions.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Acceptance Criteria
- Remove these wrapper helpers from `tests/benchmarks/source_tree_benchmark_anchor_support.py` without replacing them with another alias, helper, or registry layer:
  - `relative_manifest_path`
  - `source_tree_scorecard_case_ids`
- Rewrite `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the affected assertions keep the same behavior through direct reads of the existing owner data:
  - repo-relative manifest-path checks should derive strings directly from `manifest.path.relative_to(REPO_ROOT)` at the call sites instead of through `source_tree_support.relative_manifest_path(...)`;
  - scorecard-case iteration should derive ids directly from the existing `SOURCE_TREE_SCORECARD_EXPECTATIONS` owner surface instead of through `source_tree_support.source_tree_scorecard_case_ids()`;
  - preserve current ordering, selected-manifest coverage, tracked-report freshness checks, and scorecard row identities.
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so it treats the deleted wrappers as absent from the source-tree support module while keeping the remaining shared support API and no-local-duplicate ownership checks precise enough to catch regressions.
- Do not change benchmark manifests, workload ids, benchmark execution behavior, published row ids, or tracked project-state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'relative_manifest_path or source_tree_scorecard_case_ids or tracked_report_keeps_sample_manifests_fresh or manifest_paths'`
- `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n '^(def (relative_manifest_path|source_tree_scorecard_case_ids)\\()|source_tree_support\\.(relative_manifest_path|source_tree_scorecard_case_ids)\\(' tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Prefer direct `manifest.path.relative_to(REPO_ROOT)` and direct iteration of `SOURCE_TREE_SCORECARD_EXPECTATIONS` over another shared helper.
- Keep the run bounded to deleting these two wrappers and rewiring their current consumers; do not reopen the broader `_SourceTreeContractBuilderSpec` / contract-manifest builder stack in the same task.

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`.
  - `git status --short` was empty in this run, so the runtime counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- ID and duplicate check in this run:
  - `rg -n 'RBR-1386|RBR-1387|RBR-1388|RBR-1389' ops/state/current_status.md ops/state/backlog.md` returned no reserved future id hits for `RBR-1386`.
  - `ls -1 ops/tasks/ready`, `ls -1 ops/tasks/in_progress`, and `ls -1 ops/tasks/blocked` were empty in this checkout.
  - No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate selection in this run:
  - I inspected the `_SourceTreeContractBuilderSpec` / `_source_tree_contract_manifest(...)` stack first, but that cleanup is still wired through multiple owner records and validation tests, so it is larger than one bounded architecture-implementation run.
  - `relative_manifest_path(...)` and `source_tree_scorecard_case_ids()` are both thin wrappers over data the combined source-tree benchmark suite already has locally: `manifest.path.relative_to(REPO_ROOT)` and `SOURCE_TREE_SCORECARD_EXPECTATIONS`.
  - Their live call sites are bounded to the source-tree support module and the combined source-tree benchmark suite, so deleting them removes one more shared transit layer without touching runtime harness logic or benchmark publications.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'relative_manifest_path or source_tree_scorecard_case_ids or tracked_report_keeps_sample_manifests_fresh or manifest_paths'` passed with `3 passed, 384 deselected in 0.21s`.
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed.
  - `rg -n '^(def (relative_manifest_path|source_tree_scorecard_case_ids)\()|source_tree_support\.(relative_manifest_path|source_tree_scorecard_case_ids)\(' tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently reports the exact wrapper definitions and direct call sites this task is intended to delete.
