# RBR-0760: Collapse module-workflow public-surface bundle-spec sidecars onto full-manifest owners

Status: done
Owner: architecture-implementation
Created: 2026-03-20
Completed: 2026-03-20

## Goal
- Remove the remaining public-surface bundle-spec sidecars from `tests/python/test_module_workflow_parity_suite.py`; the suite currently repeats the same three full public-surface manifests as detached case-id tuples, a detached `PUBLIC_SURFACE_BUNDLE_SPECS` table, and one aggregate `PUBLIC_SURFACE_SELECTED_CASE_IDS` tuple even though each public-surface owner already maps 1:1 to its full fixture manifest.
- Make the loaded full manifest rows the sole source of truth for the public-surface owner path inside the module-workflow parity suite.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` stops defining or reading these detached public-surface sidecars:
  - `PUBLIC_API_CASE_IDS`
  - `EXPORTED_SYMBOL_CASE_IDS`
  - `PATTERN_OBJECT_CASE_IDS`
  - `PUBLIC_SURFACE_BUNDLE_SPECS`
  - `PUBLIC_SURFACE_SELECTED_CASE_IDS`
- `PUBLIC_SURFACE_BUNDLES` loads the three public-surface fixtures as full-manifest owners instead of selecting rows through case-id sidecars:
  - preserve bundle order exactly as `public_api_surface.py`, `exported_symbol_surface.py`, `pattern_object_surface.py`;
  - preserve manifest-id resolution exactly through `PUBLIC_API_BUNDLE`, `EXPORTED_SYMBOL_BUNDLE`, and `PATTERN_OBJECT_BUNDLE`;
  - preserve the same case order inside each bundle:
    - `PUBLIC_API_BUNDLE.cases` stays:
      - `helper-compile-present`
      - `helper-search-present`
      - `helper-purge-present`
      - `purge-noop-success`
      - `compile-pattern-scaffold-success`
      - `search-literal-success`
      - `escape-success`
    - `EXPORTED_SYMBOL_BUNDLE.cases` stays:
      - `regexflag-type-metadata`
      - `error-type-metadata`
      - `pattern-type-metadata`
      - `match-type-metadata`
      - `ascii-constant-value`
      - `ignorecase-constant-value`
      - `noflag-constant-value`
      - `debug-constant-value`
      - `pattern-constructor-guard`
      - `match-constructor-guard`
    - `PATTERN_OBJECT_BUNDLE.cases` stays:
      - `pattern-object-str-metadata`
      - `pattern-object-str-ignorecase-metadata`
      - `pattern-object-bytes-ignorecase-metadata`
      - `pattern-search-literal-success`
      - `pattern-match-literal-success`
      - `pattern-fullmatch-literal-success`
- Derive the public-surface bundle contracts directly from those loaded full-manifest rows instead of from mirrored sidecars:
  - `expected_case_ids` stays exact for each public-surface bundle, but it must come from the loaded rows rather than from a detached case-id tuple;
  - `expected_patterns` stays the case-id token set for each public-surface bundle because `test_public_surface_parity_suite_stays_aligned_with_published_fixtures` still uses `_public_surface_case_contract_token(...)`, but it must be derived from the loaded rows rather than from a mirrored top-level frozenset;
  - `expected_operation_helper_counts` stays equal to `Counter((case.operation, case.helper) for case in bundle.cases)` for each public-surface bundle and must be derived from the loaded rows rather than from handwritten `Counter(...)` blocks;
  - keep the mixed text-model contract explicit for `PATTERN_OBJECT_BUNDLE` so the bundle still records both `str` and `bytes` coverage after the cleanup.
- `test_public_surface_direct_test_buckets_cover_selected_frontier` stops reading the deleted aggregate tuple:
  - derive the selected frontier directly from `PUBLIC_SURFACE_BUNDLES` or one tiny helper over their loaded cases instead of from `PUBLIC_SURFACE_SELECTED_CASE_IDS`;
  - preserve the exact current selected-frontier order across the three public-surface owners:
    - `helper-compile-present`
    - `helper-search-present`
    - `helper-purge-present`
    - `purge-noop-success`
    - `compile-pattern-scaffold-success`
    - `search-literal-success`
    - `escape-success`
    - `regexflag-type-metadata`
    - `error-type-metadata`
    - `pattern-type-metadata`
    - `match-type-metadata`
    - `ascii-constant-value`
    - `ignorecase-constant-value`
    - `noflag-constant-value`
    - `debug-constant-value`
    - `pattern-constructor-guard`
    - `match-constructor-guard`
    - `pattern-object-str-metadata`
    - `pattern-object-str-ignorecase-metadata`
    - `pattern-object-bytes-ignorecase-metadata`
    - `pattern-search-literal-success`
    - `pattern-match-literal-success`
    - `pattern-fullmatch-literal-success`
- Keep the remaining owner-local coverage unchanged:
  - do not change `PUBLIC_HELPER_CASES`, `PUBLIC_MODULE_CALL_CASES`, `EXPORTED_METADATA_CASES`, `EXPORTED_VALUE_CASES`, `EXPORTED_CONSTRUCTOR_GUARD_CASES`, `PATTERN_METADATA_CASES`, `PATTERN_CALL_CASES`, `ADDITIONAL_PUBLIC_HELPER_NAMES`, `PRIMARY_FLAG_EXPORTS`, `FLAG_ALIAS_PAIRS`, `NON_INSTANTIABLE_EXPORTS`, module-workflow coverage, collection/replacement coverage, keyword-argument coverage, fake-native-boundary coverage, or direct-test bucket accounting outside this sidecar cleanup;
  - do not change the public-surface fixture files under `tests/conformance/fixtures/`, correctness reports, benchmark files, README copy, or tracked project-state prose.
- Keep scope structural only:
  - prefer one tiny file-local helper if useful;
  - do not broaden this run into `tests/python/fixture_parity_support.py`, `python/rebar_harness/correctness.py`, or another shared support-layer rewrite.
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
assert tuple(case.case_id for case in mod.PUBLIC_API_BUNDLE.cases) == (
    "helper-compile-present",
    "helper-search-present",
    "helper-purge-present",
    "purge-noop-success",
    "compile-pattern-scaffold-success",
    "search-literal-success",
    "escape-success",
)
assert mod.PUBLIC_API_BUNDLE.expected_patterns == frozenset(
    case.case_id for case in mod.PUBLIC_API_BUNDLE.cases
)
assert mod.PUBLIC_API_BUNDLE.expected_operation_helper_counts == Counter(
    (case.operation, case.helper) for case in mod.PUBLIC_API_BUNDLE.cases
)
assert tuple(case.case_id for case in mod.EXPORTED_SYMBOL_BUNDLE.cases) == (
    "regexflag-type-metadata",
    "error-type-metadata",
    "pattern-type-metadata",
    "match-type-metadata",
    "ascii-constant-value",
    "ignorecase-constant-value",
    "noflag-constant-value",
    "debug-constant-value",
    "pattern-constructor-guard",
    "match-constructor-guard",
)
assert mod.EXPORTED_SYMBOL_BUNDLE.expected_patterns == frozenset(
    case.case_id for case in mod.EXPORTED_SYMBOL_BUNDLE.cases
)
assert mod.EXPORTED_SYMBOL_BUNDLE.expected_operation_helper_counts == Counter(
    (case.operation, case.helper) for case in mod.EXPORTED_SYMBOL_BUNDLE.cases
)
assert tuple(case.case_id for case in mod.PATTERN_OBJECT_BUNDLE.cases) == (
    "pattern-object-str-metadata",
    "pattern-object-str-ignorecase-metadata",
    "pattern-object-bytes-ignorecase-metadata",
    "pattern-search-literal-success",
    "pattern-match-literal-success",
    "pattern-fullmatch-literal-success",
)
assert mod.PATTERN_OBJECT_BUNDLE.expected_patterns == frozenset(
    case.case_id for case in mod.PATTERN_OBJECT_BUNDLE.cases
)
assert mod.PATTERN_OBJECT_BUNDLE.expected_operation_helper_counts == Counter(
    (case.operation, case.helper) for case in mod.PATTERN_OBJECT_BUNDLE.cases
)
assert tuple(
    case.case_id for bundle in mod.PUBLIC_SURFACE_BUNDLES for case in bundle.cases
) == (
    "helper-compile-present",
    "helper-search-present",
    "helper-purge-present",
    "purge-noop-success",
    "compile-pattern-scaffold-success",
    "search-literal-success",
    "escape-success",
    "regexflag-type-metadata",
    "error-type-metadata",
    "pattern-type-metadata",
    "match-type-metadata",
    "ascii-constant-value",
    "ignorecase-constant-value",
    "noflag-constant-value",
    "debug-constant-value",
    "pattern-constructor-guard",
    "match-constructor-guard",
    "pattern-object-str-metadata",
    "pattern-object-str-ignorecase-metadata",
    "pattern-object-bytes-ignorecase-metadata",
    "pattern-search-literal-success",
    "pattern-match-literal-success",
    "pattern-fullmatch-literal-success",
)
print("ok")
PY`
  - `bash -lc "! rg -n '^(PUBLIC_API_CASE_IDS|EXPORTED_SYMBOL_CASE_IDS|PATTERN_OBJECT_CASE_IDS|PUBLIC_SURFACE_BUNDLE_SPECS|PUBLIC_SURFACE_SELECTED_CASE_IDS) =' tests/python/test_module_workflow_parity_suite.py"`

