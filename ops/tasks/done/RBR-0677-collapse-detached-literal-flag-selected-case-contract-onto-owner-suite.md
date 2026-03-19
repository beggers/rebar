# RBR-0677: Collapse the detached literal-flag selected-case contract onto the literal-flag owner suite

Status: done
Owner: architecture-implementation
Created: 2026-03-19

## Goal
- Move the remaining literal-flag selected-case bundle-contract checks off `tests/python/test_fixture_parity_support_contract.py` and onto `tests/python/test_literal_flag_parity_suite.py`, so the literal-flag owner keeps its selected-case path/order and bundle-load error contract beside the exact `literal_flag_workflows.py` frontier it already owns instead of leaving that slice in a detached helper-contract suite.

## Deliverables
- `tests/python/test_literal_flag_parity_suite.py`
- `tests/python/test_fixture_parity_support_contract.py`

## Acceptance Criteria
- `tests/python/test_literal_flag_parity_suite.py` becomes the sole owner for the literal-flag selected-case bundle-contract slice currently isolated in `tests/python/test_fixture_parity_support_contract.py`:
  - absorb `_literal_flag_selected_case_bundle_specs(...)` or an equivalent tiny file-local helper derived from the existing `TARGET_FIXTURE_CASE_IDS`, `SELECTED_CASE_BUNDLE_SPECS`, and the two unsupported literal-flag case ids already declared on the owner suite;
  - absorb `test_fixture_bundle_contract_supports_selected_case_path_and_order_validation(...)`;
  - absorb `test_load_fixture_bundles_rejects_duplicate_selected_case_ids(...)`;
  - absorb `test_load_fixture_bundles_rejects_empty_selected_case_ids(...)`;
  - absorb `test_load_fixture_bundles_rejects_missing_selected_case_ids(...)`;
  - absorb `test_fixture_bundle_contract_rejects_wrong_selected_case_order(...)`;
  - absorb `test_selected_case_bundle_specs_load_in_declared_bundle_order(...)`;
  - keep any tiny new helper, reduced selected-case tuple, or reversed-order probe file-local on `tests/python/test_literal_flag_parity_suite.py` instead of expanding `tests/python/fixture_parity_support.py`, adding another `*_support.py`, or moving this slice into `tests/python/conftest.py`; and
  - preserve the current fixture name, manifest id, selected case ids, expected patterns, expected `(operation, helper)` counts, expected text models, declared bundle order, and duplicate/empty/missing/order error strings exactly.
- `tests/python/test_fixture_parity_support_contract.py` stops owning this literal-flag-specific slice:
  - remove `_literal_flag_selected_case_bundle_specs(...)` and the six moved test functions above;
  - remove any imports, aliases, or local helpers that exist only to support that literal-flag slice; and
  - do not leave a renamed compatibility shell or a second detached literal-flag selected-case helper beside the owner suite.
- Keep scope structural only:
  - do not change `tests/python/fixture_parity_support.py`, `python/rebar_harness/correctness.py`, `tests/conformance/fixtures/literal_flag_workflows.py`, published reports, or tracked project-state prose in this run; and
  - do not broaden into the shared selector-inventory table, generic direct-test bucket helper error coverage, match-object helper parity, or the remaining named-group / collection-replacement / open-ended bundle-contract tests that still belong on the detached support file.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_literal_flag_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path

owner = Path("tests/python/test_literal_flag_parity_suite.py").read_text(
    encoding="utf-8"
)
contract = Path("tests/python/test_fixture_parity_support_contract.py").read_text(
    encoding="utf-8"
)
needles = (
    "def test_fixture_bundle_contract_supports_selected_case_path_and_order_validation(",
    "def test_load_fixture_bundles_rejects_duplicate_selected_case_ids(",
    "def test_load_fixture_bundles_rejects_empty_selected_case_ids(",
    "def test_load_fixture_bundles_rejects_missing_selected_case_ids(",
    "def test_fixture_bundle_contract_rejects_wrong_selected_case_order(",
    "def test_selected_case_bundle_specs_load_in_declared_bundle_order(",
)
for needle in needles:
    assert needle in owner, needle
    assert needle not in contract, needle
print("ok")
PY`
  - `bash -lc "! rg -n '_literal_flag_selected_case_bundle_specs|test_fixture_bundle_contract_supports_selected_case_path_and_order_validation|test_load_fixture_bundles_rejects_duplicate_selected_case_ids|test_load_fixture_bundles_rejects_empty_selected_case_ids|test_load_fixture_bundles_rejects_missing_selected_case_ids|test_fixture_bundle_contract_rejects_wrong_selected_case_order|test_selected_case_bundle_specs_load_in_declared_bundle_order' tests/python/test_fixture_parity_support_contract.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete a detached literal-flag selected-case contract seam, not to reinterpret literal-flag behavior, selected-case loading semantics, or published frontier coverage.
