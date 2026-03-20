# RBR-0770: Collapse module-workflow collection subset sidecar onto owner helper partition

Status: ready
Owner: architecture-implementation
Created: 2026-03-20

## Goal
- Remove the remaining selected-case sidecar from `tests/python/test_module_workflow_parity_suite.py`; `COLLECTION_TARGET_FIXTURE_CASE_IDS`, `COLLECTION_REPLACEMENT_UNCOVERED_CASE_IDS`, and `COLLECTION_FIXTURE_BUNDLE = load_fixture_bundles(FixtureBundleSpec(...))` currently hand-partition `collection_replacement_workflows.py` even though the selected eight rows are exactly the manifest-order `split`/`findall`/`finditer` helper partition and the uncovered seven rows are the complementary `sub`/`subn` partition.
- Make the already-published `collection_replacement_workflows.py` owner manifest the sole source of truth for this suite's collection-vs-replacement frontier.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` stops defining or reading these detached collection-sidecar symbols:
  - `COLLECTION_TARGET_FIXTURE_CASE_IDS`
  - `COLLECTION_REPLACEMENT_UNCOVERED_CASE_IDS`
  - `COLLECTION_FIXTURE_BUNDLE`
  - the collection-only `FixtureBundleSpec(...)` / `load_fixture_bundles(...)` call
  - if they become unused after the cleanup, remove the `FixtureBundleSpec` and `load_fixture_bundles` imports from this file as well.
- Load `collection_replacement_workflows.py` through the canonical full-manifest path instead of the selected-case sidecar:
  - define one owner bundle through `load_published_fixture_bundles((CORRECTNESS_FIXTURES_ROOT / "collection_replacement_workflows.py",))` or one equally direct file-local wrapper over that returned full bundle;
  - preserve manifest path `collection_replacement_workflows.py` and manifest id `collection-replacement-workflows`;
  - preserve case order exactly as the published manifest row order.
- Derive the collection/replacement frontier directly from the loaded owner rows rather than from handwritten case-id tuples:
  - the selected collection frontier must be the manifest-order rows whose helpers are `split`, `findall`, or `finditer`;
  - the uncovered frontier must be the manifest-order rows whose helpers are `sub` or `subn`;
  - preserve the exact selected case-id order:
    - `module-split-str-leading-trailing`
    - `module-split-str-no-match`
    - `pattern-split-bytes-maxsplit`
    - `module-findall-bytes-repeated`
    - `pattern-findall-str-no-match`
    - `module-finditer-str-repeated`
    - `pattern-finditer-bytes-bounded`
    - `module-findall-nonliteral-str`
  - preserve the exact uncovered case-id order:
    - `module-sub-str-repeated`
    - `module-subn-bytes-count`
    - `pattern-sub-str-no-match`
    - `pattern-subn-str-count`
    - `module-sub-template-str`
    - `module-sub-callable-str`
    - `module-sub-grouping-template`
- Keep the current published collection surfaces derived from that owner partition:
  - `PUBLISHED_COLLECTION_MODULE_CASES` stays the module-call subsequence of the selected collection frontier, in order:
    - `module-split-str-leading-trailing`
    - `module-split-str-no-match`
    - `module-findall-bytes-repeated`
    - `module-finditer-str-repeated`
    - `module-findall-nonliteral-str`
  - `PUBLISHED_COLLECTION_PATTERN_CASES` stays the pattern-call subsequence of the selected collection frontier, in order:
    - `pattern-split-bytes-maxsplit`
    - `pattern-findall-str-no-match`
    - `pattern-finditer-bytes-bounded`
- Update the collection-alignment/frontier tests to read from the owner bundle and its derived helper partition rather than from the detached selected-case bundle:
  - `test_literal_collection_suite_stays_aligned_with_published_fixture_rows`
  - `test_literal_collection_suite_tracks_published_case_frontier`
  - `test_literal_collection_direct_test_buckets_cover_selected_frontier`
- Keep the rest of the module-workflow collection/replacement coverage unchanged:
  - do not change `MODULE_COLLECTION_CASES`, `PATTERN_COLLECTION_CASES`, `BOUNDED_WILDCARD_MODULE_COLLECTION_CASES`, bounded-wildcard collection tests, literal collection matrix coverage, collection type-error coverage, unsupported-case coverage, replacement coverage, or direct-test bucket accounting outside this sidecar cleanup;
  - do not edit `tests/conformance/fixtures/collection_replacement_workflows.py`, `tests/python/fixture_parity_support.py`, correctness reports, benchmark files, README copy, or tracked project-state prose.
- Keep scope structural only:
  - prefer deleting the detached selected/uncovered tuples and the one-off selected-case bundle over adding another registry layer or another shared fixture helper;
  - if a tiny helper is useful, keep it file-local to `tests/python/test_module_workflow_parity_suite.py`.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from collections import Counter
import tests.python.test_module_workflow_parity_suite as mod

