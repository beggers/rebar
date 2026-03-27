## RBR-1445: Localize module-workflow argument-signature helpers onto owner suites

Owner: architecture-implementation
Created: 2026-03-27

## Goal
- Remove the remaining module-workflow argument-signature helper layer from `tests/python/fixture_parity_support.py`, where two helper functions still sit in shared parity support even though only the module-workflow parity suite and the combined benchmark owner suite consume them.
- Keep `tests/python/test_module_workflow_parity_suite.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` responsible for their own module-workflow argument-signature normalization so shared fixture parity support stays focused on cross-suite fixture/parity behavior instead of owner-local benchmark anchoring logic.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- Rewrite `tests/python/test_module_workflow_parity_suite.py` so it no longer imports `module_workflow_positional_args_signature` or `module_workflow_keyword_kwargs_signature` from `tests.python.fixture_parity_support`, and instead defines the module-workflow signature helper(s) it needs locally.
- Rewrite `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so it no longer imports those two helpers from `tests.python.fixture_parity_support`, and instead defines the module-workflow signature helper(s) it needs locally.
- Remove `module_workflow_positional_args_signature()`, `module_workflow_keyword_kwargs_signature()`, and their now-private `_encoded_indexlike_value()` helper from `tests/python/fixture_parity_support.py`, along with any imports that only supported that helper layer.
- Tighten `tests/python/test_fixture_parity_support_contract.py` so the shared-support contract asserts those argument-signature helpers are no longer exported from `tests.python.fixture_parity_support`.
- Update `tests/benchmarks/test_benchmark_test_support.py` only as needed so the meta-tests keep asserting the combined benchmark owner suite defines this signature surface locally rather than through shared support.
- Keep the run bounded to this shared-layer deletion:
  - do not move `IndexLike`, `RecordingIndexLike`, `IndexLikeBoomError`, `RecordingNativeBoundary`, `case_pattern`, or any bundle-loading/parity assertion helpers
  - do not change correctness fixtures, benchmark workloads, harness runtime behavior, reports, or tracked project-state files

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/python/test_fixture_parity_support_contract.py -k 'module_workflow_positional_args_signature or module_workflow_keyword_kwargs_signature'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/python/test_module_workflow_parity_suite.py -k 'workflow_keyword_kwargs_signature or workflow_positional_args_signature or AlternateIndexLike'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'module_workflow_keyword_standard_benchmark or positional_indexlike'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'source_tree_contract_helper_suites_import_shared_alias_but_define_local_helpers'`
- `bash -lc "! rg -n '^def module_workflow_(positional_args_signature|keyword_kwargs_signature)\\b|^def _encoded_indexlike_value\\b' tests/python/fixture_parity_support.py"`
- `./.venv/bin/python -m py_compile tests/python/fixture_parity_support.py tests/python/test_module_workflow_parity_suite.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/python/test_fixture_parity_support_contract.py tests/benchmarks/test_benchmark_test_support.py`

## Notes
- Queue and JSON check in this planning run:
  - `.rebar/runtime/dashboard.md` reported `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the runtime JSON counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1445|RBR-1446|RBR-1447" ops/state/current_status.md ops/state/backlog.md` returned no reserved future ids, so `RBR-1445` was available.
- Candidate selection in this run:
  - `rg -n "module_workflow_(keyword_kwargs_signature|positional_args_signature)" tests/python/fixture_parity_support.py tests/python/test_module_workflow_parity_suite.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/python/test_fixture_parity_support_contract.py tests/benchmarks/test_benchmark_test_support.py` showed those helpers are defined only in `tests/python/fixture_parity_support.py`, consumed only by `tests/python/test_module_workflow_parity_suite.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and otherwise referenced only by owner-contract/meta-test coverage.
  - `tests/benchmarks/test_benchmark_test_support.py` already treats this surface as owner-local to the combined benchmark suite, which makes the shared helper layer a good fit for bounded localization.
  - I rejected a broader `tests/benchmarks/benchmark_test_support.py` simplification as the first probe because that file still owns actively shared manifest-loading helpers across multiple benchmark suites and manifest-validation coverage, so the next bounded step there would not remove an entire cross-file layer.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/python/test_fixture_parity_support_contract.py -k 'module_workflow_positional_args_signature or module_workflow_keyword_kwargs_signature or IndexLike or RecordingIndexLike or RecordingNativeBoundary'` passed (`7 passed, 421 deselected`).
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/python/test_module_workflow_parity_suite.py -k 'workflow_keyword_kwargs_signature or workflow_positional_args_signature or AlternateIndexLike'` passed (`5 passed, 1510 deselected`).
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'module_workflow_keyword_standard_benchmark or positional_indexlike'` passed (`7 passed, 306 deselected`).
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'source_tree_contract_helper_suites_import_shared_alias_but_define_local_helpers'` passed (`1 passed, 222 deselected`).
  - `bash -lc "! rg -n '^def module_workflow_(positional_args_signature|keyword_kwargs_signature)\\b|^def _encoded_indexlike_value\\b' tests/python/fixture_parity_support.py"` is currently red because that shared argument-signature layer still exists and is the target of this task.

## Completion
- Localized the module-workflow argument-signature normalization into `tests/python/test_module_workflow_parity_suite.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, so both owner suites now define the signature helpers they use instead of importing them from shared parity support.
- Deleted `module_workflow_positional_args_signature()`, `module_workflow_keyword_kwargs_signature()`, and `_encoded_indexlike_value()` from `tests/python/fixture_parity_support.py`, leaving the shared module focused on cross-suite fixture and parity helpers.
- Tightened `tests/python/test_fixture_parity_support_contract.py` so the shared-support contract now asserts those two module-workflow signature helpers are no longer exported from `tests.python.fixture_parity_support`; `tests/benchmarks/test_benchmark_test_support.py` already covered the combined benchmark suite's owner-local helper surface and did not need changes.
- Verification in this run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/python/test_fixture_parity_support_contract.py -k 'module_workflow_positional_args_signature or module_workflow_keyword_kwargs_signature'`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/python/test_module_workflow_parity_suite.py -k 'workflow_keyword_kwargs_signature or workflow_positional_args_signature or AlternateIndexLike'`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'module_workflow_keyword_standard_benchmark or positional_indexlike'`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'source_tree_contract_helper_suites_import_shared_alias_but_define_local_helpers'`
  - `bash -lc "! rg -n '^def module_workflow_(positional_args_signature|keyword_kwargs_signature)\\b|^def _encoded_indexlike_value\\b' tests/python/fixture_parity_support.py"`
  - `./.venv/bin/python -m py_compile tests/python/fixture_parity_support.py tests/python/test_module_workflow_parity_suite.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/python/test_fixture_parity_support_contract.py tests/benchmarks/test_benchmark_test_support.py`
