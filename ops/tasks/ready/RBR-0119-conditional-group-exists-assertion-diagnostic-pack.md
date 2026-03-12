# RBR-0119: Publish a bounded assertion-conditioned conditional diagnostic pack

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published correctness scorecard with a bounded rejected-syntax manifest for assertion-conditioned conditional forms so the queue stays precise after the accepted empty-arm conditional slices land.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/conditional_group_exists_assertion_diagnostics.json`
- `tests/conformance/test_correctness_conditional_group_exists_assertion_diagnostics.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded compile-time observations through the public `rebar` API for CPython-rejected assertion-conditioned conditional forms such as `a(?(?=b)b|c)d`, and it records the compile error shape that stdlib `re` exposes.
- The pack keeps the slice narrow and explicit: one assertion-conditioned conditional site is enough, while nested conditionals, replacement-conditioned workflows, broader backtracking, and accepted empty-arm forms remain out of scope unless they are included specifically to document them as honest gaps.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- `reports/correctness/latest.json` preserves the published combined-scorecard contract and keeps the existing accepted conditional manifests intact.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed conditional diagnostics to stdlib `re` outside the existing differential harness path.
- Keep the diagnostic slice bounded to assertion-conditioned forms; do not turn this into a catch-all conditional error bucket.

## Notes
- Build on `RBR-0118`.
- This task exists so the queue keeps moving with an exact CPython-pinned diagnostic frontier instead of stopping after the last accepted empty-arm conditional form.
