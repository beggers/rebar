# RBR-0658: Collapse the detached built-native benchmark mode suite onto the shared benchmark anchor owner

Status: ready
Owner: architecture-implementation
Created: 2026-03-19

## Goal
- Delete `tests/benchmarks/test_built_native_benchmark_modes.py` by moving its remaining direct built-native smoke/full wrapper, CLI, and provenance coverage onto `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py`, so direct `rebar_harness.benchmarks` API coverage lives under one shared benchmark-contract owner instead of a detached mode-only suite beside the existing anchor owner.

## Deliverables
- `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py`
- Delete `tests/benchmarks/test_built_native_benchmark_modes.py`

## Acceptance Criteria
- `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` becomes the sole owner for the direct built-native mode coverage currently isolated in `tests/benchmarks/test_built_native_benchmark_modes.py`:
  - keep the current strict native smoke wrapper contract explicit on the owner file:
    - `run_built_native_smoke_benchmarks()` still routes through `run_benchmarks()` with `select_benchmark_manifest_paths(BUILT_NATIVE_SMOKE_MANIFEST_SELECTOR)`;
    - the wrapper still preserves both `report_path=None` and explicit report-path forwarding;
    - the wrapper still forces `smoke_only=True`, `adapter_mode=benchmarks.BUILT_NATIVE_MODE`, and `allow_fallback=False`.
  - keep the current strict native full wrapper contract explicit on the owner file:
    - `run_built_native_full_benchmarks()` still routes through `run_benchmarks()` with `select_benchmark_manifest_paths(PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR)`;
    - the wrapper still preserves both `report_path=None` and explicit report-path forwarding; and
    - the wrapper still forces `smoke_only=False`, `adapter_mode=benchmarks.BUILT_NATIVE_MODE`, and `allow_fallback=False`.
  - keep the current native CLI forwarding contract explicit on the owner file:
    - `benchmarks.main(["--native-smoke"])` and `benchmarks.main(["--native-full"])` still dispatch to the native wrappers with `report_path=None`; and
    - explicit `--report` values for both flags still forward the exact provided path to the matching wrapper.
  - keep the current strict provisioning-failure contract explicit on the owner file:
    - when `provision_built_native_runtime` returns `(None, None, "built-native mode unavailable because no \`maturin\` executable was found on PATH")`, both native wrappers still raise `benchmarks.NativeBenchmarkProvisionError`; and
    - those strict-failure wrapper paths still leave the requested report path absent.
  - keep the current direct `run_benchmarks(..., adapter_mode=benchmarks.BUILT_NATIVE_MODE)` fallback/provenance coverage explicit on the owner file:
    - the single-manifest compile-smoke direct-run probe still falls back to `"source-tree-shim"` when provisioning fails, with `implementation["native_build_tool"] is None`, `implementation["native_wheel"] is None`, `implementation["native_module_loaded"]` still a `bool`, and `implementation["native_unavailable_reason"]` still mentioning `"maturin"`; and
    - the matching built-native-available probe still reports `"built-native"` for requested/resolved mode, build mode, and timing path, keeps `implementation["native_module_name"] == "rebar._rebar"`, `implementation["native_build_tool"] == "maturin"`, `str(implementation["native_wheel"]).startswith("rebar-")`, `implementation["native_scaffold_status"] == "scaffold-only"`, `implementation["native_target_cpython_series"] == "3.12.x"`, and `scorecard["environment"]["execution_model"] == "single-interpreter subprocess workload probes against a built native wheel"` under the current `maturin` skip condition.
  - keep the current explicit built-native report-shape coverage on the owner file under the existing `maturin` skip conditions:
    - the smoke run with an explicit report path still writes a combined scorecard with phase `"phase2-module-boundary-suite"`, selection mode `"smoke"`, manifest count `3`, summary totals `6/0/6/0/6/0`, and the current six workload ids in the same order; and
    - the full-suite run with an explicit report path still writes a combined scorecard with phase `"phase3-regression-stability-suite"`, selection mode `"full"`, manifest count `len(benchmarks.published_benchmark_manifests())`, summary totals derived from the live published manifests, and a measured-plus-unimplemented partition whose total still matches the live published workload count.
  - keep any tiny helper needed for temp report paths, minimal scorecards, or shared built-native assertions file-local on `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` instead of creating another `*_support.py`, another detached benchmark suite, or moving this coverage onto `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- `tests/benchmarks/test_built_native_benchmark_modes.py` is deleted outright:
  - do not leave an import-only wrapper, compatibility shell, or renamed mode-specific suite behind.
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
    "run_built_native_smoke_benchmarks(",
    "run_built_native_full_benchmarks(",
    "adapter_mode=benchmarks.BUILT_NATIVE_MODE",
    "allow_fallback=False",
    "COMPILE_SMOKE_PROVENANCE_MANIFEST_SELECTOR",
    "--native-smoke",
    "--native-full",
):
    assert needle in source, needle
print("ok")
PY`
  - `bash -lc "! rg --files tests/benchmarks | rg 'test_built_native_benchmark_modes\\.py$'"`

