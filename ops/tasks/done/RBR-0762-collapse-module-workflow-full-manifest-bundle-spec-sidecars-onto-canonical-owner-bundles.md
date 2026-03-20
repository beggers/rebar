# RBR-0762: Collapse module-workflow full-manifest bundle-spec sidecars onto canonical owner bundles

Status: done
Owner: architecture-implementation
Created: 2026-03-20
Completed: 2026-03-20

## Goal
- Remove the remaining handwritten bundle-spec sidecars for the two module-workflow parity-suite owners that now already map 1:1 to their full manifests: `module_workflow_surface.py` and `match_behavior_smoke.py`.
- Make the loaded full-manifest rows the sole source of truth for those two owner bundles inside `tests/python/test_module_workflow_parity_suite.py`.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` stops defining or reading these detached full-manifest sidecars:
  - `MODULE_WORKFLOW_EXPECTED_CASE_IDS`
  - `MODULE_WORKFLOW_EXPECTED_PATTERNS`
  - `MODULE_WORKFLOW_EXPECTED_OPERATION_HELPER_COUNTS`
  - `MATCH_BEHAVIOR_EXPECTED_CASE_IDS`
  - `MATCH_BEHAVIOR_EXPECTED_PATTERNS`
  - `MATCH_BEHAVIOR_EXPECTED_OPERATION_HELPER_COUNTS`
  - `SELECTED_CASE_BUNDLE_SPECS`
- `MODULE_WORKFLOW_BUNDLE` and `MATCH_BEHAVIOR_BUNDLE` load as full-manifest owner bundles instead of through handwritten `FixtureBundleSpec(...)` mirrors:
  - preserve owner order exactly as `MODULE_WORKFLOW_FIXTURE_PATH`, then `MATCH_BEHAVIOR_FIXTURE_PATH`;
  - preserve manifest-id resolution exactly as `module-workflow-surface` and `match-behavior-smoke`;
  - preserve case order exactly as the loaded manifest row order for both bundles.
- Derive the bundle contracts directly from the loaded rows rather than from handwritten top-level sidecars:
  - `MODULE_WORKFLOW_BUNDLE.expected_patterns` stays `frozenset(case_pattern(case) for case in MODULE_WORKFLOW_BUNDLE.cases)`;
  - `MODULE_WORKFLOW_BUNDLE.expected_operation_helper_counts` stays `Counter((case.operation, case.helper) for case in MODULE_WORKFLOW_BUNDLE.cases)`;
  - `MODULE_WORKFLOW_BUNDLE.expected_text_models` stays `frozenset({"bytes", "str"})`;
  - `MATCH_BEHAVIOR_BUNDLE.expected_patterns` stays `frozenset(case_pattern(case) for case in MATCH_BEHAVIOR_BUNDLE.cases)`;
  - `MATCH_BEHAVIOR_BUNDLE.expected_operation_helper_counts` stays `Counter((case.operation, case.helper) for case in MATCH_BEHAVIOR_BUNDLE.cases)`;
  - `MATCH_BEHAVIOR_BUNDLE.expected_text_models` stays `frozenset({"bytes", "str"})`;
  - any ordered case-id tuple still needed by tests must be derived from `bundle.cases` or one tiny file-local helper over those loaded rows, not from a handwritten mirrored tuple.
- These tests stop reading the deleted sidecars and instead derive their selected frontier directly from the loaded bundles:
  - `test_module_workflow_parity_suite_stays_aligned_with_published_fixture`
  - `test_module_workflow_parity_suite_tracks_published_case_frontier`
  - `test_module_workflow_direct_test_buckets_cover_selected_frontier`
  - `test_module_workflow_surface_bundle_contract_covers_regression_compile_cases`
  - `test_match_behavior_parity_suite_stays_aligned_with_published_fixture`
  - `test_match_behavior_parity_suite_tracks_published_case_frontier`
  - `test_match_behavior_direct_test_bucket_covers_selected_frontier`
- Keep the still-meaningful subset selectors unchanged:
  - do not change `MODULE_WORKFLOW_BOUNDED_WILDCARD_COMPILE_CASE_IDS`, `MODULE_WORKFLOW_BOUNDED_WILDCARD_PATTERN_CASE_IDS`, `MODULE_WORKFLOW_COMPILE_ONLY_CASE_IDS`, `MODULE_WORKFLOW_COMPILE_ONLY_PATTERNS`, `MODULE_WORKFLOW_COMPILE_ONLY_OPERATION_HELPER_COUNTS`, `COLLECTION_TARGET_FIXTURE_CASE_IDS`, or `COLLECTION_REPLACEMENT_UNCOVERED_CASE_IDS`;
  - do not broaden this cleanup into the collection/replacement subset bundle, fixture files under `tests/conformance/fixtures/`, `tests/python/fixture_parity_support.py`, correctness reports, benchmarks, README, or tracked project-state prose.
- Keep scope structural only:
  - prefer the existing shared `load_published_fixture_bundles(...)` helper for these two full-manifest owners, or one equivalently direct full-manifest load path;
  - do not introduce another mirrored bundle-spec table or another detached case-id registry.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from collections import Counter
import tests.python.test_module_workflow_parity_suite as mod

assert tuple(bundle.manifest.path.name for bundle in (mod.MODULE_WORKFLOW_BUNDLE, mod.MATCH_BEHAVIOR_BUNDLE)) == (
    "module_workflow_surface.py",
    "match_behavior_smoke.py",
)
assert tuple(case.case_id for case in mod.MODULE_WORKFLOW_BUNDLE.cases) == tuple(
    case.case_id for case in mod.MODULE_WORKFLOW_BUNDLE.manifest.cases
)
assert mod.MODULE_WORKFLOW_BUNDLE.expected_patterns == frozenset(
    mod.case_pattern(case) for case in mod.MODULE_WORKFLOW_BUNDLE.cases
)
assert mod.MODULE_WORKFLOW_BUNDLE.expected_operation_helper_counts == Counter(
    (case.operation, case.helper) for case in mod.MODULE_WORKFLOW_BUNDLE.cases
)
assert mod.MODULE_WORKFLOW_BUNDLE.expected_text_models == frozenset({"bytes", "str"})
assert tuple(case.case_id for case in mod.MATCH_BEHAVIOR_BUNDLE.cases) == tuple(
    case.case_id for case in mod.MATCH_BEHAVIOR_BUNDLE.manifest.cases
)
assert mod.MATCH_BEHAVIOR_BUNDLE.expected_patterns == frozenset(
    mod.case_pattern(case) for case in mod.MATCH_BEHAVIOR_BUNDLE.cases
)
assert mod.MATCH_BEHAVIOR_BUNDLE.expected_operation_helper_counts == Counter(
    (case.operation, case.helper) for case in mod.MATCH_BEHAVIOR_BUNDLE.cases
)
assert mod.MATCH_BEHAVIOR_BUNDLE.expected_text_models == frozenset({"bytes", "str"})
print("ok")
PY`
  - `bash -lc "! rg -n '^(MODULE_WORKFLOW_EXPECTED_CASE_IDS|MODULE_WORKFLOW_EXPECTED_PATTERNS|MODULE_WORKFLOW_EXPECTED_OPERATION_HELPER_COUNTS|MATCH_BEHAVIOR_EXPECTED_CASE_IDS|MATCH_BEHAVIOR_EXPECTED_PATTERNS|MATCH_BEHAVIOR_EXPECTED_OPERATION_HELPER_COUNTS|SELECTED_CASE_BUNDLE_SPECS) =' tests/python/test_module_workflow_parity_suite.py"`

