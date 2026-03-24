# RBR-1131: Collapse whole-bundle case flattening onto shared parity support

Status: done
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining owner-local whole-bundle fixture-case flattening from the parity suites by routing it through one shared support path on `tests/python/fixture_parity_support.py`, and fold the stale grouped-capture `fixture_bundle_manifest_id` import cleanup into the same pass so the grouped-capture owner stops depending on a helper that `RBR-1129` already deleted.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_grouped_capture_parity_suite.py`
- `tests/python/test_callable_replacement_parity_suite.py`

## Acceptance Criteria
- Add one shared helper on `tests/python/fixture_parity_support.py`, or a strictly smaller equivalent on that existing path, that is canonical for flattening ordered `FixtureBundle` collections into ordered `FixtureCase` tuples:
  - it accepts an iterable of `FixtureBundle` objects;
  - it preserves the existing bundle order and the in-manifest case order;
  - it is reusable by both grouped-capture and callable-replacement parity owners; and
  - it does not add a new helper module, registry, or abstraction tier.
- `fixture_cases_by_id()` on `tests/python/fixture_parity_support.py` stops carrying its own bundle-expansion loop and delegates bundle flattening through that shared helper while preserving current behavior:
  - mixed `FixtureBundle` and `FixtureCase` iterables still work;
  - non-fixture entries still raise the same `TypeError` contract; and
  - duplicate-case rejection still reports the same `case_id`-based failure surface.
- `tests/python/test_grouped_capture_parity_suite.py` stops carrying the owner-local `_iter_fixture_cases()` path and no longer imports or parametrizes through the already-deleted `fixture_bundle_manifest_id` wrapper:
  - route `COMPILE_CASES`, `MODULE_CASES`, and `PATTERN_CASES` through the shared bundle-flattening support;
  - switch the bundle parametrization id callback to the dataclass-attached manifest-id surface already used elsewhere (`bundle.expected_manifest_id` or a strictly smaller equivalent already on `FixtureBundle`);
  - preserve the existing published bundle order, selected frontier coverage, and direct-test bucket contents; and
  - keep all grouped-capture case ordering and compile-pattern grouping behavior unchanged.
- `tests/python/test_callable_replacement_parity_suite.py` stops defining `PUBLISHED_CALLABLE_CASES` through an inline `for bundle in FIXTURE_BUNDLES for case in bundle.cases` flattening comprehension and instead uses the shared bundle-flattening support while preserving:
  - `SHARED_CALLABLE_CASES`, `MODULE_CASES`, `PATTERN_CASES`, `BYTES_MODULE_CASES`, and `BYTES_PATTERN_CASES`;
  - the current callable fixture-shape contract, direct-test bucket coverage, and pending-bytes frontier partitioning; and
  - the existing published case order and case identity.
- Extend `tests/python/test_fixture_parity_support_contract.py` with focused coverage for the shared flattening support, including:
  - a success case that proves the helper preserves bundle order and in-bundle case order; and
  - a success or tightened existing case that proves `fixture_cases_by_id()` still preserves mixed bundle-and-case ordering after delegating through the shared helper.
- Keep the cleanup structural and limited to the four files above. Do not widen it into implementation code, reports, benchmark manifests, README text, or tracked project-state prose.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py -k 'fixture_bundles_load_expected_published_owner_order or grouped_capture_direct_test_buckets_cover_selected_frontier' tests/python/test_callable_replacement_parity_suite.py::test_callable_replacement_fixture_shape_contract tests/python/test_callable_replacement_parity_suite.py::test_callable_replacement_direct_test_buckets_cover_selected_frontier tests/python/test_fixture_parity_support_contract.py::test_fixture_cases_by_id_preserves_input_order_for_bundles_and_cases`
- `bash -lc "! rg -n 'def _iter_fixture_cases\\(|fixture_bundle_manifest_id,|ids=fixture_bundle_manifest_id|PUBLISHED_CALLABLE_CASES = tuple\\(|case for bundle in FIXTURE_BUNDLES for case in bundle\\.cases|case_entries\\.extend\\(fixture\\.cases\\)' tests/python/fixture_parity_support.py tests/python/test_grouped_capture_parity_suite.py tests/python/test_callable_replacement_parity_suite.py"`

## Constraints
- Reuse `tests/python/fixture_parity_support.py` as the shared-support home; do not add a new helper module or a second case-index/cache layer.
- Prefer deleting owner-local plumbing over adding another suite-specific wrapper.
- Preserve the existing bundle-loading surfaces (`FIXTURE_BUNDLES`, `FIXTURE_BUNDLES_BY_MANIFEST_ID`, and the grouped-capture requested bundle tuple) because this task is about deleting duplicate case-flattening paths, not rewriting fixture selection.

