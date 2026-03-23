# RBR-1094: Collapse parametrize id lambdas in literal-flag parity suite

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining trivial `pytest.mark.parametrize(..., ids=lambda case: case.id)` adapters from `tests/python/test_literal_flag_parity_suite.py` so the literal-flag parity suite names its parametrized rows through named same-file helpers, or a strictly smaller equivalent, instead of seven one-purpose anonymous wrappers.

## Deliverables
- `tests/python/test_literal_flag_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_literal_flag_parity_suite.py` no longer contains any `ids=lambda case: case.id` adapters.
- Replace that wrapper layer with named same-file helpers, or a strictly smaller equivalent, while preserving the current parametrized test ownership surface intact for:
  - `test_literal_ignorecase_module_helpers_match_cpython`
  - `test_literal_ignorecase_compiled_helpers_match_cpython`
  - `test_native_literal_flag_module_workflows_match_cpython`
  - `test_native_literal_flag_compiled_workflows_match_cpython`
  - `test_native_literal_flag_compile_metadata_matches_cpython`
  - `test_native_literal_flag_module_helpers_accept_compiled_patterns_with_cpython_parity`
  - `test_fake_native_boundary_preserves_literal_flag_search_sequences`
- Keep the existing case ids stable after the cleanup:
  - module and compiled ignorecase rows still render as `case.id`;
  - native module, compiled, and compile-metadata rows still render as `case.id`;
  - native compiled-module helper rows still render as `case.id`; and
  - fake-boundary rows still render as `case.id`.
- Keep the cleanup structural and file-local to `tests/python/test_literal_flag_parity_suite.py`.
- Do not widen this task into `tests/python/fixture_parity_support.py`, `python/rebar/__init__.py`, correctness fixtures, implementation code, reports, README copy, or tracked state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_literal_flag_parity_suite.py -k 'literal_ignorecase_module_helpers_match_cpython or literal_ignorecase_compiled_helpers_match_cpython or native_literal_flag_module_workflows_match_cpython or native_literal_flag_compiled_workflows_match_cpython or native_literal_flag_compile_metadata_matches_cpython or native_literal_flag_module_helpers_accept_compiled_patterns_with_cpython_parity or fake_native_boundary_preserves_literal_flag_search_sequences'`
- `bash -lc "! rg -n 'ids=lambda case: case\\.id' tests/python/test_literal_flag_parity_suite.py"`

## Constraints
- Prefer deleting the anonymous id-wrapper layer over introducing another helper registry, support module, or detached abstraction tier.
- Keep the current parametrized test names, case ordering, native-skip behavior, and expected ids intact.
- Do not broaden this into other lambda cleanup elsewhere in the repo; keep the task bounded to the seven `ids=` adapters above.

## Notes
- `RBR-1094` is the next available unreserved task id in this checkout:
  - the highest live task id across `ops/tasks/done/`, `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` is `1093`; and
  - `rg -n 'RBR-1094|RBR-1095|RBR-1096|RBR-1097|RBR-1098|RBR-1099|RBR-1100' ops/state/current_status.md ops/state/backlog.md -g '*.md'` returned no reserved future ids in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete and current in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest runtime cycle shows the task workers completing cleanly, with no inherited-dirty checkpoint churn or stalled refresh path.
- The simplification target is concrete in the live checkout:
  - `rg -n 'ids=lambda case: case\\.id' tests/python/test_literal_flag_parity_suite.py` returned the seven remaining trivial id adapters at lines `505`, `517`, `587`, `601`, `619`, `641`, and `674` in this run.
- The focused verification slice is green in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_literal_flag_parity_suite.py -k 'literal_ignorecase_module_helpers_match_cpython or literal_ignorecase_compiled_helpers_match_cpython or native_literal_flag_module_workflows_match_cpython or native_literal_flag_compiled_workflows_match_cpython or native_literal_flag_compile_metadata_matches_cpython or native_literal_flag_module_helpers_accept_compiled_patterns_with_cpython_parity or fake_native_boundary_preserves_literal_flag_search_sequences'` returned `37 passed, 6 deselected` in this run.
