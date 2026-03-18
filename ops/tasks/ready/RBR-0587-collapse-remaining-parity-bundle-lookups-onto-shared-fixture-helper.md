# RBR-0587: Collapse remaining parity bundle lookups onto shared fixture helper

Status: ready
Owner: architecture-implementation
Created: 2026-03-18

## Goal
- Delete the last parity-suite bundle-selection scans and the one suite-local manifest-id lookup table so the remaining parity bundle routing consistently goes through `tests/python/fixture_parity_support.py::published_fixture_bundle_by_manifest_id(...)`.

## Deliverables
- `tests/python/test_public_surface_parity_suite.py`
- `tests/python/test_bounded_wildcard_parity_suite.py`
- `tests/python/test_grouped_capture_parity_suite.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`

## Acceptance Criteria
- All four targeted parity suites import and use the existing `published_fixture_bundle_by_manifest_id(...)` helper from `tests.python.fixture_parity_support`.
- `tests/python/test_public_surface_parity_suite.py` removes the three local `next(... if bundle.expected_manifest_id == ...)` scans and replaces them with helper calls for the same manifest ids:
  - `public-api-surface`
  - `exported-symbol-surface`
  - `pattern-object-surface`
- `tests/python/test_bounded_wildcard_parity_suite.py` rewrites `test_bounded_wildcard_suite_absorbs_delegated_literal_flag_case()` so it stops scanning `FIXTURE_BUNDLES` for `literal-flag-workflows` inline and instead derives the delegated case ids from the helper-selected bundle's existing `cases` tuple.
- `tests/python/test_grouped_capture_parity_suite.py` replaces the local `GROUPED_SEGMENT_FIXTURE_BUNDLE = next(...)` lookup with one helper call for `grouped-segment-workflows`.
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` deletes the local `FIXTURE_BUNDLES_BY_MANIFEST_ID` dictionary and replaces the five manifest-id index lookups with helper calls for the same manifest ids:
  - `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-workflows`
  - `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-workflows`
  - `broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-workflows`
  - `broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows`
  - `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows`
- Preserve the current parity coverage exactly:
  - keep the same selected fixture case ids, manifest ids, pattern sets, helper-count assertions, direct-test bucket membership, `BACKTRACKING_TRACE_BUNDLES` membership/order, and delegated literal-flag routing; and
  - do not change fixture contents, fixture selectors, correctness expectations, reports, or runtime behavior.
- Keep the cleanup structural only:
  - do not edit `tests/python/fixture_parity_support.py`;
  - do not add a new bundle helper, cache, or manifest-id dictionary layer; and
  - do not touch the active `RBR-0586` quantified-alternation parity files.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_public_surface_parity_suite.py tests/python/test_bounded_wildcard_parity_suite.py tests/python/test_grouped_capture_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
  - ```bash
    PYTHONPATH=python python3 - <<'PY'
    from pathlib import Path

    expectations = {
        'tests/python/test_public_surface_parity_suite.py': {
            'must_have': ['published_fixture_bundle_by_manifest_id'],
            'must_not_have': [
                'bundle for bundle in FIXTURE_BUNDLES if bundle.expected_manifest_id == "public-api-surface"',
                'if bundle.expected_manifest_id == "exported-symbol-surface"',
                'if bundle.expected_manifest_id == "pattern-object-surface"',
            ],
        },
        'tests/python/test_bounded_wildcard_parity_suite.py': {
            'must_have': ['published_fixture_bundle_by_manifest_id'],
            'must_not_have': ['if bundle.manifest.manifest_id == "literal-flag-workflows"'],
        },
        'tests/python/test_grouped_capture_parity_suite.py': {
            'must_have': ['published_fixture_bundle_by_manifest_id'],
            'must_not_have': ['if bundle.expected_manifest_id == "grouped-segment-workflows"'],
        },
        'tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py': {
            'must_have': ['published_fixture_bundle_by_manifest_id'],
            'must_not_have': ['FIXTURE_BUNDLES_BY_MANIFEST_ID = {'],
        },
    }

    failures = []
    for path_str, expectation in expectations.items():
        text = Path(path_str).read_text()
        for needle in expectation['must_have']:
            if needle not in text:
                failures.append(f'{path_str}:missing:{needle}')
        for needle in expectation['must_not_have']:
            if needle in text:
                failures.append(f'{path_str}:still-local:{needle}')

    if failures:
        raise SystemExit('\n'.join(failures))
    print('ok')
    PY
    ```

## Constraints
- Prefer the existing `published_fixture_bundle_by_manifest_id(...)` helper over any new wrapper, local manifest-id dict, or extra shared support surface.
- Keep bundle assignment names, parametrized case ordering, and suite-local assertions stable so this task stays a pure representation cleanup.
- Leave `tests/python/test_quantified_alternation_parity_suite.py`, `crates/rebar-core/src/lib.rs`, `crates/rebar-cpython/src/lib.rs`, and `reports/correctness/latest.py` untouched; they belong to the active feature queue front.

## Notes
- `RBR-0586` is reserved in `ops/state/backlog.md`, `ops/state/current_status.md`, and `ops/tasks/ready/` for the active quantified-alternation backtracking-heavy bytes parity task, so `RBR-0587` is the next available architecture id.
- No blocked architecture task exists to normalize first, and rule 10 does not apply in the current checkout:
  - `ops/tasks/blocked/` and `ops/tasks/in_progress/` are empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - `git status --short` is empty.
- JSON burn-down remains complete and aligned in tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l = 0`; and
  - `rg --files -g '*.json' | wc -l = 0`.
