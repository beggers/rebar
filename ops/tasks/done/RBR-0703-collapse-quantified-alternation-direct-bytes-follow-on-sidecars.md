# RBR-0703: Collapse quantified-alternation direct-bytes follow-on sidecars onto canonical spec records

Status: done
Owner: architecture-implementation
Created: 2026-03-19

## Goal
- Remove the mirrored `DIRECT_BYTES_FOLLOW_ON_SPECS`, `DIRECT_BYTES_FOLLOW_ON_SPEC_IDS`, and `DIRECT_BYTES_FOLLOW_ON_BUNDLES` block from `tests/python/test_quantified_alternation_parity_suite.py` so `QuantifiedAlternationDirectBytesFollowOnSpec` and `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` become the single canonical owner of direct-bytes follow-on bundle metadata, ids, and case routing.

## Deliverables
- `tests/python/test_quantified_alternation_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_quantified_alternation_parity_suite.py` stops defining these detached direct-bytes follow-on sidecars:
  - delete `DIRECT_BYTES_FOLLOW_ON_SPECS`;
  - delete `DIRECT_BYTES_FOLLOW_ON_SPEC_IDS`; and
  - delete `DIRECT_BYTES_FOLLOW_ON_BUNDLES`.
- The direct-bytes follow-on tests derive their parametrization and bundle routing directly from `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` instead of those detached registries:
  - `test_direct_bytes_follow_on_manifests_exclude_only_bytes_rows_from_generic_case_buckets` no longer reads `DIRECT_BYTES_FOLLOW_ON_SPECS` or `DIRECT_BYTES_FOLLOW_ON_SPEC_IDS`;
  - `test_direct_bytes_follow_on_cases_stay_explicit_with_one_direct_follow_on_anchor` no longer reads `DIRECT_BYTES_FOLLOW_ON_SPEC_IDS`; and
  - the `partition_direct_bytes_follow_on_case_buckets(...)` call that builds `COMPILE_CASES`, `MODULE_CASES`, and `PATTERN_CASES` no longer reads `DIRECT_BYTES_FOLLOW_ON_BUNDLES`.
- Preserve the current effective order and pairing exactly:
  - the canonical direct-bytes follow-on surface stays ordered as `bounded`, `broader-range`, `conditional`, `open-ended`, `nested-branch`, `backtracking-heavy`;
  - the parametrized test ids for the two direct-bytes follow-on contract tests stay exactly those six strings in that order; and
  - each surface record still routes the same `bundle` and supplemental `cases` pair as today.
- Keep canonical ownership unchanged:
  - do not change `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` membership, supplemental case payloads, expected operation-helper counts, expected search/fullmatch text maps, or `DIRECT_BYTES_FOLLOW_ON_CASES`;
  - do not change `FIXTURE_BUNDLES`, `QUANTIFIED_ALTERNATION_SELECTED_CASE_IDS`, `QUANTIFIED_ALTERNATION_DIRECT_TEST_CASE_ID_BUCKETS`, or the direct-parity coverage they represent; and
  - a tiny file-local helper or an added id field on `QuantifiedAlternationDirectBytesFollowOnSpec` is acceptable only if it replaces the deleted sidecars rather than introducing another mirrored registry.
- Keep scope structural only:
  - do not edit `tests/python/fixture_parity_support.py`, `python/rebar_harness/correctness.py`, correctness fixture modules under `tests/conformance/fixtures/`, published reports, or tracked project-state prose.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path

source = Path("tests/python/test_quantified_alternation_parity_suite.py").read_text(
    encoding="utf-8"
)
for needle in (
    "DIRECT_BYTES_FOLLOW_ON_SPECS",
    "DIRECT_BYTES_FOLLOW_ON_SPEC_IDS",
    "DIRECT_BYTES_FOLLOW_ON_BUNDLES",
):
    assert needle not in source, needle
print("ok")
PY`
  - `bash -lc "! rg -n 'DIRECT_BYTES_FOLLOW_ON_SPECS|DIRECT_BYTES_FOLLOW_ON_SPEC_IDS|DIRECT_BYTES_FOLLOW_ON_BUNDLES' tests/python/test_quantified_alternation_parity_suite.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete one more mirrored parameter/bundle registry layer inside the quantified-alternation parity owner, not to reinterpret the direct-bytes follow-on frontier, change which bytes cases stay explicit, or broaden the suite beyond the existing published slice.
- Prefer deriving ids and bundle routing directly from `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` over introducing another detached tuple/list/map block.

## Notes
- `RBR-0703` is the correct frontier id for this queue even though an old historical numeric hole still exists:
  - the live task tail is `RBR-0702`;
  - `rg -n "RBR-0703" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked` returned no matches; and
  - `ops/state/backlog.md` and `ops/state/current_status.md` do not reserve any missing tail ids beyond `RBR-0702`.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the last recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The detached direct-bytes follow-on sidecars are concrete and bounded in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py` currently passes (`777 passed in 1.02s`);
  - the inline source probe in Acceptance currently fails exactly on this cleanup with `AssertionError: DIRECT_BYTES_FOLLOW_ON_SPECS`; and
  - `rg -n "DIRECT_BYTES_FOLLOW_ON_SPECS|DIRECT_BYTES_FOLLOW_ON_SPEC_IDS|DIRECT_BYTES_FOLLOW_ON_BUNDLES" tests/python/test_quantified_alternation_parity_suite.py` shows the three target names are declared and consumed only inside this file.
- This simplification matches the current parity-harness information flow:
  - `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` already acts as the canonical owner of direct-bytes follow-on case payloads and expectations; and
  - deleting the mirrored `(bundle, cases)`, id, and bundle-only registries removes one more parallel owner layer without changing the published correctness slice or the direct-parity follow-on coverage.

## Completion Notes
- 2026-03-19: Added the canonical six-id ordering directly onto `QuantifiedAlternationDirectBytesFollowOnSpec` and removed the detached `DIRECT_BYTES_FOLLOW_ON_SPECS`, `DIRECT_BYTES_FOLLOW_ON_SPEC_IDS`, and `DIRECT_BYTES_FOLLOW_ON_BUNDLES` blocks from `tests/python/test_quantified_alternation_parity_suite.py`.
- 2026-03-19: Repointed the direct-bytes follow-on bucket partitioning and both direct-follow-on contract tests to derive bundle routing, supplemental-case ownership, and pytest ids directly from `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` while preserving the existing surface order and bytes-case pairing.
- 2026-03-19: Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py`, the inline source probe from Acceptance (`ok`), and `bash -lc "! rg -n 'DIRECT_BYTES_FOLLOW_ON_SPECS|DIRECT_BYTES_FOLLOW_ON_SPEC_IDS|DIRECT_BYTES_FOLLOW_ON_BUNDLES' tests/python/test_quantified_alternation_parity_suite.py"`.
