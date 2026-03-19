# RBR-0647: Catch the nested broader-range open-ended branch-local-backreference replacement-template bytes pair up on the benchmark surface

Status: ready
Owner: feature-implementation
Created: 2026-03-19

## Goal
- Extend the published source-tree benchmark surface so the exact broader-range open-ended `{2,}` nested grouped-alternation plus branch-local-backreference replacement-template bytes pair produces real `rebar` timings on the existing nested-group replacement manifest once `RBR-0645` lands.

## Deliverables
- `benchmarks/workloads/nested_group_replacement_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/nested_group_replacement_boundary.py` adds only these four bytes mirrors of the current broader-range open-ended replacement-template `str` rows:
  - `module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-bytes`
  - `module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-bytes`
  - `pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-bytes`
  - `pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-bytes`
- The new rows stay pinned to the existing Python-path public patterns, replacements, and haystacks for this exact bounded slice:
  - `rb"a((b|c){2,})\\2d"` through `module.sub(..., rb"\\1x", b"abbbd")` and `module.subn(..., rb"\\2x", b"abbbdabcbccd", 1)`;
  - `rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d"` through `Pattern.sub(rb"\\g<outer>x", b"zzacccdzz")` and `Pattern.subn(rb"\\g<inner>x", b"zzacccdabcbccdzz", 1)`.
- `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` treat the four new rows as measured source-tree workloads on the existing `broader-range-open-ended-branch-local-backreference` slice while keeping `nested-group-replacement-boundary` and the combined report at zero known gaps. Reuse the existing shared slice and zero-gap expectation surface instead of inventing another benchmark family or a bytes-only benchmark special case.
- Focused and combined benchmark publications move honestly:
  - `nested-group-replacement-boundary` moves from `28` total workloads / `28` measured workloads / `0` known gaps to `32` / `32` / `0`;
  - the combined source-tree report moves from `731` total workloads / `731` measured workloads / `0` known gaps to `735` / `735` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the four new broader-range open-ended replacement-template bytes rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/nested_group_replacement_boundary.py --report .rebar/tmp/rbr-0647-nested-broader-range-open-ended-branch-local-backreference-replacement-bytes-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already targeted behind `rebar._rebar` by `RBR-0645`; do not add new replacement semantics here.
- Reuse the existing `nested_group_replacement_boundary.py` manifest path and the consolidated source-tree benchmark assertion surface instead of inventing another benchmark family or a bytes-only benchmark module.
- Keep the measurements on the Python-facing `rebar` path; do not publish timings for Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.
- Do not broaden into conditional replacements, callable replacements, deeper grouped execution, another branch-local-backreference family, or native-path benchmark publication in this run.

## Notes
- `RBR-0647` is the next available feature task id in the current checkout; `RBR-0646` is already occupied by the done architecture cleanup task in `ops/tasks/done/`.
- Build on `RBR-0645`.
- Queue this directly behind `RBR-0645` so the broader `{2,}` non-conditional replacement-template bytes pair reaches the same Python-path benchmark surface before deeper grouped execution broadens that family.
- 2026-03-19 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `reports/correctness/latest.py` still publishes `1310` total / `1302` passed / `8` `unimplemented` overall, and `collection.replacement.nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference` still reads `16` total / `8` passed / `8` `unimplemented`, so `RBR-0645` remains the immediate parity head rather than a stale no-op;
  - `benchmarks/workloads/nested_group_replacement_boundary.py` currently contains the four adjacent `str` rows for this exact broader-range non-conditional replacement slice and none of the planned `-bytes` mirrors, while the same manifest already carries the four conditional bytes rows landed by `RBR-0629`;
  - `tests/benchmarks/benchmark_expectations.py` currently treats `broader-range-open-ended-branch-local-backreference` on `nested-group-replacement-boundary` as the four `str` rows only, so the bytes follow-on can stay on the existing shared zero-gap expectation surface;
  - `reports/benchmarks/latest.py` currently publishes `nested-group-replacement-boundary` at `28` total workloads / `28` measured workloads / `0` known gaps and the combined source-tree report at `731` / `731` / `0`; and
  - `ops/tasks/done/RBR-0643-nested-broader-range-open-ended-branch-local-backreference-replacement-bytes-pack.md` and the ready `RBR-0645` task already pin the exact patterns, replacement templates, haystacks, and owner paths for this bytes pair, so the benchmark catch-up can stay on the existing manifest without another synthesis pass.
