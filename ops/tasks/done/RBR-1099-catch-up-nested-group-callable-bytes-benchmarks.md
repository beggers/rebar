# RBR-1099: Catch up nested-group callable bytes benchmarks

Status: done
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Catch the newly published nested-group callable bytes slice up on the existing Python-path benchmark owner route by measuring the exact bounded bytes workflows that `RBR-1097` published, before broader nested callable replacement expansion reopens the frontier.

## Pattern Pair
- `rebar.sub(rb"a((b))d", lambda m: b"<" + m.group(1) + b">", b"abdabd")`
- `rebar.compile(rb"a(?P<outer>(?P<inner>b))d").subn(lambda m: b"<" + m.group("inner") + b">", b"abdabd", 1)`

## Deliverables
- `benchmarks/workloads/nested_group_callable_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Extend `benchmarks/workloads/nested_group_callable_replacement_boundary.py` on the existing owner path with only the adjacent bytes workloads for the bounded nested-group callable slice already published by `RBR-1097`:
  - numbered module `sub()` and `subn(count=1)` rows for `rb"a((b))d"` that exercise `group(1)` and `group(2)`;
  - numbered compiled-pattern `sub()` and `subn(count=1)` rows for `rb"a((b))d"` on the same bounded callback shape;
  - named module `sub()` and `subn(count=1)` rows for `rb"a(?P<outer>(?P<inner>b))d"` that exercise `group("outer")` and `group("inner")`; and
  - named compiled-pattern `sub()` and `subn(count=1)` rows for `rb"a(?P<outer>(?P<inner>b))d"` on that same bounded callback shape.
- Keep the benchmark publication bounded to the existing `nested-group-callable-replacement-boundary` manifest:
  - do not widen into alternation, quantified nested groups, branch-local backreferences, broader backtracking-heavy callable slices, or correctness publication in this run; and
  - keep the existing `str` rows on the same manifest measured and selected.
- Refresh `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` only as needed so the shared owner-path benchmark assertions and scorecard expectations explicitly require representative bytes ids for the bounded nested-group callable slice while keeping `source_tree_scorecard_case("nested-group-callable-replacement-boundary").manifest_expectation.known_gap_count == 0`.
- Regenerate `reports/benchmarks/latest.py` so the tracked source-tree benchmark publication includes the new bytes nested-group callable workload ids as measured:
  - `REPORT["summary"]` moves from `983` total / `983` measured / `0` known gaps to `991` / `991` / `0`;
  - `REPORT["summary"]["workloads_by_cache_mode"]` moves from `{"cold": 104, "purged": 425, "warm": 454}` to `{"cold": 104, "purged": 429, "warm": 458}`;
  - `REPORT["manifests"]["nested-group-callable-replacement-boundary"]` moves from `selected_workload_count == 80`, `measured_workloads == 80`, `known_gap_count == 0`, and `workload_count == 80` to `88`, `88`, `0`, and `88`; and
  - the regenerated tracked artifact publishes the new bytes nested-group callable workload ids with `status == "measured"`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'nested_group and callable and bytes'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'nested_group_callable_replacement'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/nested_group_callable_replacement_boundary.py --report .rebar/tmp/rbr-1099-nested-group-callable-bytes-benchmarks.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface, change Rust/Python regex behavior, or add broader nested callable replacement rows in this run.
- Reuse the existing `nested_group_callable_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner route. Do not create another benchmark manifest, detached benchmark suite, or native-only publication path in this run.
- Keep the scope pinned to the exact bytes nested-group callable slice already published by `RBR-1097`. Leave broader nested callable replacement expansion for later tasks.

## Notes
- `RBR-1099` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contain no live feature task file; and
  - `rg -n 'RBR-1099|RBR-1100|RBR-1101' ops/tasks ops/state -g '*.md'` returned only historical mentions inside done-task notes in this run.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- `RBR-1097` explicitly left same-family benchmark catch-up for later work on this owner family, and the narrow owner-path check in this run shows that catch-up is the next bounded slice instead of another implementation prerequisite:
  - `benchmarks/workloads/nested_group_callable_replacement_boundary.py` currently publishes only the eight `str` workload ids for the bounded `a((b))d` and `a(?P<outer>(?P<inner>b))d` callable slice;
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` already has the shared `nested-group-callable-replacement-boundary` owner-path assertions that can absorb the adjacent bytes ids without forking a new benchmark family;
  - `reports/benchmarks/latest.py` currently reports `983` total workloads, `983` measured workloads, `0` known gaps overall, and `80` selected/measured workloads for `nested-group-callable-replacement-boundary`, with no adjacent bytes workload ids on that same bounded slice; and
  - `reports/correctness/latest.py` already publishes the corresponding bytes correctness rows from `RBR-1097`, so the runtime and correctness prerequisites are in place and benchmark catch-up is now the exact missing surface.

## Completion Note
- Added the eight bounded bytes callable-replacement benchmark rows for `a((b))d` and `a(?P<outer>(?P<inner>b))d` on the existing `nested-group-callable-replacement-boundary` owner manifest, using the published angle-bracket callback shape from `RBR-1097` for numbered and named module/compiled-pattern `sub()` and `subn(count=1)` workflows.
- Refreshed the shared owner-path combined benchmark assertions so the bounded nested-group bytes workload ids are required as public measured representatives without widening the manifest beyond this exact slice.
- Regenerated `reports/benchmarks/latest.py`; the tracked publication now reports `991` total workloads, `991` measured workloads, `0` known gaps, `{"cold": 104, "purged": 429, "warm": 458}` by cache mode, and `88/88/0` selected/measured/known-gap rows for `nested-group-callable-replacement-boundary`.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'nested_group and callable and bytes'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'nested_group_callable_replacement'`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/nested_group_callable_replacement_boundary.py --report .rebar/tmp/rbr-1099-nested-group-callable-bytes-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`
