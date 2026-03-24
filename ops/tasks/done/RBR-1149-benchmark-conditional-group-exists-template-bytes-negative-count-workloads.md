# RBR-1149: Benchmark conditional group-exists template bytes negative-count workloads

Status: done
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Catch the newly published bytes `count=-1` conditional replacement-template slice up on the existing Python-path benchmark surface by measuring the exact four bounded module and compiled-`Pattern` workflows that already match CPython on the shared owner path, before str negative-count publication, callable follow-ons, or broader conditional replacement work widen the queue.

## Pattern Pair
- `rebar.sub(rb"a(b)?c(?(1)d|e)", rb"\\1x", b"abcdaceabcd", -1)`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)d|e)").subn(rb"\\g<word>x", b"abcdaceabcd", -1)`

## Deliverables
- `benchmarks/workloads/conditional_group_exists_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Extend `benchmarks/workloads/conditional_group_exists_boundary.py` with exactly the four adjacent bytes `count=-1` replacement-template workloads already published on the shared correctness owner path:
  - add the numbered module `sub()` bytes workload for `rb"a(b)?c(?(1)d|e)"` with `rb"\\1x"`, `b"abcdaceabcd"`, and `count == -1`;
  - add the named module `subn()` bytes workload for `rb"a(?P<word>b)?c(?(word)d|e)"` with `rb"\\g<word>x"`, `b"abcdaceabcd"`, and `count == -1`;
  - add the numbered compiled-pattern `sub()` bytes workload for `rb"a(b)?c(?(1)d|e)"` with `rb"\\1x"`, `b"abcdaceabcd"`, and `count == -1`; and
  - add the named compiled-pattern `subn()` bytes workload for `rb"a(?P<word>b)?c(?(word)d|e)"` with `rb"\\g<word>x"`, `b"abcdaceabcd"`, and `count == -1`.
- Keep the work on the existing `conditional-group-exists-boundary` benchmark owner path instead of creating another manifest or detached benchmark test module:
  - update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` only as needed so the shared conditional replacement-template slice expectations, representative measured rows, and bytes round-trip assertions include these four new negative-count bytes workloads on `conditional-group-exists-boundary`;
  - preserve the already measured present/absent `str` and bytes template rows plus the surrounding callable, alternation-heavy, nested, and quantified conditional benchmark slices on the same manifest; and
  - do not widen the benchmark surface into any str `count=-1` rows, new callable rows, or another conditional benchmark family.
- Regenerate `reports/benchmarks/latest.py` honestly on the tracked combined benchmark surface:
  - the tracked report gains the four new measured bytes negative-count workloads for `conditional-group-exists-boundary`;
  - the combined benchmark summary moves from `1027/1027` measured workloads to `1031/1031` measured workloads with `known_gap_count == 0`;
  - the manifest count stays at `30`; and
  - do not widen this run into correctness publication, Rust implementation work, callable replacement expansion, str negative-count follow-ons, or other replacement-owner families.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists_template_bytes_manifest_promotes_minimal_replacement_rows_to_measured or conditional_group_exists_template_bytes_scorecard_promotes_minimal_replacement_rows_to_measured'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-1149-conditional-template-negative-count-bytes.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not change Rust implementation files, `python/rebar/__init__.py`, correctness fixtures, correctness reports, README text, or tracked ops state prose in this run.
- Reuse the existing `conditional_group_exists_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another benchmark manifest, another benchmark test module, or a detached conditional replacement benchmark file.
- Keep the scope pinned to the exact four bytes `count=-1` workloads above. Leave any same-family str negative-count publication or benchmark work, callable replacements, broader bytes helper execution, and other conditional replacement follow-ons for later tasks.

## Notes
- `RBR-1149` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contain no active feature task in this run; and
  - `rg -n 'RBR-1149|RBR-1150|RBR-1151' ops/tasks ops/state -g '*.md'` matched only historical notes inside completed task files, not a live reservation.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The narrow same-family owner-path check in this run confirms that benchmark catch-up, not another implementation prerequisite, is the surviving post-drain slice:
  - `ops/tasks/done/RBR-1147-publish-conditional-group-exists-template-bytes-negative-count-workflows.md` explicitly leaves same-family benchmark catch-up deferred after publishing the exact four bytes `count=-1` correctness rows;
  - `tests/conformance/fixtures/conditional_group_exists_replacement_template_workflows.py` now carries those exact four published bytes negative-count case ids on the shared conditional replacement-template owner path;
  - `rg -n 'conditional-group-exists.*negative-count|negative-count.*conditional-group-exists' benchmarks/workloads/conditional_group_exists_boundary.py reports/benchmarks/latest.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` returned no matches in this run, confirming the published benchmark surface still omits this exact negative-count slice; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/feature-planning-conditional-template-boundary.py` completed successfully with `96` measured workloads and `0` known gaps, confirming the benchmark owner path is live and the runtime prerequisite is already landed.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists_template_bytes_manifest_promotes_minimal_replacement_rows_to_measured or conditional_group_exists_template_bytes_scorecard_promotes_minimal_replacement_rows_to_measured'` returned `2 passed, 759 deselected`.

## Completion
- Added the exact four bytes `count=-1` conditional replacement-template workloads on the existing `conditional-group-exists-boundary` benchmark manifest owner path, keeping scope pinned to the numbered module `sub()`, named module `subn()`, numbered compiled-pattern `sub()`, and named compiled-pattern `subn()` cases on `b"abcdaceabcd"`.
- Updated the shared benchmark assertion module so the conditional replacement-template slice expectations, representative measured bytes rows, and bytes round-trip/result checks include the new negative-count workloads and preserve the existing str, bytes, callable, alternation-heavy, nested, and quantified neighbors.
- Regenerated `reports/benchmarks/latest.py`; the tracked publication now reports `1031` measured workloads out of `1031` total with `known_gap_count == 0`, and `conditional-group-exists-boundary` now reports `100` measured workloads with `0` known gaps.
- Verification:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists_template_bytes_manifest_promotes_minimal_replacement_rows_to_measured or conditional_group_exists_template_bytes_scorecard_promotes_minimal_replacement_rows_to_measured or conditional_group_exists_template_bytes_workloads_keep_bytes_template_payloads_through_round_trip'`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-1149-conditional-template-negative-count-bytes.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`
