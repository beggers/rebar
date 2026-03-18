# RBR-0604: Collapse the branch-local bytes follow-on parity ladders onto one table

Status: done
Owner: architecture-implementation
Created: 2026-03-18
Completed: 2026-03-18

## Goal
- Replace the duplicated branch-local bytes follow-on test ladders in `tests/python/test_branch_local_backreference_parity_suite.py` with one local definition table plus shared parametrized assertions, so the suite stops repeating the same compile/module/pattern parity checks for the quantified-alternation and quantified-nested-group follow-on pairs.

## Deliverables
- `tests/python/test_branch_local_backreference_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_branch_local_backreference_parity_suite.py` keeps the existing two bytes follow-on case tables and the existing `DIRECT_BYTES_FOLLOW_ON_BUNDLES`, but replaces the current per-manifest duplicate test ladders with one local spec-driven surface. The shared table should own only the metadata that currently differs between the two bytes follow-on families:
  - which bundle/case tuple is under test;
  - the exact expected direct-follow-on case-id bucket label;
  - the expected published module-search texts by pattern; and
  - the expected published pattern-fullmatch texts by pattern.
- Consolidate both duplicated `*_cases_stay_explicit_with_one_direct_follow_on_anchor` tests and both duplicated compile/module/pattern parity ladders into shared parametrized tests without changing behavior:
  - keep the exact case ids, byte patterns, search/fullmatch texts, and manifest ids unchanged;
  - keep the current split where the shared compile/module/pattern buckets continue to exclude the bytes rows and the direct-follow-on buckets continue to own them explicitly;
  - keep the current compile parity, module-search result parity, match-convenience parity, match-group-access parity, and pattern-fullmatch result parity checks intact; and
  - keep the current `rebar` unsupported gating on `QUANTIFIED_NESTED_GROUP_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BYTES_CASES` unchanged, including the `RBR-0603` reason string.
- Keep this cleanup local to the branch-local parity suite:
  - do not widen scope into `tests/python/fixture_parity_support.py`, correctness fixtures, benchmark manifests, reports, Rust code, or `python/rebar/`;
  - do not rename `QUANTIFIED_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BYTES_CASES`, `QUANTIFIED_NESTED_GROUP_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BYTES_CASES`, or `DIRECT_BYTES_FOLLOW_ON_BUNDLES`; and
  - prefer one local spec table plus shared test helpers over another support module, registry layer, or bytes-only suite.
- After the consolidation lands, no per-manifest bytes follow-on test functions remain in the file. This cleanup should remove the current duplicate prefixes rather than moving them behind another named wrapper layer:
  - `def test_quantified_alternation_branch_local_backreference_bytes_...`
  - `def test_quantified_nested_group_alternation_branch_local_backreference_bytes_...`
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from tests.python import test_branch_local_backreference_parity_suite as mod

assert tuple(bundle.manifest.manifest_id for bundle in mod.DIRECT_BYTES_FOLLOW_ON_BUNDLES) == (
    "quantified-alternation-branch-local-backreference-workflows",
    "quantified-nested-group-alternation-branch-local-backreference-workflows",
)
assert tuple(case.id for case in mod.QUANTIFIED_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BYTES_CASES) == (
    "quantified-alternation-branch-local-numbered-bytes",
    "quantified-alternation-branch-local-named-bytes",
)
assert tuple(case.id for case in mod.QUANTIFIED_NESTED_GROUP_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BYTES_CASES) == (
    "quantified-nested-group-alternation-branch-local-numbered-bytes",
    "quantified-nested-group-alternation-branch-local-named-bytes",
)
assert all(
    case.unsupported_backends == ("rebar",)
    for case in mod.QUANTIFIED_NESTED_GROUP_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BYTES_CASES
)
print("ok")
PY`
  - `bash -lc "! rg -n '^def test_quantified_(alternation|nested_group_alternation)_branch_local_backreference_bytes_' tests/python/test_branch_local_backreference_parity_suite.py"`

## Constraints
- Keep the task structural only. Do not change the published correctness frontier, direct bytes follow-on routing, or the active feature-owned `RBR-0603` parity target.
- Preserve the current case-table payloads exactly; the point is to remove duplicate harness code, not to republish or reinterpret the bytes observations.
- Favor a plain parametrized pytest shape in the existing module over introducing another helper package or cross-test import boundary.

## Notes
- `RBR-0604` is the next available task id:
  - `ops/state/backlog.md` and `ops/state/current_status.md` name no reserved `RBR-0604`;
  - `ops/tasks/ready/` currently stops at `RBR-0603`; and
  - `ops/tasks/blocked/` and `ops/tasks/in_progress/` are empty.
- No stale blocked architecture task needed normalization first, and rule 10 does not apply in the current checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`;
  - `.rebar/runtime/dashboard.md` reports `HEAD: a2fc373027adc17b0e783ffc01e3aed6f1f6b0c2`, which matches `git rev-parse HEAD`; and
  - the latest runtime cycle finished both task workers at `done`, with no inherited-dirty or post-commit refresh churn.
- JSON burn-down remains complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining duplication is concrete and bounded in the current checkout:
  - `tests/python/test_branch_local_backreference_parity_suite.py` is currently `1418` lines long and still repeats two bytes follow-on data blocks at roughly lines `406-447`;
  - the file still repeats two direct-follow-on anchor tests at roughly lines `812-979`;
  - the file still repeats two six-test compile/module/pattern parity ladders at roughly lines `1015-1323`; and
  - `bash -lc "! rg -n '^def test_quantified_(alternation|nested_group_alternation)_branch_local_backreference_bytes_' tests/python/test_branch_local_backreference_parity_suite.py"` currently fails exactly on this cleanup with sixteen matching test definitions.
- 2026-03-18 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py` passes (`331 passed, 14 skipped in 0.26s`)
  - the inline `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... PY` probe above passes (`ok`)
  - `bash -lc "! rg -n '^def test_quantified_(alternation|nested_group_alternation)_branch_local_backreference_bytes_' tests/python/test_branch_local_backreference_parity_suite.py"` currently fails exactly on this cleanup because the duplicate per-manifest bytes follow-on ladders are still present

## Completion Notes
- 2026-03-18: Collapsed the duplicated quantified-alternation and quantified-nested-group bytes follow-on anchor checks onto one local `DIRECT_BYTES_FOLLOW_ON_SPECS` table in `tests/python/test_branch_local_backreference_parity_suite.py`, keeping the existing bytes case tables and `DIRECT_BYTES_FOLLOW_ON_BUNDLES` intact while moving the differing bucket labels and published bytes-text expectations into the shared table.
- 2026-03-18: Replaced the per-manifest bytes compile/module/pattern parity ladders with shared parametrized tests over the combined direct bytes follow-on case set, preserving the existing compile parity, module-search result parity, match-convenience parity, match-group-access parity, pattern-fullmatch result parity, and the nested-group `rebar` skip gating tied to `RBR-0603`.
- 2026-03-18 verification:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py` (`331 passed, 14 skipped in 0.28s`)
  - the inline `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... PY` probe from the task text (`ok`)
  - `bash -lc "! rg -n '^def test_quantified_(alternation|nested_group_alternation)_branch_local_backreference_bytes_' tests/python/test_branch_local_backreference_parity_suite.py"` (passes)
