# RBR-1106: Catch up quantified nested-group callable bytes benchmarks

Status: ready
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Catch the newly published quantified nested-group callable bytes slice up on the existing Python-path benchmark owner path by replacing the last str-only quantified callable benchmark quartet with bounded bytes workloads and refreshed scorecards before any broader same-family callable expansion reopens the frontier.

## Pattern Pair
- `rebar.sub(rb"a((bc)+)d", lambda m: b"<" + m.group(1) + b">", b"zzabcdzz")`
- `rebar.compile(rb"a(?P<outer>(?P<inner>bc)+)d").subn(lambda m: b"<" + m.group("inner") + b">", b"zzabcbcdabcbcdzz", 1)`

## Deliverables
- `benchmarks/workloads/nested_group_callable_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Extend the existing `quantified-nested-group` slice in `benchmarks/workloads/nested_group_callable_replacement_boundary.py` with only the adjacent bytes workloads for the already-landed bounded quantified nested-group callable runtime:
  - numbered module `sub()` and `subn(count=1)` rows for `rb"a((bc)+)d"` on the existing lower-bound and first-match-only haystacks;
  - named compiled-pattern `sub()` and `subn(count=1)` rows for `rb"a(?P<outer>(?P<inner>bc)+)d"` on the existing repeated-outer and first-match-only haystacks; and
  - preserve the current `str` quantified rows on the same owner path instead of moving or widening the slice.
- Keep the benchmark catch-up bounded to the existing quantified nested-group callable owner family:
  - update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` only as needed so the combined benchmark contract explicitly requires representative bytes ids for the quantified nested-group callable slice;
  - do not widen into quantified nested alternation, branch-local backreferences, broader counted repeats, correctness fixtures, README text, or tracked ops state prose; and
  - keep the surrounding grouped and nested-group callable benchmark slices green on the same manifest.
- Regenerate `reports/benchmarks/latest.py` so the tracked publication includes the adjacent bytes quantified callable rows and remains fully measured with no new known gaps:
  - `REPORT["summary"]` moves from `991` total / `991` measured / `0` known gaps to `995` / `995` / `0`;
  - the published `nested-group-callable-replacement-boundary` manifest moves from `88` selected / `88` measured / `0` known gaps to `92` / `92` / `0`; and
  - the quantified nested-group callable slice no longer appears as a str-only quartet on the published benchmark surface.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'quantified_nested_group and callable'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep the work on the Python-facing benchmark publication path. Do not widen this task into more Rust runtime changes unless a narrow benchmark publication blocker forces a tiny bridge fix for the already-landed bytes callable slice.
- Preserve the same bounded quantified nested-group callable semantics that `RBR-1102` and `RBR-1104` already landed; this task is benchmark catch-up, not broader callable-replacement design.
- Do not create a second benchmark manifest or detach this slice from `benchmarks/workloads/nested_group_callable_replacement_boundary.py`.

## Notes
- `RBR-1106` is the next available unreserved feature task id in this checkout:
  - the highest live task id across `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, and `ops/tasks/blocked/` is `1105`; and
  - `rg -n 'RBR-1106|RBR-1107|RBR-1108' ops/tasks ops/state -g '*.md'` returned no reserved future feature id in this run.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest same-family feature completion note explicitly leaves benchmark catch-up as the next deferred adjacent slice:
  - `ops/tasks/done/RBR-1104-publish-quantified-nested-group-callable-bytes-workflows.md` says to publish correctness first and leave the same-family benchmark follow-on for later; and
  - the narrow owner-path check in this run shows `benchmarks/workloads/nested_group_callable_replacement_boundary.py` still carries only four quantified nested-group callable rows, all with `text_model: 'str'`, including the former `pattern-subn-callable-named-quantified-nested-group-purged-gap` anchor.
- The existing benchmark contract already pins the exact same owner path and slice boundary:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` defines the `quantified-nested-group` slice on `nested-group-callable-replacement-boundary` with the four current str ids; and
  - the bytes callable runtime prerequisite is already satisfied by `RBR-1102`, so this is publication catch-up rather than another implementation prerequisite.
