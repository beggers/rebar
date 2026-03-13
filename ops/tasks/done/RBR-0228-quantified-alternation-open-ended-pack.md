# RBR-0228: Publish a bounded open-ended quantified-alternation correctness pack

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded manifest for workflows that reopen quantified alternation through the exact open-ended `{1,}` form so the queue takes one explicit open-ended follow-on before broader repeated-backtracking or more structural composition resumes.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/quantified_alternation_open_ended_workflows.json`
- `tests/conformance/test_correctness_quantified_alternation_open_ended_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated open-ended quantified-alternation manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for the exact numbered and named workflows `a(b|c){1,}d` and `a(?P<word>b|c){1,}d` on compile, module, and compiled-`Pattern` paths that CPython already supports.
- The published cases include lower-bound successes like `abd` and `acd`, longer bounded successes like `abcd`, `abccd`, and `abcbcd`, plus explicit no-match observations like `ad` and `abed` so the scorecard documents the open-ended frontier honestly without pretending to exhaust arbitrary-length repetition.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one open-ended `{1,}` envelope around one `b|c` alternation site is enough, while nested alternation, branch-local backreferences, conditionals, replacement semantics, broader overlapping-branch backtracking, and more structural quantified combinations remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed open-ended quantified-alternation behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0227`.
- This task exists so the queue reopens quantified alternation through one exact open-ended follow-on with an existing benchmark-gap anchor instead of jumping directly to broader repeated-backtracking work.

## Completion
- Added `tests/conformance/fixtures/quantified_alternation_open_ended_workflows.json` and wired it into `python/rebar_harness/correctness.py` so the default combined correctness publication now includes a dedicated open-ended `{1,}` quantified-alternation manifest.
- Added `tests/conformance/test_correctness_quantified_alternation_open_ended_workflows.py` to verify the manifest is present in the combined scorecard and that the numbered/named compile, module, and compiled-`Pattern` observations for `a(b|c){1,}d` and `a(?P<word>b|c){1,}d` stay honest as `pass` or `unimplemented`.
- Regenerated `reports/correctness/latest.json`; the published combined report now covers 69 manifests / 548 cases, with the new 16 open-ended quantified-alternation cases currently reported as honest `unimplemented` outcomes.
