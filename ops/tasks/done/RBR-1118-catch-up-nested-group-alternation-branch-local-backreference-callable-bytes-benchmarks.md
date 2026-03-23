# RBR-1118: Catch up nested-group alternation branch-local-backreference callable bytes benchmarks

Status: done
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Catch the newly published exact nested-group alternation plus branch-local-backreference callable bytes slice up on the existing Python-path benchmark owner path by measuring the adjacent bounded bytes workflows that `RBR-1116` published, before any same-family quantified branch-local callable expansion or broader callable-replacement work reopens the frontier.

## Pattern Pair
- `rebar.sub(rb"a((b|c))\\2d", lambda m: m.group(1) + b"x", b"abbd")`
- `rebar.compile(rb"a(?P<outer>(?P<inner>b|c))(?P=inner)d").subn(lambda m: b"<" + m.group("inner") + b">", b"accdabbd", 1)`

## Deliverables
- `benchmarks/workloads/nested_group_callable_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Extend the existing `branch-local-backreference` callable slice in `benchmarks/workloads/nested_group_callable_replacement_boundary.py` with only the adjacent bytes workloads for the already-landed exact nested-group alternation branch-local-backreference callable runtime:
  - numbered module `sub()` and `subn(count=1)` rows for `rb"a((b|c))\\2d"` on the existing `b`-branch and first-match-only haystacks;
  - named compiled-pattern `sub()` and `subn(count=1)` rows for `rb"a(?P<outer>(?P<inner>b|c))(?P=inner)d"` on the existing `c`-branch and first-match-only haystacks; and
  - preserve the current `str` exact branch-local callable rows on the same owner path instead of moving or widening the slice.
- Keep the benchmark catch-up bounded to the existing exact nested-group alternation branch-local-backreference callable owner family:
  - update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` only as needed so the combined benchmark contract explicitly requires representative bytes ids for the `branch-local-backreference` callable slice;
  - do not widen into quantified branch-local backreferences, broader counted repeats, correctness fixtures, README text, or tracked ops state prose; and
  - keep the surrounding grouped, nested-group, quantified nested-group, and broader branch-local callable benchmark slices green on the same manifest.
- Regenerate `reports/benchmarks/latest.py` so the tracked publication includes the adjacent bytes exact branch-local callable rows and remains fully measured with no new known gaps:
  - `REPORT["summary"]` moves from `999` total / `999` measured / `0` known gaps to `1003` / `1003` / `0`;
  - `REPORT["summary"]["workloads_by_cache_mode"]` moves from `{"cold": 104, "purged": 433, "warm": 462}` to `{"cold": 104, "purged": 435, "warm": 464}`;
  - `REPORT["manifests"]["nested-group-callable-replacement-boundary"]` moves from `selected_workload_count == 96`, `measured_workloads == 96`, `known_gap_count == 0`, and `workload_count == 96` to `100`, `100`, `0`, and `100`; and
  - the exact nested-group alternation branch-local-backreference callable slice no longer appears as a str-only quartet on the published benchmark surface.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'branch_local_backreference and callable and nested_group'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep the work on the Python-facing benchmark publication path. Do not widen this task into more Rust runtime changes unless a narrow benchmark publication blocker forces a tiny bridge fix for the already-landed bytes callable slice.
- Preserve the same bounded exact nested-group alternation branch-local-backreference callable semantics that `RBR-1114` and `RBR-1116` already landed; this task is benchmark catch-up, not broader callable-replacement design.
- Do not create a second benchmark manifest or detach this slice from `benchmarks/workloads/nested_group_callable_replacement_boundary.py`.

## Notes
- `RBR-1118` is the next available unreserved feature task id in this checkout:
  - the highest live task id across `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, and `ops/tasks/blocked/` is `1117`; and
  - `rg -n 'RBR-1118|RBR-1119|RBR-1120' ops/tasks ops/state -g '*.md'` returned no matches in this run.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest same-family feature completion note explicitly leaves benchmark catch-up as the next deferred adjacent slice:
  - `ops/tasks/done/RBR-1116-publish-nested-group-alternation-branch-local-backreference-callable-bytes-workflows.md` says to publish correctness first and leave same-family benchmark catch-up for later; and
  - the narrow owner-path check in this run shows `benchmarks/workloads/nested_group_callable_replacement_boundary.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `reports/benchmarks/latest.py` still carry only the four `str` workload ids for the exact branch-local callable slice, with no adjacent bytes ids yet present.
- The runtime and correctness prerequisites are already satisfied, so this is benchmark publication catch-up rather than another implementation prerequisite:
  - `ops/tasks/done/RBR-1114-implement-nested-group-alternation-branch-local-backreference-callable-bytes-parity.md` landed the exact bytes runtime path;
  - `ops/tasks/done/RBR-1116-publish-nested-group-alternation-branch-local-backreference-callable-bytes-workflows.md` expanded the correctness manifest to `text_models == ['bytes', 'str']`; and
  - `reports/benchmarks/latest.py` still reports `REPORT["manifests"]["nested-group-callable-replacement-boundary"]["workload_count"] == 96`, with the exact branch-local callable slice present only through the four `str` ids.

## Completion
- Added the four adjacent exact bytes branch-local-backreference callable workloads on the existing `benchmarks/workloads/nested_group_callable_replacement_boundary.py` owner path without widening the family: numbered module `sub()` and `subn(count=1)` rows for `a((b|c))\\2d`, plus named compiled-pattern `sub()` and `subn(count=1)` rows for `a(?P<outer>(?P<inner>b|c))(?P=inner)d`.
- Updated `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the combined benchmark contract now requires those exact bytes workload ids on the `branch-local-backreference` callable slice and explicitly asserts they are promoted as representative measured rows.
- Regenerated `reports/benchmarks/latest.py`; the tracked artifact now shows `REPORT["summary"] == {'known_gap_count': 0, 'measured_workloads': 1003, 'module_workloads': 995, 'parser_workloads': 8, 'regression_workloads': 8, 'total_workloads': 1003}`, `REPORT["summary"]["workloads_by_cache_mode"] == {'cold': 104, 'purged': 435, 'warm': 464}`, and `REPORT["manifests"]["nested-group-callable-replacement-boundary"]` with `selected_workload_count == 100`, `measured_workloads == 100`, `known_gap_count == 0`, and `workload_count == 100`.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'branch_local_backreference and callable and nested_group'`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`
