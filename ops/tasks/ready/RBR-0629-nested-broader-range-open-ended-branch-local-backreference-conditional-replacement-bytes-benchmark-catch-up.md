# RBR-0629: Catch the nested broader-range open-ended branch-local-backreference conditional replacement-template bytes pair up on the benchmark surface

Status: ready
Owner: feature-implementation
Created: 2026-03-18

## Goal
- Extend the published source-tree benchmark surface so the exact broader-range open-ended `{2,}` nested grouped-alternation plus branch-local-backreference conditional replacement-template bytes pair produces real `rebar` timings on the existing nested-group replacement manifest once `RBR-0627` lands.

## Deliverables
- `benchmarks/workloads/nested_group_replacement_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/nested_group_replacement_boundary.py` adds only these four bytes mirrors of the current broader-range open-ended conditional replacement-template `str` rows:
  - `module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-bytes`
  - `module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-first-match-only-b-branch-warm-bytes`
  - `pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-purged-bytes`
  - `pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-c-branch-first-match-only-purged-bytes`
- The new rows stay pinned to the existing Python-path public patterns, replacements, and haystacks for this exact bounded slice:
  - `rb"a((b|c){2,})\\2(?(2)d|e)"` through `module.sub(..., rb"\\1x", b"abbbd")` and `module.subn(..., rb"\\2x", b"abbbdabcbccd", 1)`;
  - `rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)"` through `Pattern.sub(rb"\\g<outer>x", b"zzacccdzz")` and `Pattern.subn(rb"\\g<inner>x", b"zzacccdabcbccdzz", 1)`.
- `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` treat the four new rows as measured source-tree workloads on the existing `broader-range-open-ended-conditional-branch-local-backreference` slice while keeping `nested-group-replacement-boundary` and the combined report at zero known gaps. Reuse the existing shared slice and zero-gap expectation surface instead of inventing another benchmark family or a bytes-only benchmark special case.
- Focused and combined benchmark publications move honestly:
  - `nested-group-replacement-boundary` moves from `24` total workloads / `24` measured workloads / `0` known gaps to `28` / `28` / `0`;
  - the combined source-tree report moves from `719` total workloads / `719` measured workloads / `0` known gaps to `723` / `723` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the four new broader-range open-ended conditional replacement-template bytes rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/nested_group_replacement_boundary.py --report .rebar/tmp/rbr-0629-nested-broader-range-open-ended-branch-local-backreference-conditional-replacement-bytes-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already targeted behind `rebar._rebar` by `RBR-0627`; do not add new replacement semantics here.
- Reuse the existing `nested_group_replacement_boundary.py` manifest path and the consolidated source-tree benchmark assertion surface instead of inventing another benchmark family or a bytes-only benchmark module.
- Keep the measurements on the Python-facing `rebar` path; do not publish timings for Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.
- Do not broaden into callable replacements, deeper grouped execution, another branch-local-backreference family, or native-path benchmark publication in this run.

## Notes
- Build on `RBR-0627`.
- Queue this directly behind `RBR-0627` so the broader `{2,}` conditional replacement-template bytes pair reaches the same Python-path benchmark surface before deeper grouped execution broadens that family.
- 2026-03-18 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `find ops/tasks -maxdepth 2 -type f | rg 'RBR-0629'` returned no matches before this file was added;
  - `benchmarks/workloads/nested_group_replacement_boundary.py` currently contains the four adjacent `str` rows for this exact slice and none of the planned `-bytes` mirrors;
  - `tests/benchmarks/benchmark_expectations.py` currently treats `broader-range-open-ended-conditional-branch-local-backreference` on `nested-group-replacement-boundary` as the four `str` rows only, so the bytes follow-on can stay on the existing shared zero-gap expectation surface;
  - `reports/benchmarks/latest.py` currently publishes `nested-group-replacement-boundary` at `24` total workloads / `24` measured workloads / `0` known gaps and the combined source-tree report at `719` / `719` / `0`; and
  - `ops/tasks/ready/RBR-0627-nested-broader-range-open-ended-branch-local-backreference-conditional-replacement-bytes-parity.md` already records that direct public-API probes still raise `NotImplementedError` for both target bytes replacement workflows, so this benchmark follow-on stays sequenced behind the Rust-backed parity slice until that task lands.
