# RBR-0768: Replace public-surface loader monkeypatch with explicit pattern extractor

Status: ready
Owner: architecture-implementation
Created: 2026-03-20

## Goal
- Remove the remaining shared-state mutation from `tests/python/test_module_workflow_parity_suite.py`; `_published_public_surface_bundles()` currently rebinds `tests.python.fixture_parity_support.case_pattern` just to make `load_published_fixture_bundles(...)` derive case-id-based contract tokens for the three public-surface owner manifests.
- Make the shared full-manifest bundle loader accept an explicit extractor for `expected_patterns` so the public-surface suite can declare its case-id contract without monkeypatching shared module state, while preserving the existing default case-pattern contract for every other caller.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/fixture_parity_support.py` exposes an explicit full-manifest loader hook instead of relying on global rebinding:
  - `load_published_fixture_bundles(...)` accepts a keyword-only optional `pattern_extractor` callable that defaults to the existing `case_pattern`;
  - the default path keeps the current behavior for ordinary pattern-backed manifests, including bundle order, `expected_patterns`, `expected_operation_helper_counts`, and `expected_text_models`;
  - keep scope narrow: do not broaden this cleanup into `load_fixture_bundles(...)`, `FixtureBundleSpec`, or another fixture-loader rewrite unless a tiny compatibility edit is strictly required to keep the focused tests green.
- `tests/python/test_module_workflow_parity_suite.py` stops monkeypatching `fixture_parity_support.case_pattern`:
  - `_published_public_surface_bundles()` passes `pattern_extractor=_public_surface_loader_token` directly to `load_published_fixture_bundles(...)`;
  - remove the `original_case_pattern = fixture_parity_support.case_pattern` save/restore block and the temporary `fixture_parity_support.case_pattern = _public_surface_loader_token` rebinding;
  - stop importing `tests.python.fixture_parity_support as fixture_parity_support` if that import becomes unnecessary after the cleanup.
- Preserve the current public-surface owner contract exactly after the cleanup:
  - `PUBLIC_SURFACE_BUNDLES` still load in the order `public_api_surface.py`, `exported_symbol_surface.py`, `pattern_object_surface.py`;
  - their manifest ids still resolve as `public-api-surface`, `exported-symbol-surface`, `pattern-object-surface`;
  - `PUBLIC_API_BUNDLE`, `EXPORTED_SYMBOL_BUNDLE`, and `PATTERN_OBJECT_BUNDLE` still resolve through `published_fixture_bundle_by_manifest_id(...)`;
  - for each public-surface bundle, `expected_patterns` stays `frozenset(case.case_id for case in bundle.cases)`;
  - for each public-surface bundle, `expected_operation_helper_counts` stays `Counter((case.operation, case.helper) for case in bundle.cases)`;
  - for each public-surface bundle, `expected_case_ids` stays `frozenset(case.case_id for case in bundle.cases)`;
  - `PATTERN_OBJECT_BUNDLE.expected_text_models` stays `frozenset({"bytes", "str"})`.
- `tests/python/test_fixture_parity_support_contract.py` covers the new loader boundary explicitly:
  - keep the existing default `load_published_fixture_bundles(...)` contract coverage intact;
  - add one focused contract test that uses existing temp-path fixture modules and proves a custom `pattern_extractor` changes only `expected_patterns`, not manifest order, loaded cases, operation/helper counts, or text-model expectations;
  - do not add new tracked fixture files for this cleanup.
- Keep scope structural only:
  - do not change fixture modules under `tests/conformance/fixtures/`, correctness or benchmark harness behavior, reports, README copy, or tracked project-state prose;
  - do not broaden this into another public-surface contract rewrite or another shared abstraction pass beyond the explicit extractor hook.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/python/test_fixture_parity_support_contract.py -k 'published_fixture_bundles or public_surface or module_workflow'`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from collections import Counter
from rebar_harness.correctness import CORRECTNESS_FIXTURES_ROOT
from tests.python.fixture_parity_support import load_published_fixture_bundles

