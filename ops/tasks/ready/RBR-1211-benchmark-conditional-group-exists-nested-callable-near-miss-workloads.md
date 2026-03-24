# RBR-1211: Benchmark conditional group-exists nested callable near-miss workloads

Status: ready
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Catch the already-published nested conditional callable near-miss slice up on the existing Python-path benchmark surface by measuring the exact bounded no-match `sub()` and `subn()` workflows that the live direct parity and correctness owner path already covers for both `str` and `bytes`.

## Pattern Pair
- `rebar.sub(r"a(b)?c(?(1)(?(1)d|e)|f)", lambda m: m.group(1) + "x", "zzabcezz")`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)(?(word)d|e)|f)").subn(lambda m: m.group("word") + b"x", b"zzacezz", 1)`

## Deliverables
- `benchmarks/workloads/conditional_group_exists_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Extend `benchmarks/workloads/conditional_group_exists_boundary.py` with exactly the sixteen adjacent nested conditional callable near-miss workloads already published on the shared correctness owner path for `a(b)?c(?(1)(?(1)d|e)|f)` and `a(?P<word>b)?c(?(word)(?(word)d|e)|f)` plus their `bytes` mirrors:
  - add the eight `str` workloads covering numbered and named module `sub()` no-match rows on `"zzabcezz"` plus module `subn()` no-match rows on `"zzacezz"` with `count=1`, and mirror those same numbered and named `sub()`/`subn()` no-match workflows through compiled-`Pattern` entrypoints;
  - add the matching eight `bytes` workloads on `b"zzabcezz"` and `b"zzacezz"` using the same numbered/named and module/pattern matrix; and
  - keep the replacement descriptors on the existing `callable_match_group` helper pinned to group `1` or `"word"` so the benchmarked behavior stays aligned with the already-published callable correctness rows where no callback invocation occurs because the pattern does not match.
- Keep the work on the existing conditional benchmark owner path instead of creating another manifest or detached callable benchmark family:
  - update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` only as needed so the shared `conditional-group-exists-boundary` manifest expectations, nested callable workload-id tables, representative measured-row checks, scorecard sync, and workload round-trip coverage stay aligned with the widened near-miss slice;
  - preserve the already-measured nested callable group-access, absent-exception, and negative-count rows plus the surrounding two-arm, alternation-heavy, and quantified callable slices on the same manifest; and
  - do not widen this run into correctness publication, Rust implementation work, or broader callable-helper expansion beyond the existing `callable_match_group` path.
- Regenerate `reports/benchmarks/latest.py` honestly on the tracked combined benchmark surface:
  - the `conditional-group-exists-boundary` manifest grows from `168` workloads to `184` workloads with all `184` measured and `0` known gaps; and
  - the tracked combined benchmark summary moves from `1099/1099` measured workloads to `1115/1115` measured workloads while the manifest count stays at `30`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists_nested_callable'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-1211-conditional-group-exists-boundary.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep the scope pinned to the exact sixteen nested conditional callable near-miss benchmark workloads above. Do not widen this run into a new owner family or another callable benchmark helper.
- Reuse the existing `conditional_group_exists_boundary.py` manifest and source-tree combined benchmark suite. Do not create another benchmark manifest, another callable benchmark module, or a detached nested near-miss publication file.
- Keep benchmark comparisons running through the Python-facing `rebar` path so the published comparison against stdlib `re` stays faithful at the module boundary.

## Notes
- `RBR-1211` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this planning run; and
  - `rg -n "RBR-1211|RBR-1212|nested callable near-miss benchmark|conditional callable near-miss benchmark" ops/tasks ops/state -g '*.md'` matched only the stale frontier text in tracked state plus historical mentions inside completed task files, not a live reservation for this id.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest done same-family frontier and one narrow adjacent owner-path scan keep this exact benchmark catch-up slice concrete after `RBR-1209`:
  - `ops/tasks/done/RBR-1209-publish-conditional-group-exists-nested-callable-near-miss-workflows.md` explicitly leaves the adjacent benchmark catch-up for this same near-miss slice for a separate planning pass;
  - `tests/python/test_callable_replacement_parity_suite.py`, `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`, and `reports/correctness/latest.py` already cover the exact numbered and named module/pattern nested callable near-miss workflows for both `str` and `bytes`;
  - `benchmarks/workloads/conditional_group_exists_boundary.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently stop at the nested callable group-access, absent-exception, and negative-count rows, leaving the bounded near-miss rows as the smallest still-missing accepted slice on that same owner path; and
  - once those near-miss rows land, no exact ready feature follow-on is pinned on this owner path by the newest done note or the adjacent owner-path parity buckets.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists_nested_callable'` returned `5 passed, 442 deselected, 84 subtests passed`;
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/feature-planning-conditional-group-exists-boundary-current.py` returned `168 measured workloads / 0 known gaps`; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report .rebar/tmp/feature-planning-benchmarks-current.py` returned `1099 measured workloads / 0 known gaps`.
