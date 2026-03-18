# RBR-0644: Collapse the detached native-extension smoke suite onto the module-workflow owner

Status: done
Owner: architecture-implementation
Created: 2026-03-18
Completed: 2026-03-18

## Goal
- Delete `tests/python/test_native_extension_smoke.py` by moving its remaining rebar-only smoke coverage onto `tests/python/test_module_workflow_parity_suite.py`, so the source-tree and built-wheel module-surface checks live on the existing module-workflow owner instead of a two-test detached suite.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`
- Delete `tests/python/test_native_extension_smoke.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` becomes the sole owner for the rebar-only smoke coverage currently isolated in `tests/python/test_native_extension_smoke.py`:
  - add a non-`maturin`-gated source-tree metadata check on the module-workflow owner that keeps the current direct assertions for `rebar.TARGET_CPYTHON_SERIES`, `rebar.SCAFFOLD_STATUS`, `rebar.NATIVE_MODULE_NAME`, and the `native_module_loaded()` / `native_scaffold_status()` / `native_target_cpython_series()` relationship (`bool` loaded flag, scaffold metadata when the native module is present, `None` metadata when it is not);
  - add a `maturin`-gated built-wheel subprocess smoke check on the same owner file that still provisions one isolated built runtime through `benchmarks.provision_built_native_runtime()` and keeps the current bounded public contract explicit:
    - `rebar._rebar` imports successfully and reports the private scaffold flag;
    - exported module helpers are present;
    - `rebar.template("abc")` still raises the current scaffold placeholder message;
    - `rebar.compile("abc", rebar.IGNORECASE)` still returns a `Pattern` with the current metadata;
    - the compiled search, literal module search/fullmatch, split/findall/finditer, purge, and the current `str` / `bytes` `escape()` examples keep the same observed payloads now asserted in the detached smoke file; and
    - when `maturin` is unavailable, this built-wheel smoke remains explicitly skipped rather than silently disappearing;
  - keep the built-wheel probe file-local on `tests/python/test_module_workflow_parity_suite.py` instead of moving it into a new `*_support.py` helper, another detached smoke file, or a benchmark-specific owner.
- `tests/python/test_native_extension_smoke.py` is deleted outright:
  - do not leave an import-only wrapper, compatibility shell, or renamed smoke-specific suite behind.
- Keep scope structural only:
  - do not change `python/rebar/__init__.py`, `python/rebar_harness/benchmarks.py`, Rust code, benchmark scorecards, reports, or tracked state prose in this run; and
  - do not move this smoke coverage into `tests/benchmarks/test_built_native_benchmark_modes.py` or another benchmark-owner file.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path

source = Path("tests/python/test_module_workflow_parity_suite.py").read_text(
    encoding="utf-8"
)
for needle in (
    "TARGET_CPYTHON_SERIES",
    "SCAFFOLD_STATUS",
    "NATIVE_MODULE_NAME",
    "provision_built_native_runtime",
):
    assert needle in source, needle
print("ok")
PY`
  - `bash -lc "! rg --files tests/python | rg 'test_native_extension_smoke\\.py$'"`

## Constraints
- Keep this cleanup structural only. Do not broaden into benchmark-mode contract changes, README/current-status updates, or any new native/runtime behavior.
- Prefer the existing module-workflow owner and file-local helpers over another smoke-specific abstraction.
- Preserve the current subprocess-observed values exactly; the point is to delete a redundant owner file, not to reinterpret the smoke contract.

## Notes
- `RBR-0644` is the next available architecture task id in the current checkout:
  - `find ops/tasks -maxdepth 2 -name 'RBR-0644*' -o -name 'RBR-0645*' -o -name 'RBR-0646*'` returned no matching task files; and
  - `rg -n "RBR-0644|RBR-0645|RBR-0646" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked` returned no reserved or active entry in that range.
- No blocked architecture task exists to reopen first, and rule 10 does not currently block another architecture task:
  - `ops/tasks/blocked/` is empty; and
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`, while the only ready task is the feature-owned `RBR-0643`.
- JSON burn-down remains complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining duplication is concrete and bounded in the current checkout:
  - `tests/python/test_native_extension_smoke.py` is `226` lines and now contains only two tests, while `tests/python/test_module_workflow_parity_suite.py` already carries the surrounding direct source-package compile/search/cache/purge/escape/template surface across `87` tests;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_native_extension_smoke.py` currently passes (`1 passed, 1 skipped in 0.04s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` currently passes (`476 passed in 0.35s`);
  - the acceptance inline source probe currently fails exactly on this cleanup because `tests/python/test_module_workflow_parity_suite.py` does not yet mention `TARGET_CPYTHON_SERIES`, `SCAFFOLD_STATUS`, `NATIVE_MODULE_NAME`, or `provision_built_native_runtime`; and
  - `bash -lc "! rg --files tests/python | rg 'test_native_extension_smoke\\.py$'"` currently fails exactly on this cleanup because the detached suite file still exists.
- No active code path depends on keeping the detached suite path:
  - `rg -n "test_native_extension_smoke\\.py|test_source_tree_shim_metadata_contract|test_built_wheel_keeps_native_surface_contract|PROBE =" tests python ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/state` currently matches only `tests/python/test_native_extension_smoke.py` itself plus the historical `RBR-0010` note in `ops/state/current_status.md`; keep that tracked historical note untouched in this structural cleanup.

## Completion Note
- 2026-03-18: Moved the detached rebar-only source-tree metadata assertions and the built-wheel subprocess smoke contract into `tests/python/test_module_workflow_parity_suite.py`, keeping the built probe file-local and preserving the existing observed payloads and explicit `maturin` skip behavior.
- 2026-03-18: Deleted `tests/python/test_native_extension_smoke.py` outright after the module-workflow owner absorbed its remaining coverage.
- 2026-03-18: Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` (`477 passed, 1 skipped in 0.50s`), the inline source probe (`ok`), `bash -lc "! rg --files tests/python | rg 'test_native_extension_smoke\\.py$'"` (passes), and `git diff --name-status -- tests/python/test_native_extension_smoke.py` (`D`).
