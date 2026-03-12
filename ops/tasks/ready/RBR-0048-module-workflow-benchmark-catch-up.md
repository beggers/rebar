# RBR-0048: Catch module-workflow benchmarks up with the post-parser behavior slices

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Update the benchmark suite so newly supported post-parser module workflows produce real `rebar` timings instead of leaving the benchmark report a milestone behind the published correctness surface.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/module_boundary.json`
- `benchmarks/workloads/collection_replacement_boundary.json`
- `benchmarks/workloads/literal_flag_boundary.json`
- `tests/benchmarks/test_post_parser_workflow_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark runner records real `rebar` timings for whichever workloads are newly supported by `RBR-0043` through `RBR-0047`, while leaving still-unsupported workflows explicit as known gaps.
- `reports/benchmarks/latest.json` reflects those newly measured module, replacement, or flag-sensitive workloads honestly instead of leaving the benchmark surface frozen at the pre-follow-on state.
- The benchmark manifests and tests stay explicit about cache mode, adapter provenance, and timing path, and they do not fabricate coverage for unsupported workflows or native paths that were not actually exercised.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0043` through `RBR-0047`; do not introduce large-haystack execution benchmarks, native-only publication requirements, or broad benchmark-schema churn.
- Preserve the existing source-tree-shim versus built-native provenance reporting from `RBR-0020`.
- Do not fabricate benchmark wins for unsupported workflows.

## Notes
- Build on `RBR-0043` through `RBR-0047`. This task exists so the benchmark report follows the next correctness wins instead of staying one milestone behind the published module-workflow surface.
