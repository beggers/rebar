# RBR-0516: Collapse scorecard report config onto one shared descriptor

Status: done
Owner: architecture-implementation
Created: 2026-03-17

## Goal
- Remove the remaining duplicated scorecard report configuration and bypass plumbing so correctness, benchmarks, the README refresh path, and report-facing tests all flow through one canonical scorecard report descriptor instead of each rebuilding published/legacy path metadata, loader-writer arguments, and direct helper calls.

## Deliverables
- `python/rebar_harness/scorecard_io.py`
- `python/rebar_harness/correctness.py`
- `python/rebar_harness/benchmarks.py`
- `scripts/rebar_ops.py`
- `tests/python/test_readme_reporting.py`
- `tests/conformance/test_combined_correctness_scorecards.py`

## Acceptance Criteria
- `python/rebar_harness/scorecard_io.py` exposes one shared scorecard report descriptor or factory that owns the repeated published-report metadata currently handwritten in both harness modules:
  - it binds `published_path`, `legacy_path`, `validate_path(...)`, `load(...)`, `write(...)`, and `remove_legacy_sidecar()` into one canonical surface;
  - it derives or stores the legacy-path rejection message, report-attribute name, scorecard kind, and module-name prefix in that same surface; and
  - it preserves current tracked `.py` report loading-writing plus optional scratch `.json` outputs exactly.
- `python/rebar_harness/correctness.py` and `python/rebar_harness/benchmarks.py` stop hand-building `SCORECARD_REPORT` and stop bypassing it in their own run and CLI paths:
  - replace the duplicated `SimpleNamespace` plus `LEGACY_REPORT_PATH_ERROR`, `SCORECARD_MODULE_NAME_PREFIX`, `SCORECARD_REPORT_ATTRIBUTE`, and `SCORECARD_KIND` setup with the shared descriptor or factory;
  - `run_correctness_harness(...)`, correctness CLI validation, `run_benchmarks(...)`, and benchmark report writes route through `SCORECARD_REPORT.validate_path(...)`, `.write(...)`, `.published_path`, and `.remove_legacy_sidecar()` instead of direct calls plus raw per-module constants; and
  - if `DEFAULT_REPORT_PATH` or `LEGACY_REPORT_PATH` remain exported for callers and tests, they alias the descriptor fields rather than shadowing separate literals.
- `scripts/rebar_ops.py` and the touched report-facing tests use the canonical descriptor instead of reconstructing report IO config:
  - `published_correctness_report_needs_refresh(...)` and `refresh_published_correctness_scorecard()` use `correctness_harness.SCORECARD_REPORT.published_path` rather than `Path(correctness_harness.DEFAULT_REPORT_PATH)`;
  - `tests/python/test_readme_reporting.py` uses `correctness.SCORECARD_REPORT.load(...)`, `correctness.SCORECARD_REPORT.write(...)`, and `benchmarks.SCORECARD_REPORT.load(...)` instead of importing the raw scorecard constant trio and calling `load_scorecard_report(...)` or `write_scorecard_report(...)` directly; and
  - `tests/conformance/test_combined_correctness_scorecards.py` loads the tracked correctness report through `correctness.SCORECARD_REPORT.load(...)` instead of importing the raw scorecard constants and `load_scorecard_report(...)`.
- Preserve current external behavior exactly:
  - keep the tracked published paths at `reports/correctness/latest.py` and `reports/benchmarks/latest.py`;
  - keep the legacy tracked JSON rejection text unchanged;
  - keep explicit scratch `.json` reports working;
  - keep built-native modes skipping writes unless `--report` is passed; and
  - do not change README rendering, scorecard payload schema, or benchmark-correctness selection behavior.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_readme_reporting.py tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_built_native_benchmark_modes.py`
  - ```bash
    PYTHONPATH=python ./.venv/bin/python - <<'PY'
    from rebar_harness import benchmarks, correctness

    assert correctness.SCORECARD_REPORT.published_path == correctness.DEFAULT_REPORT_PATH
    assert correctness.SCORECARD_REPORT.legacy_path == correctness.LEGACY_REPORT_PATH
    assert benchmarks.SCORECARD_REPORT.published_path == benchmarks.DEFAULT_REPORT_PATH
    assert benchmarks.SCORECARD_REPORT.legacy_path == benchmarks.LEGACY_REPORT_PATH
    assert correctness.SCORECARD_REPORT.load(correctness.DEFAULT_REPORT_PATH)["suite"] == "correctness"
    assert benchmarks.SCORECARD_REPORT.load(benchmarks.DEFAULT_REPORT_PATH)["suite"] == "benchmarks"
    print("ok")
    PY
    ```
  - `rg -n "SCORECARD_REPORT = SimpleNamespace|LEGACY_REPORT_PATH_ERROR = \\(|SCORECARD_MODULE_NAME_PREFIX =|SCORECARD_REPORT_ATTRIBUTE =|SCORECARD_KIND =|Path\\(correctness_harness\\.DEFAULT_REPORT_PATH\\)" python/rebar_harness/correctness.py python/rebar_harness/benchmarks.py scripts/rebar_ops.py tests/python/test_readme_reporting.py tests/conformance/test_combined_correctness_scorecards.py`
    The post-change result must be no matches.
  - `rg -n "load_scorecard_report\\(|write_scorecard_report\\(" tests/python/test_readme_reporting.py tests/conformance/test_combined_correctness_scorecards.py`
    The post-change result must be no matches.

## Constraints
- Keep this cleanup structural only. Do not change report payload contents, published report files, README text, workload or fixture selectors, or feature behavior behind `rebar`.
- Prefer one shared typed descriptor or factory in `python/rebar_harness/scorecard_io.py` over another ad hoc wrapper layer in tests or `scripts/rebar_ops.py`.
- Do not broaden into benchmark-selector cleanup, scorecard schema changes, or README-report rendering changes.

## Notes
- `RBR-0515` is reserved in `ops/state/backlog.md` and `ops/state/current_status.md`, so `RBR-0516` is the next available architecture id.
- No blocked architecture task exists to reopen first, and rule 10 does not apply in the current checkout:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `Dirty worktree: false`, and `Last Cycle Anomalies: none`;
  - `git status --short` is empty; and
  - both tracked and live JSON counts are zero (`tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, `git ls-files '*.json' | wc -l = 0`, `rg --files -g '*.json' | wc -l = 0`).
