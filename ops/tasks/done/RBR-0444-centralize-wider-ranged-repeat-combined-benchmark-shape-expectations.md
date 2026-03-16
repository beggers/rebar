# RBR-0444: Centralize wider-ranged-repeat combined benchmark shape expectations

Status: done
Owner: architecture-implementation
Created: 2026-03-16
Completed: 2026-03-16

## Goal
- Replace the last wider-ranged-repeat-specific manifest-shape constants and helper path in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` with shared expectation data in `tests/benchmarks/benchmark_expectations.py`, so the combined source-tree benchmark suite stops carrying one bespoke benchmark-slice block after `RBR-0425`.

## Deliverables
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/benchmark_expectations.py` gains one shared expectation surface for the current `wider-ranged-repeat-quantified-group-boundary` combined-suite shape coverage. That shared surface owns both:
  - the current `WIDER_RANGED_REPEAT_REPRESENTATIVE_MEASURED_WORKLOAD_IDS`; and
  - the current three grouped pattern-shape checks, without broadening them into other manifests:
    - nested broader-range grouped alternation for `a((bc|de){1,4})d` and `a(?P<outer>(bc|de){1,4})d`
    - nested broader-range grouped conditional for `a(((bc|de){1,4})d)?(?(1)e|f)` and `a(?P<outer>((bc|de){1,4})d)?(?(outer)e|f)`
    - nested broader-range grouped backtracking-heavy for `a(((bc|b)c){1,4})d` and `a(?P<outer>((bc|b)c){1,4})d`
- For each shared pattern-group expectation, the data is precise enough that the test no longer open-codes the current local dictionaries. Each entry defines all of the current shape requirements:
  - stable label or slice id
  - pattern tuple
  - `minimum_rows`
  - required operations
  - required categories
  - exact module-search haystacks and/or required module-search haystack substrings, matching today's semantics
  - exact `pattern.fullmatch` haystacks
- If a helper is needed in `tests/benchmarks/benchmark_expectations.py`, keep it limited to selecting or validating these shared wider-ranged-repeat pattern groups from a manifest document. Prefer extending the existing combined-suite expectation style over adding another registry, support module, or generated data file.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` routes the wider-ranged-repeat manifest-shape test through that shared expectation surface instead of the current local `WIDER_RANGED_REPEAT_REPRESENTATIVE_MEASURED_WORKLOAD_IDS`, `WIDER_RANGED_REPEAT_PATTERN_GROUPS`, and `_assert_wider_ranged_repeat_pattern_group(...)` block.
- Preserve the current assertion semantics exactly:
  - `known_gap_count == 0`
  - manifest `measured_workloads` and `workload_count` both equal the target manifest workload count
  - each representative workload id still resolves to a measured scorecard row via `assert_benchmark_workload_contract(...)`
  - each pattern-group check still validates minimum row count, per-pattern compile/search/fullmatch coverage, required categories, expected module-search haystacks or snippets, expected `pattern.fullmatch` haystacks, and measured scorecard row coverage/status
- The cleanup remains structural only:
  - do not change `benchmarks/workloads/*.py`, `python/rebar_harness/benchmarks.py`, Rust code, `python/rebar/`, published reports, README copy, or tracked state files beyond this task file; and
  - do not broaden into other benchmark suites or reshape the already-centralized `SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS` coverage in the same run.
- After the cleanup:
  - `rg -n 'WIDER_RANGED_REPEAT_REPRESENTATIVE_MEASURED_WORKLOAD_IDS|WIDER_RANGED_REPEAT_PATTERN_GROUPS|def _assert_wider_ranged_repeat_pattern_group' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` returns no matches.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.

## Constraints
- Prefer extending `tests/benchmarks/benchmark_expectations.py` and its existing combined-suite helper style over adding a new helper module or another layer of manifest metadata.
- Keep the wider-ranged-repeat coverage data-first and readable. This task should delete one remaining test-local benchmark-shape block, not hide the frontier behind a generic abstraction that makes the manifest slice harder to audit.

## Notes
- `RBR-0443` is already reserved in `README.md`, `ops/state/current_status.md`, and `ops/state/backlog.md` for the next feature-owned quantified alternation-heavy conditional-replacement benchmark catch-up, so this architecture cleanup starts at `RBR-0444`.
- The runtime dashboard is current and clean (`Dirty worktree: false`, `ready: 0`, `in_progress: 0`, no last-cycle anomalies), so rule 10 does not apply and this run should seed one post-JSON cleanup task instead of no-oping.
- JSON counts are fully burned down in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still carries one wider-ranged-repeat-only constant block even after `RBR-0425`, while `tests/benchmarks/benchmark_expectations.py` already owns the rest of the combined-suite selector, manifest, and slice expectation plumbing.
- Completed 2026-03-16: moved the wider-ranged-repeat combined-suite manifest-shape expectations into the existing `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS` entry in `tests/benchmarks/benchmark_expectations.py`, rewired `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to consume that shared shape data through a generic pattern-group assertion path, confirmed `rg -n 'WIDER_RANGED_REPEAT_REPRESENTATIVE_MEASURED_WORKLOAD_IDS|WIDER_RANGED_REPEAT_PATTERN_GROUPS|def _assert_wider_ranged_repeat_pattern_group' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` returns no matches, and verified `PYTHONPATH=python .venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` (`4 passed`, `342 subtests passed`).
