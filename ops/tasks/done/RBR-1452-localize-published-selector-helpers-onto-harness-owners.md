## RBR-1452: Localize published selector helpers onto harness owners

Owner: architecture-implementation
Created: 2026-03-27

## Goal
- Remove the published-subset selector helper trio from `python/rebar_harness/scorecard_io.py`.
- Keep correctness fixture selection owned by `python/rebar_harness/correctness.py` and benchmark manifest selection owned by `python/rebar_harness/benchmarks.py`, so `scorecard_io.py` goes back to scorecard/report plumbing instead of carrying selector-registry glue.

## Deliverables
- `python/rebar_harness/scorecard_io.py`
- `python/rebar_harness/correctness.py`
- `python/rebar_harness/benchmarks.py`
- `tests/python/test_ops_harness.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`

## Acceptance Criteria
- `python/rebar_harness/correctness.py` no longer imports selector-registry helpers from `rebar_harness.scorecard_io`; it owns the smallest local helper path needed to build `_CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR` and `select_correctness_fixture_paths(...)` while preserving:
  - the current selector names
  - published-order subset resolution
  - the existing correctness-specific missing-filename and unknown-selector error text
- `python/rebar_harness/benchmarks.py` no longer imports selector-registry helpers from `rebar_harness.scorecard_io`; it owns the smallest local helper path needed to build `_BENCHMARK_MANIFEST_FILENAMES_BY_SELECTOR` and `select_benchmark_manifest_paths(...)` while preserving:
  - the current selector names
  - published-order subset resolution
  - the existing benchmark-specific missing-filename and unknown-selector error text
- Delete these helper definitions from `python/rebar_harness/scorecard_io.py` instead of moving them to another shared selector module:
  - `ordered_published_subset_filenames(...)`
  - `build_published_subset_registry(...)`
  - `select_published_subset_paths(...)`
- `tests/python/test_ops_harness.py` stops owning direct unit tests for those selector helpers as `scorecard_io` behavior; relocate or replace that coverage in the owner-facing correctness/benchmark contract suites instead of recreating another detached selector-only support layer.
- `tests/python/test_fixture_parity_support_contract.py` and `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` validate selector membership, published-order, and missing-filename behavior through the owner harness APIs or owner-local helpers instead of importing selector helpers from `rebar_harness.scorecard_io`.
- Keep the run structural only:
  - do not change Rust sources, `python/rebar/__init__.py`, workload/fixture data files, published reports, README copy, scripts, or tracked project-state prose
  - do not add a replacement shared selector utility module under `python/rebar_harness/` or `tests/`

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/python/test_ops_harness.py::ReadmeReportingTest::test_scorecard_ordered_published_subset_filenames_deduplicates_requested_names tests/python/test_ops_harness.py::ReadmeReportingTest::test_scorecard_build_published_subset_registry_preserves_published_order tests/python/test_ops_harness.py::ReadmeReportingTest::test_scorecard_build_published_subset_registry_deduplicates_requested_names tests/python/test_ops_harness.py::ReadmeReportingTest::test_scorecard_build_published_subset_registry_rejects_unknown_requested_filenames tests/python/test_ops_harness.py::ReadmeReportingTest::test_scorecard_select_published_subset_paths_resolves_root_and_unknown_selector tests/python/test_fixture_parity_support_contract.py::test_canonical_published_subset_selectors_keep_explicit_membership_contract tests/python/test_fixture_parity_support_contract.py::test_correctness_selector_subset_helper_keeps_fixture_specific_missing_filename_error tests/python/test_fixture_parity_support_contract.py::test_unknown_correctness_fixture_selector_raises_clear_error tests/benchmarks/test_benchmark_publication_runtime_contracts.py::test_shared_benchmark_manifest_selectors_resolve_published_subset_invariants tests/benchmarks/test_benchmark_publication_runtime_contracts.py::test_built_native_smoke_manifest_selector_keeps_membership_contract tests/benchmarks/test_benchmark_publication_runtime_contracts.py::test_benchmark_selector_subset_helper_keeps_benchmark_specific_missing_filename_error`
- `./.venv/bin/python -m py_compile python/rebar_harness/scorecard_io.py python/rebar_harness/correctness.py python/rebar_harness/benchmarks.py tests/python/test_ops_harness.py tests/python/test_fixture_parity_support_contract.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py`
- `bash -lc "! rg -n '^def (ordered_published_subset_filenames|build_published_subset_registry|select_published_subset_paths)\\(' python/rebar_harness/scorecard_io.py"`

## Notes
- Queue and JSON check in this planning run:
  - `.rebar/runtime/dashboard.md` reported `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the runtime JSON count was not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this planning run:
  - `ops/tasks/blocked/` contained no architecture task to reopen or normalize first.
  - `rg -n 'RBR-1452|RBR-1453|RBR-1454' ops/state/current_status.md ops/state/backlog.md ops/tasks -g '*.md'` returned no reserved future-task match for `RBR-1452`.
