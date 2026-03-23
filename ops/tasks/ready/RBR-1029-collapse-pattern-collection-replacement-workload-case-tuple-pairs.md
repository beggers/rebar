# RBR-1029: Collapse pattern collection/replacement workload-case tuple pairs

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the three detached workload-id/case-id tuple pairs for the pattern collection/replacement bounded `findall`, bounded `finditer`, and `split` benchmark slices from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so those owner-path checks read from one canonical same-file pairing per slice instead of maintaining parallel tables.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines these six detached constants:
  - `_PATTERN_COLLECTION_REPLACEMENT_BOUNDED_FINDALL_WORKLOAD_IDS`
  - `_PATTERN_COLLECTION_REPLACEMENT_BOUNDED_FINDALL_CASE_IDS`
  - `_PATTERN_COLLECTION_REPLACEMENT_BOUNDED_FINDITER_WORKLOAD_IDS`
  - `_PATTERN_COLLECTION_REPLACEMENT_BOUNDED_FINDITER_CASE_IDS`
  - `_PATTERN_COLLECTION_REPLACEMENT_SPLIT_WORKLOAD_IDS`
  - `_PATTERN_COLLECTION_REPLACEMENT_SPLIT_CASE_IDS`
- Replace those parallel tuples with exactly three canonical same-file workload/case pair routes, or an equivalently smaller same-file representation, that keep these ordered pairs explicit:
  - bounded `findall`:
    - `("pattern-findall-bounded-warm-str", "pattern-findall-str-bounded")`
    - `("pattern-findall-bounded-no-match-warm-str", "pattern-findall-str-bounded-no-match")`
    - `("pattern-findall-bounded-purged-bytes", "pattern-findall-bytes-bounded")`
  - bounded `finditer`:
    - `("pattern-finditer-bounded-warm-str", "pattern-finditer-str-bounded")`
    - `("pattern-finditer-bounded-no-match-warm-str", "pattern-finditer-str-bounded-no-match")`
    - `("pattern-finditer-bounded-purged-bytes", "pattern-finditer-bytes-bounded")`
  - `split`:
    - `("pattern-split-no-match-warm-str", "pattern-split-str-no-match")`
    - `("pattern-split-repeated-warm-str", "pattern-split-str-repeated")`
    - `("pattern-split-maxsplit-purged-bytes", "pattern-split-bytes-maxsplit")`
- Keep the measured-row checks on the same owner route while deriving their expected workload ids from the canonical pairs instead of detached workload-id tables:
  - `test_collection_replacement_manifest_keeps_pattern_findall_bounded_rows_measured(...)`
  - `test_collection_replacement_manifest_keeps_pattern_finditer_bounded_rows_measured(...)`
  - `test_collection_replacement_manifest_keeps_pattern_split_rows_measured(...)`
  - each test still asserts the selected measured workload ids stay in the exact three-row order above and still asserts `len(expected_measured_workload_ids) == 3`.
- Keep the correctness/workload signature helpers on the same owner route while deriving membership from the same canonical pairs instead of detached case-id/workload-id tables:
  - `_pattern_collection_replacement_bounded_findall_correctness_case_signature(...)`
  - `_pattern_collection_replacement_bounded_finditer_correctness_case_signature(...)`
  - `_pattern_collection_replacement_split_correctness_case_signature(...)`
  - `_is_collection_replacement_pattern_findall_bounded_workload(...)`
  - `_is_collection_replacement_pattern_finditer_bounded_workload(...)`
  - `_is_collection_replacement_pattern_split_workload(...)`
  - preserve the existing operation, helper, keyword, `pos`/`endpos`, `text_model`, and `expected_exception` gates exactly; this cleanup should only remove the duplicate id plumbing.
- Keep the existing anchor-contract lane green without widening the scope:
  - `test_standard_benchmark_workloads_stay_pinned_to_exact_case_ids` still passes for the three collection/replacement pattern slices above;
  - do not widen this task into the module literal-replacement rows, the direct-pattern literal-replacement rows, benchmark manifests, reports, or scorecard totals; and
  - do not add another support module or detached registry for these ids.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_pattern_findall_bounded_rows_measured or collection_replacement_manifest_keeps_pattern_finditer_bounded_rows_measured or collection_replacement_manifest_keeps_pattern_split_rows_measured or standard_benchmark_workloads_stay_pinned_to_exact_case_ids'`
- `bash -lc "! rg -n '_PATTERN_COLLECTION_REPLACEMENT_(BOUNDED_FINDALL|BOUNDED_FINDITER|SPLIT)_(WORKLOAD|CASE)_IDS' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep the cleanup structural and local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Prefer deleting the detached tuple pairs over introducing another layer of support helpers or registry data.
- Do not edit benchmark workload manifests, correctness fixtures, reports, README/current-status/backlog prose, or the direct literal-replacement rows already queued in `RBR-1028`.

## Notes
- `RBR-1029` is the next available unreserved task id in the current checkout:
  - `rg -n "RBR-1029" ops/state/current_status.md ops/state/backlog.md ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked` returned no matches in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-ready-queue no-op rule does not trigger in this checkout:
  - `.rebar/runtime/dashboard.md` reports `ready: 1`, `in_progress: 0`, and `blocked: 0`;
  - the ready task is feature work (`RBR-1028`) rather than another architecture cleanup; and
  - the latest anomaly is a requeued feature run with `exit=1`, not inherited-dirty checkpoint churn or a stalled post-task refresh/commit path.
- The simplification target is concrete in the live checkout:
  - `rg -n '_PATTERN_COLLECTION_REPLACEMENT_(BOUNDED_FINDALL|BOUNDED_FINDITER|SPLIT)_(WORKLOAD|CASE)_IDS' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently matches only the six detached tuple constants plus their local consumers in the same file; and
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_pattern_findall_bounded_rows_measured or collection_replacement_manifest_keeps_pattern_finditer_bounded_rows_measured or collection_replacement_manifest_keeps_pattern_split_rows_measured or standard_benchmark_workloads_stay_pinned_to_exact_case_ids'` currently passes (`39 passed, 681 deselected, 3 subtests passed`).
