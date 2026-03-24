# RBR-1238: Benchmark conditional group-exists nested callable None-count workloads

Status: ready
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Catch the already-supported nested two-arm conditional callable `count=None` slice up on the existing Python-path benchmark surface by measuring the exact bounded `sub()` and `subn()` workflows that the live direct parity owner path and newly published correctness fixture already cover for both `str` and `bytes`.

## Pattern Pair
- `rebar.sub(r"a(b)?c(?(1)(?(1)d|e)|f)", lambda m: m.group(1) + "x", "zzabcdzz", None)`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)(?(word)d|e)|f)").subn(lambda m: m.group("word") + b"x", b"zzacfzz", None)`

## Deliverables
- `benchmarks/workloads/conditional_group_exists_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Extend `benchmarks/workloads/conditional_group_exists_boundary.py` with exactly the eight adjacent nested conditional callable `count=None` workloads that sit immediately behind `RBR-1236` on the shared owner path:
  - add the four `str` workloads for `a(b)?c(?(1)(?(1)d|e)|f)` and `a(?P<word>b)?c(?(word)(?(word)d|e)|f)` by mirroring the already-measured nested negative-count quartet while passing `count=None`, keeping the bounded shape on module `sub`, module `subn`, compiled-`Pattern` `sub`, and compiled-`Pattern` `subn`;
  - add the matching four `bytes` workloads for `rb"a(b)?c(?(1)(?(1)d|e)|f)"` and `rb"a(?P<word>b)?c(?(word)(?(word)d|e)|f)"` on the same numbered and named module/pattern matrix;
  - keep the replacement descriptors on the existing `callable_match_group` helper pinned to group `1` or `"word"` so CPython's invalid-`count` `TypeError` stays explicit on the same benchmark owner path instead of inventing another callable helper shape; and
  - keep the slice bounded to the nested conditional callable family only, leaving quantified `count=None`, broader callable count-contract benchmark publication, and any new owner-family expansion for later tasks.
- Keep the work on the existing conditional benchmark owner path instead of creating another manifest or detached callable benchmark family:
  - update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` only as needed so the shared `conditional-group-exists-boundary` manifest expectations, representative measured-row checks, workload-id tables, and scorecard sync stay aligned with the widened nested `count=None` slice;
  - preserve the already-measured nested callable present, absent-exception, no-match, and negative-count rows plus the surrounding top-level, alternation-heavy, and quantified callable slices on the same manifest; and
  - do not widen this run into correctness publication, Rust implementation work, or broader callable-helper expansion beyond the existing `callable_match_group` path.
- Regenerate `reports/benchmarks/latest.py` honestly on the tracked combined benchmark surface:
  - the `conditional-group-exists-boundary` manifest grows from `272` workloads to `280` workloads with all `280` measured and `0` known gaps; and
  - the tracked combined benchmark summary moves from `1203/1203` measured workloads to `1211/1211` measured workloads while the manifest count stays at `30`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'nested_callable and promotes'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'nested_callable and scorecards'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-1238-conditional-group-exists-boundary.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep the scope pinned to the exact eight nested conditional callable `count=None` benchmark workloads above. Do not widen this run into another owner family or another callable benchmark helper.
- Reuse the existing `conditional_group_exists_boundary.py` manifest and source-tree combined benchmark suite. Do not create another benchmark manifest, another callable benchmark module, or a detached nested `count=None` publication file.
- Keep benchmark comparisons running through the Python-facing `rebar` path so the published comparison against stdlib `re` stays faithful at the module boundary.

## Notes
- `RBR-1238` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this planning run; and
  - the highest filed task before this seed was `RBR-1237`.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- One narrow same-owner-path scan keeps this exact follow-on concrete after `RBR-1236`:
  - `ops/tasks/done/RBR-1236-publish-conditional-group-exists-nested-callable-none-count-workflows.md` explicitly leaves the same-route nested callable `count=None` benchmark catch-up for a separate planning pass;
  - `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` and `tests/python/test_callable_replacement_parity_suite.py` already cover the bounded nested callable `count=None` owner slice for both `str` and `bytes`;
  - `benchmarks/workloads/conditional_group_exists_boundary.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently carry the nested callable present, absent-exception, no-match, and negative-count rows but no nested callable `count=None` workloads; and
  - no newer same-family done note or blocked task pins one exact adjacent post-drain feature slice beyond this benchmark catch-up, so backlog/current-status frontier wording should say that no ready feature follow-on currently survives once this slice lands.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'nested_callable and promotes'` returned `2 passed, 105 deselected, 100 subtests passed`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'nested_callable and scorecards'` returned `1 passed, 106 deselected`;
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/feature-planning-conditional-boundary-bench.py` returned `272 measured workloads / 0 known gaps / 272 total workloads`; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report .rebar/tmp/feature-planning-benchmarks-current.py` returned `1203 measured workloads / 0 known gaps / 1203 total workloads`.
