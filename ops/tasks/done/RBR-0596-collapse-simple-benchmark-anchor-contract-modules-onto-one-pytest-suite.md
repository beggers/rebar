# RBR-0596: Collapse the remaining simple benchmark anchor contract modules onto one pytest suite

Status: done
Owner: architecture-implementation
Created: 2026-03-18

## Goal
- Replace the three remaining singleton benchmark anchor contract modules with one parameterized pytest suite so this harness layer stops repeating the same manifest-path setup, signature mapping, anchor lookup wrappers, and exact-case-id assertions across small file-local `unittest` classes.

## Deliverables
- `tests/benchmarks/test_simple_benchmark_correctness_anchor_contracts.py`
- Delete `tests/benchmarks/test_optional_group_benchmark_correctness_anchor_contract.py`
- Delete `tests/benchmarks/test_compile_proxy_correctness_anchor_contract.py`
- Delete `tests/benchmarks/test_nested_group_benchmark_correctness_anchor_contract.py`

## Acceptance Criteria
- The new suite covers exactly the three current singleton anchor-contract surfaces and no broader benchmark families:
  - compile-proxy anchor coverage for `benchmarks/workloads/compile_matrix.py` plus `benchmarks/workloads/regression_matrix.py`;
  - optional-group conditional anchor coverage for `benchmarks/workloads/optional_group_boundary.py`; and
  - measured nested-group anchor coverage for `benchmarks/workloads/nested_group_boundary.py`.
- One local definition table in `tests/benchmarks/test_simple_benchmark_correctness_anchor_contracts.py` owns the suite-specific metadata that is currently split across the three superseded modules:
  - the manifest path or paths under test;
  - the exact expected anchored case-id map for each scoped manifest/workload pair;
  - the workload-scope rule for each surface, including the nested-group excluded gap pair and the current compile-proxy `compile` / `module.compile` inclusion behavior;
  - the correctness-case and workload signature functions required for each surface; and
  - whether that surface should run anchored callback-result parity in addition to the anchor lookup assertions.
- The consolidation preserves current behavior exactly:
  - compile-proxy coverage keeps the current nine anchored rows across `compile_matrix.py` and `regression_matrix.py`, preserves the exact `EXPECTED_COMPILE_ANCHOR_CASE_IDS` mapping, and does not silently widen scope into non-compile rows or unrelated regression workloads;
  - optional-group coverage keeps only the existing `module-search-numbered-optional-group-conditional-cold-gap` row in scope and preserves its exact anchored correctness case id;
  - nested-group coverage keeps `module-search-triple-nested-group-cold-gap` and `pattern-fullmatch-named-quantified-nested-group-purged-gap` out of scope, preserves the current measured-workload order and exact anchored case-id map, and keeps direct CPython callback-result parity for the measured rows; and
  - optional-group coverage keeps its current direct anchored-result parity check instead of dropping it during consolidation.
- The consolidation stays on the existing benchmark-anchor support path:
  - continue using `load_manifest(...)`, `anchored_workload_case_ids(...)`, `unanchored_workload_ids(...)`, `published_case_ids_by_signature(...)`, and `expected_anchored_workload_case_pairs(...)`;
  - prefer one ordinary parametrized pytest module over three thin wrappers or a new helper package; and
  - do not widen scope into `benchmarks/workloads/`, `python/rebar_harness/`, published reports, README/status files, or feature/parity behavior.
