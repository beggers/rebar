# RBR-0659: Catch the nested broader-range wider-ranged-repeat branch-local-backreference replacement-template bytes pair up on the benchmark surface

Status: ready
Owner: feature-implementation
Created: 2026-03-19

## Goal
- Extend the published source-tree benchmark surface so the exact broader `{1,4}` nested grouped-alternation plus branch-local-backreference replacement-template bytes pair produces real `rebar` timings on the existing `nested-group-replacement-boundary` manifest once `RBR-0657` lands.

## Deliverables
- `benchmarks/workloads/nested_group_replacement_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/nested_group_replacement_boundary.py` adds only these four bytes mirrors of the current broader `{1,4}` replacement-template `str` rows:
  - `module-sub-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-bytes`
  - `module-subn-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-bytes`
  - `pattern-sub-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-bytes`
  - `pattern-subn-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-bytes`
- The new rows stay pinned to the existing Python-path public patterns, replacements, and haystacks for this exact bounded slice:
  - `rb"a((b|c){1,4})\\2d"` through `module.sub(..., rb"\\1x", b"abbd")` and `module.subn(..., rb"\\2x", b"abbbdaccd", 1)`;
  - `rb"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d"` through `Pattern.sub(rb"\\g<outer>x", b"zzacccccdzz")` and `Pattern.subn(rb"\\g<inner>x", b"zzacccccdabbbdzz", 1)`.
- `tests/benchmarks/benchmark_expectations.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` treat the four new rows as measured source-tree workloads on the existing `broader-range-branch-local-backreference` slice while keeping `nested-group-replacement-boundary` and the combined report at zero known gaps. Reuse the existing shared slice and zero-gap expectation surface instead of inventing another benchmark family or a bytes-only benchmark special case.
- Focused and combined benchmark publications move honestly:
  - `nested-group-replacement-boundary` moves from `36` total workloads / `36` measured workloads / `0` known gaps to `40` / `40` / `0`;
  - the combined source-tree report moves from `739` total workloads / `739` measured workloads / `0` known gaps to `743` / `743` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the four new broader `{1,4}` replacement-template bytes rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/nested_group_replacement_boundary.py --report .rebar/tmp/rbr-0659-nested-broader-range-wider-ranged-repeat-branch-local-backreference-replacement-bytes-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already targeted behind `rebar._rebar` by `RBR-0657`; do not add new replacement semantics here.
- Reuse the existing `nested_group_replacement_boundary.py` manifest path and the consolidated source-tree benchmark assertion surface instead of inventing another benchmark family or a bytes-only benchmark module.
- Keep the measurements on the Python-facing `rebar` path; do not publish timings for Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.
- Do not broaden into conditional replacements, callable replacements, deeper grouped execution, another branch-local-backreference family, or native-path benchmark publication in this run.

## Notes
- `RBR-0659` is the next available feature task id in the current checkout; `RBR-0658` is already occupied by the done architecture cleanup task in `ops/tasks/done/`.
- Build on `RBR-0657`.
- Queue this directly behind `RBR-0657` so the broader `{1,4}` non-callable replacement-template bytes pair reaches the same Python-path benchmark surface before deeper grouped execution broadens that family.
- 2026-03-19 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `reports/correctness/latest.py` currently publishes `1326` total / `1318` passed / `8` `unimplemented` overall, and `collection.replacement.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference` still reads `16` total / `8` passed / `8` `unimplemented`, so ready `RBR-0657` remains the immediate parity head rather than a stale no-op;
  - `benchmarks/workloads/nested_group_replacement_boundary.py` currently contains the four adjacent `str` rows for this exact broader `{1,4}` non-conditional replacement slice and none of the planned `-bytes` mirrors;
  - `tests/benchmarks/benchmark_expectations.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently treat `broader-range-branch-local-backreference` on `nested-group-replacement-boundary` as the four `str` rows only, so the bytes follow-on can stay on the existing shared zero-gap expectation surface;
  - `reports/benchmarks/latest.py` currently publishes `nested-group-replacement-boundary` at `36` measured workloads / `0` known gaps and the combined source-tree report at `739` / `739` / `0`; and
  - `ops/tasks/done/RBR-0655-nested-broader-range-wider-ranged-repeat-branch-local-backreference-replacement-bytes-pack.md` plus ready `RBR-0657` already pin the exact patterns, replacement templates, haystacks, and owner paths for this bytes pair, so the benchmark catch-up can stay on the existing manifest without another synthesis pass.
