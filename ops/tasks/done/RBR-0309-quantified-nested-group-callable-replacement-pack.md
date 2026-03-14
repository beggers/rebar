# RBR-0309: Publish a quantified nested-group callable-replacement correctness pack

Status: done
Owner: feature-implementation
Created: 2026-03-14

## Goal
- Extend the published correctness scorecard with one bounded quantified nested-group callable-replacement manifest so the next combined quantified-nesting-and-callback frontier is explicit after `RBR-0307` catches the adjacent template-replacement slice up on the benchmark surface.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/quantified_nested_group_callable_replacement_workflows.py`
- `tests/conformance/test_correctness_quantified_nested_group_callable_replacement_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated quantified nested-group callable-replacement manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded callable replacement observations through the public `rebar` API for quantified nested captures on `a((bc)+)d` with callables that read `match.group(1)` or `match.group(2)`, and `a(?P<outer>(?P<inner>bc)+)d` with callables that read `match.group("outer")` or `match.group("inner")`, through module and compiled-`Pattern` `sub()` and `subn()` entrypoints that CPython already supports.
- The published cases cover at least one lower-bound one-repetition callback path such as `abcd`, one repeated-inner-capture path such as `abcbcd`, and one count-limited or first-match-only path on `abcbcdabcbcd`, so the quantified outer capture and final inner capture values stay observable under repetition.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one outer capture containing one `+`-quantified inner numbered or named capture feeding a callable replacement is enough, while replacement-template behavior beyond the already-landed slice, alternation inside the repeated site, broader counted repeats, broader callback semantics, branch-local backreferences, and deeper nested grouped execution remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed quantified nested-group callable-replacement behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Queue this immediately after `RBR-0307` so benchmark catch-up lands before the next correctness frontier reopens.
- Build on `RBR-0305` and the existing callable-replacement fixture helpers.
- Keep later parity and benchmark follow-ons on the existing `benchmarks/workloads/nested_group_callable_replacement_boundary.py` path instead of forking another benchmark family when this slice moves beyond publication.

## Completion Notes
- Added `tests/conformance/fixtures/quantified_nested_group_callable_replacement_workflows.py` and wired it into `python/rebar_harness/correctness.py`, publishing eight bounded module and compiled-`Pattern` `sub()`/`subn()` callable-replacement cases across numbered and named quantified nested-group captures.
- Added representative combined-scorecard coverage in `tests/conformance/correctness_expectations.py` and a dedicated regression in `tests/conformance/test_correctness_quantified_nested_group_callable_replacement_workflows.py`.
- Updated the adjacent quantified callable contract test to assert the current honest frontier: CPython succeeds on the published callback cases while `rebar` still reports them as `unimplemented` pending the queued parity follow-on.
- Republished `reports/correctness/latest.json`; the combined scorecard now reports 787 total cases with 779 passes and 8 explicit `unimplemented` outcomes from the new quantified nested-group callable manifest.
- Verified with `cargo build -p rebar-cpython`, `PYTHONPATH=python python3 -m unittest tests.conformance.test_python_fixture_manifest_contract tests.conformance.test_correctness_quantified_nested_group_callable_replacement_contract tests.conformance.test_correctness_quantified_nested_group_callable_replacement_workflows tests.conformance.test_correctness_fixture_inventory_contract`, and `PYTHONPATH=python python3 -m rebar_harness.correctness --report reports/correctness/latest.json`.
