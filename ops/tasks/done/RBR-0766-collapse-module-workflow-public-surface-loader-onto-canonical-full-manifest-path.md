# RBR-0766: Collapse module-workflow public-surface loader onto canonical full-manifest path

Status: done
Owner: architecture-implementation
Created: 2026-03-20
Completed: 2026-03-20

## Goal
- Remove the remaining bespoke public-surface full-manifest loader from `tests/python/test_module_workflow_parity_suite.py`; `_load_public_surface_bundle(...)` currently reimplements manifest loading and `FixtureBundle` construction for three full public-surface owners even though the suite already has a shared `load_published_fixture_bundles(...)` path for exact full-manifest bundles.
- Make the canonical published-fixture load path the single source of truth for those three public-surface bundles while preserving the public-surface-specific bundle contract that uses case ids as the contract token.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` stops defining or calling the bespoke full-manifest loader:
  - remove `_load_public_surface_bundle(...)`;
  - stop importing or calling `load_fixture_manifest(...)` directly from this file.
- `PUBLIC_SURFACE_BUNDLES` loads the three public-surface owners through `load_published_fixture_bundles(...)` or one tiny file-local wrapper over its returned bundles:
  - preserve bundle load order exactly as `public_api_surface.py`, `exported_symbol_surface.py`, `pattern_object_surface.py`;
  - preserve manifest-id resolution exactly as `public-api-surface`, `exported-symbol-surface`, `pattern-object-surface`;
  - keep `PUBLIC_API_BUNDLE`, `EXPORTED_SYMBOL_BUNDLE`, and `PATTERN_OBJECT_BUNDLE` resolved through `published_fixture_bundle_by_manifest_id(...)`.
- Preserve the current public-surface bundle contract after the cleanup, but derive it from the already-loaded rows instead of from a bespoke manifest loader:
  - for each bundle, `tuple(case.case_id for case in bundle.cases)` stays equal to `tuple(case.case_id for case in bundle.manifest.cases)`;
  - for each bundle, `expected_patterns` stays `frozenset(case.case_id for case in bundle.cases)`;
  - for each bundle, `expected_operation_helper_counts` stays `Counter((case.operation, case.helper) for case in bundle.cases)`;
  - for each bundle, `expected_case_ids` stays `frozenset(case.case_id for case in bundle.cases)`;
  - `PATTERN_OBJECT_BUNDLE.expected_text_models` stays `frozenset({"bytes", "str"})`;
  - do not reintroduce detached case-id tuples, detached `Counter(...)` tables, or another one-off manifest loader for these three bundles.
- Keep the public-surface owner path behavior unchanged:
  - do not change `PUBLIC_HELPER_CASES`, `PUBLIC_MODULE_CALL_CASES`, `EXPORTED_METADATA_CASES`, `EXPORTED_VALUE_CASES`, `EXPORTED_CONSTRUCTOR_GUARD_CASES`, `PATTERN_METADATA_CASES`, `PATTERN_CALL_CASES`, `ADDITIONAL_PUBLIC_HELPER_NAMES`, `PRIMARY_FLAG_EXPORTS`, `FLAG_ALIAS_PAIRS`, or `NON_INSTANTIABLE_EXPORTS`;
  - do not change `tests/conformance/fixtures/public_api_surface.py`, `tests/conformance/fixtures/exported_symbol_surface.py`, `tests/conformance/fixtures/pattern_object_surface.py`, collection/replacement coverage, keyword-helper coverage, fake-native-boundary coverage, correctness reports, benchmarks, README copy, or tracked project-state prose.
- Keep scope structural only:
  - prefer the existing shared full-manifest loader plus one tiny file-local contract-adjustment helper if needed;
  - do not broaden this cleanup into `tests/python/fixture_parity_support.py`, another shared abstraction pass, or another parity-suite rewrite.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from collections import Counter
import tests.python.test_module_workflow_parity_suite as mod

assert tuple(bundle.manifest.path.name for bundle in mod.PUBLIC_SURFACE_BUNDLES) == (
    "public_api_surface.py",
    "exported_symbol_surface.py",
    "pattern_object_surface.py",
)
assert tuple(bundle.manifest.manifest_id for bundle in mod.PUBLIC_SURFACE_BUNDLES) == (
    "public-api-surface",
    "exported-symbol-surface",
    "pattern-object-surface",
)
for bundle in mod.PUBLIC_SURFACE_BUNDLES:
    assert tuple(case.case_id for case in bundle.cases) == tuple(
        case.case_id for case in bundle.manifest.cases
    )
    assert bundle.expected_patterns == frozenset(case.case_id for case in bundle.cases)
    assert bundle.expected_operation_helper_counts == Counter(
        (case.operation, case.helper) for case in bundle.cases
    )
    assert bundle.expected_case_ids == frozenset(case.case_id for case in bundle.cases)
assert mod.PATTERN_OBJECT_BUNDLE.expected_text_models == frozenset({"bytes", "str"})
print("ok")
PY`
  - `bash -lc "! rg -n '^(def _load_public_surface_bundle)|load_fixture_manifest\\(' tests/python/test_module_workflow_parity_suite.py"`

