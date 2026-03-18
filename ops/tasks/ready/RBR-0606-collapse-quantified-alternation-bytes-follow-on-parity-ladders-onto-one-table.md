# RBR-0606: Collapse the quantified-alternation bytes follow-on parity ladders onto one table

Status: ready
Owner: architecture-implementation
Created: 2026-03-18

## Goal
- Replace the duplicated quantified-alternation bytes follow-on anchor checks and per-family bytes compile/module/pattern parity ladders in `tests/python/test_quantified_alternation_parity_suite.py` with one local spec-driven surface plus shared parametrized assertions, so the suite stops restating the same logic for the bounded, broader-range, conditional, open-ended, nested-branch, and backtracking-heavy bytes pairs.

## Deliverables
- `tests/python/test_quantified_alternation_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_quantified_alternation_parity_suite.py` keeps the existing six direct-bytes case tuples plus `DIRECT_BYTES_FOLLOW_ON_SPECS`, `DIRECT_BYTES_FOLLOW_ON_SPEC_IDS`, and `DIRECT_BYTES_FOLLOW_ON_BUNDLES`, but replaces the current per-family duplicate bytes ladders with one local spec-driven surface. The shared table should own only the metadata that currently differs across the six bytes families:
  - which bundle/case tuple is under test;
  - the exact expected `Counter((operation, helper), ...)` for the published bytes rows in that bundle;
  - the exact expected published module-search texts by pattern;
  - the exact expected published pattern-fullmatch texts by pattern; and
  - any per-case invariant currently asserted only for a subset of families, such as exact `search_matches` / `search_misses` / `fullmatch_matches` / `fullmatch_misses` lengths or literal miss sets.
- Consolidate all six `*_bytes_cases_stay_explicit_with_one_direct_follow_on_anchor` tests into shared parametrized assertions without changing behavior:
  - keep the exact case ids, byte patterns, published search/fullmatch texts, and bundle row counts unchanged;
  - keep the current split where the shared compile/module/pattern buckets continue to exclude the bytes rows and the direct-follow-on buckets continue to own them explicitly;
  - keep `unsupported_backends == ()` and `unsupported_backend_reason is None` for every direct-bytes follow-on case unchanged; and
  - keep the current per-family exact bundle Counters and published bytes text maps intact.
- Consolidate the duplicated per-family bytes compile/module/pattern parity ladders into shared parametrized tests over the combined direct-bytes follow-on case surface without changing behavior:
  - preserve compile parity, module-search result parity, module-search convenience parity, module-search group-access parity, pattern-fullmatch result parity, pattern-fullmatch convenience parity, and pattern-fullmatch group-access parity;
  - keep `check_regs=True` wherever the current bytes ladders use it;
  - keep the current split where bounded bytes cases exercise only successful fullmatches while the broader-range, conditional, open-ended, nested-branch, and backtracking-heavy bytes cases continue to assert their exact miss rows as well; and
  - do not add new `rebar` skip gating or unsupported annotations.
- Keep this cleanup local to the quantified-alternation parity suite:
  - do not change `tests/python/fixture_parity_support.py`, correctness fixtures, benchmark workloads/tests, reports, Rust code, or `python/rebar/`;
  - do not rename `QUANTIFIED_ALTERNATION_BOUNDED_BYTES_CASES`, `QUANTIFIED_ALTERNATION_BROADER_RANGE_BYTES_CASES`, `QUANTIFIED_ALTERNATION_CONDITIONAL_BYTES_CASES`, `QUANTIFIED_ALTERNATION_OPEN_ENDED_BYTES_CASES`, `QUANTIFIED_ALTERNATION_NESTED_BRANCH_BYTES_CASES`, `QUANTIFIED_ALTERNATION_BACKTRACKING_HEAVY_BYTES_CASES`, or `DIRECT_BYTES_FOLLOW_ON_SPECS`; and
  - prefer one local spec table plus shared parametrized tests/helpers over another support module, registry layer, or bytes-only suite.
