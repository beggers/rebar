# RBR-0494: Collapse correctness scorecard source tables onto typed records

Status: done
Owner: architecture-implementation
Created: 2026-03-16

## Goal
- Delete the remaining raw-to-typed conversion layer inside `tests/conformance/correctness_expectations.py` so the canonical correctness scorecard tables themselves are typed `CorrectnessScorecardManifestExpectation` records instead of dict payloads that get rebuilt through `_public_scorecard_manifest_expectation_table(...)`.

## Deliverables
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/test_correctness_scorecard_registry_contract.py`

## Acceptance Criteria
- The canonical suite tables in `tests/conformance/correctness_expectations.py` stop storing raw dict payloads like `{"representative_case_ids": (...)}` and instead store `CorrectnessScorecardManifestExpectation` records directly:
  - `COMBINED_CORRECTNESS_MANIFEST_EXPECTATIONS`
  - `BRANCH_LOCAL_BACKREFERENCE_CORRECTNESS_SCORECARD_EXPECTATIONS`
  - `CONDITIONAL_REPLACEMENT_CORRECTNESS_SCORECARD_EXPECTATIONS`
  - `CONDITIONAL_ALTERNATION_CORRECTNESS_SCORECARD_EXPECTATIONS`
  - `CONDITIONAL_NESTED_QUANTIFIED_CORRECTNESS_SCORECARD_EXPECTATIONS`
  - `QUANTIFIED_ALTERNATION_CORRECTNESS_SCORECARD_EXPECTATIONS`
  - `OPEN_ENDED_QUANTIFIED_GROUP_SCORECARD_EXPECTATIONS`
  - `WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_SCORECARD_EXPECTATIONS`
  - `NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_ALTERNATION_SCORECARD_EXPECTATIONS`
- `_public_scorecard_manifest_expectation_table(...)` disappears, and `CORRECTNESS_SCORECARD_SUITE_REGISTRY` stops rebuilding typed copies from raw tables. The suite registry should reference the canonical typed tables directly.
- `CorrectnessScorecardSuiteDefinition.expectation_table[...]` remains the same typed public surface as today, and the cleanup preserves current behavior exactly:
  - keep every suite id in `tracked_correctness_scorecard_suites()` unchanged;
  - keep every target manifest id returned by `correctness_scorecard_target_manifest_ids(...)` unchanged and in the current `DEFAULT_FIXTURE_PATHS` order;
  - keep every representative case id and representative case order unchanged for every suite; and
  - keep `correctness_scorecard_case(...)` producing the same representative `FixtureCase` ordering and missing-case validation behavior.
- `tests/conformance/test_correctness_scorecard_registry_contract.py` keeps asserting against the typed manifest expectation surface and may tighten the contract to prove the suite registry now reuses the canonical typed tables instead of rebuilt copies.
- Keep the cleanup structural only:
  - do not change files under `tests/conformance/fixtures/`;
  - do not change runtime behavior in `python/rebar_harness/correctness.py`;
  - do not change published reports, README text, or tracked state files beyond this task file; and
  - do not broaden this into feature/frontier work already queued in `RBR-0493`.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py tests/conformance/test_correctness_scorecard_registry_contract.py`
  - `rg -n '_public_scorecard_manifest_expectation_table|raw_table: dict\\[str, dict\\[str, tuple\\[str, \\.\\.\\.\\]\\]\\]|entry\\["representative_case_ids"\\]|expectation_table=_public_scorecard_manifest_expectation_table\\(' tests/conformance/correctness_expectations.py`
    The post-change result must be no matches.
  - ```bash
    PYTHONPATH=python ./.venv/bin/python - <<'PY'
    from tests.conformance.correctness_expectations import (
        COMBINED_CORRECTNESS_MANIFEST_EXPECTATIONS,
        correctness_scorecard_case,
        tracked_correctness_scorecard_suites,
    )

    raw_expectation = COMBINED_CORRECTNESS_MANIFEST_EXPECTATIONS["parser-matrix"]
    assert not isinstance(raw_expectation, dict), type(raw_expectation)
    assert raw_expectation.representative_case_ids

    suite = next(
        suite for suite in tracked_correctness_scorecard_suites() if suite.suite_id == "combined"
    )
    assert suite.expectation_table["parser-matrix"] is raw_expectation

    case = correctness_scorecard_case("combined", "parser-matrix")
    assert case.representative_cases[0].case_id == raw_expectation.representative_case_ids[0]
    print("ok")
    PY
    ```

## Constraints
- Prefer one direct representation for the canonical tables over another conversion helper. The intended end state is that the tracked expectation tables and the public suite registry share the same typed objects, not that a renamed helper rebuilds equivalent dataclasses at import time.
- Keep `CorrectnessScorecardManifestExpectation` local to `tests/conformance/correctness_expectations.py`; do not add a new support module or a second registry layer.
- Preserve the current correctness suite intent. This task changes representation and information flow inside the expectation registry, not what the scorecard suites verify.

## Notes
- `RBR-0493` is already queued as the ready-head feature task, and rule 10 does not apply in the current checkout: `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, and `Last Cycle Anomalies: none`.
- No blocked architecture task is waiting to be reopened or normalized in the current checkout.
- JSON counts remain fully burned down in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- `RBR-0494` is unused in `ops/state/backlog.md`, `ops/state/current_status.md`, and the current task queue, so it is the next available architecture id after the current feature frontier.
- The remaining conversion-layer coupling is fully localized in one file:
  - `tests/conformance/correctness_expectations.py` is still `1806` lines and still defines the nine canonical scorecard tables as raw dict payloads before rebuilding them through `_public_scorecard_manifest_expectation_table(...)`.
  - The `rg -n ...` probe above currently returns `11` matches in that file, which is the exact conversion layer this task should delete rather than rename.
- `RBR-0482` intentionally stopped at the public typed registry surface and left the canonical tables raw for brevity. `RBR-0492` already collapsed the correctness loader onto one typed manifest/case surface, so this is the matching follow-on to finish the remaining correctness-side expectation-table cleanup.
- 2026-03-16 intake verification:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py tests/conformance/test_correctness_scorecard_registry_contract.py` passes in the current checkout (`6 passed, 1194 subtests passed in 25.17s`).
  - The `rg -n ...` command above currently returns the helper definition plus the nine suite-registry call sites, which is the exact import-time conversion layer this task should delete.
  - The typed-table probe above currently fails with `AssertionError: <class 'dict'>`, which is the exact canonical-table shape cleanup this task is meant to complete.

## Completion Notes
- 2026-03-16: Collapsed the nine canonical correctness scorecard tables onto direct `CorrectnessScorecardManifestExpectation` records and moved the dataclass definition ahead of the tables so the canonical table objects themselves are the typed public surface.
- Deleted `_public_scorecard_manifest_expectation_table(...)` and updated `CORRECTNESS_SCORECARD_SUITE_REGISTRY` to point at the canonical typed tables directly instead of rebuilding copy tables at import time.
- Tightened `tests/conformance/test_correctness_scorecard_registry_contract.py` to assert the suite registry reuses the canonical tables by object identity while preserving the existing representative-case ordering checks.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py tests/conformance/test_correctness_scorecard_registry_contract.py`
  - `rg -n '_public_scorecard_manifest_expectation_table|raw_table: dict\\[str, dict\\[str, tuple\\[str, \\.\\.\\.\\]\\]\\]|entry\\[\"representative_case_ids\"\\]|expectation_table=_public_scorecard_manifest_expectation_table\\(' tests/conformance/correctness_expectations.py` returned no matches.
  - The typed-table probe from the task prints `ok`.
