# RBR-0426: Publish a bounded two-arm conditional replacement-template correctness pack

Status: ready
Owner: feature-implementation
Created: 2026-03-15

## Goal
- Extend the published correctness scorecard with one bounded two-arm conditional replacement-template manifest so the last explicit replacement-template gap on `conditional_group_exists_boundary` moves onto the ordinary correctness/parity path before later benchmark catch-up reuses that anchor.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/conditional_group_exists_replacement_template_workflows.py`
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated two-arm conditional replacement-template manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded `module.sub()`, `module.subn()`, compiled-`Pattern.sub()`, and compiled-`Pattern.subn()` replacement-template observations through the public `rebar` API for the exact numbered and named workflows `a(b)?c(?(1)d|e)` with `\\1x`, and `a(?P<word>b)?c(?(word)d|e)` with `\\g<word>x`, that CPython already supports.
- The published cases cover at least one numbered present-capture template path, one numbered absent-capture count-limited template path, one named present-capture template path, and one named absent-capture count-limited template path, while staying on the tiny `d|e` two-arm conditional slice instead of widening into alternation-heavy arms, nested conditionals, quantified conditionals, constant replacements, callable replacements, or broader template parsing.
- The existing combined correctness scorecard suite absorbs this manifest through `tests/conformance/correctness_expectations.py` and `tests/conformance/test_combined_correctness_scorecards.py` instead of growing another bespoke wrapper.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the published scorecard just because current `rebar` behavior is incomplete.

## Constraints
- Keep this task focused on correctness publication, fixture registration, shared expectation tables, combined-scorecard coverage, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed two-arm conditional replacement-template behavior to stdlib `re` outside the existing differential harness path.
- Reuse the ordinary Python fixture path and existing combined correctness helpers instead of introducing another frontier-specific harness layer, JSON manifest, or generator.

## Notes
- Build on `RBR-0424`, `RBR-0423`, `RBR-0193`, and the existing bounded conditional replacement publication path.
- The adjacent Python-path benchmark anchor already exists as `module-sub-template-numbered-conditional-group-exists-replacement-warm-gap` in `benchmarks/workloads/conditional_group_exists_boundary.py`, so this task should publish the correctness slice first rather than widening benchmark coverage in the same run.
- Keep later Rust-backed parity on the shared conditional replacement pytest path and later benchmark catch-up on the existing `benchmarks/workloads/conditional_group_exists_boundary.py` path instead of forking another benchmark family.
