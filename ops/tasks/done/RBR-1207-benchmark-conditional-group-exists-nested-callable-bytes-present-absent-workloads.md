# RBR-1207: Benchmark conditional group-exists nested callable bytes present/absent workloads

Status: done
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Catch the already-published nested conditional callable `bytes` present/absent slice up on the existing Python-path benchmark surface by measuring the exact eight bounded module and compiled-`Pattern` `sub()`/`subn()` workflows that the live direct parity and correctness owner path already covers.

## Pattern Pair
- `rebar.sub(rb"a(b)?c(?(1)(?(1)d|e)|f)", lambda m: m.group(1) + b"x", b"zzabcdzz")`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)(?(word)d|e)|f)").subn(lambda m: m.group("word") + b"x", b"zzacfzz", 1)`

## Deliverables
- `benchmarks/workloads/conditional_group_exists_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Extend `benchmarks/workloads/conditional_group_exists_boundary.py` with exactly the eight adjacent nested conditional callable `bytes` present/absent workloads that mirror the already-measured `str` replacement/exception rows on the shared owner path for `rb"a(b)?c(?(1)(?(1)d|e)|f)"` and `rb"a(?P<word>b)?c(?(word)(?(word)d|e)|f)"`:
  - add the numbered module `sub()` present row on `b"zzabcdzz"` using the existing `callable_match_group` helper pinned to group `1`;
  - add the numbered module `subn()` absent-capture `TypeError` row on `b"zzacfzz"` with `count=1` using the same helper pinned to group `1`;
  - add the numbered compiled-pattern `sub()` present row on `b"zzabcdzz"` and the numbered compiled-pattern `subn()` absent-capture `TypeError` row on `b"zzacfzz"` for the same bounded pair;
  - add the named module `sub()` present row on `b"zzabcdzz"` using the same helper pinned to group `"word"`;
  - add the named module `subn()` absent-capture `TypeError` row on `b"zzacfzz"` with `count=1` using the same helper pinned to group `"word"`;
  - add the named compiled-pattern `sub()` present row on `b"zzabcdzz"` and the named compiled-pattern `subn()` absent-capture `TypeError` row on `b"zzacfzz"` for the same bounded pair.
- Keep the work on the existing conditional benchmark owner path instead of creating another manifest or detached callable benchmark family:
  - update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` only as needed so the shared `conditional-group-exists-boundary` slice expectations, representative measured-row checks, scorecard sync, and workload round-trip coverage stay aligned with the widened nested callable `bytes` slice;
  - preserve the already-measured nested callable `str` rows and nested callable `bytes` negative-count rows plus the surrounding two-arm, alternation-heavy, and quantified callable slices on the same manifest; and
  - do not widen this run into correctness publication, Rust implementation work, or broader callable-helper expansion beyond `callable_match_group`.
- Regenerate `reports/benchmarks/latest.py` honestly on the tracked combined benchmark surface:
  - the `conditional-group-exists-boundary` manifest grows from `160` workloads to `168` workloads with all `168` measured and `0` known gaps; and
  - the tracked combined benchmark summary moves from `1091/1091` measured workloads to `1099/1099` measured workloads while the manifest count stays at `30`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists_nested_callable or nested_callable_replacement_negative_count_bytes_rows'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-1207-conditional-group-exists-boundary.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep the scope pinned to the exact eight nested conditional callable `bytes` present/absent workloads above. Leave any later same-family callable follow-on beyond this benchmark catch-up for a separate planning pass.
- Reuse the existing `conditional_group_exists_boundary.py` manifest and source-tree combined benchmark suite. Do not create another benchmark manifest, another callable benchmark module, or a detached nested callable publication file.
- Keep benchmark comparisons running through the Python-facing `rebar` path so the published comparison against stdlib `re` stays faithful at the module boundary.

## Notes
- `RBR-1207` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this planning run; and
  - `rg -n "RBR-1207|RBR-1208" ops/tasks ops/state -g '*.md'` matched only historical mentions inside completed task files, not a live reservation for either id.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- One narrow same-owner-path scan keeps this exact follow-on concrete after `RBR-1205`:
  - `tests/python/test_callable_replacement_parity_suite.py` already exposes the exact nested callable `bytes` present and absent-capture case tables for `rb"a(b)?c(?(1)(?(1)d|e)|f)"` and `rb"a(?P<word>b)?c(?(word)(?(word)d|e)|f)"` via `CONDITIONAL_GROUP_EXISTS_NESTED_BYTES_GROUP_ACCESS_CASES` and `CONDITIONAL_GROUP_EXISTS_NESTED_BYTES_ABSENT_EXCEPTION_CASES`;
  - `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `reports/correctness/latest.py` already publish the matching eight nested callable `bytes` present/absent correctness rows on the shared owner path; and
  - `benchmarks/workloads/conditional_group_exists_boundary.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still stop at the nested callable `str` present/absent rows plus the adjacent `bytes` negative-count mirror rows, leaving the bounded nested callable `bytes` present/absent benchmark rows as the smallest still-missing accepted slice on that same owner path.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists_nested_callable or nested_callable_replacement_negative_count_bytes_rows'` returned `5 passed, 447 deselected, 52 subtests passed`;
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/feature-planning-conditional-group-exists-boundary-current.py` returned `160 measured workloads / 0 known gaps`; and
  - `python3` inspection of the tracked scorecards confirmed `reports/correctness/latest.py` still publishes `1733/1733` passing cases across `114` manifests while `reports/benchmarks/latest.py` publishes `1091/1091` measured workloads across `30` manifests, with `conditional-group-exists-boundary` currently at `160` workloads.

## Completion
- Added the eight nested conditional callable `bytes` present/absent module and compiled-`Pattern` `sub()`/`subn()` workloads on the existing `conditional-group-exists-boundary` manifest, preserving the adjacent negative-count `bytes` companions and surrounding callable slices.
- Updated the shared source-tree benchmark suite so the widened nested callable `bytes` slice stays aligned in representative measured-row checks, zero-gap bytes subsets, round-trip workload coverage, and scorecard sync against the matching `str` slice.
- Regenerated the tracked combined benchmark publication: `reports/benchmarks/latest.py` now records `conditional-group-exists-boundary` at `168` workloads with `168` measured and `0` known gaps, and the combined summary at `1099/1099` measured workloads across `30` manifests.
- Verification in this run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists_nested_callable or nested_callable_replacement_negative_count_bytes_rows'` returned `5 passed, 447 deselected, 84 subtests passed`.
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-1207-conditional-group-exists-boundary.py` returned `168 measured workloads / 0 known gaps`.
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py` regenerated the tracked scorecard to `1099 measured workloads / 0 known gaps`.
