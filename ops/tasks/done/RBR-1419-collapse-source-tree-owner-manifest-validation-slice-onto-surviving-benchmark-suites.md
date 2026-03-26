## RBR-1419: Collapse the source-tree owner manifest-validation slice onto the surviving benchmark suites

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove the remaining source-tree-owner contract slice from `tests/benchmarks/test_benchmark_manifest_validation.py` now that the surviving owner suites are `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- The manifest-validation file still imports `tests.benchmarks.source_tree_benchmark_anchor_support as source_tree_support` and rebinds `collection_replacement_support = source_tree_support`, which keeps one more cross-suite owner route alive than the benchmark test stack needs.
- Leave `tests/benchmarks/test_benchmark_manifest_validation.py` as the home for generic manifest/payload validation only, and move the owner-specific contract-row coverage back onto the surviving benchmark owner suites.

## Deliverables
- `tests/benchmarks/test_benchmark_manifest_validation.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- `tests/benchmarks/test_benchmark_manifest_validation.py` no longer imports `tests.benchmarks.source_tree_benchmark_anchor_support` and no longer defines `collection_replacement_support = source_tree_support`.
- Move the source-tree-owner contract coverage below off `tests/benchmarks/test_benchmark_manifest_validation.py` and onto the surviving owner suites, preserving the current behavior and anchor checks:
  - compiled-pattern module-compile contract-row round-trip and bounded `IGNORECASE` rejection coverage
  - compiled-pattern wrong-text-model contract-row round-trip and CPython outcome coverage
  - compiled-pattern module-success contract-row round-trip coverage
  - compiled-pattern helper-keyword contract-row round-trip, payload-type, and CPython outcome coverage
  - bounded `pattern-boundary` haystack-text-model acceptance coverage for the wrong-text-model trio
- Keep the genuinely generic manifest/payload validation coverage in `tests/benchmarks/test_benchmark_manifest_validation.py`, including loader rejection, replacement payload normalization, expected-exception normalization/validation, generic compiled-pattern validation entry-point checks, haystack-text-model entry-point checks, and module-boundary entry-point checks.
- Update the touched benchmark support-contract tests so they treat `tests/benchmarks/test_benchmark_manifest_validation.py` as a generic consumer only; add or keep an assertion that it no longer routes source-tree owner surfaces through direct imports or local aliases.
- Remove live `source_tree_support.` and `collection_replacement_support.` references from `tests/benchmarks/test_benchmark_manifest_validation.py`.
- Keep this task bounded to deleting that detached owner-validation route; do not reopen benchmark workload manifests, `source_tree_benchmark_anchor_support.py` support-surface decomposition, or report/status updates.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile_contract_rows_preserve_success_and_keyword_payload_round_trip_until_helper_invocation or compiled_pattern_wrong_text_model_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation or compiled_pattern_module_success_contract_rows_preserve_live_source_selection_and_payload_round_trip_until_helper_invocation or compiled_pattern_module_helper_keyword_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation or haystack_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio'`
- `python3 -m py_compile tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n 'from tests\\.benchmarks import source_tree_benchmark_anchor_support as source_tree_support|collection_replacement_support = source_tree_support|source_tree_support\\.|collection_replacement_support\\.' tests/benchmarks/test_benchmark_manifest_validation.py"`

## Completion
- Landed by removing the source-tree owner import/alias and all detached owner-contract rows from `tests/benchmarks/test_benchmark_manifest_validation.py`, leaving that file as a generic manifest and payload validation consumer.
- Re-homed the compiled-pattern module-compile, wrong-text-model, module-success, helper-keyword, and `pattern-boundary` haystack-text-model acceptance coverage in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Tightened the support-contract checks in `tests/benchmarks/test_benchmark_test_support.py` and `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so manifest validation is asserted to stay generic and no longer import or alias source-tree owner surfaces.
- Verification:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile_contract_rows_preserve_success_and_keyword_payload_round_trip_until_helper_invocation or compiled_pattern_wrong_text_model_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation or compiled_pattern_module_success_contract_rows_preserve_live_source_selection_and_payload_round_trip_until_helper_invocation or compiled_pattern_module_helper_keyword_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation or haystack_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio'` passed with `16 passed, 513 deselected in 0.28s`.
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'benchmark_manifest_validation_routes_owner_surfaces_through_package_imports or benchmark_manifest_validation_stays_generic_without_source_tree_owner_routes or source_tree_contract_builder_consumers_route_owner_surface_through_package_alias'` passed with `3 passed, 359 deselected in 0.42s`.
  - `python3 -m py_compile tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_test_support.py` passed.
  - `bash -lc "! rg -n 'from tests\\.benchmarks import source_tree_benchmark_anchor_support as source_tree_support|collection_replacement_support = source_tree_support|source_tree_support\\.|collection_replacement_support\\.' tests/benchmarks/test_benchmark_manifest_validation.py"` passed.

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the runtime counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` had no architecture task to reopen or normalize first.
  - `rg -n "RBR-1419|RBR-1420|RBR-1421" ops/state/current_status.md ops/state/backlog.md ops/tasks ops/state/decision_log.md` found no reserved future-id use for `RBR-1419`; the only hits were historical notes inside completed `RBR-1417` and `RBR-1418` task files.
- Candidate selection in this run:
  - `tests/benchmarks/test_benchmark_manifest_validation.py` still imports `source_tree_benchmark_anchor_support` directly and then uses `source_tree_support.` / `collection_replacement_support.` across the owner-specific compiled-pattern contract block.
  - The surviving owner suites already exist in `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, so this is a detached owner-route collapse rather than a new helper family.
  - I stopped after this first viable post-JSON candidate instead of widening into a second cleanup probe.
