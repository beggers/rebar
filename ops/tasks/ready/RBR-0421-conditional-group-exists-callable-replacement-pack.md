# RBR-0421: Publish a bounded two-arm conditional callable-replacement correctness pack

Status: ready
Owner: feature-implementation
Created: 2026-03-15

## Goal
- Extend the published correctness scorecard with one bounded two-arm conditional callable-replacement manifest so the smallest remaining callable gap on `conditional_group_exists_boundary` moves onto the ordinary correctness/parity path before another broader benchmark-only backfill takes precedence.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated two-arm conditional callable-replacement manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded `module.sub()`, `module.subn()`, compiled-`Pattern.sub()`, and compiled-`Pattern.subn()` callable-replacement observations through the public `rebar` API for the exact numbered and named workflows `a(b)?c(?(1)d|e)` and `a(?P<word>b)?c(?(word)d|e)` that CPython already supports.
- The published cases cover at least one numbered present-capture callback path, one numbered absent-capture count-limited path, one named present-capture callback path, and one named absent-capture count-limited path, while staying on the tiny `d|e` two-arm conditional slice instead of widening into alternation-heavy arms, nested conditionals, quantified conditionals, replacement-template variants, or broader callback semantics.
- The callable replacements stay bounded to the existing `callable_match_group` helper shape by reading `match.group(1)` for numbered workflows and `match.group("word")` for named workflows; do not introduce another callback helper or another manifest-specific harness layer.
- `tests/conformance/correctness_expectations.py` and `tests/conformance/test_combined_correctness_scorecards.py` absorb the new manifest through the existing combined scorecard path, and `tests/python/test_callable_replacement_parity_suite.py` continues to discover published `*callable_replacement_workflows.py` fixtures without growing another family-specific parity module.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the published scorecard just because current `rebar` behavior is incomplete.

## Constraints
- Keep this task focused on correctness publication, fixture registration, shared expectation tables, shared callable-parity fixture bookkeeping, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed two-arm conditional callable-replacement behavior to stdlib `re` outside the existing differential harness path.
- Keep later Rust-backed parity on the shared callable parity suite and later benchmark catch-up on the existing `benchmarks/workloads/conditional_group_exists_boundary.py` path instead of forking another benchmark family.

## Notes
- Build on `RBR-0193`, `RBR-0194`, `RBR-0415`, and the existing shared callable-replacement fixture path.
- The adjacent Python-path benchmark anchor already exists as `pattern-subn-callable-named-conditional-group-exists-replacement-purged-gap` in `benchmarks/workloads/conditional_group_exists_boundary.py`, so this task should publish the correctness/parity slice first rather than trying to widen benchmark coverage in the same run.
