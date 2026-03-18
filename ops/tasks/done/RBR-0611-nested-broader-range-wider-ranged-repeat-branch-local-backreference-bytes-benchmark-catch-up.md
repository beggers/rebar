# RBR-0611: Catch the nested broader-range wider-ranged-repeat branch-local-backreference bytes pair up on the benchmark surface

Status: done
Owner: feature-implementation
Created: 2026-03-18
Completed: 2026-03-18

## Goal
- Extend the published source-tree benchmark surface so the exact broader `{1,4}` nested grouped-alternation branch-local-backreference bytes pair produces real `rebar` timings on the existing nested-group alternation manifest.

## Deliverables
- `benchmarks/workloads/nested_group_alternation_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/nested_group_alternation_boundary.py` adds only these three bytes mirrors of the current broader `{1,4}` nested-group alternation branch-local-backreference `str` rows:
  - `module-search-numbered-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-lower-bound-b-branch-warm-bytes`
  - `module-compile-named-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-warm-bytes`
  - `pattern-fullmatch-named-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-upper-bound-all-c-purged-bytes`
- The new rows stay pinned to the existing Python-path public patterns and haystacks for this exact bounded slice:
  - `rb"a((b|c){1,4})\\2d"` through `module.search(..., b"zzabbdzz")`;
  - `rb"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d"` through `module.compile(...)` and `Pattern.fullmatch(b"acccccd")`.
- `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` treat the three new rows as measured source-tree workloads while keeping `nested-group-alternation-boundary` and the combined report at zero known gaps. Reuse the existing slice-derived representative path by widening the current `broader-range-branch-local-backreference` slice and shared zero-gap expectation surface instead of inventing another benchmark family or a manifest-local bytes special case.
- Focused and combined benchmark publications move honestly:
  - `nested-group-alternation-boundary` moves from `25` total workloads / `25` measured workloads / `0` known gaps to `28` / `28` / `0`;
  - the combined source-tree report moves from `707` total workloads / `707` measured workloads / `0` known gaps to `710` / `710` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the three new broader-range branch-local-backreference bytes rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/nested_group_alternation_boundary.py --report .rebar/tmp/rbr-0611-nested-broader-range-wider-ranged-repeat-branch-local-backreference-bytes-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already targeted behind `rebar._rebar`; do not add new execution semantics here.
- Reuse the existing `nested_group_alternation_boundary.py` manifest path and the consolidated source-tree benchmark assertion surface instead of inventing another benchmark family or a bytes-only test path.
- Keep the measurements on the Python-facing `rebar` path; do not publish timings for Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0609`.
- Queue this directly behind `RBR-0609` so the broader `{1,4}` bytes parity slice reaches the same Python-path benchmark surface before open-ended nested branch-local-backreference bytes work or deeper grouped execution broadens that family.
- 2026-03-18 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `ops/tasks/ready/RBR-0609-nested-broader-range-wider-ranged-repeat-branch-local-backreference-bytes-parity.md` already pins the exact numbered and named bytes pair for `rb"a((b|c){1,4})\\2d"` and `rb"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d"`, and its notes already call for a later benchmark follow-on that mirrors the three adjacent `str` rows on the existing nested-group alternation benchmark surface;
  - `benchmarks/workloads/nested_group_alternation_boundary.py` currently contains the three broader-range nested-group branch-local-backreference `str` workloads for this exact slice as `module-search-numbered-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-lower-bound-b-branch-warm-str`, `module-compile-named-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-warm-str`, and `pattern-fullmatch-named-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-upper-bound-all-c-purged-str`, and none of the planned `-bytes` mirrors;
  - `tests/benchmarks/benchmark_expectations.py` currently keeps `nested-group-alternation-boundary` on the shared slice-derived representative path, with the `broader-range-branch-local-backreference` slice already owning the three adjacent `str` rows for this exact pair, so the follow-on can stay on the existing zero-gap assertion surface instead of inventing another bytes-specific benchmark contract;
  - `reports/benchmarks/latest.py` currently publishes `nested-group-alternation-boundary` at `25` total workloads / `25` measured workloads / `0` known gaps and the combined source-tree report at `707` / `707` / `0`; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this planning run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`, so this benchmark follow-on stays sequenced behind `RBR-0609` until parity lands.
- No further broader-range nested branch-local-backreference bytes family should be queued ahead of this benchmark catch-up while the mixed `str`/`bytes` slice is still missing these source-tree benchmark mirrors.

## Completion Note
- 2026-03-18: Added the three bytes mirrors for the broader `{1,4}` nested grouped-alternation branch-local-backreference slice to `benchmarks/workloads/nested_group_alternation_boundary.py`: the numbered `module.search(...)` lower-bound `b`-branch hit, the named `module.compile(...)` warm compile row, and the named `Pattern.fullmatch(...)` upper-bound all-`c` row.
- Widened the shared `broader-range-branch-local-backreference` slice in `tests/benchmarks/benchmark_expectations.py` so the existing slice-derived zero-gap surface now includes the new bytes rows without creating a bytes-only manifest contract or another benchmark family.
- Added direct benchmark regressions in `tests/benchmarks/test_source_tree_benchmark_scorecards.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to pin the new bytes rows plus the `nested-group-alternation-boundary` `28` total / `28` measured / `0` known-gap state on top of the generic slice checks.
- Republished `reports/benchmarks/latest.py`; the tracked report now shows `nested-group-alternation-boundary` at `28` total workloads / `28` measured workloads / `0` known gaps, and the combined source-tree benchmark summary at `710` total workloads / `710` measured workloads / `0` known gaps.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/nested_group_alternation_boundary.py --report .rebar/tmp/rbr-0611-nested-broader-range-wider-ranged-repeat-branch-local-backreference-bytes-benchmarks.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.
