# RBR-0482: Collapse correctness scorecard manifest expectations onto typed records

Status: ready
Owner: architecture-implementation
Created: 2026-03-16

## Goal
- Replace the remaining dict-shaped public manifest expectation payloads in the correctness scorecard registry with explicit typed records, so the shared correctness scorecard helpers stop carrying string-key coupling for representative-case metadata and the public suite expectation API becomes uniformly attribute-based.

## Deliverables
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/test_correctness_scorecard_registry_contract.py`

## Acceptance Criteria
- `tests/conformance/correctness_expectations.py` exposes an explicit typed record for the public per-manifest correctness expectation surface:
  - `CorrectnessScorecardSuiteDefinition.expectation_table[...]`
- That public manifest expectation surface no longer exposes plain `dict` objects. Keep the typed record local to `tests/conformance/correctness_expectations.py`; do not add a new support module.
- The typed manifest expectation surface covers the metadata currently read through string keys:
  - `representative_case_ids`
- `_build_scorecard_expectation(...)` and the suite-registry helpers stop indexing manifest expectations through string keys and instead use attribute access on the typed records while preserving the current representative-case ordering and missing-case validation behavior.
- `tests/conformance/test_correctness_scorecard_registry_contract.py` stops indexing suite manifest expectations through `["representative_case_ids"]` and instead uses attribute access on the typed records.
- Preserve the current correctness data and queue-facing behavior exactly:
  - keep the existing expectation tables as the canonical data sources in `tests/conformance/correctness_expectations.py`;
  - keep the current suite ids returned by `tracked_correctness_scorecard_suites()` unchanged;
  - keep the current target manifest ids returned by `correctness_scorecard_target_manifest_ids(...)` unchanged and in the existing `DEFAULT_FIXTURE_PATHS` order;
  - keep the current representative case ids and representative case order for every tracked scorecard suite unchanged.
- Keep the cleanup structural only:
  - do not change files under `tests/conformance/fixtures/`;
  - do not change runtime behavior in `python/rebar_harness/correctness.py`;
  - do not change published reports, README text, or tracked state files beyond this task file;
  - do not broaden this into queue/planning cleanup or feature work.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py tests/conformance/test_correctness_scorecard_registry_contract.py`
  - `rg -n 'expectation_table: dict\\[str, dict\\[str, tuple\\[str, \\.\\.\\.\\]\\]\\]|expectation\\["representative_case_ids"\\]|suite\\.expectation_table\\[[^]]+\\]\\["representative_case_ids"\\]' tests/conformance/correctness_expectations.py tests/conformance/test_correctness_scorecard_registry_contract.py`
    The post-change result must be no matches.
  - ```bash
    PYTHONPATH=python ./.venv/bin/python - <<'PY'
    from tests.conformance.correctness_expectations import (
        correctness_scorecard_case,
        tracked_correctness_scorecard_suites,
    )

    suite = tracked_correctness_scorecard_suites()[0]
    target_manifest_id = next(iter(suite.expectation_table))
    expectation = suite.expectation_table[target_manifest_id]

    assert not isinstance(expectation, dict), type(expectation)
    assert expectation.representative_case_ids

    case = correctness_scorecard_case(suite.suite_id, target_manifest_id)
    assert case.representative_cases[0].case_id == expectation.representative_case_ids[0]
    print("ok")
    PY
    ```

## Constraints
- Prefer a small local dataclass or `NamedTuple` expectation surface over another renamed dict-normalization helper. The intended end state is one explicit typed manifest expectation API, not a second helper that still returns anonymous mappings.
- If the implementation keeps the raw expectation tables dict-shaped for brevity, keep that raw store local and convert it once at the public boundary; do not add another registry module or spread this cleanup across more files.
- Preserve the current correctness suite intent and representative-case assertions. This task should change how manifest expectation metadata is represented and consumed, not what the suites verify.

## Notes
- `RBR-0481` is already queued as the ready-head feature task, and the current runtime dashboard is clean (`Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `Last Cycle Anomalies: none`), so rule 10 does not apply.
- No blocked architecture task is waiting to be reopened or normalized in the current checkout.
- JSON counts remain fully burned down in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- `RBR-0482` is unused in `ops/state/backlog.md`, `ops/state/current_status.md`, and the current task queue, so it is the next available architecture id.
- The remaining public correctness expectation coupling is concentrated in three places:
  - `tests/conformance/correctness_expectations.py` still types `CorrectnessScorecardSuiteDefinition.expectation_table` as `dict[str, dict[str, tuple[str, ...]]]`.
  - `tests/conformance/correctness_expectations.py` still reads `expectation["representative_case_ids"]` inside `_build_scorecard_expectation(...)`.
  - `tests/conformance/test_correctness_scorecard_registry_contract.py` still reads `suite.expectation_table[target_manifest_id]["representative_case_ids"]`.
- The public suite expectation probe currently reports `dict` / `dict`, which is the exact shape this task is meant to replace.
- Current file sizes underline why this is still a useful bounded simplification:
  - `tests/conformance/correctness_expectations.py`: `1794` lines
  - `tests/conformance/test_correctness_scorecard_registry_contract.py`: `117` lines
- 2026-03-16 intake verification:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py tests/conformance/test_correctness_scorecard_registry_contract.py` passes in the current checkout (`5 passed, 1183 subtests passed in 25.68s`).
  - `rg -n 'expectation_table: dict\\[str, dict\\[str, tuple\\[str, \\.\\.\\.\\]\\]\\]|expectation\\["representative_case_ids"\\]|suite\\.expectation_table\\[[^]]+\\]\\["representative_case_ids"\\]' tests/conformance/correctness_expectations.py tests/conformance/test_correctness_scorecard_registry_contract.py` currently returns the three matches listed above, which is the exact string-key and dict-typed coupling this task should delete rather than rename.
  - The public typed-record probe above currently fails because `suite.expectation_table[...]` still returns a `dict`, which is the exact public-shape cleanup this task is meant to complete.
