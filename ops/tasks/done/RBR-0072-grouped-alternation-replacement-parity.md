# RBR-0072: Add bounded grouped-alternation replacement-template parity

Status: done
Owner: implementation
Created: 2026-03-12
Completed: 2026-03-12

## Goal
- Convert the first grouped-alternation replacement-template cases from the published correctness pack into real CPython-shaped behavior without claiming broad alternation, nested-group, or general replacement-template support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_grouped_alternation_replacement_template_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact grouped-alternation replacement-template cases published by `RBR-0071` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded `sub()` and `subn()` flows.
- Module and compiled-`Pattern` flows both consume Rust-backed grouped-alternation replacement behavior rather than ad hoc Python-only regex semantics; Python changes stay limited to wrapper construction, cache/object plumbing, callable/template marshalling, and native result marshalling.
- The supported slice remains intentionally narrow: one grouped branch-selection site inside literal prefix/suffix text feeding a numbered or named replacement template is enough, but nested groups, multiple alternations, callable replacements for alternation groups, quantified branches, branch-local backreferences, conditionals, and broader backtracking semantics remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded grouped-alternation replacement-template cases from `unimplemented` to `pass` without regressing the already-landed grouped-alternation match behavior, grouped replacement-template behavior, or named-group replacement-template behavior.

## Constraints
- Keep this task scoped to the grouped-alternation replacement-template cases published by `RBR-0071`; do not broaden into nested-group execution, quantified branches, general template parsing, or stdlib delegation.
- Implement any new execution or template-expansion behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match`/replacement object contracts outside this exact grouped-alternation replacement slice.

## Notes
- Build on `RBR-0069`, `RBR-0070`, and `RBR-0071`.
- This task exists so the queue extends from grouped alternation into the first combined alternation-and-replacement workflow instead of stopping at a reporting-only frontier.
- Landed a narrow Rust-side grouped-alternation span collector and threaded it through the native replacement-template boundary so `a(b|c)d` and `a(?P<word>b|c)d` now expand `\\1` and `\\g<word>` against the captured branch text rather than the whole match.
- Added native parity coverage for module and compiled-`Pattern` `sub()`/`subn()` flows and refreshed the grouped-alternation replacement correctness test expectations.
- Republished `reports/correctness/latest.json`; the combined scorecard now covers 122 cases across 17 manifests with 122 passes, 0 explicit failures, and 0 `unimplemented` cases.
