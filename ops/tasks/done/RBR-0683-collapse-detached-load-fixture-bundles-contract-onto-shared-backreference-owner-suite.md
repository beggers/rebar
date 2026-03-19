# RBR-0683: Collapse the detached `load_fixture_bundles(...)` contract onto the shared backreference owner suite

Status: done
Owner: architecture-implementation
Created: 2026-03-19

## Goal
- Move the remaining named-backreference `load_fixture_bundles(...)` selection/default/rejection contract checks off `tests/python/test_fixture_parity_support_contract.py` and onto `tests/python/test_branch_local_backreference_parity_suite.py`, so the shared backreference owner keeps its bundle-order, default-text-model, and selected-case validation semantics beside `FIXTURE_BUNDLE_SPECS`, `WHOLE_MANIFEST_BACKREFERENCE_FIXTURE_NAMES`, and `_whole_manifest_backreference_bundle_specs()` instead of leaving that slice in the detached support-contract suite.

## Deliverables
- `tests/python/test_branch_local_backreference_parity_suite.py`
- `tests/python/test_fixture_parity_support_contract.py`

## Acceptance Criteria
- `tests/python/test_branch_local_backreference_parity_suite.py` becomes the sole owner for the named-backreference `load_fixture_bundles(...)` contract slice currently isolated in `tests/python/test_fixture_parity_support_contract.py`:
  - absorb `test_load_fixture_bundles_rejects_mismatched_expected_manifest_id(...)`;
  - absorb `test_load_fixture_bundles_selected_case_ids_preserve_requested_order(...)`;
  - absorb `test_load_fixture_bundles_full_manifest_defaults_str_text_model_expectation(...)`;
  - absorb `test_load_fixture_bundles_rejects_empty_selected_case_ids(...)`;
  - absorb `test_load_fixture_bundles_rejects_duplicate_selected_case_ids(...)`;
  - absorb `test_load_fixture_bundles_rejects_missing_selected_case_ids(...)`;
  - derive the moved assertions from the shared backreference owner's existing data and helpers, including `FIXTURE_BUNDLE_SPECS`, `WHOLE_MANIFEST_BACKREFERENCE_FIXTURE_NAMES`, `_whole_manifest_backreference_bundle_specs()`, `load_fixture_bundles(...)`, `fixture_cases_for_operation(...)`, `str_case_pattern(...)`, and `assert_fixture_bundle_contract(...)`, instead of adding another `*_support.py`, widening `tests/python/conftest.py`, or reintroducing a second ad hoc `NAMED_BACKREFERENCE_PATTERN` constant beside the owner suite; and
  - preserve the current named-backreference bundle contract exactly:
    - the mismatched expected-manifest-id error string stays `named_backreference_workflows.py expected_manifest_id 'wrong-manifest-id' does not match loaded manifest_id 'named-backreference-workflows'`;
    - the selected-case order check stays pinned to `("named-backreference-pattern-search-str", "named-backreference-compile-metadata-str")`;
    - that selected-case order check still validates only the named-backreference compile plus pattern-search helper counts;
    - the full-manifest named-backreference bundle without explicit `selected_case_ids` still defaults `expected_text_models` to `frozenset({"str"})`; and
    - the empty, duplicate, and missing `selected_case_ids` error strings stay unchanged.
- `tests/python/test_fixture_parity_support_contract.py` stops owning this named-backreference slice:
  - remove the six moved test functions above;
  - remove `NAMED_BACKREFERENCE_PATTERN` once it becomes unused; and
  - do not leave a renamed compatibility shell, second named-backreference bundle validation block, or another detached selected-case spec beside the support-contract file.
- Keep scope structural only:
  - do not change `tests/python/fixture_parity_support.py`, correctness fixtures, `python/rebar_harness/correctness.py`, published reports, or tracked project-state prose in this run; and
  - do not broaden into the generic selector inventory, fixture-manifest loader validation, non-backreference bundle-loader probes, direct-test bucket helper errors, or generic match/parity helper contract tests that still belong on the detached support file.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path

