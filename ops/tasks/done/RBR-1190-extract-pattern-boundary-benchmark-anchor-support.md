# RBR-1190: Extract pattern-boundary benchmark anchor support

Status: done
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining pattern-boundary bounded-wildcard and verbose-regression anchor-support block that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving that bounded selector/signature surface into one dedicated support module, so the giant combined benchmark suite stops owning another private pattern-specific anchor layer.

## Deliverables
- `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Add one bounded shared benchmark-support module at `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py` for the current pattern-boundary bounded-wildcard and verbose-regression anchor surface that is still embedded in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`:
  - move `_PATTERN_BOUNDED_WILDCARD_WORKLOAD_IDS`;
  - move `_PATTERN_BOUNDED_WILDCARD_CASE_IDS`;
  - move `_pattern_bounded_wildcard_correctness_case_signature`;
  - move `_pattern_bounded_wildcard_workload_signature`;
  - move `_is_pattern_bounded_wildcard_workload`;
  - move `_PATTERN_SEARCH_VERBOSE_REGRESSION_WORKLOAD_IDS`;
  - move `_PATTERN_FULLMATCH_VERBOSE_REGRESSION_WORKLOAD_IDS`;
  - move `_PATTERN_VERBOSE_REGRESSION_WORKLOAD_IDS`;
  - move `_PATTERN_SEARCH_VERBOSE_REGRESSION_CASE_IDS`;
  - move `_PATTERN_FULLMATCH_VERBOSE_REGRESSION_CASE_IDS`;
  - move `_PATTERN_VERBOSE_REGRESSION_CASE_IDS`;
  - move `_pattern_verbose_regression_correctness_case_signature`;
  - move `_pattern_verbose_regression_workload_signature`; and
  - move `_is_pattern_verbose_regression_workload`.
- Keep that extracted support pinned to the current live pattern-boundary anchor surface instead of widening it:
  - preserve the current bounded-wildcard scope on the six stored `pattern.search` / `pattern.match` / `pattern.fullmatch` / `pattern.findall` / `pattern.finditer` rows, including the exact `a.c` pattern, no-kwargs requirement, `pos`/`endpos` presence, and the existing call-signature path through `_pattern_window_positional_indexlike_workload_args(...)`;
  - preserve the current verbose-regression scope on the stored `pattern.search` and `pattern.fullmatch` rows, including the exact verbose regression pattern string, `flags == 72`, no-kwargs requirement, and the current `str`/`bytes` workload-id and case-id tuples;
  - keep the workload-id and case-id tuples importable so the combined suite can continue asserting exact measured-row membership without duplicating those tuples locally; and
  - keep the extracted module limited to this pattern-boundary surface rather than absorbing module-keyword, wrong-text-model, compiled-pattern, or grouped-alternation helpers.
- Delete the duplicated inline support block from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` instead of leaving aliases or wrapper passthroughs behind.
- Add one focused support test file at `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py` that pins the moved support without reintroducing another giant-suite dependency:
  - cover one bounded-wildcard workload that stays in scope and keeps the expected workload signature;
  - cover one bounded-wildcard rejection case;
  - cover one verbose-regression workload that stays in scope and keeps the expected workload signature; and
  - cover one verbose-regression correctness-case signature.
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so it imports the moved support instead of defining that block inline:
  - keep `test_pattern_boundary_manifest_keeps_keyword_and_positional_window_rows_measured` on the same expected workload-id tuples after the extraction;
  - keep the `pattern-boundary-bounded-wildcard` and `pattern-boundary-verbose-regression` `StandardBenchmarkAnchorContractDefinition` entries on the same selectors, signatures, and exact anchored case ids after the extraction; and
  - do not widen this task into `python/rebar_harness/benchmarks.py`, benchmark manifests, correctness fixtures, reports, README text, or tracked ops state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'test_pattern_boundary_manifest_keeps_keyword_and_positional_window_rows_measured or test_standard_benchmark_manifest_keeps_expected_workloads_in_scope or test_standard_benchmark_workloads_stay_anchored_to_published_correctness_cases'`

## Constraints
- Keep this cleanup structural and limited to the pattern-boundary anchor-support extraction above. Do not widen it into broader pattern-boundary rewrites, new feature coverage, or a general breakup of the combined suite.
- Prefer one ordinary support module plus one focused support test file over another test-to-test import or another block of private inline helpers.
- Do not leave duplicate workload-id or case-id tuples behind in the combined suite.

## Notes
- Completed 2026-03-24: extracted the bounded wildcard and verbose-regression pattern-boundary anchor tuples/selectors/signatures into `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py`, added focused coverage in `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`, and switched `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to import the shared support instead of keeping that block inline.
- Verification:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'test_pattern_boundary_manifest_keeps_keyword_and_positional_window_rows_measured or test_standard_benchmark_manifest_keeps_expected_workloads_in_scope or test_standard_benchmark_workloads_stay_anchored_to_published_correctness_cases'`
- `RBR-1190` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n "RBR-119[0-9]|RBR-12[0-9]{2}" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked -g '*.md'` returned no matches in this run, so no planning-owned future id reservation blocks `RBR-1190`.
- No blocked architecture task exists to reopen or retire first in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining simplification is still concrete and bounded in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `17807` lines in this run;
  - `rg -n "_pattern_bounded_wildcard_correctness_case_signature|_pattern_bounded_wildcard_workload_signature|_is_pattern_bounded_wildcard_workload|_pattern_verbose_regression_correctness_case_signature|_pattern_verbose_regression_workload_signature|_is_pattern_verbose_regression_workload" tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still shows the full inline pattern-boundary support block at lines `8235`, `8254`, `8274`, `8494`, `8515`, and `8533`;
  - the same combined suite still uses that block in the measured-row inventory around lines `4676` to `4716` and in the `pattern-boundary-bounded-wildcard` / `pattern-boundary-verbose-regression` anchor definitions around lines `9753` to `9833`; and
  - no repo-local support module currently owns this exact bounded-wildcard plus verbose-regression anchor surface.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py` currently fails with `ERROR: file or directory not found: tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`, which belongs to the exact cleanup queued here.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'test_pattern_boundary_manifest_keeps_keyword_and_positional_window_rows_measured or test_standard_benchmark_manifest_keeps_expected_workloads_in_scope or test_standard_benchmark_workloads_stay_anchored_to_published_correctness_cases'` returned `81 passed, 513 deselected, 43 subtests passed` in this run.
