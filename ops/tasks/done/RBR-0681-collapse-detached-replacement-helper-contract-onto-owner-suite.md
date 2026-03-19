# RBR-0681: Collapse the detached replacement-helper contract onto the replacement owner suite

Status: done
Owner: architecture-implementation
Created: 2026-03-19

## Goal
- Move the remaining replacement-specific helper contract checks off `tests/python/test_fixture_parity_support_contract.py` and onto `tests/python/test_fixture_backed_replacement_parity_suite.py`, so replacement helper semantics live beside `GROUPED_REPLACEMENT_TEMPLATE_SURFACE`, its bundle specs, and the replacement-owner manifest tables instead of leaving that slice in the detached support-contract suite.

## Deliverables
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `tests/python/test_fixture_parity_support_contract.py`

## Acceptance Criteria
- `tests/python/test_fixture_backed_replacement_parity_suite.py` becomes the sole owner for the replacement-helper contract slice currently isolated in `tests/python/test_fixture_parity_support_contract.py`:
  - absorb `test_bundle_pattern_projection_and_case_source_payloads_cover_published_fixtures(...)`;
  - absorb `test_case_argument_helpers_cover_module_and_pattern_replacement_rows(...)`;
  - derive the moved assertions from the replacement owner's existing tables and helpers, including `GROUPED_REPLACEMENT_TEMPLATE_SURFACE`, `GROUPED_TEMPLATE_SELECTED_CASE_ID`, `GROUPED_REPLACEMENT_NAMED_CASE_IDS`, `published_fixture_bundle_by_manifest_id(...)`, `case_pattern(...)`, `case_replacement_argument(...)`, and `case_text_argument(...)`, instead of adding another `*_support.py`, expanding `tests/python/conftest.py`, or keeping a detached ad hoc bundle table beside the owner suite; and
  - preserve the current replacement-helper contract exactly:
    - the selected `collection-replacement-workflows` rows stay `module-sub-callable-str` plus `module-sub-grouping-template`;
    - the replacement-owner bundle pattern projection for those rows stays `{"abc", "(abc)"}`;
    - `module-sub-callable-str` keeps the callable source-argument payload `{"type": "callable_constant", "value": "x"}` with empty `source_kwargs`;
    - `module-sub-grouping-template` keeps the template source argument `r"\1x"` with empty `source_kwargs`; and
    - the `named-group-replacement-workflows` pattern row still resolves `case_replacement_argument(...)` and `case_text_argument(...)` through the pattern-call argument positions for `pattern-sub-template-named-group-str`.
- `tests/python/test_fixture_parity_support_contract.py` stops owning this replacement-specific slice:
  - remove the two moved test functions above;
  - remove the `bundle_patterns`, `case_replacement_argument`, and `case_text_argument` imports once they become unused; and
  - do not leave a renamed compatibility shell, second replacement-helper block, or another detached collection/named-group replacement probe beside the owner suite.
- Keep scope structural only:
  - do not change `tests/python/fixture_parity_support.py`, `python/rebar_harness/correctness.py`, replacement fixture manifests, published reports, or tracked project-state prose in this run; and
  - do not broaden into the generic selector inventory checks, direct-test bucket helper error coverage, match-object helper parity coverage, or the remaining non-replacement support-contract tests that still belong on the detached support file.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path

owner = Path("tests/python/test_fixture_backed_replacement_parity_suite.py").read_text(
    encoding="utf-8"
)
contract = Path("tests/python/test_fixture_parity_support_contract.py").read_text(
    encoding="utf-8"
)
needles = (
    "def test_bundle_pattern_projection_and_case_source_payloads_cover_published_fixtures(",
    "def test_case_argument_helpers_cover_module_and_pattern_replacement_rows(",
)
for needle in needles:
    assert needle in owner, needle
    assert needle not in contract, needle