## Constraints
- Keep this cleanup limited to `tests/python/test_module_workflow_parity_suite.py`.
- Do not turn this into a collection-subset rewrite, a public-surface fixture rewrite, or a shared loader API expansion.

## Notes
- `RBR-0766` is the next available task id in the current checkout:
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
PY` reported the existing tail through `RBR-0765`, no reserved missing tail ids, and `next_free RBR-0766`.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`;
  - `ops/tasks/blocked/` is empty in the current checkout; and
  - the last cycle completed both `RBR-0764` and `RBR-0765` cleanly, so there is no inherited-dirty or post-commit churn bottleneck to yield to.
- JSON burn-down remains complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- This cleanup is concrete and currently viable in the live checkout:
  - `tests/python/test_module_workflow_parity_suite.py` is the only remaining file that directly calls `load_fixture_manifest(...)` to hand-build public-surface `FixtureBundle` objects;
  - `load_published_fixture_bundles(...)` already loads `public_api_surface.py`, `exported_symbol_surface.py`, and `pattern_object_surface.py` in the required order with the required manifest ids;
  - the current public-surface bundle contract already derives entirely from loaded rows:
    - ordered case ids already equal manifest order for all three bundles;
    - `expected_patterns` already equals `frozenset(case.case_id for case in bundle.cases)` for all three bundles;
    - `expected_operation_helper_counts` already equals `Counter((case.operation, case.helper) for case in bundle.cases)` for all three bundles; and
    - `expected_case_ids` already equals `frozenset(case.case_id for case in bundle.cases)` for all three bundles;
  - the collection subset remains intentionally out of scope because `collection_replacement_workflows.py` still carries 15 published rows while `COLLECTION_TARGET_FIXTURE_CASE_IDS` intentionally selects only 8 of them.
- Baseline verification is green in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` passed (`677 passed, 1 skipped in 0.53s`);
  - the task-local public-surface bundle probe from Acceptance passed (`ok`);
  - `bash -lc "! rg -n '^(def _load_public_surface_bundle)|load_fixture_manifest\\(' tests/python/test_module_workflow_parity_suite.py"` currently fails exactly on this cleanup because the bespoke helper and direct manifest load still exist.

## Completion
- 2026-03-20: Removed the bespoke `_load_public_surface_bundle(...)` path and the direct `load_fixture_manifest(...)` import/call from `tests/python/test_module_workflow_parity_suite.py`.
- Routed the three public-surface owners through `load_published_fixture_bundles(...)`, using a tiny file-local case-id fallback only during that call because some public-surface rows have no pattern payload, then reapplied the file-local case-id contract on the returned bundles so `PUBLIC_API_BUNDLE`, `EXPORTED_SYMBOL_BUNDLE`, and `PATTERN_OBJECT_BUNDLE` still resolve through `published_fixture_bundle_by_manifest_id(...)`.
- Preserved the public-surface-specific contract derived from loaded rows: ordered case ids still match manifest order, `expected_patterns`/`expected_operation_helper_counts`/`expected_case_ids` still derive from `bundle.cases`, and `PATTERN_OBJECT_BUNDLE.expected_text_models` stays `frozenset({"bytes", "str"})`.
- Verification passed with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` (`677 passed, 1 skipped in 0.77s`), the task-local public-surface bundle probe from Acceptance (`ok`), and `bash -lc "! rg -n '^(def _load_public_surface_bundle)|load_fixture_manifest\\(' tests/python/test_module_workflow_parity_suite.py"` (passes with no matches).