owner = Path("tests/python/test_branch_local_backreference_parity_suite.py").read_text(
    encoding="utf-8"
)
contract = Path("tests/python/test_fixture_parity_support_contract.py").read_text(
    encoding="utf-8"
)
needles = (
    "def test_load_fixture_bundles_rejects_mismatched_expected_manifest_id(",
    "def test_load_fixture_bundles_selected_case_ids_preserve_requested_order(",
    "def test_load_fixture_bundles_full_manifest_defaults_str_text_model_expectation(",
    "def test_load_fixture_bundles_rejects_empty_selected_case_ids(",
    "def test_load_fixture_bundles_rejects_duplicate_selected_case_ids(",
    "def test_load_fixture_bundles_rejects_missing_selected_case_ids(",
)
for needle in needles:
    assert needle in owner, needle
    assert needle not in contract, needle
print("ok")
PY`
  - `bash -lc "! rg -n 'def test_load_fixture_bundles_rejects_mismatched_expected_manifest_id|def test_load_fixture_bundles_selected_case_ids_preserve_requested_order|def test_load_fixture_bundles_full_manifest_defaults_str_text_model_expectation|def test_load_fixture_bundles_rejects_empty_selected_case_ids|def test_load_fixture_bundles_rejects_duplicate_selected_case_ids|def test_load_fixture_bundles_rejects_missing_selected_case_ids|NAMED_BACKREFERENCE_PATTERN' tests/python/test_fixture_parity_support_contract.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete a detached named-backreference bundle-loading seam, not to reinterpret backreference behavior, selected-row coverage, or helper semantics.
- Prefer the existing shared backreference owner and file-local assertions over another helper layer.
- Do not delete `tests/python/test_fixture_parity_support_contract.py`; leave the remaining generic selector, fixture-loader, bundle-helper, and helper-parity coverage in place.

## Notes
- `RBR-0683` is the next available architecture task id in the current checkout:
  - `rg -n 'RBR-0683|RBR-0684|RBR-0685' ops/state/backlog.md ops/state/current_status.md` returned no matches; and
  - `find ops/tasks -maxdepth 2 -type f \( -name 'RBR-0683*' -o -name 'RBR-0684*' -o -name 'RBR-0685*' \) | sort` returned no files.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - the live checkout is clean and `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty aside from `.gitkeep`;
  - `.rebar/runtime/dashboard.md` reports no queue anomaly, no inherited-dirty checkpoint churn, and both task-worker runs in the last cycle finished `done`; and
  - `git status --short` is empty.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The detached named-backreference slice is concrete and already duplicated beside its natural owner in the current checkout:
  - `tests/python/test_branch_local_backreference_parity_suite.py` already owns `named_backreference_workflows.py` through `FIXTURE_BUNDLE_SPECS`, `_whole_manifest_backreference_bundle_specs()`, whole-manifest bundle validation, exact case-id validation, and derived manifest-id coverage for the shared backreference surface;
  - `tests/python/test_fixture_parity_support_contract.py` still carries the six named-backreference `load_fixture_bundles(...)` tests named above plus the detached `NAMED_BACKREFERENCE_PATTERN` constant that exists only for that slice;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py` currently passes (`564 passed in 0.80s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py` currently passes (`124 passed in 0.17s`);
  - the inline source probe in Acceptance currently reports every moved definition as absent from the owner and present in the detached support file; and
  - the final `rg` command in Acceptance currently fails exactly on this cleanup because the detached support file still contains the six target definitions plus `NAMED_BACKREFERENCE_PATTERN`.
- This simplification matches the current information flow:
  - the named-backreference bundle spec data already lives on the shared backreference owner path; and
  - the support-contract file is only keeping a second named-backreference bundle-loading seam alive beside that owner.

## Completion Notes
- Moved the six named-backreference `load_fixture_bundles(...)` contract tests onto `tests/python/test_branch_local_backreference_parity_suite.py`, deriving each setup from the existing named whole-manifest backreference bundle spec via `_whole_manifest_backreference_bundle_specs()`.
- Removed the detached copies and the unused `NAMED_BACKREFERENCE_PATTERN` constant from `tests/python/test_fixture_parity_support_contract.py`.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py`, the inline source probe from the task, and the final `rg` absence check.
