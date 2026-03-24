# RBR-1201: Benchmark conditional group-exists nested callable negative-count str workloads

Status: ready
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Catch the newly published nested conditional callable negative-count `str` slice up on the existing Python-path benchmark surface by measuring the exact four bounded module and compiled-`Pattern` `sub()`/`subn()` workflows that the live direct parity and correctness owner path already cover, before the adjacent nested `bytes` mirrors reopen correctness publication on this family.

## Pattern Pair
- `rebar.sub(r"a(b)?c(?(1)(?(1)d|e)|f)", lambda m: m.group(1) + "x", "zzabcdzz", -1)`
- `rebar.compile(r"a(?P<word>b)?c(?(word)(?(word)d|e)|f)").subn(lambda m: m.group("word") + "x", "zzacfzz", -1)`

## Deliverables
- `benchmarks/workloads/conditional_group_exists_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Extend `benchmarks/workloads/conditional_group_exists_boundary.py` with exactly the four adjacent nested conditional callable negative-count `str` workloads already published on the shared correctness owner path for `a(b)?c(?(1)(?(1)d|e)|f)` and `a(?P<word>b)?c(?(word)(?(word)d|e)|f)`:
  - add the numbered module `sub()` `count=-1` row on `"zzabcdzz"` using the existing `callable_match_group` helper pinned to group `1`;
  - add the named module `subn()` `count=-1` row on `"zzacfzz"` using the same helper pinned to group `"word"`;
  - add the numbered compiled-pattern `sub()` `count=-1` row for the same no-substitution workflow; and
  - add the named compiled-pattern `subn()` `count=-1` row for the same zero-replacement tuple workflow.
- Keep the work on the existing conditional benchmark owner path instead of creating another manifest or detached callable benchmark family:
  - update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` only as needed so the shared `conditional-group-exists-boundary` manifest expectations, representative measured-row checks, scorecard sync, and workload round-trip coverage stay aligned with the widened nested callable negative-count slice;
  - preserve the already-measured nested callable `str` present/absent rows plus the surrounding two-arm, alternation-heavy, quantified, and quantified-`bytes` callable slices on the same manifest; and
  - do not widen this run into correctness publication, Rust implementation work, nested `bytes` mirrors, or broader callable-helper expansion beyond `callable_match_group`.
- Regenerate `reports/benchmarks/latest.py` honestly on the tracked combined benchmark surface:
  - the `conditional-group-exists-boundary` manifest grows from `152` workloads to `156` workloads with all `156` measured and `0` known gaps;
  - the tracked combined benchmark summary moves from `1083/1083` measured workloads to `1087/1087` measured workloads while the manifest count stays at `30`; and
  - do not widen this run into built-native-only reporting or another benchmark family.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists and nested_callable'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-1201-conditional-group-exists-boundary.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep the scope pinned to the exact four nested conditional callable negative-count `str` workloads above. Leave the adjacent nested negative-count `bytes` correctness-publication mirrors and broader callable-helper expansion for later tasks.
- Reuse the existing `conditional_group_exists_boundary.py` manifest and benchmark-suite owner path. Do not create another benchmark manifest, another callable benchmark module, or a detached nested negative-count publication file.
- Keep benchmark comparisons running through the Python-facing `rebar` path so the published comparison against stdlib `re` stays faithful at the module boundary.

## Notes
- `RBR-1201` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this run; and
  - `rg -n "RBR-1201|RBR-1202" ops/tasks ops/state -g '*.md'` matched only historical mentions inside completed task files, not a live reservation for either id.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest done same-family frontier leaves this exact benchmark catch-up slice concrete after `RBR-1199`:
  - `ops/tasks/done/RBR-1199-publish-conditional-group-exists-nested-callable-negative-count-workflows.md` completed the bounded nested conditional callable negative-count `str` correctness-publication slice and explicitly left benchmark-side nested negative-count anchor work plus nested `bytes` mirrors for later on this owner path;
  - `tests/python/test_callable_replacement_parity_suite.py`, `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`, and `reports/correctness/latest.py` already cover the exact four numbered and named module/pattern nested conditional callable negative-count `str` workflows on the shared owner path;
  - `benchmarks/workloads/conditional_group_exists_boundary.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still stop at the nested callable `str` present/absent benchmark rows for this spelling, leaving the adjacent negative-count benchmark rows as the smallest still-missing benchmark slice on the same owner path; and
  - a narrow runtime probe in this planning run also confirmed that the deferred nested negative-count `bytes` module/pattern `sub()` and `subn()` workflows already match CPython on `rb"a(b)?c(?(1)(?(1)d|e)|f)"` and `rb"a(?P<word>b)?c(?(word)(?(word)d|e)|f)"`, which pins the post-drain survivor to the corresponding bounded `bytes` correctness-publication slice rather than a broader same-family synthesis pass.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists and nested_callable'` returned `1 passed, 533 deselected, 16 subtests passed`;
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/feature-planning-conditional-group-exists-boundary-current.py` returned `152 measured workloads / 0 known gaps`; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py` returned `1083 measured workloads / 0 known gaps`.
