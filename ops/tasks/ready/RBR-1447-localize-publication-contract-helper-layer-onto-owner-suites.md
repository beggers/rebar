## RBR-1447: Localize publication-contract helper layer onto owner suites

Owner: architecture-implementation
Created: 2026-03-27

## Goal
- Remove the publication-selector and published-manifest contract helper cluster from `tests/conftest.py` now that it is only shared by two owner suites plus `tests/python/test_shared_test_support_contract.py`.
- Move those assertions onto the correctness-fixture and benchmark-publication owner suites that actually consume them, so this support path stops routing through a generic cross-suite helper layer plus a second contract file.

## Deliverables
- `tests/conftest.py`
- `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_shared_test_support_contract.py`

## Acceptance Criteria
- Rewrite `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` so it no longer imports publication-contract helpers from `tests.conftest`, and instead owns the selector-subset and published-manifest assertion helpers it needs locally.
- Rewrite `tests/python/test_fixture_parity_support_contract.py` so it no longer imports publication-contract helpers from `tests.conftest`, and instead owns the selector-subset and published-manifest assertion helpers it needs locally.
- Delete these helper functions from `tests/conftest.py` because they are no longer shared across owner suites:
  - `declared_string_constants_by_suffix`
  - `assert_declared_string_selector_registry_contract`
  - `assert_published_selector_subset_paths_contract`
  - `assert_published_manifest_helper_contract`
  - `assert_published_manifest_helper_reload_contract`
  - `assert_published_manifest_inventory_contract`
- Update `tests/python/test_shared_test_support_contract.py` only as needed so it stops asserting import structure around the deleted publication-contract helper layer.
- Keep the run bounded to this shared-layer deletion:
  - do not change `python/rebar_harness/`, `python/rebar/`, `tests/conformance/`, or `benchmarks/workloads/`
  - do not add a replacement shared support module

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_publication_runtime_contracts.py tests/python/test_fixture_parity_support_contract.py tests/python/test_shared_test_support_contract.py`
- `./.venv/bin/python -m py_compile tests/conftest.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py tests/python/test_fixture_parity_support_contract.py tests/python/test_shared_test_support_contract.py`
- `bash -lc "! rg -n 'def (declared_string_constants_by_suffix|assert_declared_string_selector_registry_contract|assert_published_selector_subset_paths_contract|assert_published_manifest_helper_contract|assert_published_manifest_helper_reload_contract|assert_published_manifest_inventory_contract)\\b' tests/conftest.py && ! rg -n 'assert_declared_string_selector_registry_contract|assert_published_manifest_inventory_contract|assert_published_manifest_helper_contract|assert_published_manifest_helper_reload_contract|assert_published_selector_subset_paths_contract|declared_string_constants_by_suffix' tests/python/test_shared_test_support_contract.py"`

## Notes
- Queue and JSON check in this planning run:
  - `.rebar/runtime/dashboard.md` reported `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the runtime JSON counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1447|RBR-1448|RBR-1449|RBR-1450" ops/state/current_status.md ops/state/backlog.md` returned no reserved future ids, so `RBR-1447` was available.
- Candidate selection in this run:
  - `rg -n "assert_declared_string_selector_registry_contract|assert_published_manifest_inventory_contract|assert_published_manifest_helper_contract|assert_published_manifest_helper_reload_contract|assert_published_selector_subset_paths_contract|declared_string_constants_by_suffix" tests/benchmarks/test_benchmark_publication_runtime_contracts.py tests/python/test_fixture_parity_support_contract.py tests/python/test_shared_test_support_contract.py` showed that this helper cluster is consumed only by the benchmark-publication contract suite, the fixture-parity contract suite, and the generic shared-support contract file.
  - `tests/conftest.py` is 309 lines, while the two owner suites already contain the domain-specific selector and manifest assertions that use this helper layer; the remaining shared helpers now exist mainly to route owner-local checks through a generic support file.
  - `tests/python/test_shared_test_support_contract.py` still spends its opening block re-testing these helper exports even though the only live functional consumers are the two owner suites above.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_publication_runtime_contracts.py tests/python/test_fixture_parity_support_contract.py tests/python/test_shared_test_support_contract.py` passed (`655 passed, 3 skipped`).
  - `./.venv/bin/python -m py_compile tests/conftest.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py tests/python/test_fixture_parity_support_contract.py tests/python/test_shared_test_support_contract.py` passed.
  - The negative `rg` verification is intentionally red in the current checkout because `tests/conftest.py` and `tests/python/test_shared_test_support_contract.py` still carry the shared publication-contract helper layer that this task deletes.
