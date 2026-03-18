# RBR-0598: Collapse the remaining non-open-ended benchmark anchor contract modules onto one pytest suite

Status: ready
Owner: architecture-implementation
Created: 2026-03-18

## Goal
- Replace the three remaining non-bespoke benchmark anchor-contract modules with one parameterized pytest suite so this benchmark-to-correctness boundary stops repeating the same manifest-path setup, definition dataclasses, signature helpers, anchor lookup wrappers, legacy-workload filters, and callback parity loops across multiple files.

## Deliverables
- `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py`
- Delete `tests/benchmarks/test_simple_benchmark_correctness_anchor_contracts.py`
- Delete `tests/benchmarks/test_counted_repeat_benchmark_correctness_anchor_contract.py`
- Delete `tests/benchmarks/test_grouped_alternation_benchmark_correctness_anchor_contract.py`

## Acceptance Criteria
- The new suite covers exactly the three current non-open-ended benchmark anchor-contract surfaces and does not absorb the bespoke open-ended module:
  - the current compile-proxy, optional-group, and measured nested-group coverage from `tests/benchmarks/test_simple_benchmark_correctness_anchor_contracts.py`;
  - the exact-repeat and ranged-repeat non-alternation coverage from `tests/benchmarks/test_counted_repeat_benchmark_correctness_anchor_contract.py`; and
  - the grouped-alternation and grouped-alternation replacement coverage from `tests/benchmarks/test_grouped_alternation_benchmark_correctness_anchor_contract.py`.
- One local definition table in `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` owns the suite-specific metadata that is currently split across the superseded modules:
  - manifest path or paths under test;
  - the exact expected anchored case-id map for each scoped manifest/workload pair;
  - workload inclusion or exclusion rules for each surface;
  - correctness-case and workload signature functions for each surface;
  - whether that surface runs callback-result parity;
  - the expected excluded workload ids for surfaces that intentionally keep specific rows out of scope; and
  - the expected legacy-workload ids, legacy anchor-case maps, and callback anchor-case maps for surfaces that still pin those transitional rows explicitly.
- The consolidation preserves current behavior exactly for the existing simple suite surface:
  - compile-proxy coverage keeps the current nine anchored rows across `benchmarks/workloads/compile_matrix.py` and `benchmarks/workloads/regression_matrix.py` and does not widen into unrelated workloads;
  - optional-group coverage keeps only `module-search-numbered-optional-group-conditional-cold-gap` in scope and keeps its direct anchored-result parity check; and
  - nested-group coverage keeps `module-search-triple-nested-group-cold-gap` and `pattern-fullmatch-named-quantified-nested-group-purged-gap` out of scope, preserves the exact anchored case-id map, and keeps direct CPython callback-result parity for the measured rows.
- The consolidation preserves current behavior exactly for the counted-repeat surface:
  - exact-repeat and ranged-repeat coverage keep the current non-alternation workload filter on `module.compile`, `module.search`, and `pattern.fullmatch` rows only;
  - both manifests still report zero unanchored in-scope workload ids;
  - the exact anchored case-id maps stay unchanged, including the broader-range gap rows that remain pinned to the current wider-ranged-repeat correctness cases; and
  - direct CPython callback-result parity still runs for both counted-repeat definitions.
- The consolidation preserves current behavior exactly for the grouped-alternation surface:
  - `benchmarks/workloads/grouped_alternation_boundary.py` keeps the current legacy wrapper workload ids, exact anchored case-id map, exact legacy-wrapper anchor map, and callback-result parity limited to the legacy wrapper rows;
  - `benchmarks/workloads/grouped_alternation_replacement_boundary.py` keeps the current legacy nested workload ids, exact anchored case-id map, exact legacy nested anchor map, and callback-result parity on the full replacement anchor map; and
  - the new suite does not silently widen grouped-alternation scope into callable-replacement or nested-group benchmark families.
- The consolidation stays on the existing benchmark-anchor support path:
  - continue using `load_manifest(...)`, `anchored_workload_case_ids(...)`, `unanchored_workload_ids(...)`, `published_case_ids_by_signature(...)`, `expected_anchored_workload_case_pairs(...)`, and `assert_anchored_workload_case_result_parity(...)`;
  - prefer one ordinary parametrized pytest module over another helper package, registry layer, or support-file redesign; and
  - do not widen scope into `benchmarks/workloads/`, `python/rebar_harness/`, published reports, README/status files, or feature/parity behavior.
- After the consolidation lands, `rg --files tests/benchmarks | rg 'test_(simple_benchmark_correctness_anchor_contracts|counted_repeat_benchmark_correctness_anchor_contract|grouped_alternation_benchmark_correctness_anchor_contract)\\.py$'` returns no matches.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py`
  - `bash -lc "! rg --files tests/benchmarks | rg 'test_(simple_benchmark_correctness_anchor_contracts|counted_repeat_benchmark_correctness_anchor_contract|grouped_alternation_benchmark_correctness_anchor_contract)\\.py$'"`

## Constraints
- Keep this cleanup structural only. Do not change workload rows, anchored case ids, published benchmark totals, correctness fixtures, or `tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py`.
- Leave the open-ended benchmark anchor coverage separate in this run. Its special unanchored workload list, direct parity-case imports, and manual CPython dispatch are intentionally out of scope for this consolidation.
- Prefer the same local-definition-table style already used in `tests/benchmarks/test_simple_benchmark_correctness_anchor_contracts.py`; do not turn this into a new generic abstraction layer.

## Notes
- `RBR-0598` is the next available task id: `ops/state/backlog.md` and `ops/state/current_status.md` reserve no unfiled higher-priority `RBR-` ids, and the existing queue stops at `RBR-0597`.
- No blocked architecture task exists to reopen first, and rule 10 does not apply in the current checkout:
  - `ops/tasks/blocked/` and `ops/tasks/in_progress/` are empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - recent runtime state shows both task workers finishing normally in the latest cycle rather than churning inherited-dirty or post-commit refresh failures.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplicate benchmark anchor-contract surface is concrete in the current checkout:
  - `tests/benchmarks/test_simple_benchmark_correctness_anchor_contracts.py`, `tests/benchmarks/test_counted_repeat_benchmark_correctness_anchor_contract.py`, and `tests/benchmarks/test_grouped_alternation_benchmark_correctness_anchor_contract.py` currently total `1151` lines;
  - all three files import `load_manifest` plus the same `tests/benchmarks/correctness_anchor_support.py` primitives and repeat file-local manifest constants, local definition records, anchored/unanchored lookup wrappers, and pinned-case assertions over the same benchmark-to-correctness join; and
  - `tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py` is intentionally excluded because it still owns special unanchored workload ids, imports bytes direct-parity case bundles from `tests/python/test_open_ended_quantified_group_parity_suite.py`, and exercises manual CPython dispatch for those benchmark-only follow-ons.
- 2026-03-18 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_simple_benchmark_correctness_anchor_contracts.py tests/benchmarks/test_counted_repeat_benchmark_correctness_anchor_contract.py tests/benchmarks/test_grouped_alternation_benchmark_correctness_anchor_contract.py` passes (`31 passed in 0.10s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` currently fails exactly on this cleanup with `ERROR: file or directory not found: tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py`; and
  - `bash -lc "! rg --files tests/benchmarks | rg 'test_(simple_benchmark_correctness_anchor_contracts|counted_repeat_benchmark_correctness_anchor_contract|grouped_alternation_benchmark_correctness_anchor_contract)\\.py$'"` currently fails exactly on this cleanup because all three superseded files still exist.
