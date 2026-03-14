# RBR-0340: Catch nested broader-range wider-ranged-repeat quantified-group alternation plus branch-local-backreference benchmarks up with the new slice

Status: done
Owner: feature-implementation
Created: 2026-03-14

## Goal
- Extend the published benchmark surface so the bounded broader `{1,4}` counted-repeat nested-group-alternation-plus-branch-local-backreference workflows supported by `RBR-0338` produce real `rebar` timings on the existing nested-group alternation manifest instead of remaining unpublished on the benchmark side.

## Deliverables
- `benchmarks/workloads/nested_group_alternation_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- The benchmark harness catches the bounded broader `{1,4}` counted-repeat nested-group-alternation-plus-branch-local-backreference slice up on the existing `benchmarks/workloads/nested_group_alternation_boundary.py` path by adding only the minimal adjacent numbered and named compile/module/pattern rows needed to publish this exact frontier.
- `reports/benchmarks/latest.py` records real `rebar` timings for supported `a((b|c){1,4})\\2d` and `a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d` workflows through the public Python-facing `rebar` path, including one numbered lower-bound same-branch `module.search()` success such as `abbd` or `accd`, one named broader counted-repeat or upper-bound `Pattern.fullmatch()` success such as `abccd`, `abcbccd`, or `acccccd`, and one bounded compile companion that keeps the broader `{1,4}` slice observable without widening into open-ended counted repeats, replacement semantics, conditionals, or deeper nested grouped execution.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and continue measuring through the Python-facing `rebar` module boundary so comparisons against stdlib `re` stay faithful.
- The task does not broaden regex support, fork a new benchmark family, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0338`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current consolidated source-tree benchmark assertions instead of reviving standalone manifest-specific tests.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0338`.
- Keep this follow-on on the existing `nested_group_alternation_boundary.py` manifest path instead of forking another benchmark family.
- Add only the directly adjacent numbered and named rows needed to publish this exact slice cleanly; open-ended counted repeats, replacement workflows, conditionals, and deeper nested grouped execution stay out of scope.

## Completion Notes
- Added the minimal broader `{1,4}` counted-repeat branch-local trio on `benchmarks/workloads/nested_group_alternation_boundary.py`: a numbered lower-bound `module.search()` success on `zzabbdzz`, a named `module.compile()` companion, and a named upper-bound `Pattern.fullmatch()` success on `acccccd`.
- Updated the combined source-tree benchmark expectations so `nested-group-alternation-boundary` now pins three distinct measured branch-local slices on the same manifest: the earlier non-quantified rows, the `+` quantified rows, and this new broader counted-repeat `{1,4}` trio.
- Republished `reports/benchmarks/latest.py`; the tracked combined benchmark scorecard now reports `510` total workloads, `483` measured `rebar` timings, and `27` explicit known gaps, while the tracked `nested-group-alternation-boundary` manifest reports `19` workloads with `19` measured rows and `0` remaining gaps.
- Verified with `cargo build -p rebar-cpython`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --internal-probe-rebar-metadata`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_nested_group_alternation_branch_local_backreference_parity.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/nested_group_alternation_boundary.py --report /tmp/rebar-rbr0340-nested-group-alternation-bench.json`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.
