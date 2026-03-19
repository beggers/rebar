# RBR-0689: Decouple the fixture-support helper contracts from published cases

Status: done
Owner: architecture-implementation
Created: 2026-03-19

## Goal
- Make the remaining generic helper-contract coverage in `tests/python/test_fixture_parity_support_contract.py` self-contained by replacing its last published-case lookups with file-local synthetic inputs, so the shared support suite validates `case_pattern(...)`, `str_case_pattern(...)`, and match-convenience helper behavior without reaching into feature-owner fixture inventories.

## Deliverables
- `tests/python/test_fixture_parity_support_contract.py`

## Acceptance Criteria
- `tests/python/test_fixture_parity_support_contract.py` stops preloading published cases for its remaining generic helper-contract slice:
  - delete `def _fixture_cases(...)`;
  - delete `NAMED_GROUP_CASES`;
  - delete `BRANCH_LOCAL_BACKREFERENCE_CASES`; and
  - delete `COLLECTION_REPLACEMENT_CASES`.
- Rewrite the current `case_pattern(...)` / `str_case_pattern(...)` helper contract coverage so it uses file-local synthetic inputs instead of `named_group_workflows.py` and `collection_replacement_workflows.py`, while preserving the current observed helper outputs exactly:
  - the two `str` inputs still yield `r"(?P<word>abc)"` through both `case_pattern(...)` and `str_case_pattern(...)`; and
  - the `bytes` input still yields `b"abc"` through `case_pattern(...)`.
- Rewrite the helper currently named `_branch_local_named_backreference_match(...)` so `test_match_convenience_api_parity_covers_multiple_named_groups(...)` no longer depends on `branch_local_backreference_workflows.py`:
  - keep one successful module-level path and one successful compiled-pattern path;
  - keep the match object rich enough that `assert_match_parity(..., check_regs=True)` and `assert_match_convenience_api_parity(...)` still exercise multiple named groups; and
  - prefer file-local pattern/text constants or file-local synthetic `FixtureCase(...)` values over another shared helper module, another tracked fixture, or a new owner-suite dependency.
- Keep the cleanup local and structural:
  - do not change `python/rebar_harness/correctness.py`, tracked correctness fixtures under `tests/conformance/fixtures/`, owner parity suites, reports, or tracked project-state prose; and
  - do not broaden into the selector inventory table, manifest-loader schema validation, direct-test bucket coverage, or the existing local bytes match-result helper coverage that already stays off published fixtures.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path

source = Path("tests/python/test_fixture_parity_support_contract.py").read_text(
    encoding="utf-8"
)
for needle in (
    "def _fixture_cases(",
    "NAMED_GROUP_CASES",
    "BRANCH_LOCAL_BACKREFERENCE_CASES",
    "COLLECTION_REPLACEMENT_CASES",
):
    assert needle not in source, needle
print("ok")
PY`
  - `bash -lc "! rg -n 'def _fixture_cases\\(|NAMED_GROUP_CASES|BRANCH_LOCAL_BACKREFERENCE_CASES|COLLECTION_REPLACEMENT_CASES' tests/python/test_fixture_parity_support_contract.py"`

## Constraints
- Keep this cleanup structural only. The point is to remove the generic support suite's remaining published-case coupling, not to reinterpret helper semantics, broaden parity scope, or introduce another support layer.
- Prefer deleting the published-case preload seam over adding abstractions.

## Notes
- `RBR-0689` is the next available architecture-task id in the current checkout:
  - `rg -n 'RBR-0689|RBR-0690|RBR-0691' ops/state/backlog.md ops/state/current_status.md` returned no matches; and
  - `find ops/tasks -maxdepth 2 -type f | rg 'RBR-0689|RBR-0690|RBR-0691'` returned no task file.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in the live checkout before this task was added;
  - `.rebar/runtime/dashboard.md` reports no queue anomaly and both task-worker runs in the last cycle finished `done`; and
  - `git status --short --branch` reports a clean checkout on `main`.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining coupling is concrete and isolated in the current checkout:
  - `tests/python/test_fixture_parity_support_contract.py` still defines `_fixture_cases(...)`, `NAMED_GROUP_CASES`, `BRANCH_LOCAL_BACKREFERENCE_CASES`, and `COLLECTION_REPLACEMENT_CASES`;
  - the current `rg` absence check in Acceptance fails exactly on that seam;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py` currently passes (`133 passed in 0.19s`); and
  - `test_case_pattern_helpers_extract_str_and_bytes_patterns_from_published_fixtures(...)` plus `_branch_local_named_backreference_match(...)` are the remaining consumers of that preload path.

## Completion Note
- Removed `_fixture_cases(...)` plus the three published-case preload tables from `tests/python/test_fixture_parity_support_contract.py`, replacing the pattern-helper contract coverage with file-local synthetic `FixtureCase(...)` values that still yield `r"(?P<word>abc)"` for the two `str` cases and `b"abc"` for the bytes case.
- Reworked `_branch_local_named_backreference_match(...)` to use file-local pattern/text constants for one successful module-search path and one successful compiled-pattern fullmatch path while still exercising multiple named groups through `assert_match_parity(..., check_regs=True)` and `assert_match_convenience_api_parity(...)`.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py`, the inline source probe from this task, and the final `rg` absence check for the removed preload identifiers.
