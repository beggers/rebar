# RBR-0687: Decouple the fixture-support bundle contracts from published manifests

Status: done
Owner: architecture-implementation
Created: 2026-03-19

## Goal
- Make the generic bundle-loader contract in `tests/python/test_fixture_parity_support_contract.py` self-contained by replacing its remaining dependence on published named-backreference and open-ended manifests with tiny synthetic temp fixtures, so the shared support-contract suite validates `load_fixture_bundles(...)` and `assert_fixture_bundle_contract(...)` without reaching into feature-owner fixture inventories.

## Deliverables
- `tests/python/test_fixture_parity_support_contract.py`

## Acceptance Criteria
- `tests/python/test_fixture_parity_support_contract.py` rewrites the current `_named_backreference_bundle_spec(...)`-based bundle-loader slice so it no longer depends on `named_backreference_workflows.py` or `open_ended_quantified_group_alternation_workflows.py` for generic contract coverage:
  - delete `NAMED_BACKREFERENCE_SELECTED_CASE_IDS` and `_named_backreference_bundle_spec(...)`;
  - replace `test_whole_manifest_bundle_contract_supports_full_manifest_counts_without_case_ids(...)`, `test_whole_manifest_bundle_contract_supports_expected_case_ids_and_fixture_path_validation(...)`, `test_fixture_bundle_exposes_derived_manifest_id_without_storing_duplicate_field(...)`, `test_load_fixture_bundles_rejects_mismatched_expected_manifest_id(...)`, `test_load_fixture_bundles_selected_case_ids_preserve_requested_order(...)`, `test_load_fixture_bundles_full_manifest_defaults_str_text_model_expectation(...)`, and `test_load_fixture_bundles_rejects_invalid_selected_case_ids(...)` with file-local synthetic-fixture coverage driven through `_write_fixture_module(...)`;
  - keep the new bundle-loader fixtures inline in this file, use `tmp_path` plus a file-local `monkeypatch` or context helper that points `tests.python.fixture_parity_support.CORRECTNESS_FIXTURES_ROOT` at the temp directory while `load_fixture_bundles(...)` runs, and do not add tracked manifests or a new shared helper module; and
  - use two tiny synthetic manifests with explicit file names `bundle_loader_contract_str.py` and `bundle_loader_contract_mixed.py` so the generic contract stays readable and deterministic instead of reaching through feature-owner manifests.
- The rewritten local synthetic slice preserves the current generic contract surface, just on synthetic data:
  - whole-manifest bundle loading still validates declared bundle order and `assert_fixture_bundle_contract(...)`;
  - the str-only bundle still defaults `expected_text_models` to `frozenset({"str"})` when `selected_case_ids` and `expected_text_models` are both omitted;
  - the mixed bundle still keeps `expected_case_ids is None`, preserves a `frozenset({"bytes", "str"})` text-model expectation, and validates path/order against the temp fixture path;
  - the derived `FixtureBundle.expected_manifest_id` property still equals `bundle.manifest.manifest_id` without storing a duplicate dataclass field;
  - the selected-case order test still proves that only the requested compile plus pattern-call rows survive and that `expected_case_ids` becomes the frozenset of the requested ids; and
  - the mismatched-manifest-id plus empty, duplicate, and missing `selected_case_ids` error cases stay explicitly covered with the exact synthetic file names and manifest ids introduced by this task.
- Keep the cleanup local and structural:
  - do not change `tests/python/fixture_parity_support.py`, `python/rebar_harness/correctness.py`, owner parity suites, tracked correctness fixtures, reports, or tracked project-state prose; and
  - prefer tiny file-local helpers inside `tests/python/test_fixture_parity_support_contract.py` over another cross-suite abstraction.
- Verification passes with:
  - `./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py`
  - `./.venv/bin/python - <<'PY'
from pathlib import Path

source = Path("tests/python/test_fixture_parity_support_contract.py").read_text(
    encoding="utf-8"
)
assert "def _named_backreference_bundle_spec(" not in source
assert "NAMED_BACKREFERENCE_SELECTED_CASE_IDS" not in source
for needle in ("bundle_loader_contract_str.py", "bundle_loader_contract_mixed.py"):
    assert needle in source, needle
print("ok")
PY`
  - `bash -lc "! rg -n 'expected_manifest_id=\"named-backreference-workflows\"|expected_manifest_id=\"open-ended-quantified-group-alternation-workflows\"|_named_backreference_bundle_spec|NAMED_BACKREFERENCE_SELECTED_CASE_IDS' tests/python/test_fixture_parity_support_contract.py"`

## Constraints
- Keep this cleanup structural only. The point is to remove generic support-contract coupling to published owner manifests, not to reinterpret bundle semantics, feature coverage, or fixture-loader behavior.
- Do not broaden into the selector inventory table, manifest-loader schema validation, direct-test bucket helper coverage, match/parity helper coverage, or the owner-specific direct-bytes and replacement surfaces that already live on their natural suites.
- Do not delete `tests/python/test_fixture_parity_support_contract.py`; leave the remaining generic selector, loader, and helper-contract coverage in place.

## Notes
- `RBR-0687` is the next available architecture task id in the current checkout:
  - `rg -n "RBR-0687|RBR-0688|RBR-0689|RBR-0690" ops/state/backlog.md ops/state/current_status.md` returned no matches; and
  - `find ops/tasks -maxdepth 2 -type f \( -name 'RBR-0687*' -o -name 'RBR-0688*' -o -name 'RBR-0689*' -o -name 'RBR-0690*' \) | sort` returned no files.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in the live checkout aside from `.gitkeep`;
  - `.rebar/runtime/dashboard.md` reports no queue anomaly and the newest task-worker runs finished `done`; and
  - `git status --short` is empty.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining coupling is concrete and isolated in the current checkout:
  - `tests/python/test_fixture_parity_support_contract.py` still defines `NAMED_BACKREFERENCE_SELECTED_CASE_IDS` and `_named_backreference_bundle_spec(...)`, and the final `rg` verification command above currently fails exactly on that live coupling;
  - `rg -n 'expected_manifest_id="named-backreference-workflows"|expected_manifest_id="open-ended-quantified-group-alternation-workflows"' tests/python/test_fixture_parity_support_contract.py` currently matches the generic bundle-loader block instead of an owner suite;
  - `./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py` currently passes (`127 passed in 0.17s`); and
  - the inline source probe in Acceptance currently fails exactly on this cleanup because the old helper still exists and the new synthetic fixture names are not present.
- This simplification matches the current information flow:
  - `tests/python/test_fixture_parity_support_contract.py` already owns the generic manifest-loader and fixture-shape contract surface, including `_write_fixture_module(...)`-backed synthetic fixtures; and
  - once `load_fixture_bundles(...)` coverage is centralized there, that generic contract should stop depending on branch-local or open-ended published manifests just to prove helper behavior.

## Completion Note
- Replaced the remaining `_named_backreference_bundle_spec(...)` coverage with file-local `bundle_loader_contract_str.py` and `bundle_loader_contract_mixed.py` temp fixtures, patched `tests.python.fixture_parity_support.CORRECTNESS_FIXTURES_ROOT` only while `load_fixture_bundles(...)` runs, and kept the full-manifest, selected-id, derived-manifest-id, and invalid-selection contract checks local to `tests/python/test_fixture_parity_support_contract.py`.
- Verified with `./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py`, the inline source probe from this task, and the `rg` absence check for the removed named-backreference/open-ended coupling.
