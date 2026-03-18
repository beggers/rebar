# RBR-0600: Decouple the open-ended benchmark anchor contract from the parity suite

Status: done
Owner: architecture-implementation
Created: 2026-03-18
Completed: 2026-03-18

## Goal
- Move the shared open-ended supplemental bytes case tables onto the existing fixture-support path so the last bespoke benchmark anchor-contract module stops importing another test module for expected-result data.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_open_ended_quantified_group_parity_suite.py`
- `tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py`

## Acceptance Criteria
- `tests/python/fixture_parity_support.py` becomes the shared owner of the open-ended supplemental-bytes surface that is currently trapped inside `tests/python/test_open_ended_quantified_group_parity_suite.py`:
  - move `SupplementalCase`;
  - move the seven current open-ended `*_BYTES_CASES` tables without changing case ids, pattern payloads, search/fullmatch texts, or unsupported-backend markers:
    - `OPEN_ENDED_ALTERNATION_BYTES_CASES`
    - `NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES`
    - `OPEN_ENDED_CONDITIONAL_BYTES_CASES`
    - `OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES`
    - `BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES`
    - `BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES`
    - `BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES`
  - move the current direct-follow-on spec metadata unchanged, including the exact four ids and manifest pairings:
    - `broader-range-alternation` -> `broader-range-open-ended-quantified-group-alternation-workflows`
    - `open-ended-backtracking-heavy` -> `open-ended-quantified-group-alternation-backtracking-heavy-workflows`
    - `broader-range-conditional` -> `broader-range-open-ended-quantified-group-alternation-conditional-workflows`
    - `broader-range-backtracking-heavy` -> `broader-range-open-ended-quantified-group-alternation-backtracking-heavy-workflows`
- `tests/python/test_open_ended_quantified_group_parity_suite.py` imports and reuses that shared support surface instead of defining `SupplementalCase`, the seven `*_BYTES_CASES` tables, or `DIRECT_BYTES_FOLLOW_ON_SPECS` locally. Preserve the current parity behavior exactly:
  - keep the same direct-bytes follow-on routing and generic-case-bucket partitioning;
  - keep the same trace bundles, trace-case builders, and bytes-versus-`str` parity coverage; and
  - do not widen or shrink the published open-ended parity frontier.
- `tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py` stops importing from `tests.python.test_open_ended_quantified_group_parity_suite` and builds its direct-bytes signature lookup from the shared support surface instead. Preserve the current benchmark-anchor behavior exactly:
  - keep `EXPECTED_SPECIAL_UNANCHORED_WORKLOAD_IDS` unchanged;
  - keep the anchored case-id map unchanged;
  - keep the current split between anchored workloads, bytes direct-parity follow-ons, and the two `str` manual-dispatch follow-ons; and
  - keep the same CPython result-parity behavior for anchored and special-unanchored workloads.
- `tests/python/test_fixture_parity_support_contract.py` gains or updates focused coverage that locks the new shared boundary in place:
  - the shared support surface still exports the same supplemental case ids in the same order for the seven `*_BYTES_CASES` tables; and
  - the shared direct-follow-on spec ids still point at the same four manifest ids.
- Keep this cleanup structural only:
  - do not change correctness fixtures under `tests/conformance/fixtures/`;
  - do not change benchmark workload files under `benchmarks/workloads/`;
  - do not move the benchmark-only unanchored workloads onto the published correctness surface; and
  - do not touch published reports, README/status files, Rust code, or `python/rebar/`.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_open_ended_quantified_group_parity_suite.py tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py`
  - ```bash
    python3 - <<'PY'
    from pathlib import Path

    checks = {
        'tests/python/fixture_parity_support.py': {
            'must_have': [
                'class SupplementalCase:',
                'OPEN_ENDED_ALTERNATION_BYTES_CASES = (',
                'DIRECT_BYTES_FOLLOW_ON_SPECS = (',
            ],
            'must_not_have': [],
        },
        'tests/python/test_open_ended_quantified_group_parity_suite.py': {
            'must_have': [],
            'must_not_have': [
                'class SupplementalCase:',
                'OPEN_ENDED_ALTERNATION_BYTES_CASES = (',
                'DIRECT_BYTES_FOLLOW_ON_SPECS = (',
            ],
        },
        'tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py': {
            'must_have': [],
            'must_not_have': [
                'from tests.python.test_open_ended_quantified_group_parity_suite import',
            ],
        },
    }

    failures = []
    for path_str, expectation in checks.items():
        text = Path(path_str).read_text()
        for needle in expectation['must_have']:
            if needle not in text:
                failures.append(f'{path_str}:missing:{needle}')
        for needle in expectation['must_not_have']:
            if needle in text:
                failures.append(f'{path_str}:still-local:{needle}')

    if failures:
        raise SystemExit('\n'.join(failures))

    print('ok')
    PY
    ```

