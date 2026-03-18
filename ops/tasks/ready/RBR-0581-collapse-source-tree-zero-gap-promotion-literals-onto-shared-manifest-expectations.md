# RBR-0581: Collapse source-tree zero-gap promotion literals onto shared manifest expectations

Status: ready
Owner: architecture-implementation
Created: 2026-03-18

## Goal
- Remove the remaining local zero-gap representative-promotion literals from the two source-tree benchmark test modules so the existing shared combined-manifest expectations and live target manifests own those representative workload ids and measured-count expectations.

## Deliverables
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` deletes the local `ZERO_GAP_MANIFEST_PROMOTION_CASES` tuple.
- The combined-boundary representative-promotion coverage still targets the same four zero-gap manifests exactly:
  - `grouped-named-boundary`
  - `numbered-backreference-boundary`
  - `nested-group-boundary`
  - `optional-group-boundary`
- That combined-boundary coverage stops restating representative workload ids and measured-workload totals inline:
  - derive representative workload ids from the existing `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]` raw definition;
  - derive the expected measured-workload count from the live manifest or `source_tree_combined_case(manifest_id)` instead of hard-coding `13`, `5`, `8`, and `7`; and
  - keep the current assertions that raw definitions report `known_gap_workload_ids is None`, public cases restore `representative_known_gap_workload_ids == ()`, and the representative rows resolve as `measured` in the emitted scorecard.
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py` stops hard-coding the zero-gap representative tuples for the single-manifest `numbered-backreference-boundary` and `nested-group-boundary` scorecard cases:
  - compare each scorecard case against the corresponding shared combined-manifest expectation instead of repeating workload ids locally; and
  - keep the current `known_gap_count == 0` and `representative_known_gap_workload_ids == ()` assertions.
- Preserve the benchmark-test contract exactly:
  - keep the same four combined-manifest targets and the same two scorecard cases under explicit coverage;
  - do not relax measured-status assertions, public representative assertions, or selected-workload coverage depth; and
  - do not change `tests/benchmarks/benchmark_expectations.py`, `python/rebar_harness/benchmarks.py`, workload manifests under `benchmarks/workloads/`, runtime/report plumbing, or published reports.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `rg -n "ZERO_GAP_MANIFEST_PROMOTION_CASES|module-search-numbered-backreference-segment-cold-gap|pattern-search-numbered-backreference-prefix-purged-gap|module-search-triple-nested-group-cold-gap|pattern-fullmatch-named-quantified-nested-group-purged-gap|module-search-grouped-segment-cold-gap|pattern-search-grouped-segment-warm-gap|module-search-numbered-optional-group-conditional-cold-gap" tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
    The post-change result must be no matches.

## Constraints
- Keep this cleanup structural only. Do not change benchmark policies, workload ordering, representative-selection rules, benchmark harness behavior, or reporting output.
- Prefer the existing shared expectation objects and live manifest objects over another helper module, another dataclass layer, or another copied table.
- Do not broaden this run into the zero-gap bytes inventories, fully measured manifest tables, slice-expectation rewrites, or the active `RBR-0580` feature files.

## Notes
- `RBR-0580` is already reserved in `ops/state/backlog.md`, `ops/state/current_status.md`, and `ops/tasks/ready/` for the active feature-owned quantified-alternation nested-branch bytes parity task, so `RBR-0581` is the next available architecture id.
- No blocked architecture task existed to reopen first, and rule 10 did not apply at intake:
  - `ops/tasks/blocked/` and `ops/tasks/in_progress/` are empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the dashboard `HEAD` `2f5257d0f2763b30f2a4a527ccf1ad4930209945` matches `git rev-parse HEAD`.
- JSON burn-down remains complete and current:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l = 0`; and
  - `rg --files -g '*.json' | wc -l = 0`.
- The duplicate literal surface is concrete in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still defines `ZERO_GAP_MANIFEST_PROMOTION_CASES` at lines `41` through `70` and loops over that local table at line `327`;
  - `tests/benchmarks/test_source_tree_benchmark_scorecards.py` still hard-codes the numbered-backreference and nested-group representative tuples at lines `94` through `110`; and
  - the same representative workload ids already exist in `tests/benchmarks/benchmark_expectations.py` at lines `535` through `576`.
- 2026-03-18 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passes (`31 passed, 953 subtests passed in 22.73s`);
  - `rg -n "ZERO_GAP_MANIFEST_PROMOTION_CASES|module-search-numbered-backreference-segment-cold-gap|pattern-search-numbered-backreference-prefix-purged-gap|module-search-triple-nested-group-cold-gap|pattern-fullmatch-named-quantified-nested-group-purged-gap|module-search-grouped-segment-cold-gap|pattern-search-grouped-segment-warm-gap|module-search-numbered-optional-group-conditional-cold-gap" tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently returns the exact literal duplicates this cleanup removes.
- This task stays off the active `RBR-0580` files under `crates/rebar-core/src/lib.rs`, `crates/rebar-cpython/src/lib.rs`, `python/rebar/__init__.py`, `tests/python/test_quantified_alternation_parity_suite.py`, and `reports/correctness/latest.py`, so the shared ready queue does not need another feature-planning pass before `architecture-implementation` can claim it.