(bundle,) = load_published_fixture_bundles(
    (CORRECTNESS_FIXTURES_ROOT / "public_api_surface.py",),
    pattern_extractor=lambda case: case.case_id,
)
assert bundle.expected_patterns == frozenset(case.case_id for case in bundle.cases)
assert bundle.expected_operation_helper_counts == Counter(
    (case.operation, case.helper) for case in bundle.cases
)
assert bundle.expected_text_models == frozenset({"str"})
print("ok")
PY`
  - `bash -lc "! rg -n 'fixture_parity_support\\.case_pattern = _public_surface_loader_token|original_case_pattern = fixture_parity_support\\.case_pattern' tests/python/test_module_workflow_parity_suite.py"`

## Constraints
- Keep this cleanup limited to the shared published-bundle loader contract plus the one parity suite that currently monkeypatches shared loader state.
- Prefer deleting the monkeypatch and threading one explicit callable parameter over adding another wrapper layer or another bespoke public-surface loader.

## Notes
- `RBR-0768` is the next available task id in the current checkout:
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
PY` reported the existing tail through `RBR-0767`, no reserved missing tail ids, and `next_free RBR-0768`.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/blocked/`, `ops/tasks/ready/`, and `ops/tasks/in_progress/` are empty in the current checkout;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the last cycle completed both `RBR-0766` and `RBR-0767` cleanly, so there is no inherited-dirty or post-task refresh bottleneck to yield to.
- JSON burn-down remains complete and non-stale in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- This cleanup is concrete and currently viable in the live checkout:
  - `tests/python/test_module_workflow_parity_suite.py` still contains the only remaining direct rebinding of `fixture_parity_support.case_pattern`;
  - `load_published_fixture_bundles(...)` is already the canonical full-manifest path for the public-surface owners, so this cleanup can remove the monkeypatch without inventing another loader;
  - the current public-surface contract probe is green:
    - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from collections import Counter
import tests.python.test_module_workflow_parity_suite as mod

assert tuple(bundle.manifest.path.name for bundle in mod.PUBLIC_SURFACE_BUNDLES) == (
    'public_api_surface.py',
    'exported_symbol_surface.py',
    'pattern_object_surface.py',
)
assert tuple(bundle.manifest.manifest_id for bundle in mod.PUBLIC_SURFACE_BUNDLES) == (
    'public-api-surface',
    'exported-symbol-surface',
    'pattern-object-surface',
)
for bundle in mod.PUBLIC_SURFACE_BUNDLES:
    assert bundle.expected_patterns == frozenset(case.case_id for case in bundle.cases)
    assert bundle.expected_operation_helper_counts == Counter(
        (case.operation, case.helper) for case in bundle.cases
    )
    assert bundle.expected_case_ids == frozenset(case.case_id for case in bundle.cases)
assert mod.PATTERN_OBJECT_BUNDLE.expected_text_models == frozenset({'bytes', 'str'})
print('ok')
PY` passed (`ok`);
  - the focused baseline test command is green:
    - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/python/test_fixture_parity_support_contract.py -k 'published_fixture_bundles or public_surface or module_workflow'` passed (`678 passed, 1 skipped, 243 deselected in 0.58s`);
  - the current monkeypatch probe fails exactly on this cleanup boundary:
    - `bash -lc "rg -n 'fixture_parity_support\\.case_pattern = _public_surface_loader_token|original_case_pattern = fixture_parity_support\\.case_pattern' tests/python/test_module_workflow_parity_suite.py"` reports the two rebinding lines; and
  - the proposed explicit extractor probe currently fails for the exact missing hook this task adds:
    - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from collections import Counter
from rebar_harness.correctness import CORRECTNESS_FIXTURES_ROOT
from tests.python.fixture_parity_support import load_published_fixture_bundles

(bundle,) = load_published_fixture_bundles(
    (CORRECTNESS_FIXTURES_ROOT / 'public_api_surface.py',),
    pattern_extractor=lambda case: case.case_id,
)
assert bundle.expected_patterns == frozenset(case.case_id for case in bundle.cases)
assert bundle.expected_operation_helper_counts == Counter(
    (case.operation, case.helper) for case in bundle.cases
)
assert bundle.expected_text_models == frozenset({'str'})
print('ok')
PY` currently raises `TypeError: load_published_fixture_bundles() got an unexpected keyword argument 'pattern_extractor'`.
