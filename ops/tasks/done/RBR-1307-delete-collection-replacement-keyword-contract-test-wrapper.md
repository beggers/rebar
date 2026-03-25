## RBR-1307: Delete collection-replacement keyword-contract test wrapper

Status: done
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Delete the standalone `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py` layer by moving its still-useful collection-replacement keyword-contract coverage onto `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`, so the collection-replacement owner support stops carrying a second dedicated test suite for behavior that already belongs to the main owner test file.

## Deliverables
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- delete `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py`

## Acceptance Criteria
- Move the still-useful keyword-contract coverage off `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py` and onto `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`, including the current coverage for:
  - the support-ownership boundary around the collection-replacement keyword-contract surface;
  - pattern-helper and module-helper keyword-error workload builders and selector scope;
  - keyword-descriptor, numeric-descriptor, and callback-time materialization behavior;
  - internal probe measurement for keyword-error workloads; and
  - the implicit-zero `pattern.split` workload-signature normalization check.
- Keep the moved coverage behavior unchanged:
  - preserve the current selector boundaries for `_PATTERN_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS` and `_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS`;
  - preserve the current callback-time keyword-materialization assertions and CPython exception parity checks;
  - preserve the current workload-builder payload expectations and probe-measurement checks; and
  - keep the moved tests importing the owner support surface directly from `tests.benchmarks.collection_replacement_benchmark_anchor_support` plus the genuinely shared helpers from `tests.benchmarks.benchmark_test_support`, without introducing a new broker file or compatibility shim.
- Update `tests/benchmarks/test_benchmark_test_support.py` so its ownership/import assertions match the single-owner test-suite shape after the delete:
  - stop importing `tests.benchmarks.test_collection_replacement_keyword_contract_benchmark_support`;
  - point the shared collection-replacement classifier/import checks at `tests.benchmarks.test_collection_replacement_benchmark_anchor_support`; and
  - add or retain a direct assertion that the deleted keyword-contract test module is no longer imported or referenced under `tests/benchmarks`.
- Delete `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py` once its still-useful behavior and ownership assertions have been absorbed into `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'collection_replacement_keyword or keyword_error or keyword_kwargs_materialize or indexlike_descriptors_materialize or implicit_zero_maxsplit or shared_collection_replacement_classifier_contract_tests_import_from_support'`
- `bash -lc "test ! -e tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py && ! rg -n 'test_collection_replacement_keyword_contract_benchmark_support|collection_replacement_keyword_contract_benchmark_support' tests/benchmarks -g '*.py'"`

## Constraints
- Keep this cleanup structural and bounded to the benchmark test layer above. Do not change benchmark support implementation modules, workload manifests, harness runtime behavior, scorecard publication, README text, or tracked `ops/state/` prose.
- Prefer one owner test suite over two. The point is to collapse the extra keyword-contract test layer, not to relocate it behind another compatibility alias, helper module, or replacement file.
- Preserve the collection-replacement owner/support split already in the checkout: support logic stays in `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`, shared generic helpers stay in `tests/benchmarks/benchmark_test_support.py`, and this task only removes the extra test-only boundary.

## Notes
- `RBR-1307` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run; and
  - `rg -n "RBR-1307|RBR-1308|RBR-1309|RBR-1310" ops/state/current_status.md ops/state/backlog.md ops/tasks -g '*.md'` matched only historical mentions inside older done-task notes, not a live reservation for `RBR-1307`.
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue/runtime state was not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reported a clean worktree, no ready tasks, no blocked tasks, and the most recent `architecture-implementation` run finished `done`; and
  - the latest runtime snapshot showed no inherited-dirty, refresh, or commit anomaly.
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py` is a `2375`-line dedicated test file for a keyword-contract slice that already belongs to the `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` owner surface;
  - `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` is the `2807`-line main owner test suite for that same support module; and
  - `rg -n "test_collection_replacement_keyword_contract_benchmark_support|collection_replacement_keyword_contract_benchmark_support" tests/benchmarks -g '*.py'` currently reports only the import string inside `tests/benchmarks/test_benchmark_test_support.py`, confirming the extra suite is otherwise isolated.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'collection_replacement_keyword or keyword_error or keyword_kwargs_materialize or indexlike_descriptors_materialize or implicit_zero_maxsplit or shared_collection_replacement_classifier_contract_tests_import_from_support'` passed with `4 passed, 146 deselected in 0.13s`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py -k 'collection_replacement_keyword or keyword_error or keyword_kwargs_materialize or indexlike_descriptors_materialize or implicit_zero_maxsplit or shared_collection_replacement_classifier_contract_tests_import_from_support'` passed with `105 passed, 146 deselected in 0.22s`, which is the current fuller baseline before the delete; and
  - `bash -lc "test ! -e tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py && ! rg -n 'test_collection_replacement_keyword_contract_benchmark_support|collection_replacement_keyword_contract_benchmark_support' tests/benchmarks -g '*.py'"` currently fails because the dedicated test file and its remaining ownership reference still exist, and that failure belongs exactly to this cleanup.

## Completion Note
- Landed by moving the surviving collection-replacement keyword-contract coverage onto `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`, updating `tests/benchmarks/test_benchmark_test_support.py` to point at the single owner suite and assert the deleted wrapper stays unimportable/unreferenced, and deleting `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py`.
- Verification:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'collection_replacement_keyword or keyword_error or keyword_kwargs_materialize or indexlike_descriptors_materialize or implicit_zero_maxsplit or shared_collection_replacement_classifier_contract_tests_import_from_support'` passed with `90 passed, 147 deselected in 0.40s`.
  - `bash -lc "test ! -e tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py && ! rg -n 'test_collection_replacement_keyword_contract_benchmark_support|collection_replacement_keyword_contract_benchmark_support' tests/benchmarks -g '*.py'"` passed.
