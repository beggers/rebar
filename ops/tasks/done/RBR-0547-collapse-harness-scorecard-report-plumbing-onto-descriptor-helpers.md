# RBR-0547: Collapse harness scorecard report plumbing onto descriptor helpers

Status: done
Owner: architecture-implementation
Created: 2026-03-17
Completed: 2026-03-17

## Goal
- Make `ScorecardReportDescriptor` in `python/rebar_harness/scorecard_io.py` the single owner of harness-side scorecard output plumbing so `python/rebar_harness/correctness.py` and `python/rebar_harness/benchmarks.py` stop open-coding the same report-path validation, scorecard write, and retired-sidecar cleanup sequence.

## Deliverables
- `python/rebar_harness/scorecard_io.py`
- `python/rebar_harness/correctness.py`
- `python/rebar_harness/benchmarks.py`
- `tests/python/test_scorecard_io_contract.py`
- `tests/python/test_readme_reporting.py`
- `tests/benchmarks/test_built_native_benchmark_modes.py`

## Acceptance Criteria
- `python/rebar_harness/scorecard_io.py` grows the smallest descriptor-owned helper surface needed to own the remaining harness report flow:
  - one helper that resolves an optional report path while preserving `None` and the current legacy published-path rejection/error text; and
  - one helper that writes a scorecard to a resolved report path and deletes the retired legacy sidecar only when the write target is the descriptor's tracked published path.
- `python/rebar_harness/correctness.py` and `python/rebar_harness/benchmarks.py` stop open-coding the current descriptor plumbing:
  - no direct `SCORECARD_REPORT.write(...)` calls remain in either harness module;
  - no direct `SCORECARD_REPORT.remove_legacy_sidecar()` calls remain in either harness module; and
  - `correctness.main()` no longer separately validates `args.report` before calling `run_correctness_harness(...)`; it should rely on the shared harness/descriptor path while preserving the current `ValueError` to `stderr` plus exit `2` behavior for rejected paths.
- Preserve current report behavior exactly:
  - tracked published outputs still default to `reports/correctness/latest.py` and `reports/benchmarks/latest.py`;
  - explicit scratch `.json` report outputs remain supported for both harnesses;
  - built-native benchmark modes still accept `report_path=None` and only write when an explicit path is passed;
  - the retired tracked `.json` paths still raise the current error text; and
  - do not change scorecard payload structure, manifest/workload/fixture selection, or README/reporting semantics.
- `tests/python/test_scorecard_io_contract.py` adds focused coverage for the new descriptor-owned helper surface instead of broadening behavior elsewhere.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_scorecard_io_contract.py tests/python/test_readme_reporting.py tests/benchmarks/test_built_native_benchmark_modes.py`
  - `rg -n "SCORECARD_REPORT\\.write\\(|remove_legacy_sidecar\\(|validate_path\\(args\\.report\\)" python/rebar_harness/correctness.py python/rebar_harness/benchmarks.py`
    The post-change result must be no matches.

## Constraints
- Keep this cleanup structural only. Do not change `scripts/rebar_ops.py`, correctness fixtures, benchmark workloads, published reports, README text, tracked state files, or Rust / `python/rebar/` behavior in the same run.
- Prefer extending `ScorecardReportDescriptor` over adding another helper module, registry, or wrapper layer around the harness entrypoints.
- Do not remove scratch `.json` output support. The cleanup should only collapse duplicated harness plumbing, not narrow supported ad hoc output paths.

## Notes
- `RBR-0546` is already reserved in `ops/state/backlog.md` and `ops/state/current_status.md` for the next feature-owned benchmark follow-on, so `RBR-0547` is the next available architecture id.
- No blocked architecture task exists to reopen first, and rule 10 does not apply in the current checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added;
  - `.rebar/runtime/dashboard.md` is aligned with `HEAD` and reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - `git status --short` was empty in the current checkout.
- JSON burn-down remains complete in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- The duplicate harness report plumbing is concrete in the current checkout:
  - `rg -n "SCORECARD_REPORT\\.write\\(|remove_legacy_sidecar\\(|validate_path\\(args\\.report\\)" python/rebar_harness/correctness.py python/rebar_harness/benchmarks.py` currently returns five matches: two direct writes, two direct legacy-sidecar removals, and one duplicate CLI-time `validate_path(args.report)` call in `correctness.py`;
  - `correctness.py` still validates `args.report` in `main()`, and the two harness modules still contain two direct `remove_legacy_sidecar()` calls today; and
  - the current cleanup target is only harness report flow, not scorecard contents.
- 2026-03-17 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_scorecard_io_contract.py tests/python/test_readme_reporting.py tests/benchmarks/test_built_native_benchmark_modes.py` passes (`19 passed, 2 skipped in 1.64s`).

## Completion
- Added `ScorecardReportDescriptor.resolve_optional_path(...)` and `ScorecardReportDescriptor.write_resolved_report(...)` so the descriptor now owns the remaining harness-side optional-report resolution plus write-and-published-sidecar-cleanup flow.
- Rewired `python/rebar_harness/correctness.py` and `python/rebar_harness/benchmarks.py` to use the descriptor helpers, removing the direct `SCORECARD_REPORT.write(...)`, direct `remove_legacy_sidecar()`, and duplicate CLI-time `validate_path(args.report)` call from the harness modules.
- Added focused descriptor contract coverage for `None`-preserving optional-path resolution, legacy published-path rejection text, and published-only legacy-sidecar cleanup when writing to a resolved report path.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_scorecard_io_contract.py tests/python/test_readme_reporting.py tests/benchmarks/test_built_native_benchmark_modes.py` (`20 passed, 2 skipped in 1.91s`)
- `rg -n "SCORECARD_REPORT\.write\(|remove_legacy_sidecar\(|validate_path\(args\.report\)" python/rebar_harness/correctness.py python/rebar_harness/benchmarks.py` (no matches)
