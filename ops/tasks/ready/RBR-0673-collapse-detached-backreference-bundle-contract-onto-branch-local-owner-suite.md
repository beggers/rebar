# RBR-0673: Collapse the detached backreference bundle contract onto the branch-local owner suite

Status: ready
Owner: architecture-implementation
Created: 2026-03-19

## Goal
- Move the remaining named/numbered whole-manifest backreference bundle-contract checks off `tests/python/test_fixture_parity_support_contract.py` and onto `tests/python/test_branch_local_backreference_parity_suite.py`, so the branch-local/backreference owner keeps its bundle-order, manifest-path, and derived-manifest-id contract beside the exact fixture bundles it already loads instead of leaving that slice in a detached helper-contract suite.

## Deliverables
- `tests/python/test_branch_local_backreference_parity_suite.py`
- `tests/python/test_fixture_parity_support_contract.py`

## Acceptance Criteria
- `tests/python/test_branch_local_backreference_parity_suite.py` becomes the sole owner for the named/numbered whole-manifest backreference bundle-contract slice currently isolated in `tests/python/test_fixture_parity_support_contract.py`:
  - absorb `_whole_manifest_backreference_bundle_specs(...)` or an equivalent tiny file-local helper derived from the existing `FIXTURE_BUNDLE_SPECS` declarations;
  - absorb `test_whole_manifest_bundle_specs_load_in_declared_order_with_bundle_validation(...)`;
  - absorb `test_fixture_case_operation_selection_preserves_published_row_order(...)`;
  - absorb `test_whole_manifest_bundle_contract_supports_exact_case_id_validation(...)`;
  - absorb `test_expected_fixture_bundle_contract_supports_exact_case_id_validation(...)`;
  - absorb `test_fixture_bundle_exposes_derived_manifest_id_without_storing_duplicate_field(...)`;
  - keep any tiny new alias, slice helper, or `fields(FixtureBundle)` check file-local on `tests/python/test_branch_local_backreference_parity_suite.py` instead of expanding `tests/python/fixture_parity_support.py`, adding another `*_support.py`, or moving this slice into `tests/python/conftest.py`; and
  - preserve the current exact named/numbered manifest ids, expected case ids, expected patterns, `(operation, helper)` counts, pattern-call row order, fixture paths, and derived `FixtureBundle.expected_manifest_id` behavior exactly.
- `tests/python/test_fixture_parity_support_contract.py` stops owning this branch-local-specific slice:
  - remove `_whole_manifest_backreference_bundle_specs(...)` and the five moved test functions above;
  - remove any imports, aliases, or local helpers that exist only to support that slice; and
  - do not leave a renamed compatibility shell or a second detached backreference-bundle helper beside the branch-local owner.
- Keep scope structural only:
  - do not change `tests/python/fixture_parity_support.py`, `python/rebar_harness/correctness.py`, `tests/conformance/fixtures/*.py`, published reports, or tracked project-state prose in this run; and
  - do not broaden into direct-bytes follow-on routing, quantified branch-local candidate generation, match-group access, or non-backreference fixture-helper coverage.
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
    "def test_whole_manifest_bundle_specs_load_in_declared_order_with_bundle_validation(",
    "def test_fixture_case_operation_selection_preserves_published_row_order(",
    "def test_whole_manifest_bundle_contract_supports_exact_case_id_validation(",
    "def test_expected_fixture_bundle_contract_supports_exact_case_id_validation(",
    "def test_fixture_bundle_exposes_derived_manifest_id_without_storing_duplicate_field(",
)
for needle in needles:
    assert needle in owner, needle
    assert needle not in contract, needle
print("ok")
PY`
  - `bash -lc "! rg -n '_whole_manifest_backreference_bundle_specs|test_whole_manifest_bundle_specs_load_in_declared_order_with_bundle_validation|test_fixture_case_operation_selection_preserves_published_row_order|test_whole_manifest_bundle_contract_supports_exact_case_id_validation|test_expected_fixture_bundle_contract_supports_exact_case_id_validation|test_fixture_bundle_exposes_derived_manifest_id_without_storing_duplicate_field' tests/python/test_fixture_parity_support_contract.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete a detached branch-local/backreference bundle-contract slice, not to reinterpret fixture loading, manifest ordering, bundle-selection semantics, or published frontier behavior.
- Prefer the existing branch-local owner and file-local helper(s) over another shared abstraction layer.
- Do not delete `tests/python/test_fixture_parity_support_contract.py`; leave the remaining generic fixture-loader, selected-case bundle, helper-parity, and error-path coverage in place.

## Notes
- `RBR-0673` is the next available architecture task id in the current checkout:
  - `rg -n "RBR-0673|RBR-0674|RBR-0675|RBR-0676|RBR-0677" ops/state/backlog.md ops/state/current_status.md` returned no matches; and
  - `find ops/tasks -maxdepth 2 -type f \( -name 'RBR-0673*' -o -name 'RBR-0674*' -o -name 'RBR-0675*' -o -name 'RBR-0676*' -o -name 'RBR-0677*' \) | sort` returned no files.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in the current checkout;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the last cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The detached slice is concrete and already duplicated beside its natural owner in the current checkout:
  - `tests/python/test_branch_local_backreference_parity_suite.py` is `2084` lines and already declares the named and numbered backreference bundle specs directly at `FIXTURE_BUNDLE_SPECS`;
  - `tests/python/test_fixture_parity_support_contract.py` is `2540` lines and still carries `_whole_manifest_backreference_bundle_specs(...)` plus the five backreference-bundle contract tests above;
  - `rg -n "named_backreference_workflows\\.py|numbered_backreference_workflows\\.py|expected_manifest_id=\\\"named-backreference-workflows\\\"|expected_manifest_id=\\\"numbered-backreference-workflows\\\"\" tests/python/test_branch_local_backreference_parity_suite.py tests/python/test_fixture_parity_support_contract.py` shows the exact named/numbered bundle ids live in both files today;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py` currently passes (`559 passed in 0.79s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py` currently passes (`143 passed in 0.20s`);
  - the inline source probe in Acceptance currently fails exactly on this cleanup with `AssertionError: def test_whole_manifest_bundle_specs_load_in_declared_order_with_bundle_validation(` because the branch-local owner does not yet carry the moved definitions; and
  - the final `rg` command in Acceptance currently fails exactly on this cleanup because the detached support file still contains the targeted helper and test functions.
- This simplification matches the current information flow:
  - `tests/python/test_branch_local_backreference_parity_suite.py` already owns the named/numbered/branch-local backreference bundle specs, the loaded `FIXTURE_BUNDLES`, frontier coverage, and direct-test bucket contracts; and
  - the detached support file is only keeping an extra branch-local/named-numbered bundle-contract seam alive beside that owner.
