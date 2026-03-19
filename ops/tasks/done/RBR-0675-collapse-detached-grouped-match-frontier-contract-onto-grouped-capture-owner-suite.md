# RBR-0675: Collapse the detached grouped-match frontier contract onto the grouped-capture owner suite

Status: done
Owner: architecture-implementation
Created: 2026-03-19
Completed: 2026-03-19

## Goal
- Move the remaining grouped-match published-frontier and ordered-row contract checks off `tests/python/test_fixture_parity_support_contract.py` and onto `tests/python/test_grouped_capture_parity_suite.py`, so the grouped-capture owner keeps the grouped-match selected-case and uncovered-case contract beside the bundle spec, tracked case ids, and `ordered_manifest_cases_from_bundles(...)` consumers it already owns instead of leaving that slice in the detached helper-contract suite.

## Deliverables
- `tests/python/test_grouped_capture_parity_suite.py`
- `tests/python/test_fixture_parity_support_contract.py`

## Acceptance Criteria
- `tests/python/test_grouped_capture_parity_suite.py` becomes the sole owner for the grouped-match-specific frontier-contract slice currently isolated in `tests/python/test_fixture_parity_support_contract.py`:
  - absorb `test_published_case_frontier_helper_preserves_ordered_uncovered_case_ids(...)`;
  - absorb `test_published_case_frontier_helper_rejects_duplicate_selected_case_ids(...)`;
  - absorb `test_published_case_frontier_helper_rejects_duplicate_uncovered_case_ids(...)`;
  - absorb `test_published_case_frontier_helper_rejects_selected_and_uncovered_overlap(...)`;
  - absorb `test_published_case_frontier_helper_reports_missing_and_unexpected_case_ids(...)`;
  - absorb `test_published_case_frontier_helper_reports_uncovered_order_drift(...)`;
  - absorb `test_ordered_manifest_cases_from_bundles_rejects_duplicate_case_ids(...)`;
  - absorb `test_ordered_manifest_cases_from_bundles_rejects_missing_case_ids(...)`;
  - keep any tiny new grouped-match helper file-local on `tests/python/test_grouped_capture_parity_suite.py`, derived from its existing `FIXTURE_BUNDLES`, `GROUPED_MATCH_TRACKED_CASE_IDS`, `GROUPED_MATCH_UNCOVERED_CASE_IDS`, and `published_fixture_bundle_by_manifest_id(...)`, instead of expanding `tests/python/fixture_parity_support.py`, adding another `*_support.py`, or moving this slice into `tests/python/conftest.py`; and
  - preserve the current grouped-match manifest id, selected-case ids, uncovered-case ordering, ordered-row semantics, and negative-helper assertions exactly.
- `tests/python/test_fixture_parity_support_contract.py` stops owning this grouped-match-specific slice:
  - remove the grouped-match branch from `_selected_case_bundle_specs(...)`, or narrow/rename that helper so it keeps only the remaining literal-flag selected-case contract data;
  - remove `_grouped_match_bundle_and_uncovered_case_ids(...)`;
  - remove the eight moved test functions above; and
  - remove any imports, aliases, or local helpers that exist only to support that grouped-match slice.
- The detached contract file no longer mentions the grouped-match manifest after the cleanup:
  - `tests/python/test_fixture_parity_support_contract.py` no longer contains `grouped-match-workflows`; and
  - do not leave a renamed compatibility shell, second grouped-match helper, or another detached grouped-match contract beside the owner suite.
- Keep scope structural only:
  - do not change `tests/conformance/fixtures/grouped_match_workflows.py`, `tests/python/fixture_parity_support.py`, `python/rebar_harness/correctness.py`, published reports, or tracked project-state prose in this run; and
  - do not broaden into the remaining literal-flag selected-case contract tests, grouped-segment leading-capture coverage, named-group coverage, or the generic direct-test bucket helper error cases that still belong on the detached contract file.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path

owner = Path("tests/python/test_grouped_capture_parity_suite.py").read_text(
    encoding="utf-8"
)
contract = Path("tests/python/test_fixture_parity_support_contract.py").read_text(
    encoding="utf-8"
)
needles = (
    "def test_published_case_frontier_helper_preserves_ordered_uncovered_case_ids(",
    "def test_published_case_frontier_helper_rejects_duplicate_selected_case_ids(",
    "def test_published_case_frontier_helper_rejects_duplicate_uncovered_case_ids(",
    "def test_published_case_frontier_helper_rejects_selected_and_uncovered_overlap(",
    "def test_published_case_frontier_helper_reports_missing_and_unexpected_case_ids(",
    "def test_published_case_frontier_helper_reports_uncovered_order_drift(",
    "def test_ordered_manifest_cases_from_bundles_rejects_duplicate_case_ids(",
    "def test_ordered_manifest_cases_from_bundles_rejects_missing_case_ids(",
)
for needle in needles:
    assert needle in owner, needle
    assert needle not in contract, needle
