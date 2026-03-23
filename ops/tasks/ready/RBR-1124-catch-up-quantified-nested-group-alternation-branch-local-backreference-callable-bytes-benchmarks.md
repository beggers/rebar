# RBR-1124: Catch up quantified nested-group alternation branch-local-backreference callable bytes benchmarks

Status: ready
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Catch the newly published quantified nested-group alternation plus branch-local-backreference callable bytes slice up on the existing Python-path benchmark owner path by measuring the adjacent bounded bytes workflows that `RBR-1120` and `RBR-1122` landed, before any broader same-family callable expansion reopens the frontier.

## Pattern Pair
- `rebar.sub(rb"a((b|c)+)\\2d", lambda m: m.group(1) + b"x", b"abbd")`
- `rebar.compile(rb"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d").subn(lambda m: b"<" + m.group("inner") + b">", b"zzaccdabbbdzz", 1)`

## Deliverables
- `benchmarks/workloads/nested_group_callable_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Extend the existing quantified branch-local-backreference callable slice on `benchmarks/workloads/nested_group_callable_replacement_boundary.py` with only the adjacent bytes workloads for the exact bounded quantified nested-group alternation plus same-branch backreference callable runtime that now works in `rebar`:
  - numbered module `sub()` and `subn(count=1)` rows for `rb"a((b|c)+)\\2d"` on the existing lower-bound and first-match-only bounded haystacks;
  - named compiled-pattern `sub()` and `subn(count=1)` rows for `rb"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d"` on the existing mixed-branches and first-match-only bounded haystacks; and
  - preserve the current `str` quantified branch-local callable rows on the same owner path instead of moving or widening the slice.
- Keep the benchmark catch-up bounded to the existing quantified nested-group alternation branch-local-backreference callable owner family:
  - update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` only as needed so the combined benchmark contract explicitly requires representative bytes ids for the `quantified-branch-local-backreference` slice;
  - do not widen into broader counted repeats, correctness fixtures, README text, or tracked ops state prose; and
  - keep the surrounding exact nested-group, quantified nested-group alternation, broader-range branch-local-backreference, and grouped callable benchmark slices green on the same manifest.
- Regenerate `reports/benchmarks/latest.py` so the tracked publication includes the adjacent bytes quantified branch-local callable rows and remains fully measured with no new known gaps:
  - `REPORT["summary"]` moves from `1003` total / `1003` measured / `0` known gaps to `1007` / `1007` / `0`;
  - `REPORT["summary"]["workloads_by_cache_mode"]` moves from `{"cold": 104, "purged": 435, "warm": 464}` to `{"cold": 104, "purged": 437, "warm": 466}`;
  - `REPORT["manifests"]["nested-group-callable-replacement-boundary"]` moves from `selected_workload_count == 100`, `measured_workloads == 100`, `known_gap_count == 0`, and `workload_count == 100` to `104`, `104`, `0`, and `104`; and
  - the exact `quantified-branch-local-backreference` benchmark slice no longer appears as a `str`-only quartet on the published benchmark surface.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'quantified and branch_local_backreference and callable and nested_group'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep the work on the Python-facing benchmark publication path. Do not widen this task into more Rust runtime changes unless a narrow benchmark publication blocker forces a tiny bridge fix for the already-landed bytes callable slice.
- Preserve the same bounded quantified nested-group alternation branch-local-backreference callable semantics that `RBR-1120` and `RBR-1122` already landed; this task is benchmark catch-up, not broader callable-replacement design.
- Do not create a second benchmark manifest or detach this slice from `benchmarks/workloads/nested_group_callable_replacement_boundary.py`.

## Notes
- `RBR-1124` is the next available unreserved feature task id in this checkout:
  - the highest live task id across `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, and `ops/tasks/blocked/` is `1123`; and
  - `rg -n 'RBR-1124|RBR-1125|RBR-1126' ops/tasks ops/state -g '*.md'` returned only historical mentions inside done-task notes in this run.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest same-family feature completion note explicitly leaves same-family benchmark catch-up for later, and the narrow owner-path check in this run confirms benchmark publication, not another implementation prerequisite, is now the exact missing slice:
  - `ops/tasks/done/RBR-1122-publish-quantified-nested-group-alternation-branch-local-backreference-callable-bytes-workflows.md` closes the adjacent bytes correctness publication and leaves same-family benchmark catch-up for a later planning pass;
  - `tests/python/test_callable_replacement_parity_suite.py` already contains direct bytes parity coverage for the bounded numbered module and named pattern `sub()` / `subn(count=1)` workflows on `rb"a((b|c)+)\\2d"` and `rb"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d"`;
  - `benchmarks/workloads/nested_group_callable_replacement_boundary.py` still carries only the four `str` quantified branch-local callable workload ids, with no adjacent `bytes` rows yet present;
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still requires only those four `str` workload ids for the `quantified-branch-local-backreference` slice; and
  - `reports/benchmarks/latest.py` still reports `nested-group-callable-replacement-boundary` at `100` measured workloads, so this exact quantified bytes benchmark quartet remains unpublished.
- `ops/state/backlog.md` and the queue-frontier prose in `ops/state/current_status.md` already honestly describe the likely post-drain frontier for a single ready feature task: no ready feature follow-on currently survives in this checkout, so this one-task refill does not need tracked state-prose edits.
