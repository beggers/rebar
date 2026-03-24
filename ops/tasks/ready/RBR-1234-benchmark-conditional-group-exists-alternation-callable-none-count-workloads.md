# RBR-1234: Benchmark conditional group-exists alternation callable None-count workloads

Status: ready
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Catch the already-supported alternation-heavy two-arm conditional callable `count=None` slice up on the existing Python-path benchmark surface by measuring the exact bounded `sub()` and `subn()` workflows that the live direct parity owner path and newly published correctness fixture already cover for both `str` and `bytes`.

## Pattern Pair
- `rebar.sub(r"a(b)?c(?(1)(de|df)|(eg|eh))", lambda m: m.group(1) + "x", "zzabcdezz", None)`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))").subn(lambda m: m.group("word") + b"x", b"zzacehzz", None)`

## Deliverables
- `benchmarks/workloads/conditional_group_exists_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Extend `benchmarks/workloads/conditional_group_exists_boundary.py` with exactly the eight adjacent alternation-heavy conditional callable `count=None` workloads that sit immediately behind `RBR-1232` on the shared owner path:
  - add the four `str` workloads for `a(b)?c(?(1)(de|df)|(eg|eh))` and `a(?P<word>b)?c(?(word)(de|df)|(eg|eh))` by mirroring the already-measured alternation-heavy negative-count quartet while passing `count=None`, keeping the bounded shape on module `sub`, module `subn`, compiled-`Pattern` `sub`, and compiled-`Pattern` `subn`;
  - add the matching four `bytes` workloads for `rb"a(b)?c(?(1)(de|df)|(eg|eh))"` and `rb"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))"` on the same numbered and named module/pattern matrix;
  - keep the replacement descriptors on the existing `callable_match_group` helper pinned to group `1` or `"word"` so CPython's invalid-`count` `TypeError` stays explicit on the same benchmark owner path instead of inventing another callable helper shape; and
  - keep the slice bounded to the alternation-heavy top-level conditional callable family only, leaving nested, quantified, or broader callable count-contract benchmark publication for later tasks.
- Keep the work on the existing conditional benchmark owner path instead of creating another manifest or detached callable benchmark family:
  - update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` only as needed so the shared `conditional-group-exists-boundary` manifest expectations, representative measured-row checks, workload-id tables, and scorecard sync stay aligned with the widened alternation-heavy `count=None` slice;
  - preserve the already-measured alternation-heavy callable present, absent-exception, and negative-count rows plus the surrounding top-level, nested, and quantified callable slices on the same manifest; and
  - do not widen this run into correctness publication, Rust implementation work, or broader callable-helper expansion beyond the existing `callable_match_group` path.
- Regenerate `reports/benchmarks/latest.py` honestly on the tracked combined benchmark surface:
  - the `conditional-group-exists-boundary` manifest grows from `264` workloads to `272` workloads with all `272` measured and `0` known gaps; and
  - the tracked combined benchmark summary moves from `1195/1195` measured workloads to `1203/1203` measured workloads while the manifest count stays at `30`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists_callable and none_count'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-1234-conditional-group-exists-boundary.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep the scope pinned to the exact eight alternation-heavy conditional callable `count=None` benchmark workloads above. Do not widen this run into another owner family or another callable benchmark helper.
- Reuse the existing `conditional_group_exists_boundary.py` manifest and source-tree combined benchmark suite. Do not create another benchmark manifest, another callable benchmark module, or a detached alternation-heavy `count=None` publication file.
- Keep benchmark comparisons running through the Python-facing `rebar` path so the published comparison against stdlib `re` stays faithful at the module boundary.

## Notes
- `RBR-1234` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this planning run; and
  - `rg -n "RBR-1234|RBR-1235" ops/tasks ops/state -g '*.md'` matched only historical mentions inside completed task files, not a live reservation for either id.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- One narrow same-owner-path scan keeps this exact follow-on concrete behind `RBR-1232`:
  - `ops/tasks/done/RBR-1232-publish-conditional-group-exists-alternation-callable-none-count-workflows.md` explicitly leaves the same-route alternation-heavy callable `count=None` benchmark catch-up for a separate planning pass;
  - `tests/python/test_callable_replacement_parity_suite.py` already exercises the bounded alternation-heavy conditional callable `count=None` parity path on the shared owner route;
  - `benchmarks/workloads/conditional_group_exists_boundary.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently carry the alternation-heavy callable present, absent-exception, and negative-count rows but no alternation-heavy callable `count=None` workloads; and
  - no newer same-family done note or blocked task pins one exact adjacent post-drain feature slice beyond this benchmark catch-up, so backlog/current-status frontier wording should say that no ready feature follow-on currently survives once this slice lands.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists_callable and none_count'` returned `2 passed, 105 deselected, 36 subtests passed`;
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/feature-planning-conditional-none-count-current.py` returned `264 measured workloads / 0 known gaps`; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report .rebar/tmp/feature-planning-benchmarks-current.py` returned `1195 measured workloads / 0 known gaps / 1195 total workloads`.
