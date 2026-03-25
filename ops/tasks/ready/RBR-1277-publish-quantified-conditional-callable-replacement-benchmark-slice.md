## RBR-1277: Publish quantified conditional callable-replacement benchmark slice

Status: ready
Owner: feature-implementation
Created: 2026-03-25

## Goal
- Catch the existing Python-path collection/replacement benchmark publication up to the already-supported quantified conditional callable-replacement owner slice by publishing the exact workload rows already pinned in the benchmark owner support tables for the bounded quantified pair, without widening into nested callable follow-ons or another benchmark family.

## Pattern Pair
- `a(b)?c(?(1)d|e){2}`
- `a(?P<word>b)?c(?(word)d|e){2}`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Extend `benchmarks/workloads/collection_replacement_boundary.py` with the exact quantified conditional callable-replacement workload ids already enumerated by `_CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_WORKLOAD_STEMS` in `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`:
  - publish the numbered and named module `sub()` / `subn()` warm rows plus compiled-pattern `sub()` / `subn()` purged rows across both `str` and `bytes`;
  - keep the workload ids, ordering, cache modes, helper routing, timing scopes, and callback shapes aligned with the existing owner support tables instead of inventing a second manifest shape;
  - keep the bounded quantified callable publication limited to the existing present, absent-exception, `count=None`, negative-count, negative-count no-match, and no-match rows for `a(b)?c(?(1)d|e){2}` and `a(?P<word>b)?c(?(word)d|e){2}`; and
  - do not fork another manifest or move this slice onto a different benchmark route.
- Refresh the benchmark publication expectations on the same owner path:
  - keep `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` aligned with the widened quantified callable workload surface;
  - keep `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` aligned with the widened workload ids and callback-result round trips; and
  - regenerate `reports/benchmarks/latest.py` so the tracked workload and manifest totals match the landed benchmark publication.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'quantified and callable and conditional_group_exists'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_publication_runtime_contracts.py -k 'quantified and callable and conditional_group_exists'`

## Constraints
- Keep the scope pinned to the existing collection/replacement benchmark owner path for the quantified callable slice only.
- Limit edits to `benchmarks/workloads/collection_replacement_boundary.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`, and the regenerated `reports/benchmarks/latest.py` unless a tiny adjacent benchmark-harness adjustment is strictly required to publish the already-defined rows.
- Do not widen into nested conditional callable replacement benchmarks, correctness publication, runtime implementation work, or tracked `ops/state/` prose in this task.

## Notes
- `RBR-1277` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this planning run; and
  - `rg -n "RBR-1277|RBR-1278|RBR-1279" ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done ops/state/backlog.md ops/state/current_status.md -g '*.md'` found only historical mentions inside older done-task notes, not a live reservation.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- One narrow same-owner-path benchmark scan pins this exact follow-on:
  - `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` already enumerates the bounded quantified callable workload ids under `_CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_WORKLOAD_STEMS`, including the exact present, absent-exception, `count=None`, negative-count, negative-count no-match, and no-match rows for the quantified numbered and named conditional pair;
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` already expects those exact quantified callable bytes workload ids on the shared source-tree combined scorecard surface; but
  - `benchmarks/workloads/collection_replacement_boundary.py` currently contains none of those quantified callable workload ids, so the missing work is benchmark publication catch-up on the existing owner path rather than another implementation prerequisite.
- The bounded benchmark acceptance surface already exists on the current branch:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'quantified and callable and conditional_group_exists'` passed with `6 passed, 82 deselected`; and
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_publication_runtime_contracts.py -k 'quantified and callable and conditional_group_exists'` passed with `24 passed, 168 deselected`.
- No exact post-drain feature follow-on is pinned after this seed:
  - tracked state already honestly says no ready feature follow-on currently survives on the callable-replacement owner route; and
  - this narrow same-owner-path scan identified one concrete benchmark publication gap but did not expose a second adjacent unpublished callable slice beyond it.
