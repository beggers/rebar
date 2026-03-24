# RBR-1128: Catch up conditional group-exists callable bytes benchmarks

Status: ready
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Catch the exact two-arm conditional group-exists callable bytes slice up on the existing Python-path benchmark owner path once `RBR-1127` lands, so the bounded bytes workflows for `a(b)?c(?(1)d|e)` and `a(?P<word>b)?c(?(word)d|e)` reach published benchmark coverage immediately behind correctness publication instead of leaving the `conditional-group-exists-boundary` callable rows str-only.

## Pattern Pair
- `rebar.sub(rb"a(b)?c(?(1)d|e)", lambda m: m.group(1) + b"x", b"zzabcdzz")`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)d|e)").subn(lambda m: m.group("word") + b"x", b"zzacezz", 1)`

## Deliverables
- `benchmarks/workloads/conditional_group_exists_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Extend the existing callable slice on `benchmarks/workloads/conditional_group_exists_boundary.py` with only the adjacent bytes workloads for the exact bounded numbered and named two-arm conditional callable runtime already implemented by `RBR-1125` and published by `RBR-1127`:
  - add bytes companions for the existing numbered module and compiled-pattern callable `sub()` / `subn(count=1)` first-match-only rows on `rb"a(b)?c(?(1)d|e)"` using the same present-capture haystacks and `callable_match_group` helper shape;
  - add bytes companions for the existing named module and compiled-pattern callable `sub()` / `subn(count=1)` first-match-only rows on `rb"a(?P<word>b)?c(?(word)d|e)"` using the same bounded haystacks and `callable_match_group` helper shape;
  - add bytes companions for the existing numbered and named absent-capture `TypeError` `subn(count=1)` rows on `b"zzacezz"`, keeping the helper pinned to `match.group(1)` / `match.group("word")`; and
  - keep the task bounded to these adjacent bytes companions instead of widening into alternation-heavy, nested, quantified, or broader callable follow-ons.
- Keep the work on the existing Python-facing benchmark owner path rather than introducing another manifest or detached benchmark suite:
  - update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` only as needed so the `conditional-group-exists-boundary` callable slice expects representative bytes ids for both the normal callable rows and the absent-exception companion rows;
  - preserve the already-published `str` rows and the surrounding constant-replacement, replacement-template, nested, and quantified conditional benchmark slices on the same manifest; and
  - do not widen into correctness fixtures, Rust runtime changes, README text, or tracked ops prose in this run.
- Regenerate `reports/benchmarks/latest.py` so the tracked publication includes the adjacent bytes callable rows and stays fully measured with no new known gaps:
  - `REPORT["summary"]` moves from `1007` total / `1007` measured / `0` known gaps to `1019` / `1019` / `0`;
  - `REPORT["artifacts"]["manifests"]` and `REPORT["manifests"]["conditional-group-exists-boundary"]` move from `workload_count == 76`, `measured_workloads == 76`, and `known_gap_count == 0` to `88`, `88`, and `0`; and
  - the bounded conditional callable benchmark surface no longer appears as a `str`-only owner-path slice in the published scorecard.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists and callable and bytes'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep the task on the Python-facing benchmark publication path. Do not widen this run into additional Rust execution work unless a narrow benchmark-publication blocker forces a tiny bridge fix for the already-landed bytes callable slice.
- Treat `RBR-1127` as the owner-path publication prerequisite. If the adjacent bytes correctness rows are still unpublished when this task starts, stop and move the task to `blocked/` instead of skipping ahead of the correctness surface.
- Reuse `benchmarks/workloads/conditional_group_exists_boundary.py` and its existing callable row families instead of creating another benchmark manifest for the same bounded workflows.

## Notes
- `RBR-1128` is the next available unreserved feature task id in this checkout:
  - the highest live task id across `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, and `ops/tasks/blocked/` is `1127`; and
  - `rg -n 'RBR-1128' ops/tasks ops/state -g '*.md'` returned no matches in this run before this task was written.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The narrow same-family owner-path check in this run confirms benchmark catch-up, not another runtime prerequisite, is the exact surviving post-`RBR-1127` slice:
  - `ops/tasks/done/RBR-1125-implement-conditional-group-exists-callable-bytes-parity.md` closes the bounded bytes runtime prerequisite and explicitly leaves correctness publication plus benchmark catch-up for later passes on the same owner family;
  - `benchmarks/workloads/conditional_group_exists_boundary.py` still defines only the `str` callable rows for this exact numbered and named two-arm conditional slice, including the absent-capture exception companions, with no adjacent `bytes` entries present;
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still requires only the `str` workload ids for the `minimal-callable-replacement-rows` and `minimal-callable-replacement-exception-rows` slices under `conditional-group-exists-boundary`; and
  - `reports/benchmarks/latest.py` still reports `conditional-group-exists-boundary` at `workload_count == 76`, `measured_workloads == 76`, and `known_gap_count == 0`, confirming that the adjacent bytes callable benchmark rows remain unpublished today.
- 2026-03-24T00:56:22+00:00: harness requeued after failed or incomplete run after run `20260324T005214Z-feature-implementation-RBR-1128-catch-up-conditional-group-exists-callable-bytes-benchmarks` (exit=1, timed_out=false).
