# RBR-0420: Centralize scorecard CLI test support

Status: ready
Owner: architecture-implementation
Created: 2026-03-15

## Goal
- Replace the remaining duplicated subprocess/report plumbing for CLI-driven correctness and benchmark scorecard tests with one shared test-support path, so the harness-facing tests stop open-coding the same `cwd`, `PYTHONPATH`, temp-report, and JSON-loading flow in multiple places.

## Deliverables
- `tests/harness_cli_test_support.py`
- `tests/conformance/correctness_expectations.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/python/test_readme_reporting.py`

## Acceptance Criteria
- `tests/harness_cli_test_support.py` becomes the single shared owner for test-side subprocess execution of `python -m rebar_harness.correctness` and `python -m rebar_harness.benchmarks`, including:
  - repo-root `cwd` selection;
  - `PYTHONPATH=python` environment setup for subprocess runs;
  - temporary `.json` report-path lifecycle for narrow scorecard reruns; and
  - loading the CLI summary from stdout plus the temporary JSON report payload when callers want a `(summary, scorecard)` result.
- `tests/conformance/correctness_expectations.py::run_correctness_scorecard()` routes through that shared helper instead of open-coding `TemporaryDirectory()`, `subprocess.run(...)`, `cwd=REPO_ROOT`, `env={"PYTHONPATH": str(PYTHON_SOURCE)}`, and `json.loads(...)`.
- `tests/benchmarks/benchmark_expectations.py::run_source_tree_benchmark_scorecard()` routes through the same shared helper instead of open-coding the same temp-report subprocess flow for `rebar_harness.benchmarks`.
- `tests/python/test_readme_reporting.py` uses the shared helper for the current CLI-based correctness/benchmark checks:
  - the legacy tracked-path rejection tests still assert the same nonzero exit code and stderr text; and
  - the narrowed correctness report repair test still shells out through the helper and preserves its current repair assertions.
- The cleanup does not change harness behavior or published artifacts:
  - `python/rebar_harness/correctness.py`, `python/rebar_harness/benchmarks.py`, benchmark workloads, correctness fixtures, and tracked reports stay behaviorally unchanged; and
  - the helper continues to drive temporary `.json` scratch reports for test-local CLI reruns rather than touching tracked `latest.py` publications.
- After the cleanup, `rg -n 'env=\\{\"PYTHONPATH\": str\\(PYTHON_SOURCE\\)\\}|sys\\.executable, \"-m\", \"rebar_harness\\.(correctness|benchmarks)\"' tests/conformance/correctness_expectations.py tests/benchmarks/benchmark_expectations.py tests/python/test_readme_reporting.py` returns no matches.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/python/test_readme_reporting.py`.

## Constraints
- Keep this task on shared test-harness CLI/report plumbing only. Do not change Rust code, `python/rebar/`, harness runtime behavior, benchmark workloads, correctness fixture contents, published reports, README reporting, or tracked state files beyond this task file.
- Prefer one small shared helper module under `tests/` over separate correctness-only and benchmark-only support wrappers.
- Preserve the existing public helper call shapes in `run_correctness_scorecard()` and `run_source_tree_benchmark_scorecard()` unless a direct simplification in the current checkout makes a signature change clearly lower churn.

## Notes
- This is a post-JSON duplicate-plumbing follow-on after `RBR-0413`, `RBR-0416`, and `RBR-0418`: selector and pytest bootstrap cleanup landed, but the scorecard-facing tests still duplicate the same subprocess/report wiring when they drive the harness through its CLI boundary.
- The runtime dashboard is one commit behind `HEAD` in this checkout (`dashboard.md` reports `708758b04c994263c3936d9f3deb72feec611313`, while current `HEAD` is `2b5136842ec763b1ca3c5e6aad7d5ee8a6976ed5`), so its JSON count is slightly stale as reporting metadata; the live filesystem counts still show zero JSON files (`git ls-files '*.json' | wc -l = 0`, `rg --files -g '*.json' | wc -l = 0`), which keeps this run in the post-JSON simplification lane.
