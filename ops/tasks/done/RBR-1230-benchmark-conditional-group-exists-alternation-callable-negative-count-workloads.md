# RBR-1230: Benchmark conditional group-exists alternation callable negative-count workloads

Status: done
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Catch the already-supported alternation-heavy two-arm conditional callable `count=-1` slice up on the existing Python-path benchmark surface by measuring the exact bounded no-substitution workflows that the live direct parity owner path and newly published correctness fixture already cover for both `str` and `bytes`.

## Pattern Pair
- `rebar.sub(r"a(b)?c(?(1)(de|df)|(eg|eh))", lambda m: m.group(1) + "x", "zzabcdezz", -1)`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))").subn(lambda m: m.group("word") + b"x", b"zzacehzz", -1)`

## Deliverables
- `benchmarks/workloads/conditional_group_exists_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Extend `benchmarks/workloads/conditional_group_exists_boundary.py` with exactly the eight adjacent alternation-heavy conditional callable `count=-1` workloads that sit immediately behind `RBR-1227` on the shared owner path:
  - add the four `str` workloads for `a(b)?c(?(1)(de|df)|(eg|eh))` and `a(?P<word>b)?c(?(word)(de|df)|(eg|eh))` by mirroring the already-measured top-level callable negative-count rows while keeping the bounded alternation-heavy shape on module `sub`, module `subn`, compiled-`Pattern` `sub`, and compiled-`Pattern` `subn`;
  - add the matching four `bytes` workloads for `rb"a(b)?c(?(1)(de|df)|(eg|eh))"` and `rb"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))"` on the same numbered and named module/pattern matrix;
  - keep the replacement descriptors on the existing `callable_match_group` helper pinned to group `1` or `"word"` so CPython's exact `count=-1` no-substitution short-circuit stays explicit on the same benchmark owner path instead of inventing another helper shape; and
  - keep the slice bounded to the alternation-heavy top-level conditional callable family only, leaving any `count=None`, nested, quantified, or broader callable count-contract benchmark publication for later tasks.
- Keep the work on the existing conditional benchmark owner path instead of creating another manifest or detached callable benchmark family:
  - update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` only as needed so the shared `conditional-group-exists-boundary` manifest expectations, representative measured-row checks, workload-id tables, and scorecard sync stay aligned with the widened alternation-heavy negative-count slice;
  - preserve the already-measured alternation-heavy callable present and absent-exception rows plus the surrounding top-level, nested, and quantified callable slices on the same manifest; and
  - do not widen this run into correctness publication, Rust implementation work, or broader callable-helper expansion beyond the existing `callable_match_group` path.
- Regenerate `reports/benchmarks/latest.py` honestly on the tracked combined benchmark surface:
  - the `conditional-group-exists-boundary` manifest grows from `256` workloads to `264` workloads with all `264` measured and `0` known gaps; and
  - the tracked combined benchmark summary moves from `1187/1187` measured workloads to `1195/1195` measured workloads while the manifest count stays at `30`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists_callable and negative_count'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-1230-conditional-group-exists-boundary.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep the scope pinned to the exact eight alternation-heavy conditional callable `count=-1` benchmark workloads above. Do not widen this run into another owner family or another callable benchmark helper.
- Reuse the existing `conditional_group_exists_boundary.py` manifest and source-tree combined benchmark suite. Do not create another benchmark manifest, another callable benchmark module, or a detached alternation-heavy publication file.
- Keep benchmark comparisons running through the Python-facing `rebar` path so the published comparison against stdlib `re` stays faithful at the module boundary.

## Notes
- `RBR-1230` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this planning run; and
  - `rg -n "RBR-1230|RBR-1231" ops/tasks ops/state -g '*.md'` returned no live reservation for either id.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- One narrow same-owner-path scan keeps this exact follow-on concrete behind `RBR-1227`:
  - `ops/tasks/done/RBR-1227-publish-conditional-group-exists-alternation-callable-negative-count-workflows.md` just landed the matching eight alternation-heavy callable `count=-1` correctness rows on the shared owner path;
  - `benchmarks/workloads/conditional_group_exists_boundary.py` currently carries the sixteen alternation-heavy callable present and absent-exception workloads but no alternation-heavy callable `count=-1` rows;
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` already exposes the shared alternation-heavy callable benchmark slice through the `alternation-heavy-callable-replacement-rows` expectation and the `test_conditional_group_exists_callable_scorecards_keep_negative_count_follow_on_workloads_in_sync` assertion path; and
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'negative_count_short_circuits_without_callback and conditional-group-exists-alternation'` passed with `72 passed`, confirming the bounded runtime slice already exists on the current branch.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists_callable and negative_count'` returned `1 passed, 106 deselected`; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/feature-planning-conditional-boundary-current.py` returned `256 measured workloads / 0 known gaps`.

## Completion Notes
- Added the exact eight alternation-heavy conditional callable `count=-1` benchmark workloads on the shared `conditional-group-exists-boundary` owner path for numbered and named module/compiled-`Pattern` `sub()` and `subn()` coverage across `str` and `bytes`.
- Updated the combined benchmark expectations so the alternation-heavy callable slice, public zero-gap bytes subsets, and negative-count follow-on sync assertions all stay aligned with the widened manifest.
- Republished `reports/benchmarks/latest.py`; the tracked report now shows `conditional-group-exists-boundary` at `264` workloads with `264` measured and `0` known gaps, and the combined summary at `1195` measured of `1195` total workloads across `30` manifests.
- Verification run results on this branch:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists_callable and negative_count'` returned `1 passed, 106 deselected`.
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-1230-conditional-group-exists-boundary.py` returned `264 measured workloads / 0 known gaps`.
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py` returned `1195 measured workloads / 0 known gaps / 1195 total workloads`.
