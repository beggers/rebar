# RBR-0474: Collapse correctness scorecard suite accessors onto a shared registry

Status: ready
Owner: architecture-implementation
Created: 2026-03-16

## Goal
- Remove the remaining per-suite forwarding layer in `tests/conformance/correctness_expectations.py` so the combined correctness scorecard regression consumes one canonical registry of suite definitions instead of eighteen near-identical accessor wrappers plus nine repetitive suite-specific test methods.

## Deliverables
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/test_combined_correctness_scorecards.py`

## Acceptance Criteria
- Keep the existing expectation tables and `CorrectnessScorecardExpectation` contract intact:
  - `COMBINED_CORRECTNESS_MANIFEST_EXPECTATIONS`
  - `BRANCH_LOCAL_BACKREFERENCE_CORRECTNESS_SCORECARD_EXPECTATIONS`
  - `CONDITIONAL_NESTED_QUANTIFIED_CORRECTNESS_SCORECARD_EXPECTATIONS`
  - `CONDITIONAL_ALTERNATION_CORRECTNESS_SCORECARD_EXPECTATIONS`
  - `QUANTIFIED_ALTERNATION_CORRECTNESS_SCORECARD_EXPECTATIONS`
  - `CONDITIONAL_REPLACEMENT_CORRECTNESS_SCORECARD_EXPECTATIONS`
  - `WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_SCORECARD_EXPECTATIONS`
  - `NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_ALTERNATION_SCORECARD_EXPECTATIONS`
  - `OPEN_ENDED_QUANTIFIED_GROUP_SCORECARD_EXPECTATIONS`
- `tests/conformance/correctness_expectations.py` exposes one canonical suite registry plus generic helpers for:
  - enumerating the tracked correctness scorecard suites in the current test order;
  - resolving the target manifest ids for a suite; and
  - building a `CorrectnessScorecardExpectation` for a `(suite_id, target_manifest_id)` pair.
- Delete the eighteen per-suite wrapper functions that currently sit at the bottom of `tests/conformance/correctness_expectations.py`:
  - `combined_target_manifest_ids`
  - `combined_correctness_case`
  - `branch_local_backreference_scorecard_target_manifest_ids`
  - `branch_local_backreference_scorecard_case`
  - `conditional_nested_quantified_scorecard_target_manifest_ids`
  - `conditional_nested_quantified_scorecard_case`
  - `quantified_alternation_scorecard_target_manifest_ids`
  - `quantified_alternation_scorecard_case`
  - `conditional_alternation_scorecard_target_manifest_ids`
  - `conditional_alternation_scorecard_case`
  - `conditional_replacement_scorecard_target_manifest_ids`
  - `conditional_replacement_scorecard_case`
  - `wider_ranged_repeat_quantified_group_scorecard_target_manifest_ids`
  - `wider_ranged_repeat_quantified_group_scorecard_case`
  - `nested_broader_range_wider_ranged_repeat_quantified_group_alternation_scorecard_target_manifest_ids`
  - `nested_broader_range_wider_ranged_repeat_quantified_group_alternation_scorecard_case`
  - `open_ended_quantified_group_scorecard_target_manifest_ids`
  - `open_ended_quantified_group_scorecard_case`
- `tests/conformance/test_combined_correctness_scorecards.py` no longer imports or references any of those deleted wrappers and instead drives the nine suite families through the shared registry/generic helpers while keeping the same suite order:
  - combined
  - branch-local backreference
  - conditional replacement
  - conditional alternation
  - conditional nested/quantified
  - quantified alternation
  - open-ended quantified group
  - wider-ranged-repeat quantified group
  - nested broader-range wider-ranged-repeat quantified-group alternation
- Keep `assert_correctness_scorecard_suite(...)` and the representative-case evaluation path behaviorally intact: the cleanup should delete duplicated suite plumbing, not weaken report, fixture, layer, suite, or representative-case assertions.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py`
  - `rg -n '^def (combined_target_manifest_ids|combined_correctness_case|branch_local_backreference_scorecard_target_manifest_ids|branch_local_backreference_scorecard_case|conditional_nested_quantified_scorecard_target_manifest_ids|conditional_nested_quantified_scorecard_case|quantified_alternation_scorecard_target_manifest_ids|quantified_alternation_scorecard_case|conditional_alternation_scorecard_target_manifest_ids|conditional_alternation_scorecard_case|conditional_replacement_scorecard_target_manifest_ids|conditional_replacement_scorecard_case|wider_ranged_repeat_quantified_group_scorecard_target_manifest_ids|wider_ranged_repeat_quantified_group_scorecard_case|nested_broader_range_wider_ranged_repeat_quantified_group_alternation_scorecard_target_manifest_ids|nested_broader_range_wider_ranged_repeat_quantified_group_alternation_scorecard_case|open_ended_quantified_group_scorecard_target_manifest_ids|open_ended_quantified_group_scorecard_case)\\b' tests/conformance/correctness_expectations.py`
    The post-change result must be no matches.
  - `rg -n 'combined_target_manifest_ids|combined_correctness_case|branch_local_backreference_scorecard_target_manifest_ids|branch_local_backreference_scorecard_case|conditional_nested_quantified_scorecard_target_manifest_ids|conditional_nested_quantified_scorecard_case|quantified_alternation_scorecard_target_manifest_ids|quantified_alternation_scorecard_case|conditional_alternation_scorecard_target_manifest_ids|conditional_alternation_scorecard_case|conditional_replacement_scorecard_target_manifest_ids|conditional_replacement_scorecard_case|wider_ranged_repeat_quantified_group_scorecard_target_manifest_ids|wider_ranged_repeat_quantified_group_scorecard_case|nested_broader_range_wider_ranged_repeat_quantified_group_alternation_scorecard_target_manifest_ids|nested_broader_range_wider_ranged_repeat_quantified_group_alternation_scorecard_case|open_ended_quantified_group_scorecard_target_manifest_ids|open_ended_quantified_group_scorecard_case' tests/conformance/test_combined_correctness_scorecards.py`
    The post-change result must be no matches.