- Candidate selection in this planning run:
  - The first candidate, deleting `tests/python/fixture_parity_support.py` outright, was rejected as too wide for one run because the module still spans many parity-suite owners even after the recent owner-localization passes.
  - `python/rebar_harness/scorecard_io.py` still carries three selector-registry helpers that are not scorecard/report I/O and are used only to bridge `python/rebar_harness/correctness.py`, `python/rebar_harness/benchmarks.py`, and selector-contract tests.
  - `tests/benchmarks/` no longer contains a smaller detached shared support layer to burn down first, so the scorecard-selector wrapper is the remaining bounded cross-file simplification that still removes an entire shared helper layer.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/python/test_ops_harness.py::ReadmeReportingTest::test_scorecard_ordered_published_subset_filenames_deduplicates_requested_names tests/python/test_ops_harness.py::ReadmeReportingTest::test_scorecard_build_published_subset_registry_preserves_published_order tests/python/test_ops_harness.py::ReadmeReportingTest::test_scorecard_build_published_subset_registry_deduplicates_requested_names tests/python/test_ops_harness.py::ReadmeReportingTest::test_scorecard_build_published_subset_registry_rejects_unknown_requested_filenames tests/python/test_ops_harness.py::ReadmeReportingTest::test_scorecard_select_published_subset_paths_resolves_root_and_unknown_selector tests/python/test_fixture_parity_support_contract.py::test_canonical_published_subset_selectors_keep_explicit_membership_contract tests/python/test_fixture_parity_support_contract.py::test_correctness_selector_subset_helper_keeps_fixture_specific_missing_filename_error tests/python/test_fixture_parity_support_contract.py::test_unknown_correctness_fixture_selector_raises_clear_error tests/benchmarks/test_benchmark_publication_runtime_contracts.py::test_shared_benchmark_manifest_selectors_resolve_published_subset_invariants tests/benchmarks/test_benchmark_publication_runtime_contracts.py::test_built_native_smoke_manifest_selector_keeps_membership_contract tests/benchmarks/test_benchmark_publication_runtime_contracts.py::test_benchmark_selector_subset_helper_keeps_benchmark_specific_missing_filename_error` passed (`12 passed in 0.11s`).
  - `./.venv/bin/python -m py_compile python/rebar_harness/scorecard_io.py python/rebar_harness/correctness.py python/rebar_harness/benchmarks.py tests/python/test_ops_harness.py tests/python/test_fixture_parity_support_contract.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py` passed.
  - `rg -n '^def (ordered_published_subset_filenames|build_published_subset_registry|select_published_subset_paths)\(' python/rebar_harness/scorecard_io.py` currently reports the three shared selector-helper definitions at lines `35`, `55`, and `78`, so the negative `rg` verification above fails only on the exact cleanup this task queues.

## Completion
- Localized the published-subset selector helpers into `python/rebar_harness/correctness.py` and `python/rebar_harness/benchmarks.py`, preserving selector names, published-order subset resolution, and the existing correctness- and benchmark-specific error text while deleting the shared selector trio from `python/rebar_harness/scorecard_io.py`.
- Moved selector-contract coverage onto the harness owners: the correctness and benchmark support-contract suites now exercise the owner-local helpers and public selector APIs, while `tests/python/test_ops_harness.py` only asserts that `scorecard_io.py` no longer exposes the deleted selector helpers.
- Verification in this run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/python/test_ops_harness.py::ReadmeReportingTest::test_scorecard_ordered_published_subset_filenames_deduplicates_requested_names tests/python/test_ops_harness.py::ReadmeReportingTest::test_scorecard_build_published_subset_registry_preserves_published_order tests/python/test_ops_harness.py::ReadmeReportingTest::test_scorecard_build_published_subset_registry_deduplicates_requested_names tests/python/test_ops_harness.py::ReadmeReportingTest::test_scorecard_build_published_subset_registry_rejects_unknown_requested_filenames tests/python/test_ops_harness.py::ReadmeReportingTest::test_scorecard_select_published_subset_paths_resolves_root_and_unknown_selector tests/python/test_fixture_parity_support_contract.py::test_canonical_published_subset_selectors_keep_explicit_membership_contract tests/python/test_fixture_parity_support_contract.py::test_correctness_selector_subset_helper_keeps_fixture_specific_missing_filename_error tests/python/test_fixture_parity_support_contract.py::test_unknown_correctness_fixture_selector_raises_clear_error tests/benchmarks/test_benchmark_publication_runtime_contracts.py::test_shared_benchmark_manifest_selectors_resolve_published_subset_invariants tests/benchmarks/test_benchmark_publication_runtime_contracts.py::test_built_native_smoke_manifest_selector_keeps_membership_contract tests/benchmarks/test_benchmark_publication_runtime_contracts.py::test_benchmark_selector_subset_helper_keeps_benchmark_specific_missing_filename_error` passed (`12 passed in 0.42s`).
  - `./.venv/bin/python -m py_compile python/rebar_harness/scorecard_io.py python/rebar_harness/correctness.py python/rebar_harness/benchmarks.py tests/python/test_ops_harness.py tests/python/test_fixture_parity_support_contract.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py` passed.
  - `bash -lc "! rg -n '^def (ordered_published_subset_filenames|build_published_subset_registry|select_published_subset_paths)\\(' python/rebar_harness/scorecard_io.py"` passed.
