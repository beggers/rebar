# RBR-0660: Collapse the detached correctness scorecard expectation module onto the combined owner

Status: ready
Owner: architecture-implementation
Created: 2026-03-19

## Goal
- Delete `tests/conformance/correctness_expectations.py` by moving its remaining correctness scorecard expectation tables, typed records, and registry helpers onto `tests/conformance/test_combined_correctness_scorecards.py`, so the published correctness scorecard path has one owner instead of a detached expectations-only support module beside the existing combined owner.

## Deliverables
- `tests/conformance/test_combined_correctness_scorecards.py`
- Delete `tests/conformance/correctness_expectations.py`

## Acceptance Criteria
- `tests/conformance/test_combined_correctness_scorecards.py` becomes the sole owner for the scorecard expectation structures and accessors currently isolated in `tests/conformance/correctness_expectations.py`:
  - keep the current typed expectation records file-local on the owner:
    - `CorrectnessScorecardManifestExpectation`, `CorrectnessLayerExpectation`, `CorrectnessScorecardExpectation`, and `CorrectnessScorecardSuiteDefinition` remain defined on `tests/conformance/test_combined_correctness_scorecards.py`;
    - `CORRECTNESS_SCORECARD_SUITE_REGISTRY` still preserves the current suite order and target-manifest inventory for the nine tracked scorecard suites; and
    - `tracked_correctness_scorecard_suites()`, `correctness_scorecard_target_manifest_ids()`, and `correctness_scorecard_case()` still preserve their current ordering, case construction, and missing-suite or missing-manifest assertion behavior.
  - keep the current expectation tables explicit on the owner file:
    - `COMBINED_CORRECTNESS_MANIFEST_EXPECTATIONS`,
      `BRANCH_LOCAL_BACKREFERENCE_CORRECTNESS_SCORECARD_EXPECTATIONS`,
      `CONDITIONAL_NESTED_QUANTIFIED_CORRECTNESS_SCORECARD_EXPECTATIONS`,
      `CONDITIONAL_ALTERNATION_CORRECTNESS_SCORECARD_EXPECTATIONS`,
      `QUANTIFIED_ALTERNATION_CORRECTNESS_SCORECARD_EXPECTATIONS`,
      `CONDITIONAL_REPLACEMENT_CORRECTNESS_SCORECARD_EXPECTATIONS`,
      `WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_SCORECARD_EXPECTATIONS`,
      `NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_ALTERNATION_SCORECARD_EXPECTATIONS`, and
      `OPEN_ENDED_QUANTIFIED_GROUP_SCORECARD_EXPECTATIONS`
      still drive the same manifest ids, representative case ids, and cumulative suite coverage as today.
  - keep the current owner-local wiring explicit:
    - `EXPECTED_SUITE_TABLES` and `MIXED_TEXT_MIRROR_EXPECTATION_TABLES` continue to point at those tables without another import-only forwarding layer; and
    - any tiny helper needed for suite lookup or expectation assembly stays file-local on `tests/conformance/test_combined_correctness_scorecards.py` instead of creating another `*_support.py`, resurrecting `correctness_expectations.py`, or moving logic into `python/rebar_harness/correctness.py`.
- `tests/conformance/correctness_expectations.py` is deleted outright:
  - do not leave an import-only wrapper, compatibility shell, or renamed expectations-specific module behind.
- Keep scope structural only:
  - do not change `python/rebar_harness/correctness.py`, correctness fixture modules under `tests/conformance/fixtures/`, tracked reports, or tracked project-state prose in this run.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path

source = Path("tests/conformance/test_combined_correctness_scorecards.py").read_text(
    encoding="utf-8"
)
for needle in (
    "class CorrectnessScorecardExpectation",
    "class CorrectnessScorecardSuiteDefinition",
    "CORRECTNESS_SCORECARD_SUITE_REGISTRY =",
    "def tracked_correctness_scorecard_suites(",
    "def correctness_scorecard_target_manifest_ids(",
    "def correctness_scorecard_case(",
):
    assert needle in source, needle
assert "from tests.conformance.correctness_expectations import" not in source
print("ok")
PY`
  - `bash -lc "! rg --files tests/conformance | rg 'correctness_expectations\\.py$'"`

## Constraints
- Keep this cleanup structural only. Do not reinterpret correctness scorecard behavior, change suite inventories, or regenerate tracked reports.
- Prefer the existing combined correctness scorecard owner and file-local helpers over another shared support module or another detached expectation file.
- Do not move this coverage into `python/rebar_harness/correctness.py`; the harness should keep owning runtime scorecard production, not test-only expectation tables.

## Notes
- `RBR-0660` is the next available architecture task id in the current checkout:
  - `rg -n "RBR-0660|RBR-0661|RBR-0662|RBR-0663" ops/state/backlog.md ops/state/current_status.md` returned no reserved future ids in that range; and
  - `find ops/tasks -maxdepth 2 -type f \( -name 'RBR-0659*' -o -name 'RBR-0660*' -o -name 'RBR-0661*' -o -name 'RBR-0662*' -o -name 'RBR-0663*' \) | sort` returned only the active feature task `ops/tasks/ready/RBR-0659-nested-broader-range-wider-ranged-repeat-branch-local-backreference-replacement-bytes-benchmark-catch-up.md`.
- No blocked architecture task exists to reopen first, and rule 10 does not currently block another architecture cleanup:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the only ready feature task is `RBR-0659`, which stays on benchmark files rather than the conformance owner targeted here.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The detached correctness expectation layer is concrete and bounded in the current checkout:
  - `rg -n "from tests\\.conformance\\.correctness_expectations import|import tests\\.conformance\\.correctness_expectations" tests -g '*.py'` currently matches only `tests/conformance/test_combined_correctness_scorecards.py`;
  - `wc -l tests/conformance/correctness_expectations.py tests/conformance/test_combined_correctness_scorecards.py` reports `2207` lines for the detached support module and `1176` lines for the combined owner;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py` currently passes (`17 passed, 1747 subtests passed in 30.77s`);
  - `rg -n "^class CorrectnessScorecardExpectation|^class CorrectnessScorecardSuiteDefinition|^CORRECTNESS_SCORECARD_SUITE_REGISTRY =|^def tracked_correctness_scorecard_suites\\(|^def correctness_scorecard_target_manifest_ids\\(|^def correctness_scorecard_case\\(|^from tests\\.conformance\\.correctness_expectations import" tests/conformance/test_combined_correctness_scorecards.py tests/conformance/correctness_expectations.py` currently shows the class and registry/helper definitions only in `tests/conformance/correctness_expectations.py` and the import-only forwarding edge only in `tests/conformance/test_combined_correctness_scorecards.py`; and
  - `bash -lc "! rg --files tests/conformance | rg 'correctness_expectations\\.py$'"` currently fails exactly on this cleanup because the detached support file still exists.
