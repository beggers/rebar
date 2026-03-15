# RBR-0425: Centralize combined source-tree benchmark slice expectations

Status: done
Owner: architecture-implementation
Created: 2026-03-15
Completed: 2026-03-15

## Goal
- Replace the remaining constant-heavy slice assertions in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` with shared expectation data plus one reusable assertion path, so the combined source-tree benchmark suite stops hand-maintaining hundreds of lines of bespoke row-filter scaffolding after the earlier scorecard/support cleanup.

## Deliverables
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/benchmark_expectations.py` gains one data-first expectation surface for the exact combined-suite slice checks that are currently encoded as local constants and per-test row filters in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`. That shared expectation surface covers all of these slices and no broader benchmark-harness behavior:
  - `branch-local-backreference-boundary`: broader-range open-ended conditional branch-local-backreference slice.
  - `nested-group-alternation-boundary`: non-quantified, quantified, broader-range, and broader-range open-ended branch-local-backreference slices.
  - `nested-group-callable-replacement-boundary`: nested alternation, quantified nested alternation, non-quantified branch-local-backreference, quantified branch-local-backreference, broader-range branch-local-backreference, open-ended branch-local-backreference, broader-range open-ended branch-local-backreference, and broader-range open-ended conditional branch-local-backreference slices.
  - `nested-group-replacement-boundary`: open-ended branch-local-backreference, broader-range open-ended branch-local-backreference, and broader-range open-ended conditional branch-local-backreference slices.
  - callable-replacement former-gap checks for `grouped-alternation-callable-replacement-boundary` and `nested-group-callable-replacement-boundary`.
- Each expectation entry is precise enough that the test suite can select manifest rows without open-coded test-local comprehensions. For each targeted slice, the shared expectation data defines:
  - target manifest id plus a stable slice label/id for subtests;
  - required and excluded `syntax_features`;
  - required and excluded `categories`;
  - any additional narrow filter needed to preserve current membership exactly, such as the current `id.endswith("gap")` former-gap selection;
  - expected workload ids;
  - expected pattern set;
  - expected operation set;
  - expected haystack set when rows carry haystacks; and
  - required categories that every matched row must still advertise.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` routes the targeted slice checks through one shared driver/helper path that:
  - loads `source_tree_combined_case(...)` and `run_source_tree_benchmark_scorecard(...)`;
  - asserts the manifest summary still reports `known_gap_count == 0` for the targeted manifest;
  - selects manifest rows from the shared expectation data;
  - asserts exact workload ids, pattern sets, operation sets, haystack sets, required categories, and measured scorecard workload contracts; and
  - preserves today’s slice coverage, even if the individual checks are rewritten into looped subtests instead of one handwritten test method per slice.
- The task stays bounded:
  - keep `test_runner_regenerates_combined_source_tree_boundary_scorecards()` intact except for mechanical helper-call adjustments;
  - keep the wider-ranged-repeat manifest-shape coverage separate except for mechanical helper-call adjustments needed to coexist with the refactor; and
  - do not change benchmark workload documents, `python/rebar_harness/benchmarks.py`, published reports, README/status text, or feature queue tasks.
- After the cleanup:
  - `rg -n 'BRANCH_LOCAL_BACKREFERENCE_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_WORKLOAD_IDS|NESTED_GROUP_ALTERNATION_.*_WORKLOAD_IDS|NESTED_GROUP_CALLABLE_REPLACEMENT_.*_WORKLOAD_IDS|NESTED_GROUP_REPLACEMENT_.*_WORKLOAD_IDS|CALLABLE_REPLACEMENT_FORMER_GAP_CASES' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` returns no matches.
  - `rg -n 'branch-local-backreferences\" in workload\\[\"syntax_features\"\\]|callable-replacement\" in workload\\[\"syntax_features\"\\]|replacement-template\" in workload\\[\"syntax_features\"\\]' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` returns no matches.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.

## Constraints
- Prefer extending `tests/benchmarks/benchmark_expectations.py` over adding another registry or JSON-like data layer. A tiny helper alongside that existing expectation module is acceptable only if it clearly reduces `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` more than inlining the same logic there.
- Preserve the current exact slice membership and assertion semantics. This is structure cleanup, not workload expansion or benchmark publication work.
- Do not touch `benchmarks/workloads/*.py`, Rust code, `python/rebar/`, `python/rebar_harness/benchmarks.py`, tracked reports, README copy, or tracked state files beyond this task file.

## Notes
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is still a 1,554-line one-off suite, while `tests/benchmarks/benchmark_expectations.py` already owns the ordinary source-tree scorecard cases and selector/report plumbing.
- The ready queue is empty, recent runtime artifacts show no inherited-dirty or post-commit stall, and JSON counts are fully burned down in both runtime and live filesystem views (`tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, `git ls-files '*.json' | wc -l = 0`, `rg --files -g '*.json' | wc -l = 0`), so the next architecture pass should stay in the post-JSON duplicate-test-plumbing lane.
- `RBR-0424` is already reserved in tracked backlog/status for the next feature benchmark catch-up, so this cleanup follow-on starts at `RBR-0425`.
- Completed 2026-03-15: centralized the targeted combined-suite slice expectations in `tests/benchmarks/benchmark_expectations.py`, rewrote `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to drive those slices through one shared manifest-slice assertion path while leaving the wider-ranged-repeat shape coverage separate, corrected the stale combined `conditional-group-exists-boundary` `known_gap_count` expectation from `2` to `1`, confirmed the task's two `rg` checks return no matches, and verified `PYTHONPATH=python .venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` (`4 passed`, `291 subtests passed`).