- The duplicate surface is concrete and still live:
  - `python/rebar_harness/correctness.py` and `python/rebar_harness/benchmarks.py` each still define `SCORECARD_REPORT = SimpleNamespace(...)` beside the same scorecard-kind, module-prefix, report-attribute, and legacy-error boilerplate and still call raw report helpers directly in their run paths;
  - `scripts/rebar_ops.py` still wraps `correctness_harness.DEFAULT_REPORT_PATH` in `Path(...)` twice instead of using the existing descriptor's published path; and
  - `tests/python/test_readme_reporting.py` plus `tests/conformance/test_combined_correctness_scorecards.py` still rebuild report loader-writer arguments manually instead of calling `SCORECARD_REPORT.load(...)` and `.write(...)`.
- 2026-03-17 probes from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_readme_reporting.py tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_built_native_benchmark_modes.py` passes (`15 passed, 2 skipped, 1117 subtests passed in 27.12s`).
  - The inline `SCORECARD_REPORT.published_path` / `.legacy_path` / `.load(...)` probe above currently prints `ok`.
  - `rg -n "SCORECARD_REPORT = SimpleNamespace|LEGACY_REPORT_PATH_ERROR = \\(|SCORECARD_MODULE_NAME_PREFIX =|SCORECARD_REPORT_ATTRIBUTE =|SCORECARD_KIND =|Path\\(correctness_harness\\.DEFAULT_REPORT_PATH\\)" python/rebar_harness/correctness.py python/rebar_harness/benchmarks.py scripts/rebar_ops.py tests/python/test_readme_reporting.py tests/conformance/test_combined_correctness_scorecards.py` currently returns the duplicated config and bypass matches listed above, and `rg -n "load_scorecard_report\\(|write_scorecard_report\\(" tests/python/test_readme_reporting.py tests/conformance/test_combined_correctness_scorecards.py` currently returns the remaining manual test call sites this task should delete.

## Completion Notes
- Added `ScorecardReportDescriptor` plus `build_scorecard_report_descriptor(...)` to `python/rebar_harness/scorecard_io.py`, so one shared surface now owns published-path metadata, the retired legacy-path rejection text, the report attribute/module prefix, and the bound `validate_path(...)`, `load(...)`, `write(...)`, and `remove_legacy_sidecar()` helpers.
- Replaced the handwritten `SimpleNamespace` scorecard config in `python/rebar_harness/correctness.py` and `python/rebar_harness/benchmarks.py` with the shared descriptor, aliased `DEFAULT_REPORT_PATH` and `LEGACY_REPORT_PATH` off descriptor fields, and routed harness validation/writes/legacy-sidecar cleanup through `SCORECARD_REPORT` instead of the raw helper functions and per-module constants.
- Updated `scripts/rebar_ops.py` to refresh the tracked correctness publication through `correctness_harness.SCORECARD_REPORT.published_path`, and rewired `tests/python/test_readme_reporting.py` plus `tests/conformance/test_combined_correctness_scorecards.py` to use `correctness.SCORECARD_REPORT.load(...)`, `.write(...)`, and `benchmarks.SCORECARD_REPORT.load(...)` rather than rebuilding scorecard IO metadata in test code.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_readme_reporting.py tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_built_native_benchmark_modes.py`, the inline `SCORECARD_REPORT.published_path` / `.legacy_path` / `.load(...)` probe (`ok`), `rg -n "SCORECARD_REPORT = SimpleNamespace|LEGACY_REPORT_PATH_ERROR = \\(|SCORECARD_MODULE_NAME_PREFIX =|SCORECARD_REPORT_ATTRIBUTE =|SCORECARD_KIND =|Path\\(correctness_harness\\.DEFAULT_REPORT_PATH\\)" python/rebar_harness/correctness.py python/rebar_harness/benchmarks.py scripts/rebar_ops.py tests/python/test_readme_reporting.py tests/conformance/test_combined_correctness_scorecards.py`, and `rg -n "load_scorecard_report\\(|write_scorecard_report\\(" tests/python/test_readme_reporting.py tests/conformance/test_combined_correctness_scorecards.py`, which now both return no matches.
