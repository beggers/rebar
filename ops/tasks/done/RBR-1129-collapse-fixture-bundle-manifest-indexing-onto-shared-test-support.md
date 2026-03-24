# RBR-1129: Collapse fixture bundle manifest indexing onto shared test support

Status: done
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining bespoke fixture-bundle manifest-id plumbing from `tests/python/fixture_parity_support.py` by routing bundle indexing through the existing shared string-id support on `tests/conftest.py` instead of maintaining a local dict-building loop and a trivial manifest-id wrapper.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `tests/python/test_quantified_alternation_parity_suite.py`

## Acceptance Criteria
- `FixtureBundle` exposes one direct manifest-id surface on the dataclass itself, or a strictly smaller equivalent already attached to that existing type, so bundle callers no longer need `fixture_bundle_manifest_id()`.
- `tests/python/fixture_parity_support.py` stops carrying the bespoke `indexed_bundles` loop inside `published_fixture_bundles_by_manifest_id()` and instead routes that mapping through `records_by_string_id()` on `tests/conftest.py`, while preserving the current duplicate-manifest rejection behavior for fixture bundles.
- `fixture_bundle_manifest_id()` is deleted from `tests/python/fixture_parity_support.py`, and the quantified-alternation parity parametrization plus the fixture-parity support contract use the dataclass-attached manifest-id surface instead.
- `load_published_fixture_bundles()` in `tests/python/fixture_parity_support.py` continues returning the same ordered bundle tuple plus manifest-id mapping contract after the cleanup; no fixture selection, case ordering, or bundle identity changes.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` continues to build the same manifest-id keyed replacement-bundle maps and selected bundle order, but no longer depends on the deleted wrapper surface.
- Preserve current behavior after the cleanup:
  - duplicate fixture-bundle manifest ids still fail loudly instead of silently overwriting entries;
  - requested manifest-id ordering still controls the tuple returned by `requested_published_fixture_bundles()`;
  - grouped-replacement and open-ended replacement surfaces keep the same selected bundle ownership and manifest ordering; and
  - no correctness fixture coverage, replacement parity behavior, or benchmark/report state changes.
- Keep the cleanup structural and limited to the four files above. Do not widen it into implementation code, reports, README text, benchmark manifests, or tracked project-state prose.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py::test_published_fixture_bundles_by_manifest_id_returns_requested_bundles tests/python/test_fixture_parity_support_contract.py::test_published_fixture_bundles_by_manifest_id_rejects_duplicate_manifest_ids tests/python/test_fixture_parity_support_contract.py::test_requested_published_fixture_bundles_rejects_missing_manifest_ids tests/python/test_fixture_parity_support_contract.py::test_load_published_fixture_bundles_preserves_selected_path_order tests/python/test_fixture_backed_replacement_parity_suite.py::test_grouped_replacement_surface_keeps_selected_bundle_ownership_explicit tests/python/test_fixture_backed_replacement_parity_suite.py::test_bundle_pattern_projection_and_case_source_payloads_cover_published_fixtures tests/python/test_fixture_backed_replacement_parity_suite.py::test_case_argument_helpers_cover_module_and_pattern_replacement_rows tests/python/test_quantified_alternation_parity_suite.py::test_parity_suite_stays_aligned_with_published_correctness_fixture tests/python/test_quantified_alternation_parity_suite.py::test_generated_quantified_alternation_compile_cases_stay_anchored_to_published_manifests`
- `bash -lc "! rg -n 'def fixture_bundle_manifest_id\\(|if manifest_id in indexed_bundles:|indexed_bundles\\[manifest_id\\] = bundle|ids=fixture_bundle_manifest_id|fixture_bundle_manifest_id\\(' tests/python/fixture_parity_support.py tests/python/test_fixture_parity_support_contract.py tests/python/test_quantified_alternation_parity_suite.py tests/python/test_fixture_backed_replacement_parity_suite.py"`

## Constraints
- Reuse the shared id-indexing support that already exists on `tests/conftest.py`; do not add a new helper module, registry, or abstraction tier for bundle maps.
- Keep `published_fixture_bundles_by_manifest_id()` only if it becomes a thin compatibility wrapper over the shared helper; do not keep any handwritten manifest-id indexing loop in `tests/python/fixture_parity_support.py`.
- Preserve the current duplicate-manifest error wording closely enough that fixture-support contract expectations stay meaningful after the refactor.

## Notes
- `RBR-1129` is the next available unreserved task id in this checkout:
  - the highest live task id across `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, and `ops/tasks/blocked/` is `1128`; and
  - `rg -n 'RBR-1129|RBR-1130|RBR-1131|RBR-1132|RBR-1133' ops/state/backlog.md ops/state/current_status.md` returned no matches in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` contains no task files in this checkout.