## Constraints
- Prefer the existing `tests/python/fixture_parity_support.py` module over adding another support package or duplicating the supplemental bytes tables in both suites.
- Keep helper names and exported table names stable unless the updated fixture-support contract test proves the replacement surface unambiguously in the same run.
- Do not broaden this cleanup into scorecard publication, correctness-manifest reshaping, or a general rewrite of `tests/benchmarks/correctness_anchor_support.py`.

## Notes
- `RBR-0600` is the next available task id: `ops/state/backlog.md`, `ops/state/current_status.md`, the live ready queue, and the completed queue stop at `RBR-0599`, and no higher reserved `RBR-` id is named in the tracked planning/state files.
- No blocked architecture task exists to normalize first, and rule 10 does not apply in the current checkout:
  - `ops/tasks/blocked/` and `ops/tasks/in_progress/` are empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the dashboard `HEAD` `2eaa5dadd14979b2ba5c4a6da3f28cf18b58c16b` matches `git rev-parse HEAD`.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining architecture drift is concrete and bounded in the current checkout:
  - `tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py` still carries the repo's only cross-test import at line `26`, pulling six bytes supplemental tables from `tests/python/test_open_ended_quantified_group_parity_suite.py`;
  - `tests/python/test_open_ended_quantified_group_parity_suite.py` still owns `SupplementalCase` plus the seven open-ended `*_BYTES_CASES` tables and `DIRECT_BYTES_FOLLOW_ON_SPECS`, so benchmark support depends on a sibling parity test module instead of the shared fixture-support layer that already owns direct-bytes routing helpers; and
  - the benchmark module still reindexes that imported data through `_direct_parity_bytes_case_ids_by_signature()` just to validate special unanchored workload coverage, which is the boundary this cleanup should collapse.
- 2026-03-18 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_open_ended_quantified_group_parity_suite.py tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py` passes (`4052 passed in 2.76s`);
  - the Python probe above currently fails exactly on this cleanup with:
    - `tests/python/fixture_parity_support.py:missing:class SupplementalCase:`
    - `tests/python/fixture_parity_support.py:missing:OPEN_ENDED_ALTERNATION_BYTES_CASES = (`
    - `tests/python/fixture_parity_support.py:missing:DIRECT_BYTES_FOLLOW_ON_SPECS = (`
    - `tests/python/test_open_ended_quantified_group_parity_suite.py:still-local:class SupplementalCase:`
    - `tests/python/test_open_ended_quantified_group_parity_suite.py:still-local:OPEN_ENDED_ALTERNATION_BYTES_CASES = (`
    - `tests/python/test_open_ended_quantified_group_parity_suite.py:still-local:DIRECT_BYTES_FOLLOW_ON_SPECS = (`
    - `tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py:still-local:from tests.python.test_open_ended_quantified_group_parity_suite import`

## Completion Notes
- 2026-03-18: Moved `SupplementalCase`, the seven open-ended `*_BYTES_CASES` tables, and the direct-bytes follow-on id-to-manifest metadata onto `tests/python/fixture_parity_support.py`, keeping the existing case ids, payloads, and four manifest pairings unchanged.
- 2026-03-18: Updated `tests/python/test_open_ended_quantified_group_parity_suite.py` to import the shared support surface and resolve the shared follow-on specs back onto the already-loaded fixture bundles without changing the existing direct-bytes routing or generic bucket partitioning.
- 2026-03-18: Updated `tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py` to source its direct bytes signature data from `tests/python/fixture_parity_support.py`, removing the remaining cross-test import from the benchmark anchor contract.
- 2026-03-18: Added focused coverage in `tests/python/test_fixture_parity_support_contract.py` that locks the seven supplemental bytes case-id orders and the four direct-follow-on id-to-manifest mappings in place.
- 2026-03-18 verification:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_open_ended_quantified_group_parity_suite.py tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py` (`4060 passed in 2.82s`)
  - The inline `python3` ownership probe from the task text (`ok`)