## Constraints
- Keep this cleanup limited to `tests/python/test_module_workflow_parity_suite.py`.
- Do not turn this into a shared-helper rewrite, a public-surface rewrite, or a collection/replacement coverage rewrite.
- Preserve all current direct-test buckets and fixture-backed coverage behavior; only the representation of the two full-manifest owner bundles should change.

## Notes
- `RBR-0762` is the next available task id in the current checkout:
  - `python3 - <<'PY'
import pathlib, re
existing = set()
for base in ['ops/tasks/ready', 'ops/tasks/in_progress', 'ops/tasks/done', 'ops/tasks/blocked']:
    for path in pathlib.Path(base).glob('RBR-*.md'):
        m = re.match(r'(RBR-\d+[A-Z]?)', path.name)
        if m:
            existing.add(m.group(1))
text = '\n'.join(
    pathlib.Path(p).read_text(encoding='utf-8')
    for p in ['ops/state/backlog.md', 'ops/state/current_status.md']
)
reserved = set(re.findall(r'RBR-\d+[A-Z]?', text)) - existing
existing_sorted = sorted(existing, key=lambda s: (int(re.search(r'\d+', s).group()), s))
reserved_sorted = sorted(reserved, key=lambda s: (int(re.search(r'\d+', s).group()), s))
print('highest_existing_tail', existing_sorted[-10:])
print('reserved_tail', reserved_sorted[-20:])
for n in range(int(re.search(r'\d+', existing_sorted[-1]).group()), int(re.search(r'\d+', existing_sorted[-1]).group()) + 200):
    rid = f'RBR-{n:04d}'
    if rid not in existing and rid not in reserved:
        print('next_free', rid)
        break
PY` reported the existing tail through `RBR-0761`, no reserved missing tail ids, and `next_free RBR-0762`.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added; and
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`.
- JSON burn-down remains complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- This cleanup is concrete and currently viable:
  - `module_workflow_surface.py` currently contains 54 cases, and `MODULE_WORKFLOW_EXPECTED_CASE_IDS` also contains 54 case ids with no drift in either direction;
  - `match_behavior_smoke.py` currently contains 6 cases, and `MATCH_BEHAVIOR_EXPECTED_CASE_IDS` also contains 6 case ids with no drift in either direction;
  - `MODULE_WORKFLOW_EXPECTED_PATTERNS == frozenset(case_pattern(case) for case in MODULE_WORKFLOW_BUNDLE.cases)` and `MODULE_WORKFLOW_EXPECTED_OPERATION_HELPER_COUNTS == Counter((case.operation, case.helper) for case in MODULE_WORKFLOW_BUNDLE.cases)` already hold in the current checkout;
  - `MATCH_BEHAVIOR_EXPECTED_PATTERNS == frozenset(case_pattern(case) for case in MATCH_BEHAVIOR_BUNDLE.cases)` and `MATCH_BEHAVIOR_EXPECTED_OPERATION_HELPER_COUNTS == Counter((case.operation, case.helper) for case in MATCH_BEHAVIOR_BUNDLE.cases)` already hold in the current checkout;
  - `collection_replacement_workflows.py` is intentionally out of scope here because its owner manifest currently contains 15 cases while `COLLECTION_TARGET_FIXTURE_CASE_IDS` intentionally selects only 8 published collection rows, so that subset bundle is not a redundant full-manifest mirror yet.
- Baseline verification is green in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` passed (`658 passed, 1 skipped in 0.51s`);
  - the task-local full-manifest bundle probe from Acceptance passed (`ok`);
  - `bash -lc "! rg -n '^(MODULE_WORKFLOW_EXPECTED_CASE_IDS|MODULE_WORKFLOW_EXPECTED_PATTERNS|MODULE_WORKFLOW_EXPECTED_OPERATION_HELPER_COUNTS|MATCH_BEHAVIOR_EXPECTED_CASE_IDS|MATCH_BEHAVIOR_EXPECTED_PATTERNS|MATCH_BEHAVIOR_EXPECTED_OPERATION_HELPER_COUNTS|SELECTED_CASE_BUNDLE_SPECS) =' tests/python/test_module_workflow_parity_suite.py"` currently fails exactly on this cleanup because those seven sidecars still exist.

