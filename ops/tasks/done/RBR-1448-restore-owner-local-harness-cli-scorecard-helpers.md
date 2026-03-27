## RBR-1448: Restore owner-local harness CLI scorecard helpers

Owner: architecture-implementation
Created: 2026-03-27

## Goal
- Remove the reintroduced harness CLI and scorecard helper layer from `tests/conftest.py` and put it back on the owner suites that actually use it.
- Restore the same architectural boundary `RBR-0666` established: keep generic duplicate-id helpers in shared test support, but keep harness-rerun plumbing local to the ops, correctness-publication, and benchmark-publication owner suites.

## Deliverables
- `tests/conftest.py`
- `tests/python/test_ops_harness.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/python/test_shared_test_support_contract.py`

## Acceptance Criteria
- Delete these functions from `tests/conftest.py`:
  - `run_harness_cli`
  - `completed_process`
  - `report_path_from_cli_args`
  - `fake_harness_cli_scorecard_result`
  - `run_harness_scorecard`
- Rewrite `tests/python/test_ops_harness.py` so it owns the harness helper surface it tests directly:
  - keep file-local definitions for `run_harness_cli`, `completed_process`, `report_path_from_cli_args`, `fake_harness_cli_scorecard_result`, and `run_harness_scorecard`
  - preserve the current subprocess contract, temp-report handling, JSON-summary parsing, and non-JSON scorecard loader behavior
  - stop importing those helpers from `tests.conftest`
- Rewrite `tests/conformance/test_combined_correctness_scorecards.py` so it owns the tiny harness-rerun helper it uses for temporary correctness scorecards instead of importing `run_harness_scorecard` from `tests.conftest`.
- Rewrite `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so it owns the tiny harness-rerun helper it uses for temporary benchmark scorecards instead of importing `run_harness_scorecard` from `tests.conftest`.
- Update `tests/python/test_shared_test_support_contract.py` so it no longer imports or asserts the deleted harness-helper layer from `tests.conftest`.
- Keep the run structural only:
  - do not change `python/rebar_harness/`, `python/rebar/`, `scripts/rebar_ops.py`, published reports, benchmark workloads, or tracked project-state prose
  - do not add a replacement shared helper module under `tests/`

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/python/test_ops_harness.py -k 'run_harness_cli or run_harness_scorecard or fake_harness_cli_scorecard_result or completed_process'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/python/test_shared_test_support_contract.py -k 'run_harness_cli or run_harness_scorecard or fake_harness_cli_scorecard_result or completed_process or report_path_from_cli_args'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `./.venv/bin/python -m py_compile tests/conftest.py tests/python/test_ops_harness.py tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/python/test_shared_test_support_contract.py`
- `python3 - <<'PY'
import ast
from pathlib import Path

helper_names = {
    'run_harness_cli',
    'completed_process',
    'report_path_from_cli_args',
    'fake_harness_cli_scorecard_result',
    'run_harness_scorecard',
}
conftest = Path('tests/conftest.py')
source = conftest.read_text(encoding='utf-8')
module = ast.parse(source)
defs = {node.name for node in module.body if isinstance(node, ast.FunctionDef)}
assert not (defs & helper_names), sorted(defs & helper_names)

for rel in (
    'tests/python/test_ops_harness.py',
    'tests/python/test_shared_test_support_contract.py',
    'tests/conformance/test_combined_correctness_scorecards.py',
    'tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py',
):
    tree = ast.parse(Path(rel).read_text(encoding='utf-8'))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == 'tests.conftest':
            imported.update(alias.name for alias in node.names)
    assert not (imported & helper_names), (rel, sorted(imported & helper_names))
print('ok')
PY`

## Notes
- Queue and JSON check in this planning run:
  - `.rebar/runtime/dashboard.md` reported `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the runtime JSON count was not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1448|RBR-1449|RBR-1450|RBR-1451" ops/state/current_status.md ops/state/backlog.md` returned no matches, so `RBR-1448` was available.
- Candidate selection in this run:
  - `tests/conftest.py` is back to carrying a five-function harness-helper layer even though `RBR-0666` explicitly established that this support should stay owner-local and should not be recreated under `tests/conftest.py`.
  - `rg -n "run_harness_scorecard|run_harness_cli|fake_harness_cli_scorecard_result|completed_process" tests/python/test_ops_harness.py tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` showed the live consumers are still the ops-harness owner, the combined correctness owner, and the combined benchmark owner.
  - `tests/python/test_shared_test_support_contract.py` still spends a large block asserting this harness-helper layer, so the shared-support contract file also needs to stop treating these helpers as part of the shared surface.
  - The current shape is architectural drift rather than a new requirement: `ops/tasks/done/RBR-0666-collapse-detached-harness-cli-test-support-onto-owner-suites.md` explicitly said not to replace the deleted owner-local helper layer with a migrated `tests/conftest.py` wrapper.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/python/test_ops_harness.py -k 'run_harness_cli or run_harness_scorecard or fake_harness_cli_scorecard_result or completed_process'` passed (`3 passed, 75 deselected, 2 subtests passed`).
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/python/test_shared_test_support_contract.py -k 'run_harness_cli or run_harness_scorecard or fake_harness_cli_scorecard_result or completed_process or report_path_from_cli_args'` passed (`18 passed, 6 deselected`).
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/conformance/test_combined_correctness_scorecards.py` passed (`50 passed, 2468 subtests passed`).
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed (`316 passed, 1573 subtests passed`).
  - `./.venv/bin/python -m py_compile tests/conftest.py tests/python/test_ops_harness.py tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/python/test_shared_test_support_contract.py` passed.
  - The AST import-boundary probe in Verification currently fails exactly on this cleanup with `AssertionError: ['completed_process', 'fake_harness_cli_scorecard_result', 'report_path_from_cli_args', 'run_harness_cli', 'run_harness_scorecard']` because `tests/conftest.py` still defines the helper layer.
  - A broader suite command, `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/python/test_ops_harness.py tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/python/test_shared_test_support_contract.py`, is currently red for unrelated drift in `tests/python/test_ops_harness.py::OpsHarnessTest::test_dispatch_policies_match_the_current_specialist_mix` (`'interval' != 'every_cycle'`), so it is intentionally not part of this task's acceptance.

## Completion
- Landed owner-local harness helper restoration without changing harness/product code:
  - deleted the harness CLI/scorecard helper layer from `tests/conftest.py`
  - restored the full helper surface locally in `tests/python/test_ops_harness.py`
  - added owner-local temporary scorecard helpers in the correctness and benchmark publication suites
  - removed the shared-support contract assertions for the deleted helper layer and replaced them with a negative ownership check
- Verification completed in this run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/python/test_ops_harness.py -k 'run_harness_cli or run_harness_scorecard or fake_harness_cli_scorecard_result or completed_process'`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/python/test_shared_test_support_contract.py -k 'run_harness_cli or run_harness_scorecard or fake_harness_cli_scorecard_result or completed_process or report_path_from_cli_args'`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `./.venv/bin/python -m py_compile tests/conftest.py tests/python/test_ops_harness.py tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/python/test_shared_test_support_contract.py`
  - AST boundary probe from Verification now passes
