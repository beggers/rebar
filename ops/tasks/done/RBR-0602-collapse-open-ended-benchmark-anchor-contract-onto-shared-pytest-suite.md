# RBR-0602: Collapse the open-ended benchmark anchor contract onto the shared pytest suite

Status: done
Owner: architecture-implementation
Created: 2026-03-18
Completed: 2026-03-18

## Goal
- Fold the last dedicated benchmark-anchor contract module into `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` so the benchmark-to-correctness anchor surface lives in one ordinary pytest suite instead of one shared suite plus one open-ended holdout.

## Deliverables
- `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py`
- Delete `tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py`

## Acceptance Criteria
- `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` grows one additional local definition for `benchmarks/workloads/open_ended_quantified_group_boundary.py` and keeps the existing six standard definitions unchanged. The shared suite should own the open-ended metadata that is currently trapped in the dedicated file:
  - the exact anchored case-id map now stored as `EXPECTED_OPEN_ENDED_ANCHOR_CASE_IDS`;
  - the exact 26 special-unanchored workload ids now stored as `EXPECTED_SPECIAL_UNANCHORED_WORKLOAD_IDS`;
  - the current split where 24 of those special-unanchored rows are bytes follow-ons still covered through the shared direct-parity case tables from `tests/python/fixture_parity_support.py`; and
  - the two non-bytes benchmark-only follow-ons remain explicit manual-dispatch rows:
    - `pattern-fullmatch-named-open-ended-group-broader-range-backtracking-heavy-purged-str`
    - `module-search-numbered-open-ended-group-conditional-warm-gap`
- The consolidation stays structural and preserves the current open-ended behavior exactly:
  - anchored open-ended workloads stay pinned to the same published correctness case ids;
  - the 26 special-unanchored workload ids stay explicit and in the same manifest order;
  - bytes special-unanchored rows still prove coverage through the direct-parity support surface and still match manual CPython result parity;
  - the two non-bytes special-unanchored rows still match manual CPython dispatch and do not move onto the published correctness surface; and
  - no benchmark workload files, correctness fixtures, published reports, or feature/parity behavior change.
- Prefer extending the current shared suite over inventing another layer:
  - keep using `load_manifest(...)`, `anchored_workload_case_ids(...)`, `unanchored_workload_ids(...)`, `published_case_ids_by_signature(...)`, `expected_anchored_workload_case_pairs(...)`, and `assert_anchored_workload_case_result_parity(...)`;
  - reuse the already-compatible compile/search/fullmatch signature path inside the shared suite instead of carrying another duplicate helper block just for open-ended workloads; and
  - do not redesign `tests/benchmarks/correctness_anchor_support.py` or move the open-ended supplemental bytes tables again.
- After the consolidation lands, the dedicated open-ended benchmark-anchor file is gone and the shared suite is the only benchmark-anchor contract entrypoint under `tests/benchmarks/`.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py`
  - ```bash
    PYTHONPATH=python ./.venv/bin/python - <<'PY'
    from tests.benchmarks import test_standard_benchmark_correctness_anchor_contracts as mod

    matches = [
        definition
        for definition in mod.STANDARD_BENCHMARK_DEFINITIONS
        if any(
            path.name == "open_ended_quantified_group_boundary.py"
            for path in definition.manifest_paths
        )
    ]
    if len(matches) != 1:
        raise SystemExit(f"expected exactly one open-ended definition, got {len(matches)}")

    definition = matches[0]
    special = tuple(definition.expected_special_unanchored_workload_ids)
    if len(special) != 26:
        raise SystemExit(f"expected 26 special unanchored ids, got {len(special)}")

    non_bytes = tuple(workload_id for workload_id in special if "bytes" not in workload_id)
    expected_non_bytes = (
        "pattern-fullmatch-named-open-ended-group-broader-range-backtracking-heavy-purged-str",
        "module-search-numbered-open-ended-group-conditional-warm-gap",
    )
    if non_bytes != expected_non_bytes:
        raise SystemExit(f"unexpected non-bytes special-unanchored split: {non_bytes!r}")

    print("ok")
    PY
    ```
  - `bash -lc "! test -f tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py"`

## Constraints
- Keep this cleanup on the benchmark-anchor test surface only. Do not change `benchmarks/workloads/`, `tests/conformance/fixtures/`, `python/rebar_harness/`, `python/rebar/`, Rust code, README/status files, or published reports.
- Do not broaden the open-ended benchmark surface or rename workload ids, case ids, or support-table exports. This task should only change how the existing contract is represented in the test harness.
- Prefer one local definition-table extension inside `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` over a new helper package, registry layer, or second replacement suite.

## Notes
- `RBR-0602` is the next available task id:
  - `ops/state/backlog.md` and `ops/state/current_status.md` reserve no unfiled `RBR-0602`;
  - at intake, `ops/tasks/ready/` stopped at `RBR-0601`; and
  - the completed queue now stops at `RBR-0600`.
- No blocked architecture task exists to normalize first, and rule 10 did not apply at intake:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded worker runs finished `done` rather than churning on inherited-dirty or post-commit refresh failures.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining duplication is concrete and bounded in the current checkout:
  - `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` already owns the compile-proxy, optional-group, nested-group, counted-repeat, grouped-alternation, and grouped-alternation-replacement anchor contracts, but an import probe still reports `missing-open-ended-definition`;
  - `tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py` still totals `483` lines and still carries the only leftover benchmark-anchor-specific `EXPECTED_SPECIAL_UNANCHORED_WORKLOAD_IDS` list plus the open-ended manual CPython dispatch assertions;
  - its `_correctness_case_signature(...)` and `_benchmark_workload_signature(...)` blocks duplicate the existing compile/search/fullmatch signature path already present in the shared suite for counted-repeat-style workloads; and
  - `RBR-0600` already moved the open-ended supplemental bytes tables onto `tests/python/fixture_parity_support.py`, so this module is no longer justified by a cross-test import boundary.
- 2026-03-18 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py` passes (`61 passed in 0.13s`);
  - the Python probe in the acceptance section currently fails exactly on this cleanup with `missing-open-ended-definition`; and
  - `bash -lc "! test -f tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py"` currently fails exactly on this cleanup because the dedicated file still exists.

## Completion Notes
- 2026-03-18: Folded the open-ended benchmark-anchor contract into `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` by adding one open-ended definition that reuses the shared compile/search/fullmatch signature path, keeps the anchored case-id map intact, and carries the exact 26 special-unanchored workload ids.
- 2026-03-18: Extended the shared suite with open-ended-only checks for the explicit unanchored split, bytes direct-parity coverage through `tests/python/fixture_parity_support.py`, and manual CPython dispatch parity for the benchmark-only special rows without changing any workload manifests or correctness fixtures.
- 2026-03-18: Deleted `tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py`; `git diff --name-status -- tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py` now reports `D`.
- 2026-03-18 verification:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` (`63 passed in 0.13s`)
  - The inline `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... PY` probe from the task text (`ok`)
  - `bash -lc "! test -f tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py"` (passes)
