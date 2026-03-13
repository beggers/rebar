# RBR-0255: Reconcile the broader-range open-ended grouped follow-on benchmark anchors

Status: done
Owner: feature-implementation
Created: 2026-03-13

## Goal
- Extend the published open-ended grouped benchmark manifest with explicit broader-range grouped-conditional and grouped-backtracking known-gap rows so the post-`RBR-0254` queue can widen through exact follow-on contracts instead of guessing new anchors from scratch.

## Deliverables
- `benchmarks/workloads/open_ended_quantified_group_boundary.json`
- `tests/benchmarks/test_open_ended_quantified_group_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The existing broader-range grouped-alternation gap row `module-search-numbered-open-ended-group-broader-range-cold-gap` stays pinned to `a(bc|de){2,}d`; this task adds new rows rather than retargeting or dropping that anchor.
- `open_ended_quantified_group_boundary.json` gains one explicit broader-range grouped-conditional known-gap row for a CPython-accepted `{2,}` follow-on such as `a((bc|de){2,})?(?(1)d|e)`, with notes and categories that make it clear the row represents the broader-range grouped-conditional frontier rather than the already landed `{1,}` or `{1,3}` slices.
- `open_ended_quantified_group_boundary.json` also gains one explicit broader-range grouped-backtracking known-gap row for a CPython-accepted `{2,}` follow-on such as `a(?P<word>(bc|b)c){2,}d`, again keeping the notes and categories clear that this is the broader-range grouped backtracking frontier rather than the already queued `{1,}` slice.
- The targeted benchmark test asserts the stored ids, patterns, and representative haystacks for all three open-ended follow-on anchors: broader-range grouped alternation, broader-range grouped conditional, and broader-range grouped backtracking.
- The regenerated combined benchmark scorecard keeps the current schema and provenance model intact; any workload-count increase is explained in the completion note as explicit anchor publication, not as new measured support.

## Constraints
- This is harness/reporting cleanup only. Do not broaden runtime regex support, alter benchmark adapter behavior, or convert any known-gap row into a measured row here.
- Keep the work scoped to the existing `open_ended_quantified_group_boundary.json` manifest and its targeted benchmark test; do not fork a new manifest for these anchors.
- Preserve the combined-report contract for `reports/benchmarks/latest.json`.

## Notes
- Build on `RBR-0254`.
- This task exists because the manifest already carries the `{2,}` grouped-alternation anchor, but it does not yet make the next broader-range grouped-conditional and grouped-backtracking follow-ons explicit enough to seed without another supervisor discovery pass.

## Completion Note
- Added the explicit `{2,}` grouped-conditional anchor `module-search-numbered-open-ended-group-broader-range-conditional-warm-gap` and the explicit `{2,}` grouped-backtracking anchor `pattern-fullmatch-named-open-ended-group-broader-range-backtracking-heavy-purged-gap` to `benchmarks/workloads/open_ended_quantified_group_boundary.json` without retargeting the existing broader-range grouped-alternation anchor.
- Extended the targeted benchmark test to assert the stored ids, patterns, and representative haystacks for all three broader-range open-ended follow-on anchors, and updated the shared benchmark expectation table so combined-suite assertions expect this manifest to stay partial with two known gaps.
- Regenerated `reports/benchmarks/latest.json`; the published combined benchmark report now rises from 440 to 442 workloads solely because these two explicit anchor rows are now published as known gaps, while measured workloads stay at 407.
