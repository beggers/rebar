## RBR-1027: Collapse remaining replacement bundle case-id maps

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the two remaining local `cases_by_id` maps from `tests/python/test_fixture_backed_replacement_parity_suite.py` so the replacement owner suite asserts through the canonical ordered `bundle.cases` rows and selected case-id tuples instead of rebuilding detached case-id dictionaries for tiny local checks.

## Deliverables
- `tests/python/test_fixture_backed_replacement_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_fixture_backed_replacement_parity_suite.py` no longer defines `cases_by_id = {case.case_id: case for case in bundle.cases}` in either:
  - `test_bundle_pattern_projection_and_case_source_payloads_cover_published_fixtures()`
  - `_assert_direct_literal_replacement_publication_contract(...)`
- Replace the map-backed lookups with one smaller file-local route built from the canonical ordered bundle rows already loaded in those scopes:
  - prefer tuple order, direct row selection, or one strictly smaller file-local selector over another `*_BY_ID` map, registry, or helper module; and
  - keep the cleanup local to the existing owner suite instead of widening into another support surface.
- Preserve the grouped replacement collection payload contract exactly:
  - `test_bundle_pattern_projection_and_case_source_payloads_cover_published_fixtures()` still proves the bundle case ids equal `_grouped_replacement_collection_case_ids(bundle)`;
  - that ordered case-id tuple still stays exactly `(GROUPED_TEMPLATE_CALLABLE_CASE_ID, GROUPED_TEMPLATE_SELECTED_CASE_ID)`;
  - the pattern and string-pattern projections still both equal `GROUPED_REPLACEMENT_COLLECTION_PATTERNS`;
  - the callable case still carries `source_args[1] == {"type": "callable_constant", "value": "x"}` with `source_kwargs == {}`; and
  - the grouped-template case still carries `source_args[1] == r"\1x"` with `source_kwargs == {}`.
- Preserve the direct-literal publication helper contract exactly:
  - `_assert_direct_literal_replacement_publication_contract(...)` still proves `tuple(case.case_id for case in bundle.cases) == selected_case_ids`;
  - the selected owner slice from `fixture_cases_for_operation((bundle,), operation)` still stays in the same order as `selected_case_ids`;
  - the ordered `args`, `helper`, and `text_model` sequences for `selected_case_ids` still match `expected_args_by_case_id`, `expected_helpers`, and `expected_text_models` exactly; and
  - keep the existing direct module and direct pattern publication tests green without changing their selected case ids or expected payloads.
- Keep the cleanup structural and local:
  - do not edit fixture manifests, correctness-harness modules, benchmark files, reports, README/current-status/backlog prose, or non-replacement parity files; and
  - do not widen this run into replacement behavior changes, mixed-text routing cleanup, or another support abstraction.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'bundle_pattern_projection_and_case_source_payloads_cover_published_fixtures or collection_replacement_manifest_publishes_direct_module_literal_replacement_rows_in_order or collection_replacement_manifest_publishes_direct_pattern_literal_replacement_rows_in_order'`
- `bash -lc "! rg -n 'cases_by_id = \\{case\\.case_id: case for case in bundle\\.cases\\}' tests/python/test_fixture_backed_replacement_parity_suite.py"`

## Constraints
- Keep the cleanup structural and local to `tests/python/test_fixture_backed_replacement_parity_suite.py`.
- Prefer deleting the detached case-id maps over introducing another selector layer.
- Do not edit fixture manifests, harness modules, benchmark files, reports, or tracked project-state prose in this run.

## Notes
- `RBR-1027` is the next available unreserved task id in the current checkout:
  - `rg -n "RBR-1027" ops/state/current_status.md ops/state/backlog.md ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked` returned no matches in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git status --short` was empty in this run;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and no last-cycle anomalies; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- The simplification target is concrete in the live checkout:
  - `tests/python/test_fixture_backed_replacement_parity_suite.py` still defines local `cases_by_id` maps at lines `1728` and `2464`;
  - the focused pytest selector in Verification currently passes (`3 passed, 1298 deselected`); and
  - the final `! rg ...` check currently fails exactly on those two remaining detached maps.
