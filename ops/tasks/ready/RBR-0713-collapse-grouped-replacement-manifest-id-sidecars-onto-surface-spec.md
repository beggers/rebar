# RBR-0713: Collapse grouped-replacement manifest-id sidecars onto the surface spec

Status: ready
Owner: architecture-implementation
Created: 2026-03-19

## Goal
- Remove the detached grouped-replacement manifest-id tables from `tests/python/test_fixture_backed_replacement_parity_suite.py` so the grouped replacement parity owner keeps one canonical `ReplacementSurfaceSpec` definition for bundle order and match/template-expand manifest routing.

## Deliverables
- `tests/python/test_fixture_backed_replacement_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_fixture_backed_replacement_parity_suite.py` stops defining these detached grouped-replacement manifest-id sidecars:
  - delete `GROUPED_REPLACEMENT_BUNDLE_MANIFEST_IDS`;
  - delete `GROUPED_REPLACEMENT_MATCH_GROUP_ACCESS_MANIFEST_IDS`; and
  - delete `GROUPED_REPLACEMENT_TEMPLATE_EXPAND_MANIFEST_IDS`.
- The grouped-replacement surface definition becomes the sole owner for that metadata instead of the deleted constants:
  - the `ReplacementSurfaceSpec` with `id=GROUPED_REPLACEMENT_TEMPLATE_SURFACE_ID` no longer reads the deleted constants for `match_group_access_manifest_ids` or `template_expand_manifest_ids`;
  - `test_grouped_replacement_surface_keeps_selected_bundle_ownership_explicit` no longer reads `GROUPED_REPLACEMENT_BUNDLE_MANIFEST_IDS`; and
  - if a tiny file-local helper is useful, keep it surface/spec-driven instead of introducing another detached tuple, set, or registry block.
- Preserve the current grouped-replacement routing contract exactly:
  - the grouped-replacement bundle order stays exactly `collection-replacement-workflows`, `named-group-replacement-workflows`, `grouped-alternation-replacement-workflows`, `nested-group-replacement-workflows`, `nested-group-alternation-replacement-workflows`, `quantified-nested-group-replacement-workflows`, `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-replacement-workflows`;
  - the grouped-replacement `match_group_access_manifest_ids` stays exactly `named-group-replacement-workflows`;
  - the grouped-replacement `template_expand_manifest_ids` stays exactly `collection-replacement-workflows`, `named-group-replacement-workflows`, `grouped-alternation-replacement-workflows`, `nested-group-replacement-workflows`, `nested-group-alternation-replacement-workflows`, `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-replacement-workflows`; and
  - `GROUPED_REPLACEMENT_TEMPLATE_SURFACE`, `MATCH_GROUP_ACCESS_CASE_PARAMS`, and `TEMPLATE_EXPAND_CASE_PARAMS` keep the same effective bundle membership, case routing, and ordering as today.
- Keep canonical grouped-replacement ownership otherwise unchanged:
  - do not change `GROUPED_REPLACEMENT_BUNDLE_CONTRACT_MANIFEST_IDS`, `GROUPED_REPLACEMENT_COMPILE_PATTERNS`, `GROUPED_REPLACEMENT_COLLECTION_CASE_IDS`, `GROUPED_REPLACEMENT_NAMED_CASE_IDS`, `GROUPED_REPLACEMENT_SUPPLEMENTAL_NO_MATCH_CASES`, `GROUPED_REPLACEMENT_SUPPLEMENTAL_REPEATED_CASES`, `GROUPED_REPLACEMENT_TEMPLATE_SURFACE`, or the replacement parity surface they represent; and
  - do not broaden into the open-ended or conditional replacement surfaces in this task.
- Keep scope structural only:
  - do not edit `tests/python/fixture_parity_support.py`, correctness fixture modules under `tests/conformance/fixtures/`, `python/rebar_harness/correctness.py`, published reports, or tracked project-state prose.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path

source = Path("tests/python/test_fixture_backed_replacement_parity_suite.py").read_text(
    encoding="utf-8"
)
for needle in (
    "GROUPED_REPLACEMENT_BUNDLE_MANIFEST_IDS = (",
    "GROUPED_REPLACEMENT_MATCH_GROUP_ACCESS_MANIFEST_IDS = (",
    "GROUPED_REPLACEMENT_TEMPLATE_EXPAND_MANIFEST_IDS = (",
):
    assert needle not in source, needle
