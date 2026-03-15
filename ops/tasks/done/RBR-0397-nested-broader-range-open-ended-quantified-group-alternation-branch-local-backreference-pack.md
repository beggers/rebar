# RBR-0397: Publish a nested broader-range open-ended quantified-group alternation plus branch-local-backreference correctness pack

Status: done
Owner: feature-implementation
Created: 2026-03-15

## Goal
- Extend the published correctness scorecard with one bounded broader-range open-ended `{2,}` counted-repeat nested-group-alternation-plus-branch-local-backreference manifest so the plain search/fullmatch frontier reopens next to the just-landed replacement and callable-replacement slices.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_workflows.py`
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `tests/python/test_branch_local_backreference_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated broader-range open-ended `{2,}` counted-repeat nested-group-alternation-plus-branch-local-backreference manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded compile, `module.search()`, and compiled-`Pattern.fullmatch()` observations through the public `rebar` API for the exact numbered and named workflows `a((b|c){2,})\2d` and `a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d` that CPython already supports.
- The published cases include a numbered lower-bound same-branch success such as `abbbd` or `acccd`, a numbered mixed-branch or longer-repetition success such as `abcbccd`, `abbbbd`, or `accccd`, one explicit no-match that proves one inner repetition is still too few or the replay is missing, one named lower-bound search success that keeps `outer` and `inner` observable, one named mixed-branch or doubled-haystack `Pattern.fullmatch()` success that keeps the final selected branch observable, and at least one named no-match that keeps the broader-range open-ended `{2,}` floor honest without widening into deeper nested grouped execution.
- The existing combined correctness scorecard suite absorbs this manifest through `tests/conformance/correctness_expectations.py` and `tests/conformance/test_combined_correctness_scorecards.py` instead of growing another bespoke wrapper.
- The shared `tests/python/test_branch_local_backreference_parity_suite.py` surface continues to discover published `*branch_local_backreference_workflows.py` fixtures and covers this new manifest through the existing fixture-bundle path instead of adding another manifest-specific parity module.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one outer capture around one broader-range open-ended `{2,}` `(b|c)` site immediately replayed by one same-branch backreference is enough, while replacement semantics, callable replacements, broader lower bounds, and deeper nested grouped execution remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixture registration, shared expectation tables, shared branch-local-backreference parity fixture bookkeeping, combined-scorecard coverage, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed broader-range open-ended `{2,}` counted-repeat nested-group-alternation-plus-branch-local-backreference behavior to stdlib `re` outside the existing differential harness path.
- Reuse the existing combined correctness scorecard helpers and branch-local-backreference parity suite instead of introducing another frontier-specific harness layer.

## Notes
- Build on `RBR-0395`, `RBR-0390`, and the existing shared branch-local-backreference fixture/parity surfaces.
- A direct `PYTHONPATH=python ./.venv/bin/python` probe in the current checkout already shows representative numbered and named `module.search()` and compiled-`Pattern.fullmatch()` cases for this exact `{2,}` slice matching CPython through the public `rebar` API, so keep the publication honest and expect the next parity follow-on to be triaged immediately if the shared suite confirms the same coverage already passes.
- Leave later Rust-boundary parity triage and any benchmark catch-up to follow-on planning after this correctness pack lands; do not fork a new benchmark family in the same run.

## Completion
- Added the new `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-workflows` manifest, registered it in the published correctness fixture list, and wired it through the combined/open-ended scorecard expectation tables plus the shared branch-local parity bundle.
- Republished `reports/correctness/latest.py`; the tracked report now covers 907 total/passing cases across 101 manifests, and the new 10-case manifest is fully passing.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest tests/python/test_branch_local_backreference_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py -q` (`256 passed, 949 subtests passed`).
- The shared branch-local parity suite already passes this exact `{2,}` slice through the current public API, so any Rust-boundary parity follow-on for the same bounded workflows should be re-triaged before reseeding it.