## Notes
- `RBR-1131` is the next available unreserved task id in this checkout:
  - the highest live task id across `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, and `ops/tasks/blocked/` is `1130`; and
  - `rg -n 'RBR-1131|RBR-1132|RBR-1133|RBR-1134|RBR-1135' ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` returned no reserved future ids in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete and current in both tracked and live views for this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 2`, `in_progress: 0`, and `blocked: 0`;
  - the latest feature-worker run was requeued after a normal nonzero task exit under `sandbox: danger-full-access`, not because of inherited-dirty checkpoint churn or a stalled post-task refresh/commit path; and
  - no architecture task is currently waiting in `ready/`, `in_progress/`, or `blocked/`.
- The remaining duplication is concrete in the live checkout:
  - `tests/python/fixture_parity_support.py` still expands bundle cases inline inside `fixture_cases_by_id()`;
  - `tests/python/test_grouped_capture_parity_suite.py` still imports `fixture_bundle_manifest_id`, still parametrizes with `ids=fixture_bundle_manifest_id`, and still carries owner-local `_iter_fixture_cases()` bundle flattening;
  - `tests/python/test_callable_replacement_parity_suite.py` still defines `PUBLISHED_CALLABLE_CASES` through an inline whole-bundle flattening comprehension; and
  - the negative `rg` verification above fails exactly on those targeted lines in the current checkout.
- Verification status in this run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py::test_callable_replacement_fixture_shape_contract tests/python/test_callable_replacement_parity_suite.py::test_callable_replacement_direct_test_buckets_cover_selected_frontier tests/python/test_fixture_parity_support_contract.py::test_fixture_cases_by_id_preserves_input_order_for_bundles_and_cases` returned `17 passed`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py -k 'fixture_bundles_load_expected_published_owner_order or grouped_capture_direct_test_buckets_cover_selected_frontier'` currently fails during collection because `tests/python/test_grouped_capture_parity_suite.py` still imports the deleted `fixture_bundle_manifest_id` symbol from `tests/python/fixture_parity_support.py`, which is part of the exact cleanup scoped here; and
  - `bash -lc "! rg -n 'def _iter_fixture_cases\\(|fixture_bundle_manifest_id,|ids=fixture_bundle_manifest_id|PUBLISHED_CALLABLE_CASES = tuple\\(|case for bundle in FIXTURE_BUNDLES for case in bundle\\.cases|case_entries\\.extend\\(fixture\\.cases\\)' tests/python/fixture_parity_support.py tests/python/test_grouped_capture_parity_suite.py tests/python/test_callable_replacement_parity_suite.py"` currently fails exactly on the targeted duplicate and stale-helper lines above.

## Completion Note
- Added shared `flatten_fixture_bundles()` support on `tests/python/fixture_parity_support.py` and routed `fixture_cases_by_id()` bundle expansion through it while preserving the mixed bundle-and-case ordering contract.
- Removed grouped-capture owner-local bundle flattening and the stale `fixture_bundle_manifest_id` import, switched bundle ids to `bundle.expected_manifest_id`, and moved callable-replacement published-case flattening onto the same shared helper.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py::test_fixture_bundles_load_expected_published_owner_order tests/python/test_grouped_capture_parity_suite.py::test_grouped_capture_direct_test_buckets_cover_selected_frontier`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py::test_callable_replacement_fixture_shape_contract tests/python/test_callable_replacement_parity_suite.py::test_callable_replacement_direct_test_buckets_cover_selected_frontier tests/python/test_fixture_parity_support_contract.py::test_fixture_cases_by_id_preserves_input_order_for_bundles_and_cases tests/python/test_fixture_parity_support_contract.py::test_flatten_fixture_bundles_preserves_bundle_and_case_order tests/python/test_fixture_parity_support_contract.py::test_fixture_cases_by_id_accepts_mixed_bundle_and_case_entries`
  - `bash -lc "! rg -n 'def _iter_fixture_cases\\(|fixture_bundle_manifest_id,|ids=fixture_bundle_manifest_id|PUBLISHED_CALLABLE_CASES = tuple\\(|case for bundle in FIXTURE_BUNDLES for case in bundle\\.cases|case_entries\\.extend\\(fixture\\.cases\\)' tests/python/fixture_parity_support.py tests/python/test_grouped_capture_parity_suite.py tests/python/test_callable_replacement_parity_suite.py"`
