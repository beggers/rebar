# RBR-1112: Catch up quantified nested-group alternation callable bytes benchmarks

Status: done
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Catch the newly published quantified nested-group alternation callable bytes slice up on the existing Python-path benchmark owner path by measuring the exact bounded bytes workflows that `RBR-1110` published, before any broader same-family callable-replacement expansion reopens the frontier.

## Pattern Pair
- `rebar.sub(rb"a((b|c)+)d", lambda m: b"<" + m.group(1) + b">", b"zzabdzz")`
- `rebar.compile(rb"a(?P<outer>(?P<inner>b|c)+)d").subn(lambda m: b"<" + m.group("inner") + b">", b"zzabccdacbbdzz", 1)`

## Deliverables
- `benchmarks/workloads/nested_group_callable_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Extend the existing `quantified-nested-alternation` slice in `benchmarks/workloads/nested_group_callable_replacement_boundary.py` with only the adjacent bytes workloads for the already-landed bounded quantified nested-group alternation callable runtime:
  - numbered module `sub()` and `subn(count=1)` rows for `rb"a((b|c)+)d"` on the existing lower-bound `b`-branch and first-match-only mixed-branch haystacks;
  - named compiled-pattern `sub()` and `subn(count=1)` rows for `rb"a(?P<outer>(?P<inner>b|c)+)d"` on the existing repeated-mixed and first-match-only `c`-branch haystacks; and
  - preserve the current `str` quantified nested alternation rows on the same owner path instead of moving or widening the slice.
- Keep the benchmark catch-up bounded to the existing quantified nested-group alternation callable owner family:
  - update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` only as needed so the combined benchmark contract explicitly requires representative bytes ids for the `quantified-nested-alternation` slice;
  - do not widen into quantified nested-group non-alternation rows, branch-local backreferences, broader counted repeats, correctness fixtures, README text, or tracked ops state prose; and
  - keep the surrounding grouped, nested-group, and quantified nested-group callable benchmark slices green on the same manifest.
- Regenerate `reports/benchmarks/latest.py` so the tracked publication includes the adjacent bytes quantified nested alternation callable rows and remains fully measured with no new known gaps:
  - `REPORT["summary"]` moves from `995` total / `995` measured / `0` known gaps to `999` / `999` / `0`;
  - `REPORT["summary"]["workloads_by_cache_mode"]` moves from `{"cold": 104, "purged": 431, "warm": 460}` to `{"cold": 104, "purged": 433, "warm": 462}`;
  - `REPORT["manifests"]["nested-group-callable-replacement-boundary"]` moves from `selected_workload_count == 92`, `measured_workloads == 92`, `known_gap_count == 0`, and `workload_count == 92` to `96`, `96`, `0`, and `96`; and
  - the quantified nested-group alternation callable slice no longer appears as a str-only quartet on the published benchmark surface.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'quantified_nested_group_alternation and callable'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep the work on the Python-facing benchmark publication path. Do not widen this task into more Rust runtime changes unless a narrow benchmark publication blocker forces a tiny bridge fix for the already-landed bytes callable slice.
- Preserve the same bounded quantified nested-group alternation callable semantics that `RBR-1108` and `RBR-1110` already landed; this task is benchmark catch-up, not broader callable-replacement design.
- Do not create a second benchmark manifest or detach this slice from `benchmarks/workloads/nested_group_callable_replacement_boundary.py`.

## Notes
- `RBR-1112` is the next available unreserved feature task id in this checkout:
  - the highest live task id across `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, and `ops/tasks/blocked/` is `1111`; and
  - `rg -n 'RBR-1112|RBR-1113|RBR-1114|RBR-1115' ops/tasks ops/state -g '*.md'` returned only historical mentions inside done-task notes in this run.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest same-family feature completion note explicitly leaves benchmark catch-up as the next deferred adjacent slice:
  - `ops/tasks/done/RBR-1110-publish-quantified-nested-group-alternation-callable-bytes-workflows.md` says to publish correctness first and leave the same-family benchmark follow-on for later; and
  - the narrow owner-path check in this run shows `benchmarks/workloads/nested_group_callable_replacement_boundary.py` and `reports/benchmarks/latest.py` still carry only the four `str` workload ids for the bounded quantified nested-group alternation callable slice, with no adjacent bytes ids yet present.
- The existing benchmark contract already pins the exact same owner path and slice boundary:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` defines the `quantified-nested-alternation` slice on `nested-group-callable-replacement-boundary` with the four current `str` ids; and
  - the bytes callable runtime and correctness prerequisites are already satisfied by `RBR-1108` and `RBR-1110`, so this is benchmark publication catch-up rather than another implementation prerequisite.
- `ops/state/backlog.md` and the queue-frontier prose in `ops/state/current_status.md` already honestly describe the post-drain frontier for a single ready feature task: no ready feature follow-on currently survives in this checkout, so this run does not need tracked state-prose edits.

## Completion
- Extended `benchmarks/workloads/nested_group_callable_replacement_boundary.py` with only the adjacent four bytes quantified nested-group alternation callable rows on the existing `quantified-nested-alternation` owner slice, keeping the existing `str` rows and surrounding callable families unchanged.
- Refreshed `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the combined benchmark contract now requires representative bytes ids for that slice and so the full published-suite summary expectation matches the widened tracked benchmark surface.
- Regenerated `reports/benchmarks/latest.py`; the tracked publication now reports `999` total / `999` measured / `0` known gaps, `workloads_by_cache_mode == {'cold': 104, 'purged': 433, 'warm': 462}`, and `nested-group-callable-replacement-boundary` at `96` selected / `96` measured / `0` known gaps / `96` total workloads.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`
