# RBR-0671: Collapse the detached module-workflow surface bundle contract onto its parity owner

Status: done
Owner: architecture-implementation
Created: 2026-03-19

## Goal
- Move the remaining module-workflow-surface bundle-contract checks off `tests/python/test_fixture_parity_support_contract.py` and onto `tests/python/test_module_workflow_parity_suite.py`, so the module-workflow owner keeps its manifest-shape and compile-row ordering contract beside the workflows it already exercises instead of leaving that slice in a detached helper-contract suite.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/python/test_fixture_parity_support_contract.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` becomes the sole owner for the module-workflow-surface bundle-contract slice currently isolated in `tests/python/test_fixture_parity_support_contract.py`:
  - absorb `test_module_workflow_surface_bundle_contract_covers_verbose_compile_case(...)`;
  - absorb `test_module_workflow_surface_compile_case_selection_preserves_row_order(...)`;
  - keep any tiny new helper, full-manifest bundle spec, or compile-only selection constant file-local on `tests/python/test_module_workflow_parity_suite.py` instead of expanding `tests/python/fixture_parity_support.py`, adding another `*_support.py`, or moving this slice into `tests/python/conftest.py`; and
  - preserve the current bundle expectations exactly, including the explicit `workflow-compile-str-verbose-regression` row, the compile-only ordered case selection, and the `module_workflow_surface.py` fixture path.
- `tests/python/test_fixture_parity_support_contract.py` stops owning this module-workflow-specific slice:
  - remove the two moved test functions and any imports, params, aliases, or local helpers that exist only to support them; and
  - the detached contract file no longer mentions `test_module_workflow_surface_bundle_contract_covers_verbose_compile_case`, `test_module_workflow_surface_compile_case_selection_preserves_row_order`, `module_workflow_surface.py`, or `workflow-compile-str-verbose-regression`.
- Keep scope structural only:
  - do not change `tests/python/fixture_parity_support.py`, `tests/conformance/fixtures/module_workflow_surface.py`, `python/rebar/`, `crates/`, published reports, or tracked project-state prose in this run;
  - do not broaden into the detached public-surface, collection-helper, or bounded-wildcard sections already parked on `tests/python/test_module_workflow_parity_suite.py`; and
  - preserve the current error strings and ordered-case assertions exactly.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path

owner = Path("tests/python/test_module_workflow_parity_suite.py").read_text(
    encoding="utf-8"
)
contract = Path("tests/python/test_fixture_parity_support_contract.py").read_text(
    encoding="utf-8"
)
needles = (
    "def test_module_workflow_surface_bundle_contract_covers_verbose_compile_case(",
    "def test_module_workflow_surface_compile_case_selection_preserves_row_order(",
)
for needle in needles:
    assert needle in owner, needle
    assert needle not in contract, needle
print("ok")
PY`
  - `bash -lc "! rg -n 'module_workflow_surface\\.py|workflow-compile-str-verbose-regression' tests/python/test_fixture_parity_support_contract.py"`

## Constraints
- Keep this cleanup structural only. The point is to move an owner-specific manifest-contract slice out of a detached support suite, not to reinterpret module-workflow semantics, fixture-manifest loading, or published frontier selection.
- Prefer the existing module-workflow parity owner and file-local helpers over another shared abstraction layer.
- Do not delete `tests/python/test_fixture_parity_support_contract.py`; leave the remaining generic backend-fixture, manifest-loader, bundle-contract, and parity-helper coverage in place.

## Notes
- `RBR-0671` is the next available architecture task id in the current checkout:
  - `rg -n "RBR-0671|RBR-0672|RBR-0673|RBR-0674|RBR-0675" ops/state/backlog.md ops/state/current_status.md` returned no matches; and
  - `find ops/tasks -maxdepth 2 -type f \( -name 'RBR-0671*' -o -name 'RBR-0672*' -o -name 'RBR-0673*' -o -name 'RBR-0674*' -o -name 'RBR-0675*' \) | sort` returned no live task file in that range.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/blocked/`, `ops/tasks/ready/`, and `ops/tasks/in_progress/` are currently empty aside from queue keepers;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the dashboard `HEAD` matches `git rev-parse HEAD` (`a4efbbd15666c62408e148386bdbc132b0a2e86c`), so the runtime view is not lagging behind this checkout.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The detached slice is concrete and bounded in the current checkout:
  - `tests/python/test_module_workflow_parity_suite.py` already owns the surrounding module-workflow fixture surface via `MODULE_WORKFLOW_FIXTURE_PATH`, `MODULE_WORKFLOW_EXPECTED_CASE_IDS`, `MODULE_WORKFLOW_EXPECTED_PATTERNS`, `MODULE_WORKFLOW_EXPECTED_OPERATION_HELPER_COUNTS`, `MODULE_WORKFLOW_BUNDLE`, `COMPILE_CASES`, and the adjacent alignment/frontier tests `test_module_workflow_parity_suite_stays_aligned_with_published_fixture(...)`, `test_module_workflow_parity_suite_tracks_published_case_frontier(...)`, and `test_module_workflow_direct_test_buckets_cover_selected_frontier(...)`;
  - `wc -l tests/python/test_module_workflow_parity_suite.py tests/python/test_fixture_parity_support_contract.py` currently reports `3792` lines for the owner file and `2637` lines for the detached contract file;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` currently passes (`487 passed, 1 skipped in 0.40s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py` currently passes (`145 passed in 0.20s`);
- the inline source probe in Acceptance currently fails exactly on this cleanup with `AssertionError: def test_module_workflow_surface_bundle_contract_covers_verbose_compile_case(` because the owner file does not yet carry the moved definitions; and
- `bash -lc "! rg -n 'module_workflow_surface\\.py|workflow-compile-str-verbose-regression' tests/python/test_fixture_parity_support_contract.py"` currently fails exactly on this cleanup because the detached contract still owns the module-workflow-specific fixture path and verbose compile row checks.

## Completion
- 2026-03-19: Moved `test_module_workflow_surface_bundle_contract_covers_verbose_compile_case(...)` and `test_module_workflow_surface_compile_case_selection_preserves_row_order(...)` onto `tests/python/test_module_workflow_parity_suite.py`, keeping the compile-only selection constants file-local on the owner suite.
- 2026-03-19: Removed the detached module-workflow-specific fixture-path and verbose-compile-row contract coverage from `tests/python/test_fixture_parity_support_contract.py`; the detached contract file no longer mentions `module_workflow_surface.py` or `workflow-compile-str-verbose-regression`.

## Verification
- 2026-03-19: `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` (`489 passed, 1 skipped`)
- 2026-03-19: `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py` (`143 passed`)
- 2026-03-19: `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... PY` (`ok`)
- 2026-03-19: `bash -lc "! rg -n 'module_workflow_surface\\.py|workflow-compile-str-verbose-regression' tests/python/test_fixture_parity_support_contract.py"`
