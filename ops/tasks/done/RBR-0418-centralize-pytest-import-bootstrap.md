# RBR-0418: Centralize pytest import bootstrap under `tests/conftest.py`

Status: done
Owner: architecture-implementation
Created: 2026-03-15
Completed: 2026-03-15

## Goal
- Make one root `tests/conftest.py` the sole pytest-owned import-path bootstrap for the repo, so benchmark, conformance, and the remaining source-tree wrapper tests stop open-coding `sys.path` mutation before importing `rebar_harness` or `rebar`.

## Deliverables
- Add `tests/conftest.py`
- `tests/python/conftest.py`
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/test_correctness_fixture_inventory_contract.py`
- `tests/conformance/test_python_fixture_manifest_contract.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/native_benchmark_test_support.py`
- `tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py`
- `tests/benchmarks/test_python_benchmark_manifest_contract.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/python/test_rust_compile_match_boundary.py`
- `tests/python/test_readme_reporting.py`

## Acceptance Criteria
- Add a root `tests/conftest.py` that derives `REPO_ROOT` / `PYTHON_SOURCE` once and inserts the repo `python/` tree onto `sys.path` for pytest collection.
- `tests/conftest.py` becomes the only file under `tests/` that mutates `sys.path` to expose repo-local Python modules during pytest runs.
- `tests/python/conftest.py` keeps only the cache-purge and backend-selection fixtures. It no longer owns repo-root / Python-source bootstrap.
- Every listed deliverable above imports successfully through the root pytest bootstrap instead of a file-local `sys.path.append(...)` or `sys.path.insert(...)` block.
- Files that still need `PYTHON_SOURCE` for subprocess environments may keep a local path constant, but no file outside `tests/conftest.py` should mutate `sys.path`.
- Files that only used `PYTHON_SOURCE` for in-process imports drop that constant entirely instead of keeping dead path plumbing.
- Do not change benchmark or correctness behavior while removing the bootstrap duplication:
  - keep the current subprocess `cwd` and `env={"PYTHONPATH": ...}` behavior where scorecard runners or built-native helpers already depend on it;
  - keep existing report paths, manifest/fixture contents, scorecard payloads, and assertion logic unchanged; and
  - do not broaden the task into converting `unittest` suites to pytest-style tests.
- After the cleanup, `rg -n "sys\\.path\\.(append|insert)\\(" tests | rg -v '^tests/conftest.py:'` returns no matches.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/conformance/test_correctness_fixture_inventory_contract.py tests/conformance/test_python_fixture_manifest_contract.py tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py tests/benchmarks/test_python_benchmark_manifest_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_adapter_provenance.py tests/benchmarks/test_built_native_benchmark_modes.py tests/python/test_rust_compile_match_boundary.py tests/python/test_readme_reporting.py`.

## Constraints
- Keep this task on test-harness bootstrap plumbing only. Do not change Rust code, `python/rebar/`, benchmark workloads, correctness fixtures, published reports, README reporting, or tracked state files beyond this task file.
- Prefer the standard pytest `tests/conftest.py` path over adding another bespoke support module, environment wrapper, or generated bootstrap layer.
- Preserve local `REPO_ROOT` / `PYTHON_SOURCE` constants where subprocess environment assembly still needs them. The cleanup target is duplicated import-path mutation, not every path constant.
- Do not add fallback bootstrap wrappers just to preserve ad hoc `python tests/...` execution. The supported verification path for this cleanup remains pytest.

## Notes
- The runtime dashboard is clean and current for `HEAD`, the ready queue is empty, and both tracked and live JSON counts are zero (`tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, `git ls-files '*.json' | wc -l = 0`, `rg --files -g '*.json' | wc -l = 0`), so this run should seed a post-JSON harness simplification instead of another JSON burn-down task.
- `tests/python/conftest.py` already acts as the shared pytest bootstrap for the parity suites, but the same repo-path wiring is still duplicated across benchmark and conformance helpers plus a couple remaining python wrapper tests.
- Current `rg -n "sys\\.path\\.(append|insert)\\(" tests` hits the same bootstrap pattern in `tests/conformance/correctness_expectations.py`, `tests/conformance/test_correctness_fixture_inventory_contract.py`, `tests/conformance/test_python_fixture_manifest_contract.py`, `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/native_benchmark_test_support.py`, `tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py`, `tests/benchmarks/test_python_benchmark_manifest_contract.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, `tests/python/conftest.py`, `tests/python/test_rust_compile_match_boundary.py`, and `tests/python/test_readme_reporting.py`.
- This task extends the existing single-owner pytest pattern to the rest of the repo without inventing another registry or helper abstraction.

## Completion
- 2026-03-15: Added root `tests/conftest.py` as the sole pytest-owned import bootstrap, deriving `REPO_ROOT` / `PYTHON_SOURCE` once and inserting the repo `python/` tree onto `sys.path` for collection.
- 2026-03-15: Removed file-local `sys.path` mutation from the listed conformance, benchmark, and python test helpers; kept local `PYTHON_SOURCE` constants only in modules that still assemble subprocess `PYTHONPATH` environments.
- 2026-03-15: Trimmed `tests/python/conftest.py` down to cache-purge and backend-selection fixtures so it no longer owns repo-root bootstrap plumbing.

## Verification
- 2026-03-15: `rg -n "sys\\.path\\.(append|insert)\\(" tests | rg -v '^tests/conftest.py:'` (no matches)
- 2026-03-15: `PYTHONPATH=python .venv/bin/python -m pytest -q tests/conformance/test_correctness_fixture_inventory_contract.py tests/conformance/test_python_fixture_manifest_contract.py tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py tests/benchmarks/test_python_benchmark_manifest_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_adapter_provenance.py tests/benchmarks/test_built_native_benchmark_modes.py tests/python/test_rust_compile_match_boundary.py tests/python/test_readme_reporting.py` (`61 passed, 3 skipped, 2979 subtests passed`)
