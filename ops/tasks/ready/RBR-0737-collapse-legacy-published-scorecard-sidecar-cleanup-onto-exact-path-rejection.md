# RBR-0737: Collapse legacy published-scorecard sidecar cleanup onto exact-path rejection

Status: ready
Owner: architecture-implementation
Created: 2026-03-20

## Goal
- Remove the obsolete "auto-delete `latest.json` sidecar" plumbing from the published scorecard path while preserving the one behavior that still matters: explicit writes to the retired published paths `reports/correctness/latest.json` and `reports/benchmarks/latest.json` must keep failing with the current guidance toward the tracked `.py` publications or a non-tracked scratch `.json` path.

## Deliverables
- `python/rebar_harness/scorecard_io.py`
- `scripts/rebar_ops.py`
- `tests/python/test_ops_harness.py`

## Acceptance Criteria
- `python/rebar_harness/scorecard_io.py` stops carrying a dedicated legacy-sidecar cleanup API:
  - remove `retired_published_scorecard_sidecar_path(...)`; and
  - stop deleting a sibling `published_path.with_suffix(".json")` from `ScorecardReportDescriptor.write(...)` when writing the tracked `.py` publication.
- Exact retired-path rejection still survives where it belongs:
  - `ScorecardReportDescriptor.validate_path(...)` / `resolve_optional_path(...)` still reject the exact retired sibling `published_path.with_suffix(".json")` with the existing error string that points callers at the tracked `.py` publication or a non-tracked scratch `.json` path; and
  - general scratch `.json` load/write support in `load_scorecard_report(...)` and `write_scorecard_report(...)` stays intact.
- `scripts/rebar_ops.py` no longer treats a stray published-scorecard sidecar as refresh drift or cleanup work:
  - `published_correctness_report_needs_refresh(...)` no longer returns `True` merely because `reports/correctness/latest.json` exists; and
  - `refresh_published_correctness_scorecard(...)` no longer unlinks or special-cases that sidecar before deciding whether the tracked `.py` scorecard needs regeneration.
- `tests/python/test_ops_harness.py` becomes the sole owner of the simplified contract:
  - keep the existing CLI rejection checks for `reports/correctness/latest.json` and `reports/benchmarks/latest.json`;
  - keep the non-retired scratch `.json` acceptance checks;
  - replace the current sidecar-deletion assertions with coverage that proves publishing to the tracked `.py` path and refreshing an already-current correctness scorecard leave a stray sibling `latest.json` alone; and
  - inline any exact retired-path computation with `published_path.with_suffix(".json")` or another tiny file-local expression instead of recreating a top-level sidecar helper.
- Keep scope structural only:
  - do not change the published scorecard payload shape, README/reporting prose, runtime dashboard output, or the ordinary `.json` scratch-output behavior; and
  - do not broaden into unrelated ops-harness failures outside the scorecard subset.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_ops_harness.py -k 'legacy_tracked_json_path or scorecard_report_descriptor or refresh_published_correctness_scorecard'`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
import pathlib
import tempfile

from rebar_harness import scorecard_io

with tempfile.TemporaryDirectory() as temp_dir:
    root = pathlib.Path(temp_dir)
    reports_root = root / "reports" / "correctness"
    reports_root.mkdir(parents=True)
    published_path = reports_root / "latest.py"
    legacy_path = published_path.with_suffix(".json")
    descriptor = scorecard_io.build_scorecard_report_descriptor(
        published_path=published_path,
        scorecard_kind="correctness",
    )
    scorecard = {"schema_version": "1.0", "totals": {"cases": 1, "passed": 1}}
    descriptor.write(scorecard, published_path)
    legacy_path.write_text("{}\n", encoding="utf-8")
    descriptor.write(scorecard, published_path)
    assert legacy_path.exists(), legacy_path
print("ok")
PY`
  - `bash -lc "! rg -n 'retired_published_scorecard_sidecar_path|removed_legacy_report|retired_sidecar_path\\.unlink|retired_sidecar_path\\.exists' python/rebar_harness/scorecard_io.py scripts/rebar_ops.py tests/python/test_ops_harness.py"`

## Constraints
- Keep the cleanup focused on deleting legacy tracked-JSON self-healing, not on reopening published `.json` scorecard paths as first-class outputs.
- Prefer one exact retired-path check at the descriptor boundary over duplicated refresh-time cleanup logic.
- Do not add a new helper/support module or another detached scorecard contract file.

## Notes
- `RBR-0737` is the next available architecture-task id in the current checkout:
  - `ops/tasks/done/` already extends through `RBR-0736`;
  - the reserved `RBR-` ids named in `ops/state/backlog.md` and `ops/state/current_status.md` also stop at `RBR-0736`; and
  - there is no missing tail id to reuse.
- No blocked architecture task exists to reopen first, and the current runtime state does not hit rule 10:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty before this task is added; and
  - `.rebar/runtime/dashboard.md` is aligned with the clean checkout at `HEAD` `6a812abf6eb019ff7b50917e6bca3cb68be3d853`, reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`.
- JSON burn-down is complete, so this run should spend its architecture slot on residual report-plumbing cleanup instead of another blob-removal task:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining sidecar cleanup is concrete and bounded in the current checkout:
  - `rg -n 'retired_published_scorecard_sidecar_path|removed_legacy_report|retired_sidecar_path\\.unlink|retired_sidecar_path\\.exists' python/rebar_harness/scorecard_io.py scripts/rebar_ops.py tests/python/test_ops_harness.py` matches only those three owner files;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_ops_harness.py -k 'legacy_tracked_json_path or scorecard_report_descriptor or refresh_published_correctness_scorecard'` currently passes (`8 passed, 37 deselected in 1.76s`);
  - the temp publish probe in Acceptance currently fails exactly on this cleanup because `ScorecardReportDescriptor.write(...)` still deletes `latest.json`; and
  - the final `rg` absence check in Acceptance currently fails exactly on this cleanup because the helper and refresh-time sidecar variables still exist.
- `RBR-0325` retired the tracked correctness `latest.json` publication path and `RBR-0650` moved the surviving `scorecard_io` contract onto `tests/python/test_ops_harness.py`; with both tracked and live JSON counts now at zero, the remaining auto-delete/auto-refresh sidecar path is obsolete compatibility plumbing rather than an active publication lane.