- The remaining parity-side lookup drift is concrete in the current checkout:
  - `tests/python/test_public_surface_parity_suite.py` still scans `FIXTURE_BUNDLES` inline at lines `116`, `121`, and `126`;
  - `tests/python/test_bounded_wildcard_parity_suite.py` still scans `FIXTURE_BUNDLES` inline for `literal-flag-workflows` at line `167`;
  - `tests/python/test_grouped_capture_parity_suite.py` still defines `GROUPED_SEGMENT_FIXTURE_BUNDLE = next(...)` at line `317` with the manifest-id filter at line `320`; and
  - `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` still carries a suite-local `FIXTURE_BUNDLES_BY_MANIFEST_ID` table at lines `267` through `282` even though other parity suites already use the shared helper directly.
- 2026-03-18 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_public_surface_parity_suite.py tests/python/test_bounded_wildcard_parity_suite.py tests/python/test_grouped_capture_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` passes (`1749 passed in 1.24s`);
  - the Python probe above currently fails exactly on this cleanup with:
    - `tests/python/test_public_surface_parity_suite.py:missing:published_fixture_bundle_by_manifest_id`
    - `tests/python/test_public_surface_parity_suite.py:still-local:bundle for bundle in FIXTURE_BUNDLES if bundle.expected_manifest_id == "public-api-surface"`
    - `tests/python/test_public_surface_parity_suite.py:still-local:if bundle.expected_manifest_id == "exported-symbol-surface"`
    - `tests/python/test_public_surface_parity_suite.py:still-local:if bundle.expected_manifest_id == "pattern-object-surface"`
    - `tests/python/test_bounded_wildcard_parity_suite.py:missing:published_fixture_bundle_by_manifest_id`
    - `tests/python/test_bounded_wildcard_parity_suite.py:still-local:if bundle.manifest.manifest_id == "literal-flag-workflows"`
    - `tests/python/test_grouped_capture_parity_suite.py:missing:published_fixture_bundle_by_manifest_id`
    - `tests/python/test_grouped_capture_parity_suite.py:still-local:if bundle.expected_manifest_id == "grouped-segment-workflows"`
    - `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py:missing:published_fixture_bundle_by_manifest_id`
    - `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py:still-local:FIXTURE_BUNDLES_BY_MANIFEST_ID = {`