print("ok")
PY`
  - `bash -lc "! rg -n 'grouped-match-workflows|_grouped_match_bundle_and_uncovered_case_ids|test_published_case_frontier_helper_preserves_ordered_uncovered_case_ids|test_published_case_frontier_helper_rejects_duplicate_selected_case_ids|test_published_case_frontier_helper_rejects_duplicate_uncovered_case_ids|test_published_case_frontier_helper_rejects_selected_and_uncovered_overlap|test_published_case_frontier_helper_reports_missing_and_unexpected_case_ids|test_published_case_frontier_helper_reports_uncovered_order_drift|test_ordered_manifest_cases_from_bundles_rejects_duplicate_case_ids|test_ordered_manifest_cases_from_bundles_rejects_missing_case_ids' tests/python/test_fixture_parity_support_contract.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete a detached grouped-match contract seam, not to reinterpret grouped-capture fixture selection, published frontier behavior, or `ordered_manifest_cases_from_bundles(...)` semantics.
- Prefer the existing grouped-capture parity owner and file-local helpers over another shared abstraction layer.
- Do not delete `tests/python/test_fixture_parity_support_contract.py`; leave the remaining generic fixture-loader, selected-case bundle, helper-parity, and error-path coverage in place.

## Notes
- `RBR-0675` is the next available architecture task id in the current checkout:
  - `rg -n "RBR-0675|RBR-0676|RBR-0677|RBR-0678|RBR-0679" ops/state/backlog.md ops/state/current_status.md` returned no matches; and
  - `find ops/tasks -maxdepth 2 -type f \( -name 'RBR-0675*' -o -name 'RBR-0676*' -o -name 'RBR-0677*' -o -name 'RBR-0678*' -o -name 'RBR-0679*' \) | sort` returned no files.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in the current checkout;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the last cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The detached grouped-match slice is concrete and already duplicated beside its natural owner in the current checkout:
  - `tests/python/test_grouped_capture_parity_suite.py` already owns the grouped-match bundle spec, `GROUPED_MATCH_TRACKED_CASE_IDS`, `GROUPED_MATCH_UNCOVERED_CASE_IDS`, the positive frontier assertion in `test_grouped_capture_parity_suite_tracks_published_case_frontier(...)`, and the `ordered_manifest_cases_from_bundles(...)` consumers that depend on that same grouped-match bundle;
  - `tests/python/test_fixture_parity_support_contract.py` still carries the grouped-match branch inside `_selected_case_bundle_specs(...)`, `_grouped_match_bundle_and_uncovered_case_ids(...)`, the six grouped-match frontier-helper tests, and the two grouped-match `ordered_manifest_cases_from_bundles(...)` error-path tests listed above;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py` currently passes (`417 passed in 0.34s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py` currently passes (`138 passed in 0.20s`);
  - the inline source probe in Acceptance currently reports `needs-move`, because all eight target test definitions still live only on `tests/python/test_fixture_parity_support_contract.py`; and
  - the final `rg` command in Acceptance currently fails exactly on this cleanup because the detached contract file still contains the grouped-match manifest id, helper, and moved test names.

## Completion Note
- 2026-03-19: Moved the grouped-match frontier-helper and `ordered_manifest_cases_from_bundles(...)` contract tests onto `tests/python/test_grouped_capture_parity_suite.py`, keeping the grouped-match bundle lookup and case-id split file-local on the owner suite and preserving the existing grouped-match error strings exactly.
- 2026-03-19: Removed the detached grouped-match selected-bundle helper/spec branch and the grouped-match-dependent ordered-row coverage from `tests/python/test_fixture_parity_support_contract.py`; the detached contract file no longer mentions `grouped-match-workflows`.

## Verification
- 2026-03-19: `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py` (`426 passed`)
- 2026-03-19: `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py` (`129 passed`)
- 2026-03-19: `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... PY` (`ok`)
- 2026-03-19: `bash -lc "! rg -n 'grouped-match-workflows|_grouped_match_bundle_and_uncovered_case_ids|test_published_case_frontier_helper_preserves_ordered_uncovered_case_ids|test_published_case_frontier_helper_rejects_duplicate_selected_case_ids|test_published_case_frontier_helper_rejects_duplicate_uncovered_case_ids|test_published_case_frontier_helper_rejects_selected_and_uncovered_overlap|test_published_case_frontier_helper_reports_missing_and_unexpected_case_ids|test_published_case_frontier_helper_reports_uncovered_order_drift|test_ordered_manifest_cases_from_bundles_rejects_duplicate_case_ids|test_ordered_manifest_cases_from_bundles_rejects_missing_case_ids' tests/python/test_fixture_parity_support_contract.py"` (no matches)