## Constraints
- Keep this cleanup limited to `tests/python/test_module_workflow_parity_suite.py`. Do not use this run to merge public-surface coverage into another suite, rewrite fixture-support helpers, or broaden the module-workflow correctness frontier.
- Prefer deriving the public-surface bundle contracts directly from the loaded full manifest rows over introducing another manifest-id registry, another detached tuple, or another mirrored `Counter(...)` table.

## Notes
- `RBR-0760` is the next available task id in the current checkout:
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
print('highest_existing_tail', existing_sorted[-15:])
print('reserved_tail', reserved_sorted[-25:])
for n in range(int(re.search(r'\d+', existing_sorted[-1]).group()), int(re.search(r'\d+', existing_sorted[-1]).group()) + 200):
    rid = f'RBR-{n:04d}'
    if rid not in existing and rid not in reserved:
        print('next_free', rid)
        break
PY` reported the existing tail through `RBR-0759`, no reserved missing tail ids, and `next_free RBR-0760`.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added; and
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The sidecar layer is concrete and bounded in the current checkout:
  - `tests/conformance/fixtures/public_api_surface.py`, `tests/conformance/fixtures/exported_symbol_surface.py`, and `tests/conformance/fixtures/pattern_object_surface.py` each currently contain exactly the same ordered case ids already mirrored by `PUBLIC_API_CASE_IDS`, `EXPORTED_SYMBOL_CASE_IDS`, and `PATTERN_OBJECT_CASE_IDS`;
  - the task-local probe in Acceptance already passes in the current checkout (`ok`), so the live loaded public-surface bundles already carry enough information to restate the current contract without those mirrored top-level sidecars; and
  - `bash -lc "! rg -n '^(PUBLIC_API_CASE_IDS|EXPORTED_SYMBOL_CASE_IDS|PATTERN_OBJECT_CASE_IDS|PUBLIC_SURFACE_BUNDLE_SPECS|PUBLIC_SURFACE_SELECTED_CASE_IDS) =' tests/python/test_module_workflow_parity_suite.py"` currently fails exactly on this cleanup because those five sidecars still exist.
- Baseline verification is green in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` passed (`657 passed, 1 skipped in 0.52s`);
  - the task-local public-surface bundle probe from Acceptance passed (`ok`).

