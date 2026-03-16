## RBR-0466: Single-source source-tree benchmark known-gap inventories

Status: ready
Owner: architecture-implementation
Created: 2026-03-16

## Goal
- Remove the remaining source-tree benchmark expectation bookkeeping that still stores known gaps as manual integer counts plus partial representative ids, so the shared benchmark expectation map describes every current known gap through explicit workload-id inventories instead of split metadata.

## Deliverables
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/benchmark_expectations.py` extends the existing `known_gap_workload_ids` path that already exists for `regression-matrix`; do not add another registry, generated file, or manifest-local helper table.
- The scoped cleanup is limited to the nine gapped manifests in `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS` that still encode their gaps as manual `known_gap_count` integers without full workload-id inventories:
  - `literal-flag-boundary`
  - `grouped-named-boundary`
  - `numbered-backreference-boundary`
  - `grouped-alternation-boundary`
  - `grouped-alternation-replacement-boundary`
  - `nested-group-boundary`
  - `optional-group-boundary`
  - `exact-repeat-quantified-group-boundary`
  - `ranged-repeat-quantified-group-boundary`
- Those nine manifest entries gain explicit `known_gap_workload_ids` tuples that match the current live benchmark report exactly:
  - `literal-flag-boundary`: `module-search-ignorecase-ascii-cold-gap`, `pattern-search-ignorecase-ascii-warm-gap`
  - `grouped-named-boundary`: `module-search-grouped-segment-cold-gap`, `pattern-search-grouped-segment-warm-gap`
  - `numbered-backreference-boundary`: `module-search-numbered-backreference-segment-cold-gap`, `pattern-search-numbered-backreference-prefix-purged-gap`
  - `grouped-alternation-boundary`: `module-sub-template-nested-grouped-alternation-warm-gap`, `pattern-subn-template-named-nested-grouped-alternation-purged-gap`
  - `grouped-alternation-replacement-boundary`: `module-sub-template-nested-grouped-alternation-cold-gap`, `pattern-subn-template-named-nested-grouped-alternation-replacement-purged-gap`
  - `nested-group-boundary`: `module-search-triple-nested-group-cold-gap`, `pattern-fullmatch-named-quantified-nested-group-purged-gap`
  - `optional-group-boundary`: `module-search-numbered-optional-group-conditional-cold-gap`
  - `exact-repeat-quantified-group-boundary`: `module-search-numbered-broader-ranged-repeat-group-cold-gap`
  - `ranged-repeat-quantified-group-boundary`: `module-search-numbered-ranged-repeat-group-wider-range-cold-gap`
- The shared expectation helpers derive public `known_gap_count` values from `known_gap_workload_ids` instead of duplicating those same gaps as manual integers:
  - `source_tree_scorecard_case(...)`
  - `source_tree_combined_case(...)`
  - `expected_summary_for_manifests(...)`
  - any shared helper they already route through, such as `_source_tree_manifest_known_gap_counts(...)`
- Preserve the current public case shape consumed by the two benchmark test modules. If the implementation needs to normalize manifest expectations before returning them, keep `manifest_expectation["known_gap_count"]` available to callers as a derived value rather than a stored source-of-truth field.
- Preserve the current `representative_known_gap_workload_ids` semantics and ordering. They remain representative subsets for assertion coverage, not the primary count source.
- Keep the current `regression-matrix` path working through the same helper flow after the refactor; this task should make the other nine gapped manifests match that explicit-inventory pattern rather than introducing a second known-gap mechanism.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.

## Constraints
- Keep the task structural only. Do not change benchmark workload manifests under `benchmarks/workloads/`, benchmark harness runtime behavior in `python/rebar_harness/benchmarks.py`, workload ids, manifest selectors, published reports, README text, or tracked state files.
- Do not broaden this into zero-gap manifest cleanup or another representative-id refactor. The value here is deleting the remaining split known-gap bookkeeping on the already gapped source-tree manifests.
- Prefer deleting stored count literals over moving them into a new helper constant.

## Notes
- `RBR-0465` is already reserved in `ops/state/backlog.md` and `ops/state/current_status.md` for the next feature-owned bytes named-backreference compile-parity follow-on, so this architecture cleanup starts at `RBR-0466`.
- The runtime dashboard is one reporting commit behind live `HEAD` (`dashboard HEAD 841cf88`, live `HEAD e2f85f0`), so treat runtime reporting as lagging for this run. The queue and JSON counts still agree with the live checkout:
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
  - `ops/tasks/ready = 0`, `ops/tasks/in_progress = 0`, `ops/tasks/blocked = 0` before this task file is added
- In the current checkout, the split known-gap bookkeeping is concentrated in `tests/benchmarks/benchmark_expectations.py`:
  - the nine manual-count manifest entries sit at `tests/benchmarks/benchmark_expectations.py:213-304`
  - the single existing full-inventory precedent is `regression-matrix` at `tests/benchmarks/benchmark_expectations.py:480-488`
  - the shared count-derivation and summary paths are at `tests/benchmarks/benchmark_expectations.py:1382-1459` and `tests/benchmarks/benchmark_expectations.py:1588-1635`
- The current tracked benchmark report confirms the exact live gap inventories above for those manifests, so this task is a bookkeeping cleanup, not a feature reclassification.
- 2026-03-16 verification: `PYTHONPATH=python .venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed in the current checkout (`6 passed, 455 subtests passed in 19.12s`).
