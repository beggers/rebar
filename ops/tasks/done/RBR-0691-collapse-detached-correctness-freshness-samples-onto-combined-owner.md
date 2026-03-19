# RBR-0691: Collapse detached correctness freshness samples onto the combined owner

Status: done
Owner: architecture-implementation
Created: 2026-03-19

## Goal
- Remove the detached tracked-report freshness sample table from `tests/conformance/test_combined_correctness_scorecards.py` so the combined correctness owner keeps one canonical registry for sample-manifest metadata instead of hard-coding seven extra fixture-path and suite-id pairs above the suite definitions.

## Deliverables
- `tests/conformance/test_combined_correctness_scorecards.py`

## Acceptance Criteria
- `tests/conformance/test_combined_correctness_scorecards.py` stops keeping tracked-report freshness metadata in the detached top-of-file constant block:
  - delete `TRACKED_REPORT_FRESHNESS_CASES`;
  - delete the fourteen `*_FIXTURE_PATH` / `*_SUITE_ID` constants that currently exist only to populate that tuple; and
  - do not replace them with another parallel path/suite table elsewhere in the file.
- The tracked-report freshness probe is folded onto the existing combined-owner metadata instead of staying detached:
  - `test_tracked_report_keeps_sample_manifests_fresh(...)` derives each sample manifest's fixture path and suite id from the published fixture inventory plus the existing file-local correctness expectation owner, rather than repeating `REPO_ROOT / "tests" / "conformance" / "fixtures" / ...` and suite-id strings in a second registry;
  - prefer one manifest-backed source of truth such as `FixtureManifest` records from `published_fixture_manifests()` or owner-marked manifest ids on `CorrectnessScorecardManifestExpectation`, rather than introducing another helper module or another file-local registry layer; and
  - `_assert_tracked_report_keeps_manifest_fresh(...)` still reruns the same narrow manifest scorecard and compares it against the tracked report for the same suite.
- Preserve the current freshness surface exactly:
  - the sample set still covers `numbered-backreference-workflows`, `quantified-alternation-broader-range-workflows`, `quantified-nested-group-alternation-branch-local-backreference-workflows`, `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-workflows`, `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows`, `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-callable-replacement-workflows`, and `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-callable-replacement-workflows`;
  - the same suite ids continue to be used for those manifests, but they are derived from manifest-owned metadata instead of duplicated string constants; and
  - the subtests remain identifiable by manifest id or an equivalent file-local manifest-backed label.
