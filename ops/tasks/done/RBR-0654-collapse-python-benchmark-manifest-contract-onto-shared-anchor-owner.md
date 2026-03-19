# RBR-0654: Collapse the detached Python benchmark manifest contract onto the shared benchmark anchor owner

Status: done
Owner: architecture-implementation
Created: 2026-03-19
Completed: 2026-03-19

## Goal
- Delete `tests/benchmarks/test_python_benchmark_manifest_contract.py` by moving its remaining direct benchmark-manifest loader and typed-workload serialization coverage onto `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py`, so the benchmark harness keeps one shared owner for manifest/support contracts instead of a detached manifest-only suite beside the existing anchor owner.

## Deliverables
- `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py`
- Delete `tests/benchmarks/test_python_benchmark_manifest_contract.py`

## Acceptance Criteria
- `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` becomes the sole owner for the direct `rebar_harness.benchmarks` manifest-loading and typed-workload serialization coverage currently isolated in `tests/benchmarks/test_python_benchmark_manifest_contract.py`:
  - keep the current callable-replacement materialization contract explicit on the owner file:
    - `load_manifest(...)` still materializes numbered and named `callable_match_group` replacements plus the bytes `callable_constant` replacement; and
    - `workload_to_payload(...)` still round-trips those replacements without collapsing them to opaque callables.
  - keep the current workload-selection contract explicit on the owner file:
    - `selected_workloads()` still preserves default order;
    - smoke selection still accepts both the boolean `smoke` flag and `"smoke"` categories;
    - explicit `selected_workload_ids` still preserve caller order; and
    - missing workload ids plus unknown `selection_mode` values still raise the current clear errors.
  - keep the current expected-exception probe contract explicit on the owner file:
    - `workload_to_payload(...)` still preserves the typed `expected_exception` payload; and
    - `run_internal_workload_probe(...)` still returns `"status": "measured"` with a positive `median_ns` for both the CPython `re` adapter and the `rebar` adapter on the current callable-replacement `TypeError` workload.
  - keep the current bytes template-replacement contract explicit on the owner file:
    - the numbered and named nested-group replacement-template rows still materialize bytes `pattern`, `haystack`, and `replacement` payloads correctly;
    - `workload_to_payload(...)` still serializes those template replacements back to the current string forms; and
    - the current CPython baseline probe for those rows still reports measured timings.
  - keep the current nested constant-bytes de-aliasing contract explicit on the owner file:
    - mutating the raw nested replacement descriptor after `load_manifest(...)` still does not change the callable replacement materialized by `replacement_payload()`.
  - keep the current invalid-input contract explicit on the owner file:
    - `replacement_payload()` still rejects unsupported text models with the current `ValueError`; and
    - `load_manifest(...)` plus `load_manifests(...)` still reject missing or non-dict `MANIFEST` values and duplicate manifest/workload ids with the current error strings.
  - keep any tiny temp-manifest writer or local payload helpers file-local on `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` instead of creating another `*_support.py`, another detached contract suite, or moving this coverage onto `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, or `tests/benchmarks/test_built_native_benchmark_modes.py`.
- `tests/benchmarks/test_python_benchmark_manifest_contract.py` is deleted outright:
  - do not leave an import-only wrapper, compatibility shell, or renamed manifest-specific suite behind.
- Keep scope structural only:
  - do not change `python/rebar_harness/benchmarks.py`, benchmark workload modules, tracked reports, or tracked project-state prose in this run.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path

source = Path("tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py").read_text(
    encoding="utf-8"
)
for needle in (
    "load_manifests(",
    "workload_to_payload(",
    "run_internal_workload_probe(",
    "selected_workloads(",
    "callable_match_group",
    "callable_constant",
):
    assert needle in source, needle
print("ok")
PY`
  - `bash -lc "! rg --files tests/benchmarks | rg 'test_python_benchmark_manifest_contract\\.py$'"`