## Constraints
- Keep this cleanup structural only. The point is to delete a detached benchmark-mode owner, not to reinterpret benchmark behavior, manifest inventory, native provisioning semantics, or tracked report wiring.
- Prefer the existing shared benchmark anchor owner and file-local helpers over another detached suite or a new support module.
- Preserve the current built-native failure-path, provenance, wrapper, CLI, and scorecard-shape behavior exactly.
- Do not move this coverage into `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`; keep the source-tree publication owner focused on tracked source-tree scorecard surfaces rather than direct built-native wrapper plumbing.

## Notes
- `RBR-0658` is the next available architecture task id in the current checkout:
  - `rg -n "RBR-0658|RBR-0659|RBR-0660" ops/state/backlog.md ops/state/current_status.md` returned no reserved future ids in that range; and
  - `find ops/tasks -maxdepth 2 -type f \( -name 'RBR-0657*' -o -name 'RBR-0658*' -o -name 'RBR-0659*' -o -name 'RBR-0660*' \) | sort` returned only the active feature task `ops/tasks/ready/RBR-0657-nested-broader-range-wider-ranged-repeat-branch-local-backreference-replacement-bytes-parity.md`.
- No blocked architecture task exists to reopen first, and rule 10 does not currently block another architecture cleanup:
  - `ops/tasks/blocked/` is empty;
  - the only ready task is the feature-owned `RBR-0657`; and
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining detached built-native mode owner is concrete and bounded in the current checkout:
  - `wc -l tests/benchmarks/test_built_native_benchmark_modes.py tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` reports `374` lines for the detached mode suite and `2848` lines for the shared benchmark anchor owner;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` currently passes (`87 passed in 0.17s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_built_native_benchmark_modes.py` currently passes (`7 passed, 3 skipped in 0.08s`);
  - `rg -n "test_native_smoke_runner_uses_explicit_report_paths_only|test_native_smoke_cli_uses_explicit_report_paths_only|test_native_smoke_mode_requires_real_built_runtime|test_run_benchmarks_reports_built_native_provenance_when_available|test_native_full_runner_uses_explicit_report_paths_only|test_native_full_cli_uses_explicit_report_paths_only|test_native_full_mode_requires_real_built_runtime|test_native_full_mode_writes_built_native_report_with_known_gaps" tests/benchmarks/test_built_native_benchmark_modes.py tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` currently matches only `tests/benchmarks/test_built_native_benchmark_modes.py`;
  - the inline source probe in Acceptance currently fails exactly on this cleanup with `AssertionError: run_built_native_smoke_benchmarks(` because `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` does not yet carry the absorbed built-native wrapper coverage; and
  - `bash -lc "! rg --files tests/benchmarks | rg 'test_built_native_benchmark_modes\\.py$'"` currently fails exactly on this cleanup because the detached file still exists.
- The ownership simplification matches the current benchmark harness shape:
  - `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` already owns shared benchmark selector inventory, manifest-loading, workload-selection, replacement-payload, and internal-probe contracts for `rebar_harness.benchmarks`; and
  - that owner already keeps the `BUILT_NATIVE_SMOKE_MANIFEST_SELECTOR` inventory explicit, so absorbing the remaining direct native wrapper/CLI/provenance coverage there removes the last detached benchmark-mode suite without changing the tracked source-tree publication owner.
