# RBR-1205: Benchmark conditional group-exists nested callable negative-count bytes workloads

Status: ready
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Catch the newly published nested conditional callable negative-count `bytes` slice up on the existing Python-path benchmark surface by measuring the exact four bounded module and compiled-`Pattern` `sub()`/`subn()` workflows that the live direct parity and correctness owner path already cover.

## Pattern Pair
- `rebar.sub(rb"a(b)?c(?(1)(?(1)d|e)|f)", lambda m: m.group(1) + b"x", b"zzabcdzz", -1)`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)(?(word)d|e)|f)").subn(lambda m: m.group("word") + b"x", b"zzacfzz", -1)`

## Deliverables
- `benchmarks/workloads/conditional_group_exists_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Extend `benchmarks/workloads/conditional_group_exists_boundary.py` with exactly the four adjacent nested conditional callable negative-count `bytes` workloads already published on the shared correctness owner path for `rb"a(b)?c(?(1)(?(1)d|e)|f)"` and `rb"a(?P<word>b)?c(?(word)(?(word)d|e)|f)"`:
  - add the numbered module `sub()` `count=-1` row on `b"zzabcdzz"` using the existing `callable_match_group` helper pinned to group `1`;
  - add the named module `subn()` `count=-1` row on `b"zzacfzz"` using the same helper pinned to group `"word"`;
  - add the numbered compiled-pattern `sub()` `count=-1` row for the same no-substitution workflow; and
  - add the named compiled-pattern `subn()` `count=-1` row for the same zero-replacement tuple workflow.
- Keep the work on the existing conditional benchmark owner path instead of creating another manifest or detached callable benchmark family:
  - update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` only as needed so the shared `conditional-group-exists-boundary` manifest expectations, representative measured-row checks, scorecard sync, and workload round-trip coverage stay aligned with the widened nested callable negative-count slice;
  - preserve the already-measured nested callable `str` rows plus the surrounding two-arm, alternation-heavy, quantified, and quantified-`bytes` callable slices on the same manifest; and
  - do not widen this run into correctness publication, Rust implementation work, or broader callable-helper expansion beyond `callable_match_group`.
- Regenerate `reports/benchmarks/latest.py` honestly on the tracked combined benchmark surface:
  - the `conditional-group-exists-boundary` manifest grows from `156` workloads to `160` workloads with all `160` measured and `0` known gaps; and
  - the tracked combined benchmark summary moves from `1087/1087` measured workloads to `1091/1091` measured workloads while the manifest count stays at `30`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists_nested_callable or negative_count_follow_on_workloads_in_sync'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-1205-conditional-group-exists-boundary.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep the scope pinned to the exact four nested conditional callable negative-count `bytes` workloads above. Leave broader same-family expansion for later tasks.
- Reuse the existing `conditional_group_exists_boundary.py` manifest and benchmark-suite owner path. Do not create another benchmark manifest, another callable benchmark module, or a detached nested negative-count publication file.
- Keep benchmark comparisons running through the Python-facing `rebar` path so the published comparison against stdlib `re` stays faithful at the module boundary.

## Notes
- `RBR-1205` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this planning run; and
  - `rg -n "RBR-1205|RBR-1206" ops/tasks ops/state -g '*.md'` returned no matches before this task was seeded.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest done same-family frontier keeps this exact benchmark catch-up slice concrete:
  - `ops/tasks/done/RBR-1203-publish-conditional-group-exists-nested-callable-negative-count-bytes-workflows.md` explicitly leaves the adjacent nested conditional callable negative-count `bytes` benchmark catch-up slice for later on this owner path;
  - `tests/python/test_callable_replacement_parity_suite.py`, `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`, and `reports/correctness/latest.py` already cover the exact four numbered and named module/pattern nested conditional callable negative-count `bytes` workflows on the shared owner path; and
  - `benchmarks/workloads/conditional_group_exists_boundary.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still stop at the nested callable negative-count `str` benchmark rows for this spelling, leaving the adjacent `bytes` mirror rows as the smallest still-missing slice on the same owner path.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists_nested_callable or negative_count_follow_on_workloads_in_sync'` returned `4 passed, 452 deselected, 36 subtests passed`;
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/feature-planning-conditional-group-exists-boundary-current.py` returned `156 measured workloads / 0 known gaps`; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py` returned `1087 measured workloads / 0 known gaps`.