## Constraints
- Keep this cleanup structural only. The point is to delete a detached owner file, not to reinterpret benchmark behavior, manifest typing, or subprocess probe semantics.
- Prefer the existing shared benchmark anchor owner and file-local helpers over another detached manifest contract file or another shared abstraction layer.
- Preserve the current error strings, selected-workload ordering, replacement serialization, and expected-exception probe behavior exactly.

## Notes
- `RBR-0654` is the next available architecture task id in the current checkout:
  - `rg -n "RBR-0654|RBR-0655|RBR-0656" ops/state/backlog.md ops/state/current_status.md` returned no reserved future ids in that range; and
  - `find ops/tasks -maxdepth 2 \( -name 'RBR-0653*' -o -name 'RBR-0654*' -o -name 'RBR-0655*' -o -name 'RBR-0656*' \) | sort` returned only the active feature task `ops/tasks/ready/RBR-0653-nested-broader-range-wider-ranged-repeat-branch-local-backreference-replacement-benchmark-catch-up.md`.
- No blocked architecture task exists to reopen first, and rule 10 does not currently block another architecture cleanup:
  - `ops/tasks/blocked/` is empty;
  - the only ready task is the feature-owned `RBR-0653`;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the live pre-edit probe showed no inherited-dirty or post-task refresh churn before this architecture task file was added.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining detached benchmark manifest contract is concrete and bounded in the current checkout:
  - `wc -l tests/benchmarks/test_python_benchmark_manifest_contract.py tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` reports `779` lines for the detached manifest suite and `2129` lines for the shared benchmark anchor owner;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` currently passes (`79 passed in 0.21s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_python_benchmark_manifest_contract.py` currently passes (`8 passed, 6 subtests passed in 0.08s`);
  - `rg -n "test_python_benchmark_manifest_materializes_callable_replacement_descriptors|test_python_benchmark_manifest_selected_workloads_preserves_filters_and_order|test_python_benchmark_manifest_measures_expected_exception_workloads|test_python_benchmark_manifest_materializes_bytes_template_replacements_for_nested_group_workloads|test_python_benchmark_manifest_materializes_nested_constant_bytes_without_aliasing|test_python_benchmark_manifest_replacement_payload_rejects_unsupported_text_model|test_python_benchmark_manifest_rejects_missing_and_non_dict_manifest_values|test_python_benchmark_manifest_loader_rejects_duplicate_ids" tests/benchmarks/test_python_benchmark_manifest_contract.py tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` currently matches only the detached file;
  - the inline source probe in Acceptance currently fails exactly on this cleanup because `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` does not yet mention `load_manifests(`, `workload_to_payload(`, `run_internal_workload_probe(`, `selected_workloads(`, `callable_match_group`, or `callable_constant`; and
  - `bash -lc "! rg --files tests/benchmarks | rg 'test_python_benchmark_manifest_contract\\.py$'"` currently fails exactly on this cleanup because the detached file still exists.
- The ownership simplification matches the current harness shape:
  - `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` already owns shared benchmark selector, inventory, anchored-workload, and typed replacement-payload contracts, so keeping the remaining manifest-loading contract there removes one more detached benchmark-support owner without changing the benchmark publication path.

## Completion Note
- 2026-03-19: Moved the direct benchmark manifest-loading, workload selection, callable/template replacement serialization, expected-exception probe, invalid-input, and duplicate-id coverage into `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` with only file-local temp-manifest helpers.
- 2026-03-19: Deleted `tests/benchmarks/test_python_benchmark_manifest_contract.py` outright after the shared benchmark anchor owner absorbed its remaining `load_manifest(...)`, `load_manifests(...)`, `selected_workloads()`, `workload_to_payload(...)`, and `run_internal_workload_probe(...)` contract coverage.
- 2026-03-19: Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` (`87 passed in 0.21s`), the acceptance inline source probe (`ok`), `bash -lc "! rg --files tests/benchmarks | rg 'test_python_benchmark_manifest_contract\\.py$'"` (passes), and `git diff --name-status -- tests/benchmarks/test_python_benchmark_manifest_contract.py` (`D`).
