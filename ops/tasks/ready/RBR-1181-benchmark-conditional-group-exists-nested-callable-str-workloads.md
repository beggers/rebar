# RBR-1181: Benchmark conditional group-exists nested callable str workloads

Status: ready
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Catch the newly published `str` nested conditional callable-replacement slice up on the existing Python-path benchmark surface by measuring the exact eight bounded module and compiled-`Pattern` workflows that the live runtime and correctness owner path already cover, before bytes mirrors, quantified conditional callable follow-ons, or broader callable-helper expansion widen this family again.

## Pattern Pair
- `rebar.sub(r"a(b)?c(?(1)(?(1)d|e)|f)", callable_match_group(1, suffix="x"), "zzabcdzz")`
- `rebar.compile(r"a(?P<word>b)?c(?(word)(?(word)d|e)|f)").subn(callable_match_group("word", suffix="x"), "zzacfzz", 1)`

## Deliverables
- `benchmarks/workloads/conditional_group_exists_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Extend `benchmarks/workloads/conditional_group_exists_boundary.py` with exactly the eight adjacent `str` nested conditional callable workloads already published on the shared correctness owner path:
  - add numbered module `sub()` and `subn()` workloads for `r"a(b)?c(?(1)(?(1)d|e)|f)"` using `callable_match_group(1, suffix="x")`, with the present-arm success haystack `zzabcdzz` and the absent-capture `TypeError` haystack `zzacfzz`;
  - add numbered compiled-pattern `sub()` and `subn()` workloads for the same spelling on the same present and absent haystacks, keeping the absent-capture `TypeError` outcome explicit on the benchmark surface;
  - add named module `sub()` and `subn()` workloads for `r"a(?P<word>b)?c(?(word)(?(word)d|e)|f)"` using `callable_match_group("word", suffix="x")`, with the matching present-arm success and absent-capture `TypeError` workflows; and
  - add named compiled-pattern `sub()` and `subn()` workloads for the same named spelling on the same present and absent haystacks.
- Keep the work on the existing `conditional-group-exists-boundary` benchmark owner path instead of creating another manifest or detached benchmark test module:
  - update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` only as needed so the shared callable slice expectations, representative measured workload sets, and single-manifest scorecard assertions include these eight new nested conditional callable `str` rows on `conditional-group-exists-boundary`;
  - preserve the already measured two-arm and alternation-heavy callable rows, the nested constant-replacement rows, the quantified conditional rows, and the surrounding replacement-template and constant-replacement coverage on the same manifest; and
  - do not widen this run into bytes mirrors, correctness publication, Rust implementation work, quantified conditional callable benchmarks, or another conditional benchmark family.
- Regenerate `reports/benchmarks/latest.py` honestly on the tracked combined benchmark surface:
  - the tracked report gains the eight new measured `str` nested conditional callable workloads for `conditional-group-exists-boundary`;
  - the combined benchmark summary moves from `1059/1059` measured workloads to `1067/1067` measured workloads with `known_gap_count == 0`;
  - the manifest count stays at `30`; and
  - `REPORT["manifests"]["conditional-group-exists-boundary"]` moves from `workload_count == 128`, `measured_workloads == 128`, and `known_gap_count == 0` to `136`, `136`, and `0`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_source_tree_combined_slice_filters_match_expected_manifest_rows`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeScorecardBenchmarkSuiteTest::test_single_manifest_scorecards_keep_slice_backed_representatives`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-1181-conditional-nested-callable-str.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not change Rust implementation files, `python/rebar/__init__.py`, correctness fixtures, correctness reports, README text, or tracked ops state prose in this run.
- Reuse the existing `conditional_group_exists_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another benchmark manifest, another benchmark test module, or a detached conditional callable benchmark file.
- Keep the scope pinned to the exact eight `str` nested conditional callable workloads above. Leave bytes mirrors, quantified conditional callable follow-ons, and broader callable helper expansion for later tasks.

## Notes
- `RBR-1181` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this run; and
  - `rg -n "^ID: RBR-1181$|^ID: RBR-1182$|RBR-1181|RBR-1182" ops/tasks ops/state -g '*.md'` matched only an architecture-task completion note, not a live feature reservation for either id.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest done same-family frontier leaves this exact benchmark catch-up slice concrete after `RBR-1179`:
  - `ops/tasks/done/RBR-1179-publish-conditional-group-exists-nested-callable-workflows.md` completed the bounded nested conditional callable `str` publication slice and explicitly left same-family benchmark catch-up, bytes mirrors, quantified conditional callable follow-ons, and broader callable helper expansion for later on this owner path;
  - `tests/python/test_callable_replacement_parity_suite.py` already covers the exact numbered and named module/pattern nested conditional callable `sub()` and `subn()` success and absent-capture `TypeError` workflows for this slice;
  - `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` and `reports/correctness/latest.py` already publish those exact eight nested conditional callable `str` rows on the shared conditional callable owner path; and
  - `benchmarks/workloads/conditional_group_exists_boundary.py` and `reports/benchmarks/latest.py` still stop at nested `search`/`fullmatch` plus constant-replacement `sub()`/`subn()` probes for this spelling, so the nested callable benchmark catch-up remains the smallest surviving same-family slice and no implementation prerequisite blocks it.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_source_tree_combined_slice_filters_match_expected_manifest_rows tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeScorecardBenchmarkSuiteTest::test_single_manifest_scorecards_keep_slice_backed_representatives` returned `2 passed, 54 subtests passed`;
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/feature-planning-conditional-nested-callable-bench-current.py` completed successfully with `128` measured workloads and `0` known gaps, confirming the existing benchmark owner path is stable before this follow-on lands; and
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... PY` direct probes confirmed the exact `str` nested conditional callable workflows already match CPython on `rebar`, while the bytes mirrors still raise scaffold `NotImplementedError`, which keeps the immediate follow-on pinned to bytes parity rather than a bytes benchmark catch-up.
