# RBR-0664: Collapse the detached report assertion module onto the scorecard owners

Status: done
Owner: architecture-implementation
Created: 2026-03-19
Completed: 2026-03-19

## Goal
- Delete `tests/report_assertions.py` by moving its remaining correctness-report and source-tree benchmark-report assertion helpers onto the only two suites that still consume them, so the tracked scorecard publication paths each own their own assertion surface instead of sharing one detached support module beside those owners.

## Deliverables
- `tests/conformance/test_combined_correctness_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- Delete `tests/report_assertions.py`

## Acceptance Criteria
- `tests/conformance/test_combined_correctness_scorecards.py` becomes the sole owner for the correctness report assertion surface currently isolated in `tests/report_assertions.py`:
  - keep the current correctness-facing contract helpers explicit on the owner file:
    - `assert_correctness_case_record_matches(...)`,
      `assert_correctness_fixture_contract(...)`,
      `assert_correctness_layer_contract(...)`,
      `assert_correctness_report_contract(...)`,
      `assert_correctness_suite_case_accounting(...)`,
      `assert_correctness_suite_contract(...)`,
      `assert_correctness_suites_present(...)`,
      `find_correctness_case_record(...)`, and
      `find_correctness_suite_record(...)`
      remain defined on `tests/conformance/test_combined_correctness_scorecards.py`;
  - keep any tiny helper needed for correctness summary recomputation, diagnostics recomputation, tracked-report existence checks, baseline metadata checks, or case/suite lookup file-local on that owner instead of leaving another detached support layer behind.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` becomes the sole owner for the source-tree benchmark report assertion surface currently isolated in `tests/report_assertions.py`:
  - keep the current source-tree benchmark contract helpers explicit on the owner file:
    - `assert_benchmark_manifest_contract(...)`,
      `assert_benchmark_workload_contract(...)`,
      `assert_source_tree_benchmark_contract(...)`,
      `find_manifest_record(...)`,
      `find_workload_document(...)`, and
      `find_workload_record(...)`
      remain defined on `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`;
  - keep any tiny helper needed for benchmark summary/cache accounting, tracked-report existence checks, baseline metadata checks, artifact-manifest record assembly, or workload/manifest lookup file-local on that owner instead of leaving another detached support layer behind.
- `tests/report_assertions.py` is deleted outright:
  - do not leave an import-only wrapper, compatibility shell, or renamed assertion-specific support module behind.
- Keep scope structural only:
  - do not change `python/rebar_harness/correctness.py`, `python/rebar_harness/benchmarks.py`, `tests/harness_cli_test_support.py`, `tests/python/test_ops_harness.py`, published reports, or tracked project-state prose in this run.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path

correctness = Path("tests/conformance/test_combined_correctness_scorecards.py").read_text(
    encoding="utf-8"
)
benchmarks = Path("tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py").read_text(
    encoding="utf-8"
)

for needle in (
    "def assert_correctness_case_record_matches(",
    "def assert_correctness_fixture_contract(",
    "def assert_correctness_layer_contract(",
    "def assert_correctness_report_contract(",
    "def assert_correctness_suite_case_accounting(",
    "def assert_correctness_suite_contract(",
    "def assert_correctness_suites_present(",
    "def find_correctness_case_record(",
    "def find_correctness_suite_record(",
):
    assert needle in correctness, needle

for needle in (
    "def assert_benchmark_manifest_contract(",
    "def assert_benchmark_workload_contract(",
    "def assert_source_tree_benchmark_contract(",
    "def find_manifest_record(",
    "def find_workload_document(",
    "def find_workload_record(",
):
    assert needle in benchmarks, needle