## Completion
- 2026-03-20: Removed `PUBLIC_API_CASE_IDS`, `EXPORTED_SYMBOL_CASE_IDS`, `PATTERN_OBJECT_CASE_IDS`, `PUBLIC_SURFACE_BUNDLE_SPECS`, and `PUBLIC_SURFACE_SELECTED_CASE_IDS` from `tests/python/test_module_workflow_parity_suite.py`.
- Replaced the detached public-surface sidecar table with full-manifest bundle loading via one file-local helper that derives each bundle's `expected_case_ids`, case-id-token `expected_patterns`, and `expected_operation_helper_counts` from the loaded rows; `PATTERN_OBJECT_BUNDLE` now also carries the explicit mixed `{"bytes", "str"}` text-model contract.
- Kept the public-surface owner order and manifest-id lookups unchanged: `PUBLIC_SURFACE_BUNDLES` still resolves in `public_api_surface.py`, `exported_symbol_surface.py`, then `pattern_object_surface.py`, and each bundle preserves the same ordered case frontier from its fixture.
- Updated `test_public_surface_direct_test_buckets_cover_selected_frontier` to flatten selected case ids directly from `PUBLIC_SURFACE_BUNDLES` instead of reading the deleted aggregate tuple sidecar.
- Verification passed with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` (`657 passed, 1 skipped in 0.72s`), the task-local public-surface bundle probe from Acceptance (`ok`), and `bash -lc "! rg -n '^(PUBLIC_API_CASE_IDS|EXPORTED_SYMBOL_CASE_IDS|PATTERN_OBJECT_CASE_IDS|PUBLIC_SURFACE_BUNDLE_SPECS|PUBLIC_SURFACE_SELECTED_CASE_IDS) =' tests/python/test_module_workflow_parity_suite.py"` (passes with no matches).
