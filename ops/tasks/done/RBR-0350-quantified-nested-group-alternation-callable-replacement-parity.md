# RBR-0350: Add quantified nested-group alternation callable-replacement parity

Status: done
Owner: feature-implementation
Created: 2026-03-15

## Goal
- Convert the quantified nested-group alternation callable-replacement cases from `RBR-0348` into real Rust-backed behavior without claiming broader counted-repeat grouped callbacks, branch-local-backreference callbacks, replacement-template variants, or deeper nested grouped execution support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_quantified_nested_group_alternation_callable_replacement_parity.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The exact quantified nested-group alternation callable-replacement cases published by `RBR-0348` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded module and compiled-`Pattern` `sub()` and `subn()` callable-replacement workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, callable marshalling, and native result marshalling.
- The supported slice remains intentionally narrow: one outer capturing group containing one `+`-quantified inner numbered or named capturing group with one literal alternation site feeding callable replacements is enough, including a numbered lower-bound branch path such as `abd` or `acd`, a numbered repeated or mixed-branch path such as `abccd` or `acbbd`, a named lower-bound or mixed-branch path that keeps the quantified outer capture observable, and one count-limited or first-match-only doubled-haystack case that keeps the final selected inner branch observable under replacement, while broader counted repeats like `{1,4}` or `{1,}`, branch-local-backreference callbacks, replacement-template variants, broader callback semantics, and deeper nested grouped execution remain out of scope.
- `reports/correctness/latest.py` flips the bounded quantified nested-group alternation callable-replacement cases from `unimplemented` to `pass` without regressing the already-landed quantified nested-group callable-replacement slice, quantified nested-group alternation slice, nested-group alternation callable-replacement slice, or the surrounding callable-replacement and capture-metadata surfaces.

## Constraints
- Keep this task scoped to the cases published by `RBR-0348`; do not broaden into wider counted repeats, branch-local backreferences, replacement-template workflows, general callback helpers, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` and callable-replacement contracts outside this exact quantified nested-group alternation callable-replacement slice.

## Notes
- Build on `RBR-0348`, `RBR-0313`, `RBR-0320`, and `RBR-0344`.
- Keep later benchmark catch-up on the existing `benchmarks/workloads/nested_group_callable_replacement_boundary.py` path; the follow-on should add only the minimal quantified nested alternation rows needed to publish this exact bounded slice instead of forking another benchmark family.

## Completion Notes
- Added a dedicated Rust captured-span collector for quantified nested-group alternation callable replacement and exposed it through `rebar._rebar`, so the existing Python callable-marshalling path now handles `a((b|c)+)d` and `a(?P<outer>(?P<inner>b|c)+)d` without adding ad hoc Python regex semantics.
- Added focused parity coverage in `tests/python/test_quantified_nested_group_alternation_callable_replacement_parity.py` for compile metadata, module and compiled-pattern `sub()` / `subn()` parity, callback match-object parity, and no-match callable behavior on this exact bounded slice.
- Republished the tracked combined correctness scorecard in `reports/correctness/latest.py`; the verified tracked summary is 841 total cases, 841 passes, 0 failures, and 0 `unimplemented`, and the `quantified-nested-group-alternation-callable-replacement-workflows` manifest now reports 8 passes and 0 `unimplemented`.
- Verified with `cargo build -p rebar-cpython`, `PYTHONPATH=python ./.venv/bin/python -m pytest tests/python/test_quantified_nested_group_alternation_callable_replacement_parity.py`, `PYTHONPATH=python ./.venv/bin/python -m pytest tests/python/test_callable_replacement_parity_suite.py -k "quantified and alternation and callable"`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/quantified_nested_group_alternation_callable_replacement_workflows.py --report /tmp/rbr0350-quantified-nested-group-alternation-callable-replacement.json`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`, and `PYTHONPATH=python ./.venv/bin/python -m pytest tests/conformance/test_combined_correctness_scorecards.py`.
