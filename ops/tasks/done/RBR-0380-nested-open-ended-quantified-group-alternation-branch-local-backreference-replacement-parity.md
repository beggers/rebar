# RBR-0380: Add open-ended `{1,}` nested-group alternation plus branch-local-backreference replacement-template parity

Status: done
Owner: feature-implementation
Created: 2026-03-15

## Goal
- Convert the open-ended `{1,}` nested-group alternation plus branch-local-backreference replacement-template cases published by `RBR-0378` into real CPython-shaped behavior without claiming broader counted-repeat grouped replacement, callable replacement, broader template parsing, or deeper nested grouped execution support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_open_ended_quantified_group_replacement_template_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The exact published `nested_open_ended_quantified_group_alternation_branch_local_backreference_replacement_workflows.py` cases from `RBR-0378` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` `sub()` / `subn()` flows using `\\1x`, `\\2x`, `\\g<outer>x`, and `\\g<inner>x`.
- Backend-parameterized Python parity coverage for this slice lives on an ordinary pytest path in `tests/python/test_open_ended_quantified_group_replacement_template_parity_suite.py`, driven directly from the published fixture instead of another file-local scenario table, bespoke manifest layer, or native-only `unittest` gate.
- Module and compiled-`Pattern` flows both consume Rust-backed open-ended counted-repeat replacement behavior rather than ad hoc Python-only regex semantics; Python changes stay limited to wrapper construction, cache/object plumbing, template marshalling, and native result marshalling.
- The supported slice remains intentionally narrow: one outer capture around one open-ended `{1,}` `(b|c)` site immediately replayed by one same-branch backreference feeding numbered or named replacement templates is enough, including one numbered lower-bound same-branch path such as `abbd` or `accd`, one numbered longer repeated-branch or mixed-haystack path such as `abbbd`, `abccd`, `abcbccd`, `abbbdaccd`, or `abcbccdabbd`, one named path that keeps the open-ended `{1,}` `outer` capture observable under template replacement, and one named first-match-only or doubled-haystack path that keeps the final selected `inner` branch observable, while broader lower bounds like `{2,}`, benchmark rows, callable replacements, broader template parsing, broader callback semantics, and deeper nested grouped execution remain out of scope.
- `reports/correctness/latest.py` flips the bounded open-ended `{1,}` replacement-template cases from `unimplemented` to `pass` without regressing the already-landed quantified nested-group replacement-template surface, the adjacent open-ended callable-replacement slice, or other published nested replacement behavior.

## Constraints
- Keep this task scoped to the cases published by `RBR-0378`; do not broaden into broader lower bounds like `{2,}`, benchmark work, callable replacement semantics, general replacement-template parsing, or stdlib delegation.
- Implement any new execution or template-expansion behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern` / `Match` / replacement object contracts outside this exact open-ended `{1,}` nested-group branch-local-backreference replacement slice.
- Reuse ordinary pytest parameterization plus the published fixture-loading path and existing parity helpers instead of adding JSON manifests, generators, or another manifest-specific harness layer.

## Notes
- Build on `RBR-0378`, `RBR-0374`, `RBR-0305`, and the existing nested-group replacement boundary.
- Keep later benchmark catch-up on the existing `benchmarks/workloads/nested_group_replacement_boundary.py` path; do not fork another benchmark family when the benchmark follow-on is seeded.

## Completion
- Added a Rust-core collector dedicated to the exact published open-ended `{1,}` nested-group alternation plus branch-local-backreference replacement-template slice, then routed the native template-substitution boundary through it so module and compiled-`Pattern` `sub()` / `subn()` now expand `\\1`, `\\2`, `\\g<outer>`, and `\\g<inner>` from real captured spans without widening into unpublished broader counted-repeat template cases.
- Added fixture-driven pytest parity coverage in `tests/python/test_open_ended_quantified_group_replacement_template_parity_suite.py`, keeping the slice on the ordinary backend-parameterized Python parity path and asserting alignment with the published `nested_open_ended_quantified_group_alternation_branch_local_backreference_replacement_workflows.py` manifest.
- Republished the tracked combined correctness scorecard at `reports/correctness/latest.py`; the tracked summary now reads `881` executed / `881` passed / `0` failed / `0` unimplemented, and the open-ended replacement manifest rows now show `8` passed / `0` unimplemented.
- Verified with `cargo build -p rebar-cpython`, `./.venv/bin/python -m pytest tests/python/test_open_ended_quantified_group_replacement_template_parity_suite.py -q`, `./.venv/bin/python -m pytest tests/python/test_quantified_nested_group_replacement_template_parity.py -q`, `./.venv/bin/python -m pytest tests/python/test_callable_replacement_parity_suite.py -q`, `./.venv/bin/python -m pytest tests/conformance/test_combined_correctness_scorecards.py -q`, `./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_benchmark_scorecards.py -q`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_open_ended_quantified_group_alternation_branch_local_backreference_replacement_workflows.py --report .rebar/tmp/rbr-0380-open-ended-template.json`, which reported `8` executed / `8` passed / `0` unimplemented for the task-local scratch run.
- The shared `nested-group-replacement-boundary` benchmark scorecard contract remains green, but direct Python-path benchmark rows for this exact open-ended template slice are still intentionally absent and remain queued separately in `RBR-0382`.