print("ok")
PY`
  - `bash -lc "! rg -n 'test_bundle_pattern_projection_and_case_source_payloads_cover_published_fixtures|test_case_argument_helpers_cover_module_and_pattern_replacement_rows|bundle_patterns|case_replacement_argument|case_text_argument' tests/python/test_fixture_parity_support_contract.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete a detached replacement-helper contract seam, not to reinterpret replacement-template behavior, bundle selection, or helper semantics.
- Prefer the existing fixture-backed replacement owner and file-local assertions over another shared abstraction layer.
- Do not delete `tests/python/test_fixture_parity_support_contract.py`; leave the remaining generic selector, fixture-loader, bundle-contract, and helper-parity coverage in place.

## Notes
- `RBR-0681` is the next available architecture task id in the current checkout:
  - `rg -n "RBR-0681|RBR-0682|RBR-0683" ops/state/backlog.md ops/state/current_status.md` returned no matches; and
  - `find ops/tasks -maxdepth 2 -type f \( -name 'RBR-0681*' -o -name 'RBR-0682*' -o -name 'RBR-0683*' \) | sort` returned no files.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - before this task was seeded, the live checkout had no preexisting ready or in-progress task file besides `.gitkeep`, `ops/tasks/blocked/` had no blocked task file, and the newest task-worker runs in `.rebar/runtime/task_state.json` both finished `done`;
  - `.rebar/runtime/dashboard.md` is lagging the live checkout because it still reports a dirty worktree while `git status --short` is empty, so queue state was confirmed from the live filesystem instead of trusting the stale report alone; and
  - there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The detached replacement-helper slice is concrete and already duplicated beside its natural owner in the current checkout:
  - `tests/python/test_fixture_backed_replacement_parity_suite.py` already imports `case_replacement_argument(...)` and `case_text_argument(...)`, owns `GROUPED_REPLACEMENT_TEMPLATE_SURFACE`, `GROUPED_TEMPLATE_SELECTED_CASE_ID`, `GROUPED_REPLACEMENT_NAMED_CASE_IDS`, and the collection/named-group replacement bundle tables that the detached tests exercise;
  - `tests/python/test_fixture_parity_support_contract.py` still carries the two replacement-specific tests named in Acceptance plus the `bundle_patterns`, `case_replacement_argument`, and `case_text_argument` imports that exist there only for this detached slice;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py` currently passes (`1143 passed in 0.82s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py` currently passes (`121 passed in 0.18s`);
  - the inline source probe in Acceptance currently reports that both target definitions are absent from the replacement owner and still present in the detached support file; and
  - the final `rg` command in Acceptance currently fails exactly on this cleanup because the detached support file still contains the two target test definitions plus the replacement-helper imports that only serve them.
- This simplification matches the current information flow:
  - the fixture-backed replacement owner already carries the manifest ids, selected case ids, template positions, and helper semantics those detached tests assert; and
  - the support-contract file is only keeping a second replacement-specific contract seam alive beside that owner.

## Completion
- 2026-03-19: Widened the grouped replacement owner’s `collection-replacement-workflows` bundle selection to the existing two-row helper-contract slice (`module-sub-callable-str` plus `module-sub-grouping-template`), updated the owner-local compile/template-expand expectations to match that structural ownership, and moved the two replacement-helper contract tests onto `tests/python/test_fixture_backed_replacement_parity_suite.py`.
- 2026-03-19: Removed the moved replacement-specific tests plus the now-unused `bundle_patterns`, `case_replacement_argument`, and `case_text_argument` imports from `tests/python/test_fixture_parity_support_contract.py`, leaving the remaining generic selector, fixture-loader, bundle-contract, and helper-parity coverage in place.
- Verification:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... PY`
  - `bash -lc "! rg -n 'test_bundle_pattern_projection_and_case_source_payloads_cover_published_fixtures|test_case_argument_helpers_cover_module_and_pattern_replacement_rows|bundle_patterns|case_replacement_argument|case_text_argument' tests/python/test_fixture_parity_support_contract.py"`
