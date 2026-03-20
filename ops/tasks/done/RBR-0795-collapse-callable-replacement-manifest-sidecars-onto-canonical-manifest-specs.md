# RBR-0795: Collapse callable replacement manifest sidecars onto canonical manifest specs

Status: done
Owner: architecture-implementation
Created: 2026-03-20

## Goal
- Remove the remaining manifest-selection sidecars from `tests/python/test_callable_replacement_parity_suite.py` now that the file already has one canonical manifest inventory in `CALLABLE_MANIFEST_SPECS`.
- Keep the suite deriving its near-miss and pattern-return-type-error frontier expectations from the live callable manifest specs and case tables instead of a duplicated boolean field plus extra manifest-id frozensets.

## Deliverables
- `tests/python/test_callable_replacement_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_callable_replacement_parity_suite.py` no longer defines or references:
  - the `has_near_miss_matrix` field on `CallableManifestSpec`;
  - `CALLABLE_NEAR_MISS_MANIFEST_IDS`; or
  - `PATTERN_RETURN_TYPE_ERROR_EXPECTED_MANIFEST_IDS`.
- Every `CallableManifestSpec(...)` entry stops passing `has_near_miss_matrix=...`, and the suite still validates the same near-miss frontier without another manifest-id registry:
  - keep `expected_near_miss_patterns` as the canonical manifest-local fact;
  - derive any manifest-level near-miss expectation directly from `CALLABLE_MANIFEST_SPECS`, `CALLABLE_NEAR_MISS_CASE_SPECS`, or the existing live helper tables; and
  - preserve the current near-miss parity coverage for the four callable manifests that already exercise that matrix.
- `test_pattern_callable_replacement_return_type_error_cases_cover_quantified_callable_fixture_frontier()` still proves the same mixed-text quantified/broader-range/open-ended callable slice is covered, but it derives the expected manifest ids from the canonical callable manifest specs plus the existing `CALLABLE_RETURN_TYPE_ERROR_MANIFEST_KEYWORDS` selector instead of a hand-maintained frozenset.
- Preserve the existing callable replacement surface and verification behavior:
  - keep `CALLABLE_MANIFEST_SPECS`, `CALLABLE_NEAR_MISS_CASE_SPECS`, `CALLABLE_FIXTURE_PATHS`, `PENDING_REBAR_MANIFEST_IDS`, `PENDING_REBAR_CASE_IDS`, the published-bundle loading checks, the fixture-shape contract tests, and the mixed-text pending-bytes partition assertions intact;
  - do not change published fixture contents under `tests/conformance/fixtures/`, harness code under `python/rebar_harness/`, benchmark files, reports, README copy, or tracked project-state prose; and
  - do not broaden into feature work or parity behavior changes.
- Verification passes with:
  - `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py`
  - `bash -lc "! rg -n 'has_near_miss_matrix|CALLABLE_NEAR_MISS_MANIFEST_IDS|PATTERN_RETURN_TYPE_ERROR_EXPECTED_MANIFEST_IDS' tests/python/test_callable_replacement_parity_suite.py"`

## Constraints
- Keep this cleanup limited to `tests/python/test_callable_replacement_parity_suite.py`.
- Prefer deleting duplicated manifest-state plumbing over adding another helper registry or another spec field.

## Notes
- `RBR-0795` is free in the current checkout:
  - before adding this file, `rg -n "RBR-0795|RBR-0796|RBR-0797" ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` returned no matches; and
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` did not already contain an `RBR-0795` task before this file was added.
- No blocked architecture task exists to reopen first, and rule 10 does not apply:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the last cycle completed both `RBR-0793` and `RBR-0794` cleanly, so there is no inherited-dirty or post-task commit bottleneck to yield to.
- JSON burn-down is complete in both tracked and live views, so this stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The cleanup target is concrete and isolated in the live checkout:
  - `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py` currently passes (`2747 passed in 2.03s`);
  - `rg -n "has_near_miss_matrix|CALLABLE_NEAR_MISS_MANIFEST_IDS|PATTERN_RETURN_TYPE_ERROR_EXPECTED_MANIFEST_IDS" tests/python/test_callable_replacement_parity_suite.py` currently reports only this file, showing the duplicated manifest-state layer is local to one suite; and
  - the current matches are exactly the duplicated state this task should delete: the `CallableManifestSpec` boolean field and assignments, the near-miss manifest-id sidecar, the pattern-return-type-error manifest-id sidecar, and the two tests that still read them.
- This follows the same post-JSON parity-suite simplification track as the recent sidecar-removal tasks:
  - `ops/tasks/done/RBR-0782-collapse-remaining-owner-manifest-loader-wrappers-onto-canonical-bundle-loads.md`
  - `ops/tasks/done/RBR-0789-collapse-replacement-contract-bundle-spec-sidecars-onto-canonical-owner-bundle-loads.md`
  - `ops/tasks/done/RBR-0793-delete-dead-spec-based-fixture-bundle-loader-plumbing.md`
- 2026-03-20: Removed the `CallableManifestSpec.has_near_miss_matrix` field plus the `CALLABLE_NEAR_MISS_MANIFEST_IDS` and `PATTERN_RETURN_TYPE_ERROR_EXPECTED_MANIFEST_IDS` sidecars from `tests/python/test_callable_replacement_parity_suite.py`, replaced them with derived near-miss and return-type-error frontier helpers driven by `CALLABLE_MANIFEST_SPECS`, `CALLABLE_NEAR_MISS_CASE_SPECS`, and the live published callable bundles, and preserved the existing callable fixture, pending-bytes, and parity verification surface. Verified with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py` (`2747 passed in 2.13s`) and `bash -lc "! rg -n 'has_near_miss_matrix|CALLABLE_NEAR_MISS_MANIFEST_IDS|PATTERN_RETURN_TYPE_ERROR_EXPECTED_MANIFEST_IDS' tests/python/test_callable_replacement_parity_suite.py"` (passed with no matches).
