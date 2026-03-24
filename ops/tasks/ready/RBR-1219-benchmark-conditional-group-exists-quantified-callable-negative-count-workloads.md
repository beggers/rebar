Status: ready
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Catch the already-published quantified conditional callable negative-count slice up on the existing Python-path benchmark surface by measuring the exact bounded `count=-1` `sub()` and `subn()` workflows that the live direct parity and correctness owner path already covers for both `str` and `bytes`.

## Pattern Pair
- `rebar.sub(r"a(b)?c(?(1)d|e){2}", lambda m: m.group(1) + "x", "zzabcddzz", -1)`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)d|e){2}").subn(lambda m: m.group("word") + b"x", b"zzacedzz", -1)`

## Deliverables
- `benchmarks/workloads/conditional_group_exists_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Extend `benchmarks/workloads/conditional_group_exists_boundary.py` with exactly the thirty-two adjacent quantified conditional callable negative-count workloads already published on the shared correctness owner path for `a(b)?c(?(1)d|e){2}` and `a(?P<word>b)?c(?(word)d|e){2}` plus their `bytes` mirrors:
  - add the sixteen `str` workloads covering numbered and named module/compiled-`Pattern` `sub()` and `subn()` entrypoints with `count=-1`;
  - keep the bounded present-match rows on `"zzabcddzz"` and the bounded absent-capture rows on `"zzaceezz"` aligned with the direct parity tables while preserving CPython's exact negative-count short-circuit behavior where no replacement occurs and the callable is not invoked;
  - add the matching bounded no-match rows on `"zzabcdezz"` and `"zzacedzz"` so the quantified near-miss branch stays explicit on the shared benchmark path even though the callback never runs; and
  - mirror the same sixteen workloads for `bytes` on `b"zzabcddzz"`, `b"zzaceezz"`, `b"zzabcdezz"`, and `b"zzacedzz"` without widening beyond the existing `callable_match_group` helper route.
- Keep the work on the existing conditional benchmark owner path instead of creating another manifest or detached callable benchmark family:
  - update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` only as needed so the shared `conditional-group-exists-boundary` manifest expectations, quantified callable workload-id tables, representative measured-row checks, scorecard sync, and workload-to-correctness anchor coverage stay aligned with the widened negative-count slice;
  - preserve the already-measured quantified callable present-match, absent-short-circuit, and near-miss rows plus the surrounding two-arm, nested, and alternation-heavy callable slices on the same manifest; and
  - do not widen this run into correctness publication, Rust implementation work, or broader callable-helper expansion beyond the existing `callable_match_group` path.
- Regenerate `reports/benchmarks/latest.py` honestly on the tracked combined benchmark surface:
  - the `conditional-group-exists-boundary` manifest grows from `200` workloads to `232` workloads with all `232` measured and `0` known gaps; and
  - the tracked combined benchmark summary moves from `1131/1131` measured workloads to `1163/1163` measured workloads while the manifest count stays at `30`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists_quantified_callable'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-1219-conditional-group-exists-boundary.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep the scope pinned to the exact thirty-two quantified callable negative-count benchmark workloads above. Do not widen this run into a new owner family or another callable benchmark helper.
- Reuse the existing `conditional_group_exists_boundary.py` manifest and source-tree combined benchmark suite. Do not create another benchmark manifest, another callable benchmark module, or a detached quantified negative-count publication file.
- Keep benchmark comparisons running through the Python-facing `rebar` path so the published comparison against stdlib `re` stays faithful at the module boundary.

## Notes
- `RBR-1219` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this planning run; and
  - `python3` inspection across `ops/tasks/done/`, `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` returned `1219` as the next unused id.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest done same-family frontier keeps this exact benchmark catch-up slice concrete after `RBR-1217`:
  - `ops/tasks/done/RBR-1217-publish-conditional-group-exists-quantified-callable-negative-count-workflows.md` explicitly leaves the adjacent benchmark catch-up for the same quantified `count=-1` slice to a separate planning pass;
  - `tests/python/test_callable_replacement_parity_suite.py`, `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`, and `reports/correctness/latest.py` already cover the exact numbered and named module/pattern quantified callable negative-count workflows for both `str` and `bytes`;
  - `benchmarks/workloads/conditional_group_exists_boundary.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently carry quantified callable present, absent-short-circuit, and near-miss rows but no quantified callable negative-count rows; and
  - no newer same-family done task or blocked note pins an exact post-drain feature follow-on after this benchmark catch-up slice lands.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists_quantified_callable'` returned `6 passed, 145 deselected, 144 subtests passed`;
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/feature-planning-rbr-1219-conditional-group-exists-boundary.py` returned `200 measured workloads / 0 known gaps`; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report .rebar/tmp/feature-planning-rbr-1219-benchmarks.py` returned `1131 measured workloads / 0 known gaps`.
