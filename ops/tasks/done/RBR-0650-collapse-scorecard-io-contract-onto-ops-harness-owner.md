# RBR-0650: Collapse the detached scorecard IO contract onto the ops harness owner

Status: done
Owner: architecture-implementation
Created: 2026-03-19
Completed: 2026-03-19

## Goal
- Delete `tests/python/test_scorecard_io_contract.py` by moving its remaining `rebar_harness.scorecard_io` contract coverage onto `tests/python/test_ops_harness.py`, so the scorecard report/config/report-refresh path has one owner instead of a small detached utility suite beside the existing ops/report owner.

## Deliverables
- `tests/python/test_ops_harness.py`
- Delete `tests/python/test_scorecard_io_contract.py`

## Acceptance Criteria
- `tests/python/test_ops_harness.py` becomes the sole owner for the direct `scorecard_io` coverage currently isolated in `tests/python/test_scorecard_io_contract.py`:
  - absorb the current baseline/interpreter provenance assertions for `build_cpython_baseline(version_family="3.12.x")`;
  - absorb the current Python-module round-trip check for `format_python_scorecard_module(..., report_attribute="REPORT")` plus `load_python_dict_attribute(...)`;
  - absorb the current `.py` and `.json` round-trip checks for `write_scorecard_report(...)` and `load_scorecard_report(...)`;
  - absorb the current malformed-input rejection checks for missing `REPORT`, non-dict `.py`, non-dict `.json`, unsupported `.txt` input, and unsupported `.txt` output;
  - absorb the current `ScorecardReportDescriptor` path-resolution contract, including `resolve_optional_path(None)`, acceptance of the tracked published `.py` path, and rejection of the retired published `.json` sidecar with the same error string; and
  - absorb the current descriptor write behavior that leaves a scratch `.json` output alone but deletes the retired sidecar only when writing to the published `.py` path.
- Keep the absorbed coverage inside `OpsHarnessTest` with `test_scorecard_*` method names so the existing scorecard subset remains the stable owner surface, and keep any tiny helper local to `tests/python/test_ops_harness.py` instead of adding another `*_support.py` module or a new detached test file.
- `tests/python/test_scorecard_io_contract.py` is deleted outright:
  - do not leave an import-only wrapper, compatibility shell, or renamed scorecard-io-specific suite behind.
- Keep scope structural only:
  - do not change `python/rebar_harness/scorecard_io.py`, `scripts/rebar_ops.py`, published reports, or tracked project-state prose in this run; and
  - do not broaden into the unrelated dispatch-policy drift currently making the full `tests/python/test_ops_harness.py` file red outside the scorecard subset.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_ops_harness.py -k scorecard`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path

source = Path("tests/python/test_ops_harness.py").read_text(encoding="utf-8")
for needle in (
    "build_cpython_baseline(",
    "format_python_scorecard_module(",
    "build_scorecard_report_descriptor(",
    "load_scorecard_report(",
    "write_scorecard_report(",
):
    assert needle in source, needle
print("ok")
PY`
  - `bash -lc "! rg --files tests/python | rg 'test_scorecard_io_contract\\.py$'"`

## Constraints
- Keep this cleanup structural only. The point is to delete a detached owner file, not to reinterpret scorecard behavior or change report-path semantics.
- Prefer the existing ops/report owner and file-local helpers over another dedicated scorecard-utility suite.
- Preserve the current error strings and sidecar-cleanup behavior exactly; the absorbed tests should keep the live contract honest, not rewrite it.

## Notes
- `RBR-0650` is the next available architecture task id in the current checkout:
  - `rg -n 'RBR-0649|RBR-0650|RBR-0651|RBR-0652' ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked` returns only the active feature task `RBR-0649` and no reserved `RBR-0650+` entries in the live queue/state files; and
  - `find ops/tasks -maxdepth 2 \( -name 'RBR-0649*' -o -name 'RBR-0650*' -o -name 'RBR-0651*' -o -name 'RBR-0652*' \) | sort` returns only `ops/tasks/ready/RBR-0649-nested-broader-range-wider-ranged-repeat-branch-local-backreference-replacement-pack.md`.
- No blocked architecture task exists to reopen first, and rule 10 does not currently block another architecture cleanup:
  - `ops/tasks/blocked/` contains only `.gitkeep`;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the recent feature, architecture, and reporting task runs completed cleanly in the current checkout.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON simplification:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returns `0`; and
  - `rg --files -g '*.json' | wc -l` returns `0`.
- The remaining detached scorecard contract is concrete and bounded in the current checkout:
  - `wc -l tests/python/test_scorecard_io_contract.py tests/python/test_ops_harness.py` reports `220` lines for the detached suite and `802` lines for the existing ops/report owner;
  - `rg -n 'test_build_cpython_baseline_reports_current_interpreter_shape|test_format_python_scorecard_module_round_trips_through_python_loader|test_scorecard_report_round_trips_for_supported_extensions|test_scorecard_report_loaders_and_writers_reject_malformed_inputs|test_scorecard_report_descriptor_resolves_optional_paths_and_rejects_retired_sidecar|test_scorecard_report_descriptor_writes_reports_and_only_cleans_up_published_sidecar' tests/python/test_scorecard_io_contract.py tests/python/test_ops_harness.py` currently matches only `tests/python/test_scorecard_io_contract.py`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_scorecard_io_contract.py` currently passes (`7 passed in 0.05s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_ops_harness.py -k scorecard` currently passes (`5 passed, 21 deselected in 1.66s`);
  - the inline source probe in Acceptance currently fails exactly on this cleanup with `AssertionError: build_cpython_baseline(` because `tests/python/test_ops_harness.py` does not yet carry the absorbed `scorecard_io` contract;
  - `bash -lc "! rg --files tests/python | rg 'test_scorecard_io_contract\\.py$'"` currently fails exactly on this cleanup because the detached suite still exists; and
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_ops_harness.py tests/python/test_scorecard_io_contract.py` is currently red for unrelated drift because `tests/python/test_ops_harness.py::OpsHarnessTest::test_dispatch_policies_match_the_current_specialist_mix` still expects interval dispatch for `cleanup`, so keep this cleanup's verification isolated to the scorecard subset instead of broadening into agent-dispatch policy work.

## Completion Note
- 2026-03-19: Moved the detached `scorecard_io` baseline, Python-module round-trip, supported `.py`/`.json` round-trip, malformed-input rejection, descriptor path-resolution, and descriptor sidecar-cleanup assertions onto `tests/python/test_ops_harness.py` as `OpsHarnessTest.test_scorecard_*` coverage.
- 2026-03-19: Deleted `tests/python/test_scorecard_io_contract.py` outright after `tests/python/test_ops_harness.py` absorbed the direct `build_cpython_baseline()`, `format_python_scorecard_module()`, `load_scorecard_report()`, `write_scorecard_report()`, and `build_scorecard_report_descriptor()` contract checks.
- 2026-03-19: Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_ops_harness.py -k scorecard` (`11 passed, 21 deselected, 2 subtests passed in 1.66s`), the acceptance inline source probe (`ok`), `bash -lc "! rg --files tests/python | rg 'test_scorecard_io_contract\\.py$'"` (passes), and `git diff --name-status -- tests/python/test_scorecard_io_contract.py` (`D`).
