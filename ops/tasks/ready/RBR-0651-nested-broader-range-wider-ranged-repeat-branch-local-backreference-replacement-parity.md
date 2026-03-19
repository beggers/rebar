# RBR-0651: Convert the nested broader-range wider-ranged-repeat branch-local-backreference replacement-template pack to real parity

Status: ready
Owner: feature-implementation
Created: 2026-03-19

## Goal
- Convert the exact broader `{1,4}` counted-repeat nested grouped-alternation plus branch-local-backreference replacement-template `str` slice into real Rust-backed behavior on the existing shared replacement parity surface once the publication pack lands, without widening into benchmark catch-up, bytes, callable replacement, or another grouped frontier.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The exact `str` replacement-template workflows stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` `sub()` / `subn()` flows using:
  - `r"a((b|c){1,4})\\2d"` with `r"\\1x"` or `r"\\2x"`;
  - `r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d"` with `r"\\g<outer>x"` or `r"\\g<inner>x"`.
- The shared replacement follow-on surface becomes real parity coverage instead of a pending slice:
  - numbered `module.sub(..., "\\1x", "abbd")` and `module.subn(..., "\\2x", "abbbdaccd", 1)` match CPython;
  - numbered compiled `Pattern.sub("\\1x", "zzabcbccdzz")` and `Pattern.subn("\\2x", "zzaccdabcbccdzz", 1)` match CPython;
  - named `module.sub(..., "\\g<outer>x", "abcbccd")` and `module.subn(..., "\\g<inner>x", "abbbdaccd", 1)` match CPython; and
  - named compiled `Pattern.sub("\\g<outer>x", "zzacccccdzz")` and `Pattern.subn("\\g<inner>x", "zzacccccdabbbdzz", 1)` match CPython.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` keeps those rows on the existing shared replacement suite but drops any pending behavior for this broader `{1,4}` manifest; do not fork a second parity suite, a manifest-local shim, or a replacement-specific benchmark harness.
- Any new parsing, repeated-span collection, template expansion, or replacement execution semantics live behind `rebar._rebar`; Python changes stay limited to public-surface marshalling, cache/object plumbing, template argument handling, and native result marshalling.
- `reports/correctness/latest.py` is regenerated honestly. Building on the expanded publication state expected once the shared `{1,4}` replacement rows are present, the combined report should move from `1318` total / `1310` passed / `8` `unimplemented` across `111` manifests to `1318` / `1318` / `0`, and `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-replacement-workflows` should move from `8` total / `0` passed / `8` `unimplemented` to `8` / `8` / `0` with `str` coverage.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_replacement_workflows.py --report .rebar/tmp/rbr-0651-nested-broader-range-wider-ranged-repeat-branch-local-backreference-replacement-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the implementation bounded to the `str` rows on this exact broader `{1,4}` replacement-template slice. Do not broaden into bytes, benchmark rows, callable replacements, broader template parsing, deeper grouped execution, another branch-local-backreference family, or stdlib delegation.
- Reuse the existing shared replacement parity suite and correctness fixture. Do not create another `str`-only replacement manifest, another parity module, or another benchmark family in this run.
- Keep this slice Rust-backed, not Python-only.

## Notes
- `RBR-0651` is the next available feature task id in the current checkout; `RBR-0650` is already occupied by the done architecture cleanup task in `ops/tasks/done/`.
- Build on `RBR-0649`.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` already carries the adjacent broader `{2,}` open-ended replacement-template bundle on the same shared surface, so this `{1,4}` `str` slice can stay on the existing parity suite once published instead of inventing another path.
- `benchmarks/workloads/nested_group_replacement_boundary.py` already carries the adjacent `{1,}` and broader-range open-ended `{2,}` replacement-template rows but no wider-ranged-repeat `{1,4}` sibling, so later Python-path benchmark catch-up can stay on that existing manifest without another synthesis pass.
- 2026-03-19 feature-planning probes confirm this follow-on is concrete from the tracked frontier:
  - the ready `RBR-0649` publication task already pins the exact patterns, replacement templates, haystacks, and shared replacement owner path for the eight `str` rows this parity slice needs to convert;
  - `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_replacement_workflows.py` does not yet exist in the current checkout, so `RBR-0649` remains the immediate publication head rather than a stale no-op;
  - after `cargo build -p rebar-cpython`, direct public-API probes for all eight target workflows still raise `NotImplementedError` from `rebar.sub()`, `rebar.subn()`, `rebar.Pattern.sub()`, `rebar.Pattern.subn()`, or the compile placeholder path, so Rust-backed parity is not already satisfied in the current checkout; and
  - the later benchmark catch-up can mirror the same module and compiled-`Pattern` owner shapes on `benchmarks/workloads/nested_group_replacement_boundary.py` once this parity slice lands, because the adjacent wider replacement frontier already uses that shared manifest.
