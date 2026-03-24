# RBR-1135: Catch up conditional group-exists template bytes benchmarks

Status: blocked
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Catch the exact two-arm conditional group-exists replacement-template bytes slice up on the existing Python-path benchmark owner path once `RBR-1133` lands, so the bounded bytes workflows for `a(b)?c(?(1)d|e)` and `a(?P<word>b)?c(?(word)d|e)` reach published benchmark coverage immediately behind correctness publication instead of leaving the `conditional-group-exists-boundary` template rows `str`-only.

## Pattern Pair
- `rebar.sub(rb"a(b)?c(?(1)d|e)", rb"\\1x", b"zzabcdzz")`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)d|e)").subn(rb"\\g<word>x", b"zzacezz", 1)`

## Deliverables
- `benchmarks/workloads/conditional_group_exists_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Extend the existing replacement-template slice on `benchmarks/workloads/conditional_group_exists_boundary.py` with only the adjacent bytes workloads for the exact bounded numbered and named two-arm conditional template runtime already implemented by `RBR-1130` and published by `RBR-1133`:
  - add bytes companions for the existing numbered module and compiled-pattern template `sub()` / `subn(count=1)` rows on `rb"a(b)?c(?(1)d|e)"`, using the same present-capture and absent-capture haystacks plus the bounded `rb"\\1x"` template;
  - add bytes companions for the existing named module and compiled-pattern template `sub()` / `subn(count=1)` rows on `rb"a(?P<word>b)?c(?(word)d|e)"`, using the same bounded haystacks plus `rb"\\g<word>x"`; and
  - keep the task bounded to these adjacent bytes template companions instead of widening into callable replacements, alternation-heavy arms, nested conditionals, quantified conditionals, or broader template parsing.
- Keep the work on the existing Python-facing benchmark owner path rather than introducing another manifest or detached benchmark suite:
  - update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` only as needed so the `minimal-template-replacement-rows` slice expects the representative bytes workload ids for both the numbered and named module/pattern `sub()` / `subn(count=1)` template rows on this exact owner path;
  - extend the matching zero-gap bytes representative subset for `conditional-group-exists-boundary` only as needed so the new bytes template rows are required to stay fully measured; and
  - preserve the already-published `str` rows plus the surrounding constant-replacement, callable-replacement, alternation-heavy, nested, and quantified conditional benchmark slices on the same manifest.
- Regenerate `reports/benchmarks/latest.py` so the tracked publication includes the adjacent bytes template rows and stays fully measured with no new known gaps:
  - `REPORT["summary"]` moves from `1019` total / `1019` measured / `0` known gaps to `1027` / `1027` / `0`;
  - `REPORT["manifests"]["conditional-group-exists-boundary"]` moves from `workload_count == 88`, `measured_workloads == 88`, and `known_gap_count == 0` to `96`, `96`, and `0`; and
  - the bounded conditional replacement-template benchmark surface no longer appears as a `str`-only owner-path slice in the published scorecard.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists and template and bytes'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep the task on the Python-facing benchmark publication path. Do not widen this run into additional Rust execution work unless a narrow benchmark-publication blocker forces a tiny bridge fix for the already-landed bytes template slice.
- Treat `RBR-1133` as the owner-path publication prerequisite. If the adjacent bytes correctness rows are still unpublished when this task starts, stop and move the task to `blocked/` instead of skipping ahead of the correctness surface.
- Reuse `benchmarks/workloads/conditional_group_exists_boundary.py` and its existing template row family instead of creating another benchmark manifest for the same bounded workflows.

## Notes
- `RBR-1135` is the next available unreserved feature task id in this checkout:
  - the highest live task id across `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, and `ops/tasks/blocked/` is `1134`; and
  - `rg -n 'RBR-1135|RBR-1136|RBR-1137' ops/tasks ops/state -g '*.md'` returned no reserved future feature ids in this run before this task was written.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The narrow same-family owner-path check in this run confirms benchmark catch-up, not another runtime prerequisite, is the exact surviving post-`RBR-1133` slice:
  - `ops/tasks/done/RBR-1130-implement-conditional-group-exists-template-bytes-parity.md` closes the bounded bytes runtime prerequisite and explicitly leaves publication plus benchmark catch-up for later passes on the same owner family;
  - `ops/tasks/ready/RBR-1133-publish-conditional-group-exists-template-bytes-workflows.md` already reserves the adjacent correctness-publication step on the shared replacement owner path;
  - `benchmarks/workloads/conditional_group_exists_boundary.py` still defines only the eight `str` replacement-template rows for this exact numbered and named two-arm conditional slice, with no adjacent bytes template entries present;
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still requires only the `str` workload ids for `minimal-template-replacement-rows` under `conditional-group-exists-boundary`; and
  - `reports/benchmarks/latest.py` still reports `conditional-group-exists-boundary` at `workload_count == 88`, `measured_workloads == 88`, and `known_gap_count == 0`, confirming that the adjacent bytes template benchmark rows remain unpublished today.

## Blocker Notes
- 2026-03-24: Stopped without touching benchmark artifacts because the task's prerequisite correctness publication is still blocked in this checkout.
- Direct verification in this run:
  - `ops/tasks/blocked/RBR-1133-publish-conditional-group-exists-template-bytes-workflows.md` remains blocked, so the adjacent correctness rows are not yet published.
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... rebar.sub(rb"a(b)?c(?(1)d|e)", rb"\\1x", b"zzabcdzz") ... PY` still raises `NotImplementedError: rebar.sub() is a scaffold placeholder; the re-compatible API is not implemented yet`.
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'conditional and replacement and template and bytes'` passes unchanged at `64 passed, 1252 deselected`, which confirms only the already-landed bounded bytes subset is covered today and not the unpublished full owner-path slice this benchmark task depends on.
- Follow-up needed before reopening:
  - finish and land `RBR-1133` so the exact numbered and named bytes replacement-template workflows for `a(b)?c(?(1)d|e)` and `a(?P<word>b)?c(?(word)d|e)` are published in `reports/correctness/latest.py`;
  - then rerun this task to add the eight adjacent bytes benchmark rows on `conditional-group-exists-boundary` and refresh `reports/benchmarks/latest.py`.