## Completion
- 2026-03-20: Removed `MODULE_WORKFLOW_EXPECTED_CASE_IDS`, `MODULE_WORKFLOW_EXPECTED_PATTERNS`, `MODULE_WORKFLOW_EXPECTED_OPERATION_HELPER_COUNTS`, `MATCH_BEHAVIOR_EXPECTED_CASE_IDS`, `MATCH_BEHAVIOR_EXPECTED_PATTERNS`, `MATCH_BEHAVIOR_EXPECTED_OPERATION_HELPER_COUNTS`, and `SELECTED_CASE_BUNDLE_SPECS` from `tests/python/test_module_workflow_parity_suite.py`.
- Replaced the handwritten `FixtureBundleSpec(...)` mirrors for `module_workflow_surface.py` and `match_behavior_smoke.py` with a direct full-manifest load through `load_published_fixture_bundles(...)`, keeping the owner load order fixed as `module_workflow_surface.py` then `match_behavior_smoke.py` and validating the resolved manifest ids at import time.
- Added one tiny file-local `_published_case_ids(...)` helper and updated the affected parity/frontier assertions to derive ordered case ids directly from the loaded bundles instead of from detached mirrored tuples.
- Kept the compile-only and collection/replacement subset selectors unchanged; only the two redundant full-manifest owner bundles moved to the canonical full-manifest load path.
- Verification passed with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` (`658 passed, 1 skipped in 0.74s`), the task-local full-manifest bundle probe from Acceptance (`ok`), and `bash -lc "! rg -n '^(MODULE_WORKFLOW_EXPECTED_CASE_IDS|MODULE_WORKFLOW_EXPECTED_PATTERNS|MODULE_WORKFLOW_EXPECTED_OPERATION_HELPER_COUNTS|MATCH_BEHAVIOR_EXPECTED_CASE_IDS|MATCH_BEHAVIOR_EXPECTED_PATTERNS|MATCH_BEHAVIOR_EXPECTED_OPERATION_HELPER_COUNTS|SELECTED_CASE_BUNDLE_SPECS) =' tests/python/test_module_workflow_parity_suite.py"` (passes with no matches).
