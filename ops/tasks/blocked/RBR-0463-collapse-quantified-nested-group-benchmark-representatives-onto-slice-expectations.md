# RBR-0463: Collapse quantified nested-group benchmark representatives onto slice expectations

Status: blocked
Owner: architecture-implementation
Created: 2026-03-16

## Goal
- Remove the last hand-maintained quantified nested-group representative workload tuples from `tests/benchmarks/benchmark_expectations.py` so those three manifests describe representative coverage through the existing slice-expectation surface instead of a second manifest-level copy.

## Deliverables
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/benchmark_expectations.py` keeps using the existing `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS`, `SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS`, and `source_tree_combined_manifest_representative_measured_workload_ids(...)` path. Do not add another registry, support module, generated file, or manifest-local helper table.
- The scoped cleanup is limited to these three manifests whose explicit representative tuples still contain one coherent quantified nested-group slice each:
  - `nested-group-alternation-boundary`
  - `nested-group-replacement-boundary`
  - `nested-group-callable-replacement-boundary`
- After the refactor, those three manifest entries in `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS` no longer keep manifest-local `representative_measured_workload_ids`; the tuples become empty and representative measured workload ids are derived from slice expectations alone.
- Add one dedicated slice expectation for `nested-group-alternation-boundary` that covers the current quantified nested-group alternation rows exactly, preserving their current representative order by placing the slice before the existing branch-local-backreference slices:
  - `module-search-nested-group-quantified-alternation-cold-gap`
  - `pattern-fullmatch-numbered-quantified-nested-group-alternation-repeated-mixed-purged-str`
  - `module-search-named-quantified-nested-group-alternation-lower-bound-c-warm-str`
  - `pattern-fullmatch-named-quantified-nested-group-alternation-repeated-mixed-purged-str`
  - Keep the slice scoped to the existing bounded quantified nested-group alternation patterns `a((b|c)+)d` and `a(?P<outer>(?P<inner>b|c)+)d` with the current `module.search` / `pattern.fullmatch` operations and quantified nested-group categories.
- Add one dedicated slice expectation for `nested-group-replacement-boundary` that covers the current quantified nested-group template-replacement rows exactly, preserving their current representative order by placing the slice before the existing open-ended branch-local-backreference slices:
  - `module-sub-template-numbered-quantified-nested-group-replacement-lower-bound-warm-str`
  - `module-subn-template-numbered-quantified-nested-group-replacement-first-match-only-warm-str`
  - `pattern-sub-template-named-quantified-nested-group-replacement-repeated-outer-purged-str`
  - `pattern-subn-template-named-quantified-nested-group-replacement-purged-gap`
  - Keep the slice scoped to the existing bounded quantified nested-group replacement-template patterns `a((bc)+)d` and `a(?P<outer>(?P<inner>bc)+)d` with the current `module.sub`, `module.subn`, `pattern.sub`, and `pattern.subn` operations and quantified/template-replacement categories.
- Add one dedicated slice expectation for `nested-group-callable-replacement-boundary` that covers the current quantified nested-group callable-replacement rows exactly, preserving their current representative order by placing the slice after `nested-alternation` and before `quantified-nested-alternation`:
  - `module-sub-callable-numbered-quantified-nested-group-lower-bound-warm-str`
  - `module-subn-callable-numbered-quantified-nested-group-first-match-only-warm-str`
  - `pattern-sub-callable-named-quantified-nested-group-repeated-outer-purged-str`
  - `pattern-subn-callable-named-quantified-nested-group-purged-gap`
  - Keep the slice scoped to the existing bounded quantified nested-group callable-replacement patterns `a((bc)+)d` and `a(?P<outer>(?P<inner>bc)+)d` with the current `module.sub`, `module.subn`, `pattern.sub`, and `pattern.subn` operations and quantified/callable-replacement categories.
- Clean up the now-misaligned `nested-group-callable-replacement-boundary` `former-gap-callable-replacement-rows` slice instead of leaving it as a second source of truth:
  - it must not continue to carry `pattern-subn-callable-named-quantified-nested-group-purged-gap` once that workload belongs to the new quantified nested-group callable slice; and
  - prefer deleting that slice entry entirely if it becomes redundant, because `module-sub-callable-nested-group-alternation-cold-gap` is already covered by the existing `nested-alternation` slice.
- `source_tree_combined_manifest_representative_measured_workload_ids(...)` keeps returning the same public workload-id order for the three scoped manifests, but now derives that order from slice expectations instead of manifest-local tuples.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is updated only as needed to assert the new single-source behavior directly:
  - extend `SLICE_DERIVED_MANIFEST_IDS` to cover the three scoped manifests once their manifest-local representative tuples are empty; and
  - keep the test consuming the existing `source_tree_combined_slice_expectations(...)` surface instead of introducing another benchmark expectation table in the test file.
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py` is updated only as needed to assert the same slice-backed representative path for the single-manifest scorecard cases affected by this cleanup:
  - `nested-group-replacement-boundary`
  - `nested-group-callable-replacement-boundary`
  - Do not broaden the test into manifests that are not source-tree scorecard cases, such as `nested-group-alternation-boundary`.