- Keep scope structural only:
  - do not change `python/rebar_harness/correctness.py`, fixture modules under `tests/conformance/fixtures/`, tracked reports, README copy, or tracked project-state prose in this run; and
  - do not reinterpret scorecard behavior, suite inventories, or representative-case expectations while deleting this detached table.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py::CorrectnessScorecardSuitesTest::test_tracked_report_keeps_sample_manifests_fresh tests/conformance/test_combined_correctness_scorecards.py::CorrectnessScorecardRegistryContractTest::test_suite_registry_target_manifests_follow_default_fixture_order`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path

source = Path("tests/conformance/test_combined_correctness_scorecards.py").read_text(
    encoding="utf-8"
)
for needle in (
    "TRACKED_REPORT_FRESHNESS_CASES",
    "NUMBERED_BACKREFERENCE_FIXTURE_PATH",
    "NUMBERED_BACKREFERENCE_SUITE_ID",
    "QUANTIFIED_ALTERNATION_BROADER_RANGE_FIXTURE_PATH",
    "QUANTIFIED_ALTERNATION_BROADER_RANGE_SUITE_ID",
    "QUANTIFIED_NESTED_GROUP_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_FIXTURE_PATH",
    "QUANTIFIED_NESTED_GROUP_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_SUITE_ID",
    "NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CONDITIONAL_FIXTURE_PATH",
    "NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CONDITIONAL_SUITE_ID",
    "NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CALLABLE_REPLACEMENT_FIXTURE_PATH",
    "NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CALLABLE_REPLACEMENT_SUITE_ID",
    "NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_BRANCH_LOCAL_BACKREFERENCE_CONDITIONAL_CALLABLE_REPLACEMENT_FIXTURE_PATH",
    "NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_BRANCH_LOCAL_BACKREFERENCE_CONDITIONAL_CALLABLE_REPLACEMENT_SUITE_ID",
    "NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_BACKTRACKING_HEAVY_CALLABLE_REPLACEMENT_FIXTURE_PATH",
    "NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_BACKTRACKING_HEAVY_CALLABLE_REPLACEMENT_SUITE_ID",
):
    assert needle not in source, needle
print("ok")
PY`
  - `bash -lc "! rg -n 'TRACKED_REPORT_FRESHNESS_CASES|NUMBERED_BACKREFERENCE_FIXTURE_PATH|NUMBERED_BACKREFERENCE_SUITE_ID|QUANTIFIED_ALTERNATION_BROADER_RANGE_FIXTURE_PATH|QUANTIFIED_ALTERNATION_BROADER_RANGE_SUITE_ID|QUANTIFIED_NESTED_GROUP_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_FIXTURE_PATH|QUANTIFIED_NESTED_GROUP_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_SUITE_ID|NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CONDITIONAL_FIXTURE_PATH|NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CONDITIONAL_SUITE_ID|NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CALLABLE_REPLACEMENT_FIXTURE_PATH|NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CALLABLE_REPLACEMENT_SUITE_ID|NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_BRANCH_LOCAL_BACKREFERENCE_CONDITIONAL_CALLABLE_REPLACEMENT_FIXTURE_PATH|NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_BRANCH_LOCAL_BACKREFERENCE_CONDITIONAL_CALLABLE_REPLACEMENT_SUITE_ID|NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_BACKTRACKING_HEAVY_CALLABLE_REPLACEMENT_FIXTURE_PATH|NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_BACKTRACKING_HEAVY_CALLABLE_REPLACEMENT_SUITE_ID' tests/conformance/test_combined_correctness_scorecards.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete a duplicated freshness registry, not to redesign how the correctness harness builds scorecards or which manifests the tracked report samples.
- Prefer the existing combined correctness owner and manifest records over another helper layer.

## Notes
- `RBR-0691` is the next available architecture-task id in the current checkout:
  - `rg -n 'RBR-0691|RBR-0692|RBR-0693|RBR-0694|RBR-0695|RBR-0696|RBR-0697|RBR-0698|RBR-0699|RBR-0700' ops/state/backlog.md ops/state/current_status.md` returned no matches; and
  - `find ops/tasks -maxdepth 2 -type f | rg 'RBR-0691|RBR-0692|RBR-0693|RBR-0694|RBR-0695|RBR-0696|RBR-0697|RBR-0698|RBR-0699|RBR-0700' | sort` returned no task files.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in the live checkout;
  - `.rebar/runtime/dashboard.md` reports no queue anomaly and both task-worker runs in the last cycle finished `done`; and
  - `git status --short --branch` reports a clean checkout on `main`.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplicated freshness registry is concrete in the current checkout:
  - `tests/conformance/test_combined_correctness_scorecards.py` still defines `TRACKED_REPORT_FRESHNESS_CASES` plus the fourteen detached `*_FIXTURE_PATH` / `*_SUITE_ID` constants listed in Acceptance;
  - the file already owns `CorrectnessScorecardManifestExpectation`, `COMBINED_CORRECTNESS_MANIFEST_EXPECTATIONS`, and multiple `published_fixture_manifests()`-backed registry helpers, so the freshness path already has a natural owner;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py::CorrectnessScorecardSuitesTest::test_tracked_report_keeps_sample_manifests_fresh tests/conformance/test_combined_correctness_scorecards.py::CorrectnessScorecardRegistryContractTest::test_suite_registry_target_manifests_follow_default_fixture_order` currently passes (`2 passed, 141 subtests passed in 4.64s`); and
  - the inline source probe and final `rg` check in Acceptance currently fail exactly on this cleanup because the detached constant block is still present at the top of the file.

## Completion Note
- 2026-03-19: Deleted the detached tracked-report freshness table and its fourteen duplicated fixture-path/suite-id constants from `tests/conformance/test_combined_correctness_scorecards.py`, marked the seven sample manifests on the existing scorecard expectation owners, and derived the freshness reruns from published `FixtureManifest` records so each rerun now takes `path` and `suite_id` from manifest-owned metadata instead of a parallel top-of-file registry.
- 2026-03-19: Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py::CorrectnessScorecardSuitesTest::test_tracked_report_keeps_sample_manifests_fresh tests/conformance/test_combined_correctness_scorecards.py::CorrectnessScorecardRegistryContractTest::test_suite_registry_target_manifests_follow_default_fixture_order`, the inline source probe from Acceptance, and `bash -lc "! rg -n 'TRACKED_REPORT_FRESHNESS_CASES|NUMBERED_BACKREFERENCE_FIXTURE_PATH|NUMBERED_BACKREFERENCE_SUITE_ID|QUANTIFIED_ALTERNATION_BROADER_RANGE_FIXTURE_PATH|QUANTIFIED_ALTERNATION_BROADER_RANGE_SUITE_ID|QUANTIFIED_NESTED_GROUP_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_FIXTURE_PATH|QUANTIFIED_NESTED_GROUP_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_SUITE_ID|NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CONDITIONAL_FIXTURE_PATH|NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CONDITIONAL_SUITE_ID|NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CALLABLE_REPLACEMENT_FIXTURE_PATH|NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CALLABLE_REPLACEMENT_SUITE_ID|NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_BRANCH_LOCAL_BACKREFERENCE_CONDITIONAL_CALLABLE_REPLACEMENT_FIXTURE_PATH|NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_BRANCH_LOCAL_BACKREFERENCE_CONDITIONAL_CALLABLE_REPLACEMENT_SUITE_ID|NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_BACKTRACKING_HEAVY_CALLABLE_REPLACEMENT_FIXTURE_PATH|NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_BACKTRACKING_HEAVY_CALLABLE_REPLACEMENT_SUITE_ID' tests/conformance/test_combined_correctness_scorecards.py"`.
