## RBR-1261: Delete dead standard-anchor helper duplicates from combined benchmark broker

Status: done
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Shrink `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by deleting the dead local copies of standard benchmark anchor helpers that are already owned and tested in `tests/benchmarks/standard_benchmark_anchor_support.py`, so the 10k-line combined broker stops carrying duplicate support logic that it does not use.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/standard_benchmark_anchor_support.py`
- `tests/benchmarks/test_standard_benchmark_anchor_support.py`

## Acceptance Criteria
- Delete these three dead helper definitions from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`:
  - `_definition_workloads_by_id(...)`
  - `_direct_parity_case_ids_by_signature(...)`
  - `_manual_expected_result(...)`
- Keep `tests/benchmarks/standard_benchmark_anchor_support.py` as the single owner of those helpers; do not add a new wrapper module, alias layer, or copied helper block elsewhere.
- Remove any imports from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` that become unused only because those dead duplicate helpers were deleted.
- Preserve the current standard benchmark anchor support surface exactly:
  - `tests/benchmarks/test_standard_benchmark_anchor_support.py` must keep exercising the support-owned helper implementations;
  - `tests/benchmarks/standard_benchmark_anchor_support.py` must keep exporting the same helper names and `STANDARD_BENCHMARK_DEFINITIONS` surface; and
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` must keep collecting cleanly without reintroducing local fallback copies of the deleted helpers.
- Do not widen this cleanup into workload manifests, `python/rebar_harness/benchmarks.py`, reports, README text, or tracked `ops/state/` prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_standard_benchmark_anchor_support.py`
- `bash -lc "! rg -n 'def (_definition_workloads_by_id|_direct_parity_case_ids_by_signature|_manual_expected_result)\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep the cleanup structural and bounded to the three benchmark support files listed above.
- Prefer deleting the dead duplicate code over moving it to another broker file or adding indirection.
- Do not change the semantics, signatures, or call sites of the support-owned helper implementations.

## Notes
- `RBR-1261` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run; and
  - `rg -n "RBR-1261|RBR-1262|RBR-1263|RBR-1264" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -g '*.md'` found no reserved follow-on ids in tracked state or live queue files outside historical note text in an older done-task note.
- No blocked architecture task exists to reopen or retire first in this run.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The simplification is concrete in the live checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `10410` lines in this run;
  - `tests/benchmarks/standard_benchmark_anchor_support.py` is `452` lines; and
  - `tests/benchmarks/test_standard_benchmark_anchor_support.py` is `419` lines.
- The duplicate helpers are dead in the combined broker and already exercised through the support owner:
  - `rg -n "_definition_workloads_by_id\\(|_direct_parity_case_ids_by_signature\\(|_manual_expected_result\\(" tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` matched only the three local definitions in the combined suite;
  - an AST name-use probe over `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` reported zero in-file references to those three helper names beyond their own definitions; and
  - `rg -n "_definition_workloads_by_id|_direct_parity_case_ids_by_signature|_manual_expected_result" tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/standard_benchmark_anchor_support.py` shows the support module owns the live implementations and the support test suite exercises them directly.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py` passed with `203 passed`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_standard_benchmark_anchor_support.py` passed with `291 tests collected`.
  - `bash -lc "! rg -n 'def (_definition_workloads_by_id|_direct_parity_case_ids_by_signature|_manual_expected_result)\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently fails because the three dead duplicate helper definitions still live in the combined suite, and that failure belongs to the exact cleanup queued here.

## Completion Note
- Deleted the dead local `_definition_workloads_by_id(...)`, `_direct_parity_case_ids_by_signature(...)`, and `_manual_expected_result(...)` helper copies from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so `tests/benchmarks/standard_benchmark_anchor_support.py` remains the single owner of those helpers.
- Verified `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py` (`203 passed`), `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_standard_benchmark_anchor_support.py` (`291 tests collected`), and `bash -lc "! rg -n 'def (_definition_workloads_by_id|_direct_parity_case_ids_by_signature|_manual_expected_result)\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` (passed with no matches).
