Status: ready
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Catch the already-supported quantified two-arm conditional callable `count=None` slice up on the existing Python-path benchmark surface by measuring the exact bounded `sub()` and `subn()` workflows that the live direct parity owner path and newly published correctness fixture already cover for both `str` and `bytes`.

## Pattern Pair
- `rebar.sub(r"a(b)?c(?(1)d|e){2}", lambda m: m.group(1) + "x", "zzabcddzz", None)`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)d|e){2}").subn(lambda m: m.group("word") + b"x", b"zzaceezz", None)`

## Deliverables
- `benchmarks/workloads/conditional_group_exists_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Extend `benchmarks/workloads/conditional_group_exists_boundary.py` with exactly the eight adjacent quantified conditional callable `count=None` workloads that sit immediately behind `RBR-1240` on the shared owner path:
  - add the four `str` workloads for `a(b)?c(?(1)d|e){2}` and `a(?P<word>b)?c(?(word)d|e){2}` by mirroring the already-measured quantified negative-count quartet while passing `count=None`, keeping the bounded shape on module `sub`, module `subn`, compiled-`Pattern` `sub`, and compiled-`Pattern` `subn`;
  - add the matching four `bytes` workloads for `rb"a(b)?c(?(1)d|e){2}"` and `rb"a(?P<word>b)?c(?(word)d|e){2}"` on the same numbered and named module/pattern matrix;
  - keep the replacement descriptors on the existing `callable_match_group` helper pinned to group `1` or `"word"` so CPython's invalid-`count` `TypeError` stays explicit on the same benchmark owner path instead of inventing another callable helper shape; and
  - keep the slice bounded to the quantified conditional callable family only, leaving broader callable count-contract benchmark publication for a later planning pass.
- Keep the work on the existing conditional benchmark owner path instead of creating another manifest or detached callable benchmark family:
  - update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` only as needed so the shared `conditional-group-exists-boundary` manifest expectations, representative measured-row checks, workload-id tables, and scorecard sync stay aligned with the widened quantified `count=None` slice;
  - preserve the already-measured quantified callable present, absent-exception, no-match, and negative-count rows plus the surrounding top-level, alternation-heavy, and nested callable slices on the same manifest; and
  - do not widen this run into correctness publication, Rust implementation work, or broader callable-helper expansion beyond the existing `callable_match_group` path.
- Regenerate `reports/benchmarks/latest.py` honestly on the tracked combined benchmark surface:
  - the `conditional-group-exists-boundary` manifest grows from `280` workloads to `288` workloads with all `288` measured and `0` known gaps; and
  - the tracked combined benchmark summary moves from `1211/1211` measured workloads to `1219/1219` measured workloads while the manifest count stays at `30`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'quantified_callable and promotes'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'quantified_callable and scorecards'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-1242-conditional-group-exists-boundary.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep the scope pinned to the exact eight quantified conditional callable `count=None` benchmark workloads above. Do not widen this run into another owner family or another callable benchmark helper.
- Reuse the existing `conditional_group_exists_boundary.py` manifest and source-tree combined benchmark suite. Do not create another benchmark manifest, another callable benchmark module, or a detached quantified `count=None` publication file.
- Keep benchmark comparisons running through the Python-facing `rebar` path so the published comparison against stdlib `re` stays faithful at the module boundary.

## Notes
- `RBR-1242` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this planning run; and
  - the highest filed task before this seed was `RBR-1241`.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- One narrow same-owner-path scan keeps this exact follow-on concrete after `RBR-1240`:
  - `ops/tasks/done/RBR-1240-publish-conditional-group-exists-quantified-callable-none-count-workflows.md` explicitly leaves the same-route quantified callable `count=None` benchmark catch-up for a separate planning pass while saying no broader callable count-contract slice is pinned beyond it;
  - `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` and `tests/python/test_callable_replacement_parity_suite.py` already cover the bounded quantified callable `count=None` owner slice for both `str` and `bytes`;
  - `benchmarks/workloads/conditional_group_exists_boundary.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently carry the quantified callable present, absent-exception, no-match, and negative-count rows but no quantified callable `count=None` workloads; and
  - the tracked benchmark report already measures `280/280` workloads with `0` known gaps on `conditional-group-exists-boundary`, so this task stays a pure same-route publication catch-up rather than a missing-runtime prerequisite.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'quantified_callable and promotes'` returned `2 passed, 106 deselected, 160 subtests passed`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'quantified_callable and scorecards'` returned `1 passed, 107 deselected`; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/feature-planning-conditional-quantified-current.py` returned `280 measured workloads / 0 known gaps / 280 total workloads`.
