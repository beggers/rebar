# RBR-0648: Collapse the detached built-native benchmark provenance suite onto the built-native mode owner

Status: ready
Owner: architecture-implementation
Created: 2026-03-19

## Goal
- Delete `tests/benchmarks/test_benchmark_adapter_provenance.py` by moving its remaining direct `run_benchmarks()` built-native fallback/provenance coverage onto `tests/benchmarks/test_built_native_benchmark_modes.py`, so the built-native benchmark path has one owner instead of a small detached provenance-only suite beside the stricter smoke/full wrapper owner.

## Deliverables
- `tests/benchmarks/test_built_native_benchmark_modes.py`
- Delete `tests/benchmarks/test_benchmark_adapter_provenance.py`

## Acceptance Criteria
- `tests/benchmarks/test_built_native_benchmark_modes.py` becomes the sole owner for the direct built-native fallback/provenance coverage currently isolated in `tests/benchmarks/test_benchmark_adapter_provenance.py`:
  - keep the current single-manifest direct-run probe explicit on the owner file, selecting `select_benchmark_manifest_path(COMPILE_SMOKE_PROVENANCE_MANIFEST_SELECTOR)` or an equivalent file-local constant rooted at `compile_smoke.py`; do not move this path selection into a new helper module or another benchmark suite;
  - absorb the current fallback contract for `benchmarks.run_benchmarks(..., adapter_mode=benchmarks.BUILT_NATIVE_MODE)` with `provision_built_native_runtime` patched to return `(None, None, "built-native mode unavailable because no \`maturin\` executable was found on PATH")`:
    - `implementation["adapter_mode_requested"]` still reports `"built-native"`;
    - `implementation["adapter_mode_resolved"]`, `implementation["build_mode"]`, and `implementation["timing_path"]` still fall back to `"source-tree-shim"`;
    - `implementation["native_module_loaded"]` stays a `bool`;
    - `implementation["native_unavailable_reason"]` still contains `"maturin"`; and
    - `implementation["native_build_tool"]` and `implementation["native_wheel"]` stay `None`;
  - keep the current built-native-available provenance smoke explicit on the same owner file when `maturin` is present:
    - `implementation["adapter_mode_requested"]`, `implementation["adapter_mode_resolved"]`, `implementation["build_mode"]`, and `implementation["timing_path"]` all report `"built-native"`;
    - `implementation["native_module_loaded"]` is truthy and `implementation["native_module_name"] == "rebar._rebar"`;
    - `implementation["native_scaffold_status"] == "scaffold-only"` and `implementation["native_target_cpython_series"] == "3.12.x"`;
    - `implementation["native_unavailable_reason"]` stays `None`;
    - `implementation["native_build_tool"] == "maturin"` and `str(implementation["native_wheel"]).startswith("rebar-")`; and
    - `scorecard["environment"]["execution_model"]` remains `"single-interpreter subprocess workload probes against a built native wheel"`;
  - preserve the current strict smoke/full wrapper coverage already owned by `tests/benchmarks/test_built_native_benchmark_modes.py`; do not weaken or delete the existing `allow_fallback=False` assertions while absorbing the direct `run_benchmarks()` provenance checks; and
  - keep any tiny helper needed for this move file-local on `tests/benchmarks/test_built_native_benchmark_modes.py` instead of creating a `*_support.py`, another detached provenance suite, or moving this coverage into `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py`.
- `tests/benchmarks/test_benchmark_adapter_provenance.py` is deleted outright:
  - do not leave an import-only wrapper, compatibility shell, or renamed provenance-specific suite behind.
- Keep scope structural only:
  - do not change `python/rebar_harness/benchmarks.py`, benchmark workload modules, tracked reports, or tracked project-state prose in this run.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_built_native_benchmark_modes.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path

source = Path("tests/benchmarks/test_built_native_benchmark_modes.py").read_text(
    encoding="utf-8"
)
for needle in (
    "COMPILE_SMOKE_PROVENANCE_MANIFEST_SELECTOR",
    "run_benchmarks(",
    "allow_fallback",
    "adapter_mode=benchmarks.BUILT_NATIVE_MODE",
):
    assert needle in source, needle
print("ok")
PY`
  - `bash -lc "! rg --files tests/benchmarks | rg 'test_benchmark_adapter_provenance\\.py$'"`

## Constraints
- Keep this cleanup structural only. Do not broaden into benchmark behavior changes, workload publication changes, or report regeneration.
- Prefer the existing built-native mode owner and file-local helpers over another support module or another detached benchmark suite.
- Preserve the current observed provenance payloads exactly; the point is to delete a redundant owner file, not to reinterpret built-native fallback behavior.
- Do not move this coverage into `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, or `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py`.

## Notes
- `RBR-0648` is the next available architecture task id in the current checkout:
  - `rg -n "RBR-0648|RBR-0649|RBR-0650|RBR-0651|RBR-0652" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done` returned only historical mentions inside done-task notes, with no reserved or active entry in the live queue/state files; and
  - `find ops/tasks -maxdepth 2 \( -name 'RBR-0648*' -o -name 'RBR-0649*' -o -name 'RBR-0650*' -o -name 'RBR-0651*' -o -name 'RBR-0652*' \) | sort` returned no matching task files.
- No blocked architecture task exists to reopen first, and rule 10 does not currently block another architecture task:
  - `ops/tasks/blocked/` is empty;
  - the only ready task is the feature-owned `RBR-0647`; and
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`.
- JSON burn-down is complete, but the runtime report is behind `HEAD`, so the zero count was confirmed live:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0` at `HEAD: c3e09f1a3e689270b706054282ce23ed4f1db3d3`;
  - `git rev-parse HEAD` returned `71fac90c5ce3bca40d5b5e7d930525503abab07f`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining duplication is concrete and bounded in the current checkout:
  - `wc -l tests/benchmarks/test_benchmark_adapter_provenance.py tests/benchmarks/test_built_native_benchmark_modes.py` reports `80` lines for the detached provenance suite and `310` lines for the existing built-native mode owner;
  - `rg -n "test_native_mode_falls_back_to_source_shim_when_build_tooling_is_unavailable|test_native_mode_reports_built_native_provenance_when_available|COMPILE_SMOKE_PROVENANCE_MANIFEST_SELECTOR|run_benchmarks\\(" tests/benchmarks/test_benchmark_adapter_provenance.py tests/benchmarks/test_built_native_benchmark_modes.py` currently matches only the detached file;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_built_native_benchmark_modes.py` currently passes (`6 passed, 2 skipped in 0.08s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_adapter_provenance.py` currently passes (`1 passed, 1 skipped in 0.06s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_built_native_benchmark_modes.py tests/benchmarks/test_benchmark_adapter_provenance.py` currently passes (`7 passed, 3 skipped in 0.08s`);
  - the inline source probe in Acceptance currently fails exactly on this cleanup because `tests/benchmarks/test_built_native_benchmark_modes.py` does not yet mention `COMPILE_SMOKE_PROVENANCE_MANIFEST_SELECTOR`; and
  - `bash -lc "! rg --files tests/benchmarks | rg 'test_benchmark_adapter_provenance\\.py$'"` currently fails exactly on this cleanup because the detached file still exists.
