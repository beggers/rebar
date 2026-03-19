# RBR-0646: Collapse the detached default benchmark manifest inventory contract onto the shared anchor owner

Status: ready
Owner: architecture-implementation
Created: 2026-03-19

## Goal
- Delete `tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py` by moving its remaining selector and published-inventory assertions onto `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py`, so the benchmark harness keeps one support owner for published-manifest shape instead of a detached inventory-only contract beside the higher-level anchor suite.

## Deliverables
- `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py`
- Delete `tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py`

## Acceptance Criteria
- `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` becomes the sole owner for the default benchmark selector and published inventory coverage currently isolated in `tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py`:
  - keep the current selector error and inventory shape coverage explicit on the owner file:
    - `select_benchmark_manifest_paths("missing-selector")` still raises the current clear unknown-selector error;
    - `select_benchmark_manifest_path(PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR)` still rejects the multi-manifest selector;
    - the published full-suite selector still resolves to every tracked benchmark workload module except `compile_smoke.py`;
    - the built-native smoke selector still resolves to exactly `pattern_boundary.py`, `collection_replacement_boundary.py`, and `literal_flag_boundary.py`;
    - `published_benchmark_manifests()` still stays cached and preserves the shared selector order via `manifest.path`; and
    - the published full-suite inventory still enforces globally unique benchmark `manifest_id` and `workload_id` values, with every published manifest contributing at least one workload and every workload pointing back to a published manifest id.
  - keep any tiny helper needed for this move file-local on `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` instead of creating another benchmark support module, registry layer, or forwarding shell.
- `tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py` is deleted outright:
  - do not leave an import-only wrapper, compatibility shell, or renamed inventory-specific suite behind.
- Keep scope structural only:
  - do not change `python/rebar_harness/benchmarks.py`, benchmark workload modules, `tests/benchmarks/benchmark_expectations.py`, published reports, or tracked project-state prose in this run; and
  - do not move this inventory coverage into `tests/benchmarks/test_built_native_benchmark_modes.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, or another scorecard-specific owner.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_built_native_benchmark_modes.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path

source = Path("tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py").read_text(
    encoding="utf-8"
)
for needle in (
    "PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR",
    "BUILT_NATIVE_SMOKE_MANIFEST_SELECTOR",
    "COMPILE_SMOKE_PROVENANCE_MANIFEST_SELECTOR",
    "published_benchmark_manifests",
):
    assert needle in source, needle
print("ok")
PY`
  - `bash -lc "! rg --files tests/benchmarks | rg 'test_default_benchmark_manifest_inventory_contract\\.py$'"`

## Constraints
- Keep this cleanup structural only. Do not broaden into benchmark behavior changes, workload publication changes, or report regeneration.
- Prefer the existing shared anchor owner and file-local helpers over another detached benchmark contract file or another shared abstraction layer.
- Preserve the current selector names, manifest ordering, and inventory expectations exactly; the point is to delete a redundant owner file, not to reinterpret benchmark coverage.

## Notes
- `RBR-0646` is the next available architecture task id in the current checkout:
  - `rg -n "RBR-0646|RBR-0647|RBR-0648|RBR-0649" ops/state/backlog.md ops/state/current_status.md` returned no reserved future ids in this range; and
  - `find ops/tasks -maxdepth 2 -name 'RBR-0646*' -o -name 'RBR-0647*' -o -name 'RBR-0648*' -o -name 'RBR-0649*'` returned no matching task files before this task was added.
- No blocked architecture task exists to reopen first, and rule 10 does not currently block another architecture task:
  - `ops/tasks/blocked/` is empty; and
  - the live queue check shows one ready feature task (`RBR-0645`) with no blocked architecture work.
- Runtime reporting is slightly behind `HEAD`, so the JSON decision used live filesystem counts rather than trusting the stale dashboard alone:
  - `.rebar/runtime/dashboard.md` still reports `HEAD: 3841b744733a85e781f754f056f01c623402c223`, while `git rev-parse HEAD` returned `5a130993216a798d7385ca609332d8df3cfd561f`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining detached benchmark contract is concrete and bounded in the current checkout:
  - `tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py` is `140` lines, while `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` is already the shared benchmark-support owner at `2025` lines and already covers the adjacent published workload scope, cache reuse, anchored-case mapping, legacy workload handling, and special unanchored workload contracts;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` currently passes (`79 passed, 791 subtests passed in 0.20s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` currently passes (`73 passed in 0.13s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_built_native_benchmark_modes.py` currently passes (`6 passed, 2 skipped in 0.07s`);
  - `rg -n "PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR|BUILT_NATIVE_SMOKE_MANIFEST_SELECTOR|COMPILE_SMOKE_PROVENANCE_MANIFEST_SELECTOR|published_benchmark_manifests" tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` currently returns no matches, so the inline source probe above fails exactly on this cleanup; and
  - `bash -lc "! rg --files tests/benchmarks | rg 'test_default_benchmark_manifest_inventory_contract\\.py$'"` currently fails exactly on this cleanup because the detached file still exists.
- The ownership simplification matches the correctness side of the repo:
  - `tests/python/test_fixture_parity_support_contract.py` already owns the published correctness selector, ordering, and uniqueness contracts in one support module, while the benchmark side still splits comparable selector/inventory coverage into a detached file.
