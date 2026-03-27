## RBR-1449: Localize non-parity fixture support usage onto owner suites

Owner: architecture-implementation
Created: 2026-03-27

## Goal
- Remove the remaining benchmark and correctness-publication dependency path from `tests/benchmarks/` and `tests/conformance/` into `tests/python/fixture_parity_support.py`.
- Keep `tests/python/fixture_parity_support.py` scoped to Python parity suites and its own contract surface instead of letting benchmark/report owners route through a Python-lane support module.

## Deliverables
- `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/conformance/test_combined_correctness_scorecards.py`

## Acceptance Criteria
- Rewrite `tests/conformance/test_combined_correctness_scorecards.py` so it no longer imports `manifest_records_by_id` from `tests.python.fixture_parity_support`, and instead owns the tiny manifest-id indexing helper it needs locally.
- Rewrite `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` so it no longer imports support helpers from `tests.python.fixture_parity_support`, and instead owns the duplicate-id, callable-signature, and match/pattern parity helpers it needs locally.
- Rewrite `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so it no longer imports support helpers or published-bytes case constants from `tests.python.fixture_parity_support`, and instead owns the local helper and bounded bytes-surface data it needs for benchmark assertions.
- Keep the run structural only:
  - do not change `python/rebar_harness/`, `python/rebar/`, `tests/python/*.py`, published reports, or tracked project-state prose
  - do not add a replacement shared support module under `tests/`
- After the cleanup, no file under `tests/benchmarks/` or `tests/conformance/` may import from `tests.python.fixture_parity_support`.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_publication_runtime_contracts.py tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `./.venv/bin/python -m py_compile tests/benchmarks/test_benchmark_publication_runtime_contracts.py tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n 'from tests\\.python\\.fixture_parity_support import|import tests\\.python\\.fixture_parity_support|fixture_parity_support\\.' tests/benchmarks/test_benchmark_publication_runtime_contracts.py tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Notes
- Completed 2026-03-27:
  - Localized manifest indexing in `tests/conformance/test_combined_correctness_scorecards.py`.
  - Localized duplicate-id, callable-signature, and pattern/match parity helpers in `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`.
  - Localized record helpers, bounded bytes supplemental cases, and case accessors in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
  - Verified the three owner suites no longer import from `tests.python.fixture_parity_support`.
- Verification in this run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_publication_runtime_contracts.py tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed (`561 passed, 3 skipped, 4041 subtests passed`).
  - `./.venv/bin/python -m py_compile tests/benchmarks/test_benchmark_publication_runtime_contracts.py tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed.
  - `bash -lc "! rg -n 'from tests\\.python\\.fixture_parity_support import|import tests\\.python\\.fixture_parity_support|fixture_parity_support\\.' tests/benchmarks/test_benchmark_publication_runtime_contracts.py tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` passed.

- Queue and JSON check in this planning run:
  - `.rebar/runtime/dashboard.md` reported `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the runtime JSON count was not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` contained only `.gitkeep`, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1449|RBR-1450|RBR-1451|RBR-1452" ops/state/current_status.md ops/state/backlog.md` returned no matches, so `RBR-1449` was available.
- Candidate selection in this run:
  - `rg -n "from tests\\.python\\.fixture_parity_support import|import tests\\.python\\.fixture_parity_support|fixture_parity_support\\." tests/python tests/conformance tests/benchmarks` showed only three non-parity consumers left: `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `tests/conformance/test_combined_correctness_scorecards.py`.
  - Those files currently pull a bounded helper subset across the owner boundary:
    - `tests/conformance/test_combined_correctness_scorecards.py` imports only `manifest_records_by_id`.
    - `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` imports `assert_match_result_parity`, `assert_pattern_parity`, `callable_match_group_signature`, and `duplicate_string_ids`.
    - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` imports helper functions plus the open-ended and broader-range bytes case constants.
  - `tests/python/fixture_parity_support.py` is still a large Python-lane support module (`2061` lines), so keeping benchmark and publication suites coupled to it preserves a cross-lane architecture path even after the earlier shared-helper cleanup tasks landed.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_publication_runtime_contracts.py tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed (`561 passed, 3 skipped, 4041 subtests passed`).
  - `./.venv/bin/python -m py_compile tests/benchmarks/test_benchmark_publication_runtime_contracts.py tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/python/fixture_parity_support.py tests/python/test_fixture_parity_support_contract.py` passed.
  - The negative `rg` verification is intentionally red in the current checkout because the three owner suites still import from `tests.python.fixture_parity_support`, which is the exact boundary this task removes.
