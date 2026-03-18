# RBR-0634: Collapse retired scorecard sidecar plumbing onto published report paths

Status: ready
Owner: architecture-implementation
Created: 2026-03-18

## Goal
- Delete the remaining explicit `legacy_path` scorecard plumbing now that tracked and live JSON counts are both zero, while preserving the one real boundary it still protects: callers must not recreate `reports/correctness/latest.json` or `reports/benchmarks/latest.json` as tracked sidecars beside the published `.py` scorecards.

## Deliverables
- `python/rebar_harness/scorecard_io.py`
- `python/rebar_harness/correctness.py`
- `python/rebar_harness/benchmarks.py`
- `scripts/rebar_ops.py`
- `tests/python/test_scorecard_io_contract.py`
- `tests/python/test_readme_reporting.py`

## Acceptance Criteria
- `python/rebar_harness/scorecard_io.py` deletes the stored legacy-sidecar state from the descriptor surface:
  - `ScorecardReportDescriptor` no longer stores `legacy_path` or `legacy_path_error`; and
  - `build_scorecard_report_descriptor(...)` no longer requires or accepts a `legacy_path=` argument.
- The retired tracked JSON sidecar path is derived from the published report path instead of being threaded through the harness as separate config:
  - derive the blocked sidecar from `published_path` locally inside the descriptor or an equally local helper path owned by `python/rebar_harness/scorecard_io.py`;
  - keep the current rejection behavior for the exact tracked paths `reports/correctness/latest.json` and `reports/benchmarks/latest.json`; and
  - keep the current user-facing error guidance unchanged about using the tracked `.py` publication path or a non-tracked temporary `.json` path for scratch output.
- Collapse the extra published-write wrapper that exists only for legacy-sidecar cleanup:
  - `python/rebar_harness/correctness.py` and `python/rebar_harness/benchmarks.py` stop calling `write_resolved_report(...)`;
  - route scorecard writes through one remaining descriptor-owned write path while preserving benchmark `report_path=None` behavior; and
  - do not replace `write_resolved_report(...)` with another second public write wrapper beside `write(...)`.
- `scripts/rebar_ops.py` and the touched report-facing tests stop reaching through descriptor internals that exist only for the retired sidecar:
  - no `.legacy_path` access remains in `scripts/rebar_ops.py` or `tests/python/test_readme_reporting.py`;
  - no `remove_legacy_sidecar()` call remains in `scripts/rebar_ops.py`; and
  - published correctness refresh still treats a stray sibling `latest.json` sidecar as stale state that must be removed and, when necessary, still refreshes the tracked `.py` scorecard.
- Preserve current behavior exactly:
  - the tracked published scorecards stay at `reports/correctness/latest.py` and `reports/benchmarks/latest.py`;
  - explicit scratch `.json` report outputs outside those tracked paths still work;
  - `rebar_harness.benchmarks` still accepts `report_path=None` and only writes when a concrete path is passed; and
  - do not change scorecard payload schemas, fixture/workload selectors, README rendering, or runtime `.rebar/` JSON artifacts.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_scorecard_io_contract.py tests/python/test_readme_reporting.py tests/benchmarks/test_built_native_benchmark_modes.py`
  - `bash -lc "! rg -n 'legacy_path|legacy_path_error|remove_legacy_sidecar|write_resolved_report' python/rebar_harness/scorecard_io.py python/rebar_harness/correctness.py python/rebar_harness/benchmarks.py scripts/rebar_ops.py tests/python/test_scorecard_io_contract.py tests/python/test_readme_reporting.py"`

## Constraints
- Keep this cleanup structural only. Do not change published scorecard contents, README/state prose, Rust code, `python/rebar/` behavior, fixture/workload data, or benchmark/correctness frontier scope in the same run.
- Preserve the existing rejection text for the retired tracked JSON scorecard paths instead of weakening that boundary or reopening tracked JSON output under `reports/`.
- Prefer deleting fields, parameters, and wrapper helpers over adding another compatibility layer or another report-path abstraction.

## Notes
- `RBR-0634` is the next available architecture task id in the current checkout:
  - `ops/state/backlog.md`, `ops/state/current_status.md`, `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contain no reserved or active `RBR-0634` through `RBR-0649` entry.
- No blocked architecture task exists to reopen first, and rule 10 does not apply in the current runtime state:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` is aligned with `HEAD` (`1b0333a5159dda0b973fd8d7dea1b83f52bb83ca`), reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest cycle finished both task workers cleanly, so the queue is not stalled on inherited-dirty or post-commit refresh churn.
- JSON burn-down is complete in both tracked and live views, so this follow-on can spend the cycle on report-plumbing simplification instead of more blob removal:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining legacy-sidecar plumbing is concrete in the current checkout:
  - `bash -lc "! rg -n 'legacy_path|legacy_path_error|remove_legacy_sidecar|write_resolved_report' python/rebar_harness/scorecard_io.py python/rebar_harness/correctness.py python/rebar_harness/benchmarks.py scripts/rebar_ops.py tests/python/test_scorecard_io_contract.py tests/python/test_readme_reporting.py"` currently fails with matches in all six target files because that explicit sidecar state and wrapper surface is still live; and
  - those matches are now plumbing-only: the repo no longer tracks any published JSON scorecards, but the descriptor still stores a separate `legacy_path`, carries a second published-write wrapper, and exposes a sidecar-removal method largely to support those deleted tracked artifacts.
- 2026-03-18 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_scorecard_io_contract.py tests/python/test_readme_reporting.py tests/benchmarks/test_built_native_benchmark_modes.py` passes (`20 passed, 2 skipped in 1.82s`).