assert "from tests.report_assertions import" not in correctness
assert "from tests.report_assertions import" not in benchmarks
print("ok")
PY`
  - `bash -lc "! rg -n 'from tests\\.report_assertions import' tests -g '*.py'"`
  - `bash -lc "! rg --files tests | rg 'report_assertions\\.py$'"`

## Constraints
- Keep this cleanup structural only. Do not reinterpret correctness scorecard behavior, source-tree benchmark scorecard behavior, manifest accounting, workload accounting, or tracked report semantics.
- Prefer the two existing scorecard owners and file-local helpers over another shared support module.
- Do not move the source-tree benchmark assertion surface onto `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py`; that owner should stay focused on direct `rebar_harness.benchmarks` contract coverage rather than tracked source-tree publication assertions.
- Do not move the correctness assertion surface onto `tests/python/test_ops_harness.py`; the tracked correctness publication owner should keep its own assertion surface.

## Notes
- `RBR-0664` is the next available architecture task id in the current checkout:
  - `rg -n "RBR-066[3-9]|RBR-067[0-9]" ops/state/backlog.md ops/state/current_status.md` currently returns only the active feature frontier `RBR-0663`; and
  - `find ops/tasks -maxdepth 2 -type f \( -name 'RBR-0663*' -o -name 'RBR-0664*' -o -name 'RBR-0665*' -o -name 'RBR-0666*' -o -name 'RBR-0667*' -o -name 'RBR-0668*' -o -name 'RBR-0669*' -o -name 'RBR-0670*' \) | sort` currently returns only `ops/tasks/ready/RBR-0663-nested-broader-range-wider-ranged-repeat-branch-local-backreference-callable-replacement-bytes-parity.md`.
- No blocked architecture task exists to reopen first, and rule 10 does not currently block another architecture cleanup:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the only ready task is the feature-owned `RBR-0663`, with recent architecture and feature work committing cleanly.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `.rebar/runtime/loop_state.json` still reports `tracked_json_blob_count: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The detached report-assertion layer is concrete and bounded in the current checkout:
  - `rg -n "from tests\\.report_assertions import" tests -g '*.py'` currently matches only `tests/conformance/test_combined_correctness_scorecards.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`;
  - `wc -l tests/report_assertions.py tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` reports `658` lines for the detached support module, `3370` lines for the correctness owner, and `4056` lines for the benchmark owner;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently passes (`58 passed, 2924 subtests passed in 55.07s`);
  - the inline source probe in Acceptance currently fails exactly on this cleanup with `AssertionError: def assert_correctness_report_contract(` because the owner files do not yet carry the absorbed assertion definitions and still import `tests.report_assertions`; and
  - both `bash -lc "! rg -n 'from tests\\.report_assertions import' tests -g '*.py'"` and `bash -lc "! rg --files tests | rg 'report_assertions\\.py$'"` currently fail exactly on this cleanup because the detached support module and its imports still exist.
- The ownership simplification matches the current publication-harness shape:
  - `tests/conformance/test_combined_correctness_scorecards.py` already owns the tracked correctness scorecard expectations and tracked correctness publication checks that consume the correctness-side assertion helpers; and
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` already owns the tracked source-tree benchmark scorecard expectations and tracked source-tree publication checks that consume the benchmark-side assertion helpers.

## Completion Note
- 2026-03-19: Inlined the remaining correctness report assertion helpers onto `tests/conformance/test_combined_correctness_scorecards.py`, inlined the remaining source-tree benchmark report assertion helpers onto `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and deleted `tests/report_assertions.py` instead of leaving another wrapper or support module behind.

## Verification
- 2026-03-19: `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` (`58 passed, 2924 subtests passed in 54.82s`)
- 2026-03-19: `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... PY` (passed; confirmed the required helper definitions are present on both owner files and both files no longer import `tests.report_assertions`)
- 2026-03-19: `bash -lc "! rg -n 'from tests\\.report_assertions import' tests -g '*.py'"` (no matches)
- 2026-03-19: `bash -lc "! rg --files tests | rg 'report_assertions\\.py$'"` (no matches)
- 2026-03-19: `git diff --name-status -- tests/report_assertions.py` (`D	tests/report_assertions.py`)
