# RBR-0050: Publish a grouped-match and capture correctness pack

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published correctness scorecard past the current 80-case frontier with a bounded grouped-match/capture manifest so the next compatibility surface is explicit before broader syntax work resumes.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/grouped_match_workflows.json`
- `tests/conformance/test_correctness_grouped_match_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows beyond the current eight-manifest, 80-case publication by adding a dedicated grouped-match/capture manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded numbered-capture observations for grouped-literal workflows through the public `rebar` API, including concrete `Match` metadata such as `group(1)`, `groups()`, `span(1)`, and `lastindex` on exact module or `Pattern` cases that CPython already supports.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: numbered captures for tiny grouped-literal workflows are in scope, while named groups, nested captures, and broader grouping syntax remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed grouped behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0047` and the existing `Match` scaffold surface.
- This task exists so the worker can expose the next bounded compatibility frontier in the scorecard before or immediately after the current published module-workflow gaps close.

## Completion Note
- Added a ninth correctness manifest, `grouped-match-workflows`, covering grouped single-capture module and `Pattern` match metadata plus two-capture honest gaps.
- Extended match-result normalization so grouped cases publish explicit `group(1)` and `span(1)` observations without changing runtime behavior.
- Republished `reports/correctness/latest.json` from the combined default fixture set; the published scorecard now covers 86 cases across 9 manifests with 84 passes and 2 honest `unimplemented` grouped multi-capture gaps.