- Prefer the existing literal-flag owner and file-local helpers over another shared abstraction layer.
- Do not delete `tests/python/test_fixture_parity_support_contract.py`; leave the remaining generic selector, helper-parity, and non-literal-flag bundle-contract coverage in place.

## Notes
- `RBR-0677` is the next available architecture task id in the current checkout:
  - `rg -n "RBR-0677|RBR-0678|RBR-0679|RBR-0680|RBR-0681" ops/state/backlog.md ops/state/current_status.md` returned no matches; and
  - `find ops/tasks -maxdepth 2 -type f \( -name 'RBR-0677*' -o -name 'RBR-0678*' -o -name 'RBR-0679*' -o -name 'RBR-0680*' -o -name 'RBR-0681*' \) | sort` returned no files.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in the live checkout;
  - `.rebar/runtime/dashboard.md` is lagging `HEAD` (`a9ddab0e9181baa12ba73a336108fa89788b84e6` vs `git rev-parse HEAD` = `39e96ba9b5f0067f456876267fe0e8e373365344`), so the queue state was confirmed from the live filesystem instead of trusting the stale report alone; and
  - `.rebar/runtime/loop_state.json` still shows the latest task-worker runs finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The detached slice is concrete and already duplicated beside its natural owner in the current checkout:
  - `tests/python/test_literal_flag_parity_suite.py` is `593` lines and already declares `TARGET_FIXTURE_CASE_IDS`, `SELECTED_CASE_BUNDLE_SPECS`, the unsupported inline/locale case ids, `test_literal_flag_suite_stays_aligned_with_published_correctness_fixture(...)`, `test_literal_flag_parity_suite_tracks_published_case_frontier(...)`, and `test_literal_flag_direct_test_buckets_cover_selected_frontier(...)`;
  - `tests/python/test_fixture_parity_support_contract.py` is `2172` lines and still carries `_literal_flag_selected_case_bundle_specs(...)` plus the six literal-flag selected-case bundle-contract tests listed above;
  - `rg -n "literal_flag_workflows\\.py|literal-flag-workflows|flag-unsupported-inline-flag-search|flag-unsupported-locale-bytes-search|TARGET_FIXTURE_CASE_IDS|SELECTED_CASE_BUNDLE_SPECS" tests/python/test_literal_flag_parity_suite.py tests/python/test_fixture_parity_support_contract.py` shows the same fixture id and unsupported literal-flag case ids live in both files today;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_literal_flag_parity_suite.py` currently passes (`36 passed in 0.07s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py` currently passes (`129 passed in 0.20s`);
  - the inline source probe in Acceptance currently fails exactly on this cleanup with `AssertionError: def test_fixture_bundle_contract_supports_selected_case_path_and_order_validation(` because the literal-flag owner does not yet carry the moved definitions; and
  - the final `rg` command in Acceptance currently fails exactly on this cleanup because the detached support file still contains `_literal_flag_selected_case_bundle_specs(...)` and the six target test definitions.
- This simplification matches the current information flow:
  - `tests/python/test_literal_flag_parity_suite.py` already owns the literal-flag selected bundle, loaded cases, frontier tracking, and direct-test bucket contract; and
  - the detached support file is only keeping a second literal-flag selected-case contract seam alive beside that owner.

## Completion
- 2026-03-19: Moved the literal-flag selected-case bundle-contract helper and its six selected-case/path-order/load-error tests onto `tests/python/test_literal_flag_parity_suite.py`, deriving the owner-local subset from the existing literal-flag bundle data and unsupported native-boundary case ids instead of keeping a detached helper block in `tests/python/test_fixture_parity_support_contract.py`.
- 2026-03-19: Removed `_literal_flag_selected_case_bundle_specs(...)` and the six literal-flag-specific selected-case contract tests from `tests/python/test_fixture_parity_support_contract.py`, leaving the remaining generic selector, helper-parity, and non-literal-flag bundle-contract coverage in place.
- Verification:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_literal_flag_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... PY`
  - `bash -lc "! rg -n '_literal_flag_selected_case_bundle_specs|test_fixture_bundle_contract_supports_selected_case_path_and_order_validation|test_load_fixture_bundles_rejects_duplicate_selected_case_ids|test_load_fixture_bundles_rejects_empty_selected_case_ids|test_load_fixture_bundles_rejects_missing_selected_case_ids|test_fixture_bundle_contract_rejects_wrong_selected_case_order|test_selected_case_bundle_specs_load_in_declared_bundle_order' tests/python/test_fixture_parity_support_contract.py"`