- After the consolidation lands, `rg --files tests/benchmarks | rg 'test_(optional_group_benchmark_correctness_anchor_contract|nested_group_benchmark_correctness_anchor_contract|compile_proxy_correctness_anchor_contract)\\.py$'` returns no matches.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_simple_benchmark_correctness_anchor_contracts.py`
  - `bash -lc "! rg --files tests/benchmarks | rg 'test_(optional_group_benchmark_correctness_anchor_contract|nested_group_benchmark_correctness_anchor_contract|compile_proxy_correctness_anchor_contract)\\.py$'"`

## Constraints
- Keep this cleanup structural only. Do not change workload rows, anchored case ids, published benchmark totals, correctness fixtures, or queue/state prose.
- Prefer the same local-definition-table style already used by `tests/benchmarks/test_counted_repeat_benchmark_correctness_anchor_contract.py` and `tests/benchmarks/test_grouped_alternation_benchmark_correctness_anchor_contract.py` instead of inventing another generic registry layer.
- Keep any compile-proxy special handling minimal and local to the new suite if the current helper surface still treats raw `compile` workloads differently from `module.compile`; do not broaden this task into a larger `correctness_anchor_support.py` redesign.

## Notes
- `RBR-0595` is already reserved in `ops/state/backlog.md`, `ops/state/current_status.md`, and `ops/tasks/ready/` for the active quantified-alternation branch-local-backreference bytes publication task, so `RBR-0596` is the next available architecture id.
- No blocked architecture task exists to reopen first, and rule 10 does not apply in the live checkout:
  - `ops/tasks/blocked/` and `ops/tasks/in_progress/` are empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - recent runtime state shows both task workers completing normally in the latest recorded cycle rather than churning inherited-dirty or post-commit refresh failures.
- The runtime dashboard lags the live checkout head in this run, so JSON state was cross-checked live before seeding this task:
  - `.rebar/runtime/dashboard.md` still reports `HEAD: ee9dafc4db9e41acd18c85adf8752ad4cacee881`;
  - `git rev-parse HEAD` returned `67a6b5a0b29cb3550a01fb40dd09b83a170d8118`; and
  - both `git ls-files '*.json' | wc -l` and `rg --files -g '*.json' | wc -l` returned `0`.
- The duplicate simple-anchor surface is concrete in the current checkout:
  - `tests/benchmarks/test_optional_group_benchmark_correctness_anchor_contract.py`, `tests/benchmarks/test_compile_proxy_correctness_anchor_contract.py`, and `tests/benchmarks/test_nested_group_benchmark_correctness_anchor_contract.py` currently total `463` lines;
  - all three files repeat the same anchor-contract skeleton: repo-root/manifest path setup, file-local correctness and workload signature helpers, thin `anchored_workload_case_ids(...)` / `unanchored_workload_ids(...)` wrappers, and three or four assertions around in-scope workload ids, anchored-case lookup completeness, and exact pinned case ids; and
  - the larger neighboring benchmark anchor suites have already converged on the intended local-definition-table shape in `tests/benchmarks/test_counted_repeat_benchmark_correctness_anchor_contract.py` and `tests/benchmarks/test_grouped_alternation_benchmark_correctness_anchor_contract.py`.
- 2026-03-18 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_compile_proxy_correctness_anchor_contract.py tests/benchmarks/test_optional_group_benchmark_correctness_anchor_contract.py tests/benchmarks/test_nested_group_benchmark_correctness_anchor_contract.py` passes (`10 passed, 6 subtests passed in 0.08s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_simple_benchmark_correctness_anchor_contracts.py` currently fails exactly on this cleanup with `ERROR: file or directory not found: tests/benchmarks/test_simple_benchmark_correctness_anchor_contracts.py`; and
  - `bash -lc "! rg --files tests/benchmarks | rg 'test_(optional_group_benchmark_correctness_anchor_contract|nested_group_benchmark_correctness_anchor_contract|compile_proxy_correctness_anchor_contract)\\.py$'"` currently fails exactly on this cleanup because all three superseded files still exist.

## Completion Notes
- Added `tests/benchmarks/test_simple_benchmark_correctness_anchor_contracts.py` as one parameterized pytest suite with a single local definition table for the compile-proxy, optional-group conditional, and measured nested-group anchor-contract surfaces.
- Kept the exact compile-proxy nine-row anchor map across `benchmarks/workloads/compile_matrix.py` and `benchmarks/workloads/regression_matrix.py`, preserved the optional-group conditional single-row scope and direct parity check, and preserved the nested-group measured-row order plus exclusion of `module-search-triple-nested-group-cold-gap` and `pattern-fullmatch-named-quantified-nested-group-purged-gap`.
- Deleted `tests/benchmarks/test_compile_proxy_correctness_anchor_contract.py`, `tests/benchmarks/test_optional_group_benchmark_correctness_anchor_contract.py`, and `tests/benchmarks/test_nested_group_benchmark_correctness_anchor_contract.py`; `git diff --name-status -- ...` now reports each path as `D`.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_simple_benchmark_correctness_anchor_contracts.py` (`13 passed in 0.08s`) and `bash -lc "! rg --files tests/benchmarks | rg 'test_(optional_group_benchmark_correctness_anchor_contract|nested_group_benchmark_correctness_anchor_contract|compile_proxy_correctness_anchor_contract)\\.py$'"` (no matches).