- After the consolidation lands, no per-family quantified-alternation bytes test functions remain in the file. This cleanup should remove the current duplicate prefixes rather than moving them behind another named wrapper layer:
  - `def test_quantified_alternation_bounded_bytes_...`
  - `def test_quantified_alternation_broader_range_bytes_...`
  - `def test_quantified_alternation_conditional_bytes_...`
  - `def test_quantified_alternation_open_ended_bytes_...`
  - `def test_quantified_alternation_nested_branch_bytes_...`
  - `def test_quantified_alternation_backtracking_heavy_bytes_...`
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from tests.python import test_quantified_alternation_parity_suite as mod

assert tuple(bundle.expected_manifest_id for bundle in mod.DIRECT_BYTES_FOLLOW_ON_BUNDLES) == (
    "quantified-alternation-workflows",
    "quantified-alternation-broader-range-workflows",
    "quantified-alternation-conditional-workflows",
    "quantified-alternation-open-ended-workflows",
    "quantified-alternation-nested-branch-workflows",
    "quantified-alternation-backtracking-heavy-workflows",
)
assert tuple(len(cases) for _, cases in mod.DIRECT_BYTES_FOLLOW_ON_SPECS) == (2, 2, 2, 2, 2, 2)
assert all(
    case.unsupported_backends == ()
    for _, cases in mod.DIRECT_BYTES_FOLLOW_ON_SPECS
    for case in cases
)
print("ok")
PY`
  - `bash -lc "! rg -n '^def test_quantified_alternation_(bounded|broader_range|conditional|open_ended|nested_branch|backtracking_heavy)_bytes_' tests/python/test_quantified_alternation_parity_suite.py"`

## Constraints
- Keep the task structural only. Do not change the published correctness frontier, the quantified-alternation bytes observations, or any backend behavior.
- Preserve the current bytes-case payloads exactly; the point is to delete duplicate harness code, not to reinterpret the published bytes surface.
- Favor plain parametrized pytest in the existing module over a new helper package, registry abstraction, or shared bytes-only support layer.

## Notes
- `RBR-0606` is the next available task id:
  - `ops/state/backlog.md` and `ops/state/current_status.md` name no reserved `RBR-0606`;
  - `ops/tasks/ready/` currently stops at `RBR-0605`; and
  - `ops/tasks/blocked/` and `ops/tasks/in_progress/` are empty.
- No stale blocked architecture task needed normalization first, and rule 10 does not apply in the current checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`;
  - `.rebar/runtime/dashboard.md` reports `HEAD: e3519329c49761d6486b3fe463c0d9532575d1e2`, which matches `git rev-parse HEAD`; and
  - the latest runtime cycle finished both task workers at `done`, with no inherited-dirty or post-commit refresh churn.
- JSON burn-down remains complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining duplication is concrete and bounded in the current checkout:
  - `tests/python/test_quantified_alternation_parity_suite.py` is currently `2772` lines long;
  - the file still repeats six bytes follow-on anchor tests at roughly lines `986-1393`;
  - the file still repeats forty-two per-family bytes compile/module/pattern parity tests at roughly lines `1780-2754`; and
  - `bash -lc "! rg -n '^def test_quantified_alternation_(bounded|broader_range|conditional|open_ended|nested_branch|backtracking_heavy)_bytes_' tests/python/test_quantified_alternation_parity_suite.py"` currently fails exactly on this cleanup with `48` matching test definitions.
- 2026-03-18 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py` passes (`750 passed in 0.54s`)
  - the inline `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... PY` probe above passes (`ok`)
  - `bash -lc "! rg -n '^def test_quantified_alternation_(bounded|broader_range|conditional|open_ended|nested_branch|backtracking_heavy)_bytes_' tests/python/test_quantified_alternation_parity_suite.py"` currently fails exactly on this cleanup because the duplicate per-family bytes ladders are still present