assert mod.COLLECTION_REPLACEMENT_BUNDLE.manifest.path == (
    mod.CORRECTNESS_FIXTURES_ROOT / "collection_replacement_workflows.py"
)
assert mod.COLLECTION_REPLACEMENT_BUNDLE.manifest.manifest_id == (
    "collection-replacement-workflows"
)
assert tuple(case.case_id for case in mod.COLLECTION_REPLACEMENT_BUNDLE.cases) == tuple(
    case.case_id for case in mod.COLLECTION_REPLACEMENT_BUNDLE.manifest.cases
)
assert mod.COLLECTION_REPLACEMENT_BUNDLE.expected_patterns == frozenset(
    mod.case_pattern(case) for case in mod.COLLECTION_REPLACEMENT_BUNDLE.cases
)
assert mod.COLLECTION_REPLACEMENT_BUNDLE.expected_operation_helper_counts == Counter(
    (case.operation, case.helper) for case in mod.COLLECTION_REPLACEMENT_BUNDLE.cases
)
assert tuple(
    case.case_id
    for case in mod.COLLECTION_REPLACEMENT_BUNDLE.cases
    if case.helper in {"split", "findall", "finditer"}
) == (
    "module-split-str-leading-trailing",
    "module-split-str-no-match",
    "pattern-split-bytes-maxsplit",
    "module-findall-bytes-repeated",
    "pattern-findall-str-no-match",
    "module-finditer-str-repeated",
    "pattern-finditer-bytes-bounded",
    "module-findall-nonliteral-str",
)
assert tuple(
    case.case_id
    for case in mod.COLLECTION_REPLACEMENT_BUNDLE.cases
    if case.helper in {"sub", "subn"}
) == (
    "module-sub-str-repeated",
    "module-subn-bytes-count",
    "pattern-sub-str-no-match",
    "pattern-subn-str-count",
    "module-sub-template-str",
    "module-sub-callable-str",
    "module-sub-grouping-template",
)
assert tuple(case.case_id for case in mod.PUBLISHED_COLLECTION_MODULE_CASES) == (
    "module-split-str-leading-trailing",
    "module-split-str-no-match",
    "module-findall-bytes-repeated",
    "module-finditer-str-repeated",
    "module-findall-nonliteral-str",
)
assert tuple(case.case_id for case in mod.PUBLISHED_COLLECTION_PATTERN_CASES) == (
    "pattern-split-bytes-maxsplit",
    "pattern-findall-str-no-match",
    "pattern-finditer-bytes-bounded",
)
print("ok")
PY`
  - `bash -lc "! rg -n '^(COLLECTION_FIXTURE_BUNDLE|COLLECTION_TARGET_FIXTURE_CASE_IDS|COLLECTION_REPLACEMENT_UNCOVERED_CASE_IDS) =|FixtureBundleSpec\\(|load_fixture_bundles\\(' tests/python/test_module_workflow_parity_suite.py"`

## Constraints
- Keep this cleanup limited to `tests/python/test_module_workflow_parity_suite.py`.
- Do not turn this into a shared `FixtureBundleSpec` rewrite, a replacement-parity rewrite, or a broader module-workflow suite refactor.

## Notes
- `RBR-0770` is the next available task id in the current checkout:
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
PY` reported the existing tail through `RBR-0769`, no reserved missing tail ids, and `next_free RBR-0770`.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in the current checkout; and
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`.
- JSON burn-down remains complete and current in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The cleanup is concrete and currently viable in the live checkout:
  - `collection_replacement_workflows.py` currently publishes 15 rows, and the current sidecar partition already matches the owner-manifest helper split exactly:
    - the selected collection rows are the manifest-order `split`/`findall`/`finditer` partition; and
    - the uncovered rows are the manifest-order `sub`/`subn` complement;
  - `tests/python/test_module_workflow_parity_suite.py` is the only file still carrying this detached selected/uncovered case-id layer for the collection owner path; and
  - the file-local sidecar-removal probe currently fails exactly on this cleanup boundary:
    - `bash -lc "! rg -n '^(COLLECTION_FIXTURE_BUNDLE|COLLECTION_TARGET_FIXTURE_CASE_IDS|COLLECTION_REPLACEMENT_UNCOVERED_CASE_IDS) =|FixtureBundleSpec\\(|load_fixture_bundles\\(' tests/python/test_module_workflow_parity_suite.py"` currently reports the sidecar tuple definitions plus the selected-case bundle load.
- Baseline verification is green in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` passed (`677 passed, 1 skipped in 0.52s`);
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from rebar_harness.correctness import CORRECTNESS_FIXTURES_ROOT, load_fixture_manifest
import tests.python.test_module_workflow_parity_suite as mod

manifest = load_fixture_manifest(
    CORRECTNESS_FIXTURES_ROOT / "collection_replacement_workflows.py"
)
collection_case_ids = tuple(
    case.case_id
    for case in manifest.cases
    if case.helper in {"split", "findall", "finditer"}
)
replacement_case_ids = tuple(
    case.case_id
    for case in manifest.cases
    if case.helper in {"sub", "subn"}
)
assert mod.COLLECTION_TARGET_FIXTURE_CASE_IDS == collection_case_ids
assert mod.COLLECTION_REPLACEMENT_UNCOVERED_CASE_IDS == replacement_case_ids
print("ok")
PY` passed (`ok`);
  - the future-state owner-bundle probe in Acceptance currently fails for the exact missing cleanup because `tests/python/test_module_workflow_parity_suite.py` does not yet expose `COLLECTION_REPLACEMENT_BUNDLE`.
