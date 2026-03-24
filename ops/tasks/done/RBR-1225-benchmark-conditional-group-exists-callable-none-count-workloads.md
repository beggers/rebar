# RBR-1225: Benchmark conditional group-exists callable None-count workloads

Status: done
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Catch the already-supported and now-queued top-level two-arm conditional callable `count=None` slice up on the existing Python-path benchmark surface by measuring the exact bounded `sub()` and `subn()` workflows that the live direct parity owner path already covers for both `str` and `bytes`.

## Pattern Pair
- `rebar.sub(r"a(b)?c(?(1)d|e)", lambda m: m.group(1) + "x", "zzabcdzz", None)`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)d|e)").subn(lambda m: m.group("word") + b"x", b"zzacezz", None)`

## Deliverables
- `benchmarks/workloads/conditional_group_exists_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Extend `benchmarks/workloads/conditional_group_exists_boundary.py` with exactly the twenty-four adjacent top-level two-arm conditional callable `count=None` workloads that sit immediately behind `RBR-1223` on the shared owner path:
  - add the twelve `str` workloads for `a(b)?c(?(1)d|e)` and `a(?P<word>b)?c(?(word)d|e)` across numbered and named module/compiled-`Pattern` `sub()` and `subn()` entrypoints by mirroring the already-measured present, absent-exception, and negative-count top-level callable rows while passing `count=None`;
  - add the matching twelve `bytes` workloads for `rb"a(b)?c(?(1)d|e)"` and `rb"a(?P<word>b)?c(?(word)d|e)"` on the same numbered/named module/pattern matrix;
  - keep the replacement descriptors on the existing `callable_match_group` helper pinned to group `1` or `"word"` so CPython's `TypeError` remains explicit on the same benchmark owner path instead of inventing another helper shape; and
  - keep the slice bounded to the top-level two-arm conditional callable family only, leaving alternation-heavy, nested, quantified, and any broader callable count-contract benchmark publication for later tasks.
- Keep the work on the existing conditional benchmark owner path instead of creating another manifest or detached callable benchmark family:
  - update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` only as needed so the shared `conditional-group-exists-boundary` manifest expectations, representative measured-row checks, workload-id tables, scorecard sync, and correctness-anchor coverage stay aligned with the widened top-level `count=None` slice;
  - preserve the already-measured top-level callable present, absent-exception, and negative-count rows plus the surrounding nested, quantified, and alternation-heavy callable slices on the same manifest; and
  - do not widen this run into correctness publication, Rust implementation work, or broader callable-helper expansion beyond the existing `callable_match_group` path.
- Regenerate `reports/benchmarks/latest.py` honestly on the tracked combined benchmark surface:
  - the `conditional-group-exists-boundary` manifest grows from `232` workloads to `256` workloads with all `256` measured and `0` known gaps; and
  - the tracked combined benchmark summary moves from `1163/1163` measured workloads to `1187/1187` measured workloads while the manifest count stays at `30`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists_callable'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-1225-conditional-group-exists-boundary.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep the scope pinned to the exact twenty-four top-level conditional callable `count=None` benchmark workloads above. Do not widen this run into a new owner family or another callable benchmark helper.
- Reuse the existing `conditional_group_exists_boundary.py` manifest and source-tree combined benchmark suite. Do not create another benchmark manifest, another callable benchmark module, or a detached top-level `count=None` publication file.
- Keep benchmark comparisons running through the Python-facing `rebar` path so the published comparison against stdlib `re` stays faithful at the module boundary.

## Notes
- `RBR-1225` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained only `RBR-1223` as live feature work in this planning run; and
  - `rg -n "RBR-1225|RBR-1226" ops/tasks ops/state -g '*.md'` matched only historical mentions inside completed task files, not a live reservation for this id.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- One narrow same-owner-path scan keeps this exact follow-on concrete behind `RBR-1223`:
  - `tests/python/test_callable_replacement_parity_suite.py` already exercises the bounded top-level conditional callable `count=None` parity path with `72 passed` on `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'none_count_matches_cpython_typeerror and conditional-group-exists and not alternation and not nested and not quantified'`;
  - `ops/tasks/ready/RBR-1223-publish-conditional-group-exists-callable-none-count-workflows.md` already pins the adjacent correctness publication slice for those same top-level numbered and named module/pattern `str` and `bytes` workflows;
  - `benchmarks/workloads/conditional_group_exists_boundary.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently carry the top-level callable present, absent-exception, and negative-count rows but no top-level callable `count=None` workloads; and
  - no newer same-family done task or blocked note pins an exact post-drain feature follow-on after this benchmark catch-up slice, so the existing backlog/current-status frontier wording remains honest without a separate state edit in this run.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists_callable'` returned `5 passed, 112 deselected, 60 subtests passed`;
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/feature-planning-conditional-callable-current.py` returned `232 measured workloads / 0 known gaps`; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report .rebar/tmp/feature-planning-benchmarks-current.py` returned `1163 measured workloads / 0 known gaps`.

## Completion
- Added the exact 24 top-level conditional callable `count=None` benchmark rows to `benchmarks/workloads/conditional_group_exists_boundary.py`, plus the minimal benchmark-harness count-materialization support needed for explicit `None`.
- Updated `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the shared conditional manifest expectations, bytes representative subsets, scorecard sync checks, and suffix-only callable replacement round-trips cover the new `count=None` rows without widening into nested, quantified, or alternation-heavy follow-ons.
- Regenerated the tracked combined benchmark publication in `reports/benchmarks/latest.py`; the tracked artifact now shows `conditional-group-exists-boundary` at `256` workloads and the combined published benchmark summary at `1187/1187` measured workloads across `30` manifests.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists_callable'` -> `10 passed, 100 deselected, 160 subtests passed`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-1225-conditional-group-exists-boundary.py` -> `256 measured workloads / 0 known gaps`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py` -> `1187 measured workloads / 0 known gaps`