## Constraints
- Prefer deleting the per-suite wrapper layer over replacing it with another set of one-line forwarding helpers under different names.
- Keep the scope to correctness scorecard test plumbing. Do not change files under `tests/conformance/fixtures/`, harness runtime behavior in `python/rebar_harness/correctness.py`, published reports, README text, or tracked state files beyond this task file.
- Do not change the manifest sequencing or suite coverage of the existing combined correctness scorecard regression; this task should only change where the suite metadata comes from.
- If a tiny local helper or dataclass keeps the registry legible, keep it in `tests/conformance/correctness_expectations.py`; do not add a new support module for this cleanup.

## Notes
- `RBR-0473` is already reserved and queued for feature-owned benchmark work, so `RBR-0474` is the next available architecture id.
- The runtime dashboard is current and clean for this run (`Generated: 2026-03-16T14:07:11+00:00`, `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `Last Cycle Anomalies: none`), so rule 10 does not apply.
- JSON counts remain fully burned down in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- The current duplication is concentrated in two places:
  - `tests/conformance/correctness_expectations.py` contains eighteen near-identical suite accessors at lines `1688` through `1840`.
  - `tests/conformance/test_combined_correctness_scorecards.py` contains nine near-identical suite-specific test methods plus eighteen imports/references to those wrappers.
- Current file sizes underline why this is still a useful bounded simplification:
  - `tests/conformance/correctness_expectations.py`: `1841` lines
  - `tests/conformance/test_combined_correctness_scorecards.py`: `229` lines
- 2026-03-16 intake verification:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py` passes in the current checkout (`9 passed, 1044 subtests passed in 25.02s`).
  - `rg -n '^def (combined_target_manifest_ids|combined_correctness_case|branch_local_backreference_scorecard_target_manifest_ids|branch_local_backreference_scorecard_case|conditional_nested_quantified_scorecard_target_manifest_ids|conditional_nested_quantified_scorecard_case|quantified_alternation_scorecard_target_manifest_ids|quantified_alternation_scorecard_case|conditional_alternation_scorecard_target_manifest_ids|conditional_alternation_scorecard_case|conditional_replacement_scorecard_target_manifest_ids|conditional_replacement_scorecard_case|wider_ranged_repeat_quantified_group_scorecard_target_manifest_ids|wider_ranged_repeat_quantified_group_scorecard_case|nested_broader_range_wider_ranged_repeat_quantified_group_alternation_scorecard_target_manifest_ids|nested_broader_range_wider_ranged_repeat_quantified_group_alternation_scorecard_case|open_ended_quantified_group_scorecard_target_manifest_ids|open_ended_quantified_group_scorecard_case)\\b' tests/conformance/correctness_expectations.py` currently returns the eighteen wrapper definitions listed above, which is the exact cleanup this task is meant to remove.
  - `rg -n 'combined_target_manifest_ids|combined_correctness_case|branch_local_backreference_scorecard_target_manifest_ids|branch_local_backreference_scorecard_case|conditional_nested_quantified_scorecard_target_manifest_ids|conditional_nested_quantified_scorecard_case|quantified_alternation_scorecard_target_manifest_ids|quantified_alternation_scorecard_case|conditional_alternation_scorecard_target_manifest_ids|conditional_alternation_scorecard_case|conditional_replacement_scorecard_target_manifest_ids|conditional_replacement_scorecard_case|wider_ranged_repeat_quantified_group_scorecard_target_manifest_ids|wider_ranged_repeat_quantified_group_scorecard_case|nested_broader_range_wider_ranged_repeat_quantified_group_alternation_scorecard_target_manifest_ids|nested_broader_range_wider_ranged_repeat_quantified_group_alternation_scorecard_case|open_ended_quantified_group_scorecard_target_manifest_ids|open_ended_quantified_group_scorecard_case' tests/conformance/test_combined_correctness_scorecards.py` currently returns the expected import and call-site matches for those wrappers, which this task should delete rather than rename.