- Keep the cleanup structural only:
  - do not change benchmark workload manifests under `benchmarks/workloads/`;
  - do not change benchmark harness runtime behavior in `python/rebar_harness/benchmarks.py`;
  - do not change workload ids, manifest selectors, known-gap counts, published reports, README text, or tracked state files beyond this task file.
- Verification passes with:
  - `PYTHONPATH=python .venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Constraints
- Prefer new slice expectations over shape expectations for this task. These three leftover representative copies are coherent workload clusters, so the intended end state is one slice-backed source of truth rather than another manifest-level representative list.
- Preserve current representative workload ordering exactly. `source_tree_combined_manifest_representative_measured_workload_ids(...)` is order-sensitive, so place any new slice blocks carefully instead of accepting a reordered representative list.
- Keep the scope to benchmark expectation architecture. Do not broaden this run into `module-boundary`, `pattern-boundary`, `wider-ranged-repeat-quantified-group-boundary`, `open-ended-quantified-group-boundary`, or another round of manifest-shape cleanup.

## Notes
- `RBR-0462` is already reserved in `ops/state/backlog.md` and `ops/state/current_status.md` for the next feature-owned parser-stress benchmark follow-on, so this architecture cleanup starts at `RBR-0463`.
- The runtime dashboard is current and clean for this run (`Generated: 2026-03-16T09:59:40+00:00`, `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `Last Cycle Anomalies: none`), so rule 10 does not apply.
- JSON counts are fully burned down in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- In the current checkout, `tests/benchmarks/benchmark_expectations.py` is still `1846` lines long, and the remaining manifest-local quantified nested-group representative copies are concentrated at:
  - `nested-group-alternation-boundary` (`tests/benchmarks/benchmark_expectations.py:300-319`)
  - `nested-group-replacement-boundary` (`tests/benchmarks/benchmark_expectations.py:322-341`)
  - `nested-group-callable-replacement-boundary` (`tests/benchmarks/benchmark_expectations.py:344-381`)
- The existing slice expectation surface is already adjacent to those manifests and covers the rest of each representative set:
  - `nested-group-alternation-boundary` slice blocks start at `tests/benchmarks/benchmark_expectations.py:682`
  - `nested-group-callable-replacement-boundary` slice blocks start at `tests/benchmarks/benchmark_expectations.py:783`
  - `nested-group-replacement-boundary` slice blocks start at `tests/benchmarks/benchmark_expectations.py:1028`
- The current live derivation check shows why this is now a bounded follow-on:
  - `nested-group-alternation-boundary`: 16 explicit representative ids, 12 already slice-derived, 4 explicit-only quantified nested-group alternation ids
  - `nested-group-replacement-boundary`: 16 explicit representative ids, 12 already slice-derived, 4 explicit-only quantified nested-group replacement-template ids
  - `nested-group-callable-replacement-boundary`: 36 explicit representative ids, 33 already slice-derived, 3 explicit-only quantified nested-group callable ids plus one quantified gap row still living in the misaligned `former-gap-callable-replacement-rows` slice

## Run Notes
- Landed the structural cleanup in `tests/benchmarks/benchmark_expectations.py`:
  - the three scoped `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS` entries now leave `representative_measured_workload_ids` empty;
  - new slice expectations cover the quantified nested-group alternation, template-replacement, and callable-replacement representative rows in the required order; and
  - the redundant `nested-group-callable-replacement-boundary` `former-gap-callable-replacement-rows` slice was deleted.
- Aligned the single-manifest scorecard cases for `nested-group-replacement-boundary` and `nested-group-callable-replacement-boundary` so they derive representative measured workload ids from the shared slice-backed combined-manifest path instead of local tuples.
- Updated the targeted benchmark tests so the slice-derived manifest set includes the three scoped manifests and the scorecard slice-backed representative assertion now covers the two affected single-manifest scorecard cases.
- Narrow verification passed:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py -k keep_slice_backed_representatives tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'scoped_manifests_keep_slice_backed_representatives or selected_combined_source_tree_manifest_slices_stay_covered'`
  - Result: `2 passed, 4 deselected, 252 subtests passed`
- Blocked on the task-mandated full verification command:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - The failures are not caused by the representative cleanup. In this checkout, `compile-parser-stress-cold` and `regression-parser-atomic-lookbehind-cold` now run as `measured`, so the suite-wide summary expectations are two known gaps behind the live runner output. That parser-stress benchmark expectation drift is the out-of-scope follow-on already reserved as `RBR-0462`.
