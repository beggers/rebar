# RBR-0439: Publish a bounded quantified alternation-heavy conditional replacement correctness pack

Status: done
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Extend the published correctness scorecard with one bounded quantified alternation-heavy two-arm conditional replacement manifest so the quantified `{2}` replacement slice already adjacent to the live conditional benchmark boundary moves onto the ordinary correctness/parity path before parity or benchmark catch-up widen the frontier again.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/conditional_group_exists_quantified_alternation_replacement_workflows.py`
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated quantified alternation-heavy conditional replacement manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded `module.sub()`, `module.subn()`, compiled-`Pattern.sub()`, and compiled-`Pattern.subn()` constant-replacement observations through the public `rebar` API for the exact numbered and named workflows `a(b)?c(?(1)(de|df)|(eg|eh)){2}` and `a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}` that CPython already supports.
- The published cases cover both present-capture and absent-capture outcomes for that exact quantified `{2}` alternation-heavy replacement shape, including bounded workflows that keep the first and second alternation branches explicit on both the yes and else arms, while staying out of replacement templates, callable replacements, deeper nesting, broader repeat ranges, branch-local backreferences, or any non-`{2}` expansion.
- The existing combined correctness scorecard suite absorbs this manifest through `tests/conformance/correctness_expectations.py` and `tests/conformance/test_combined_correctness_scorecards.py` instead of growing another wrapper or manifest-local regression module.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the published scorecard just because current `rebar` behavior is incomplete.
- Verification passes with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_correctness_fixture_inventory_contract.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_quantified_alternation_replacement_workflows.py --report .rebar/tmp/rbr-0439-conditional-quantified-alternation-replacement.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.

## Constraints
- Keep this task focused on correctness publication, fixture registration, shared expectation tables, combined-scorecard coverage, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed quantified alternation-heavy conditional replacement behavior to stdlib `re` outside the existing differential harness path.
- Keep later Rust-backed parity on the shared conditional replacement pytest path and later benchmark catch-up on the existing `benchmarks/workloads/conditional_group_exists_boundary.py` path instead of forking another benchmark family.

## Notes
- Build on `RBR-0190`, `RBR-0196`, `RBR-0197`, `RBR-0203`, and `RBR-0437`.
- The adjacent Python-path benchmark surface already carries the same quantified alternation-heavy pattern pair on `benchmarks/workloads/conditional_group_exists_boundary.py` for `module.search()` and `Pattern.fullmatch()`, so this task should publish the replacement slice first rather than widening benchmarks in the same run.
- The intended post-publication follow-on is Rust-backed parity on the shared `tests/python/test_conditional_group_exists_replacement_parity_suite.py` surface.

## Completion Notes
- Added `conditional-group-exists-quantified-alternation-replacement-workflows` as a new published correctness fixture with eight bounded numbered and named `module.sub()` / `module.subn()` / `Pattern.sub()` / `Pattern.subn()` constant-replacement observations for `a(b)?c(?(1)(de|df)|(eg|eh)){2}` and `a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}`.
- Registered the manifest in the published correctness fixture set and the shared conditional-replacement scorecard expectations so the existing inventory and combined-scorecard suites absorb it without adding a manifest-local regression module.
- Regenerated the tracked published scorecard in `reports/correctness/latest.py`; the tracked artifact now reports `957` total cases across `107` manifests with `949` passes, `0` failures, and `8` honest `unimplemented` cases, which are the new quantified alternation-heavy conditional replacement workflows pending `RBR-0441`.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_correctness_fixture_inventory_contract.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_quantified_alternation_replacement_workflows.py --report .rebar/tmp/rbr-0439-conditional-quantified-alternation-replacement.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.
