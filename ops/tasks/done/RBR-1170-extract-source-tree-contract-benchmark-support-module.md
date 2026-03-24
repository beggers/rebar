## RBR-1170: Extract source-tree contract benchmark support module

Status: done
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the shared source-tree contract-builder plumbing that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving it into one dedicated benchmark-support module, so the giant combined benchmark suite stops owning the generic manifest/workload synthesis layer that already feeds multiple contract families.

## Deliverables
- `tests/benchmarks/source_tree_contract_benchmark_support.py`
- `tests/benchmarks/test_source_tree_contract_benchmark_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Add one bounded shared benchmark-support module at `tests/benchmarks/source_tree_contract_benchmark_support.py` for the current generic source-tree contract-builder surface that is still embedded in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`:
  - move `_SourceTreeContractBuilderSpec`;
  - move `_source_tree_contract_manifest_payload(...)`;
  - move `_source_tree_contract_workload(...)`;
  - move `_source_tree_contract_manifest(...)`; and
  - move `_contract_source_workloads(...)`.
- Keep that support module as ordinary Python benchmark support code limited to the existing source-tree contract synthesis surface that is already reused by:
  - the compiled-pattern module-helper keyword contract family;
  - the compiled-pattern module success and `module.compile` contract families; and
  - the wrong-text-model owner-contract family.
- Add focused coverage at `tests/benchmarks/test_source_tree_contract_benchmark_support.py` for the moved helper surface:
  - cover manifest-payload field dropping plus `timing_scope` and `notes` injection;
  - cover workload reconstruction through the canonical `-contract` payload path and default benchmark metadata; and
  - cover source-workload selection order and drift detection on representative live manifest rows without copying the large combined-owner matrix.
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so it imports and uses the moved support instead of defining that generic contract-builder block inline:
  - keep the compiled-pattern module-helper keyword, compiled-pattern success, compiled-pattern `module.compile`, and wrong-text-model contract tests on the same manifest ids, contract workload ids, timing scopes, and drift wording;
  - keep the existing owner-spec and contract-case structures in place unless the moved support makes a smaller equivalent possible inside this same bounded cleanup; and
  - remove the moved helper definitions from the combined benchmark file once the new support module owns them.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k '(compiled_pattern_module_helper_keyword_contract or compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success or compiled_pattern_module_compile_success_and_keyword_contract or wrong_text_model_rows_until_helper_invocation or wrong_text_model_contract_workloads or wrong_text_model_callbacks_preserve_precompile_contract)'`

## Constraints
- Keep the cleanup structural and limited to the three files above. Do not widen it into benchmark manifests, harness implementation code, correctness fixtures, README text, reports, or tracked ops state prose.
- Prefer deleting the inline shared contract-builder block from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` over leaving local wrapper aliases there.
- Do not widen this task into standard benchmark anchor support, compiled-pattern module-helper route support, wrong-text-model selector/owner helpers, or unrelated benchmark-family extractions that already live on support modules.

## Notes
- `RBR-1170` is the next available unreserved architecture task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n 'RBR-1170|RBR-1171|RBR-1172|source_tree_contract_benchmark_support|SourceTreeContractBuilderSpec' ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` matched only historical mentions inside completed task files and did not reveal a live reservation or sibling task at `RBR-1170`.
- No blocked architecture task exists to reopen or retire first in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining simplification is concrete and still cross-file in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `20601` lines in this run;
  - `rg -n '^class _SourceTreeContractBuilderSpec|^def _source_tree_contract_manifest_payload\\(|^def _source_tree_contract_workload\\(|^def _source_tree_contract_manifest\\(|^def _contract_source_workloads\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` returned the shared helper block at lines `16426`, `16434`, `16455`, `16479`, and `17057`;
  - the compiled-pattern module-helper keyword contract surface still calls `_source_tree_contract_manifest(...)` and `_source_tree_contract_workload(...)` at lines `16743`, `16799`, `16832`, and `16869`;
  - the compiled-pattern success and `module.compile` contract surfaces still depend on the same helpers across lines `16904` through `17982`; and
  - the wrong-text-model owner-contract surface still depends on that same helper family across lines `18062` through `18330`.
- Verification status in this run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k '(compiled_pattern_module_helper_keyword_contract or compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success or compiled_pattern_module_compile_success_and_keyword_contract or wrong_text_model_rows_until_helper_invocation or wrong_text_model_contract_workloads or wrong_text_model_callbacks_preserve_precompile_contract)'` returned `197 passed, 557 deselected` in this run.

## Completion
- Extracted the shared source-tree contract-builder helpers into `tests/benchmarks/source_tree_contract_benchmark_support.py` and updated `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to import that support instead of defining the contract-builder block inline.
- Added focused coverage in `tests/benchmarks/test_source_tree_contract_benchmark_support.py` for manifest payload field dropping plus `timing_scope`/`notes` injection, contract workload reconstruction with default benchmark metadata, manifest defaults, and selector-order drift detection against representative live manifest rows.
- Verification in this run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_contract_benchmark_support.py` returned `5 passed`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k '(compiled_pattern_module_helper_keyword_contract or compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success or compiled_pattern_module_compile_success_and_keyword_contract or wrong_text_model_rows_until_helper_invocation or wrong_text_model_contract_workloads or wrong_text_model_callbacks_preserve_precompile_contract)'` returned `197 passed, 557 deselected`.