print("ok")
PY`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
import tests.python.test_fixture_backed_replacement_parity_suite as mod

surface = mod.GROUPED_REPLACEMENT_TEMPLATE_SURFACE
assert tuple(bundle.expected_manifest_id for bundle in surface.bundles) == (
    "collection-replacement-workflows",
    "named-group-replacement-workflows",
    "grouped-alternation-replacement-workflows",
    "nested-group-replacement-workflows",
    "nested-group-alternation-replacement-workflows",
    "quantified-nested-group-replacement-workflows",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-replacement-workflows",
)
assert surface.spec.match_group_access_manifest_ids == (
    "named-group-replacement-workflows",
)
assert surface.spec.template_expand_manifest_ids == (
    "collection-replacement-workflows",
    "named-group-replacement-workflows",
    "grouped-alternation-replacement-workflows",
    "nested-group-replacement-workflows",
    "nested-group-alternation-replacement-workflows",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-replacement-workflows",
)
print("ok")
PY`
  - `bash -lc "! rg -n 'GROUPED_REPLACEMENT_(BUNDLE_MANIFEST_IDS|MATCH_GROUP_ACCESS_MANIFEST_IDS|TEMPLATE_EXPAND_MANIFEST_IDS)' tests/python/test_fixture_backed_replacement_parity_suite.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete one more parallel manifest-id owner layer inside the grouped replacement parity owner, not to reinterpret replacement semantics, alter which manifest rows drive template expansion or match-group-access coverage, or broaden the surface beyond the current published slice.
- Prefer the existing grouped-replacement `ReplacementSurfaceSpec` and file-local assertions over another detached top-level manifest-id table or another support abstraction.

## Notes
- `RBR-0713` is the next available architecture-task id in the current checkout:
  - `python3 - <<'PY'
import pathlib, re
existing = set()
for base in ['ops/tasks/ready', 'ops/tasks/in_progress', 'ops/tasks/done', 'ops/tasks/blocked']:
    for path in pathlib.Path(base).glob('RBR-*.md'):
        m = re.match(r'(RBR-\\d+[A-Z]?)', path.name)
        if m:
            existing.add(m.group(1))
text = '\\n'.join(
    pathlib.Path(p).read_text(encoding='utf-8')
    for p in ['ops/state/backlog.md', 'ops/state/current_status.md']
)
mentioned = set(re.findall(r'RBR-\\d+[A-Z]?', text))
reserved = sorted(mentioned - existing, key=lambda s: (int(re.search(r'\\d+', s).group()), s))
existing_sorted = sorted(existing, key=lambda s: (int(re.search(r'\\d+', s).group()), s))
print('highest_existing_tail:', existing_sorted[-20:])
print('reserved_missing_tail:', reserved[-20:])
PY` reported the highest existing tail as `RBR-0693` through `RBR-0712` and no reserved missing tail ids.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The grouped-replacement manifest-id sidecars are concrete and bounded in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py` currently passes (`1149 passed in 0.85s`);
  - `rg -n "GROUPED_REPLACEMENT_BUNDLE_MANIFEST_IDS|GROUPED_REPLACEMENT_MATCH_GROUP_ACCESS_MANIFEST_IDS|GROUPED_REPLACEMENT_TEMPLATE_EXPAND_MANIFEST_IDS" tests/python/test_fixture_backed_replacement_parity_suite.py` shows the three constants are declared once and consumed only by the grouped-replacement surface spec literal plus one grouped-surface ownership test in the same file;
  - the inline source probe in Acceptance currently fails exactly on this cleanup with `AssertionError: GROUPED_REPLACEMENT_BUNDLE_MANIFEST_IDS = (`; and
  - the final `rg` absence check in Acceptance currently fails exactly on this cleanup because all three constants still exist.
- This simplification matches the current replacement-harness information flow:
  - `ReplacementSurfaceSpec` already owns the grouped-replacement bundle specs, compile pattern expectations, supplemental replacement cases, pending-bytes follow-on behavior, and the match/template-expand manifest-id fields that currently point at the detached constants; and
  - deleting the extra top-level manifest-id tables removes one more parallel owner layer without changing the published replacement parity surface.