- JSON burn-down remains complete and current in both tracked and live views for this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, and `blocked: 0`; and
  - the latest runtime cycle shows `feature-implementation` finishing `RBR-1127` as `done`, with no inherited-dirty checkpoint churn or stalled post-task refresh path.
- The remaining bespoke plumbing is concrete in the live checkout:
  - `tests/python/fixture_parity_support.py:347` still carries `fixture_bundle_manifest_id()` as a one-line wrapper over bundle manifest ids;
  - `tests/python/fixture_parity_support.py:701` through `:712` still build the bundle mapping through a handwritten `indexed_bundles` loop;
  - `tests/python/test_quantified_alternation_parity_suite.py:643` through `:655` still use `fixture_bundle_manifest_id` for parametrization ids; and
  - `tests/python/test_fixture_parity_support_contract.py:4154` still exercises that same wrapper directly instead of a dataclass-attached manifest-id surface.
- The focused verification slice is green in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py::test_published_fixture_bundles_by_manifest_id_returns_requested_bundles tests/python/test_fixture_parity_support_contract.py::test_published_fixture_bundles_by_manifest_id_rejects_duplicate_manifest_ids tests/python/test_fixture_parity_support_contract.py::test_requested_published_fixture_bundles_rejects_missing_manifest_ids tests/python/test_fixture_parity_support_contract.py::test_load_published_fixture_bundles_preserves_selected_path_order tests/python/test_fixture_backed_replacement_parity_suite.py::test_grouped_replacement_surface_keeps_selected_bundle_ownership_explicit tests/python/test_fixture_backed_replacement_parity_suite.py::test_bundle_pattern_projection_and_case_source_payloads_cover_published_fixtures tests/python/test_fixture_backed_replacement_parity_suite.py::test_case_argument_helpers_cover_module_and_pattern_replacement_rows tests/python/test_quantified_alternation_parity_suite.py::test_parity_suite_stays_aligned_with_published_correctness_fixture tests/python/test_quantified_alternation_parity_suite.py::test_generated_quantified_alternation_compile_cases_stay_anchored_to_published_manifests` returned `19 passed` in this run.
- The negative `rg` verification currently fails exactly on the targeted wrapper and handwritten indexing lines above, so it is an acceptance check for this cleanup rather than unrelated repo drift.

## Completion
- Removed `fixture_bundle_manifest_id()` and switched bundle id consumers to `FixtureBundle.expected_manifest_id`.
- Replaced the handwritten manifest-id indexing loop in `published_fixture_bundles_by_manifest_id()` with `tests.conftest.records_by_string_id(...)`, while preserving the duplicate-manifest failure wording for the single-duplicate path covered by the contract tests.
- Tightened the direct contract test so `test_published_fixture_bundles_by_manifest_id_rejects_duplicate_manifest_ids` now exercises duplicate bundle manifest ids instead of duplicate requested ids.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py::test_published_fixture_bundles_by_manifest_id_returns_requested_bundles tests/python/test_fixture_parity_support_contract.py::test_published_fixture_bundles_by_manifest_id_rejects_duplicate_manifest_ids tests/python/test_fixture_parity_support_contract.py::test_requested_published_fixture_bundles_rejects_missing_manifest_ids tests/python/test_fixture_parity_support_contract.py::test_load_published_fixture_bundles_preserves_selected_path_order tests/python/test_fixture_backed_replacement_parity_suite.py::test_grouped_replacement_surface_keeps_selected_bundle_ownership_explicit tests/python/test_fixture_backed_replacement_parity_suite.py::test_bundle_pattern_projection_and_case_source_payloads_cover_published_fixtures tests/python/test_fixture_backed_replacement_parity_suite.py::test_case_argument_helpers_cover_module_and_pattern_replacement_rows tests/python/test_quantified_alternation_parity_suite.py::test_parity_suite_stays_aligned_with_published_correctness_fixture tests/python/test_quantified_alternation_parity_suite.py::test_generated_quantified_alternation_compile_cases_stay_anchored_to_published_manifests`
  - `bash -lc "! rg -n 'def fixture_bundle_manifest_id\\(|if manifest_id in indexed_bundles:|indexed_bundles\\[manifest_id\\] = bundle|ids=fixture_bundle_manifest_id|fixture_bundle_manifest_id\\(' tests/python/fixture_parity_support.py tests/python/test_fixture_parity_support_contract.py tests/python/test_quantified_alternation_parity_suite.py tests/python/test_fixture_backed_replacement_parity_suite.py"`
