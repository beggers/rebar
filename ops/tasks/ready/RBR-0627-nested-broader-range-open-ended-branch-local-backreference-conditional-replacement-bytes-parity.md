# RBR-0627: Convert the nested broader-range open-ended branch-local-backreference conditional replacement-template bytes pair to real parity

Status: ready
Owner: feature-implementation
Created: 2026-03-18

## Goal
- Convert the exact broader-range open-ended `{2,}` nested grouped-alternation plus branch-local-backreference conditional replacement-template bytes pair published by `RBR-0625` from honest `unimplemented` outcomes into Rust-backed behavior on the existing shared replacement parity surface, without widening into benchmark catch-up, callable replacement, or another bytes frontier.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The exact bytes replacement-template workflows published by `RBR-0625` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` `sub()` / `subn()` flows using:
  - `rb"a((b|c){2,})\\2(?(2)d|e)"` with `rb"\\1x"` or `rb"\\2x"`;
  - `rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)"` with `rb"\\g<outer>x"` or `rb"\\g<inner>x"`.
- The bytes follow-on surface introduced by `RBR-0625` in `tests/python/test_fixture_backed_replacement_parity_suite.py` becomes real parity coverage instead of a `rebar`-only pending slice:
  - numbered `module.sub(..., rb"\\1x", b"abbbd")` and `module.subn(..., rb"\\2x", b"abbbdabcbccd", 1)` match CPython;
  - numbered compiled `Pattern.sub(rb"\\1x", b"zzabcbccdzz")` and `Pattern.subn(rb"\\2x", b"zzacccdabbbdzz", 1)` match CPython;
  - named `module.sub(..., rb"\\g<outer>x", b"abcbccd")` and `module.subn(..., rb"\\g<inner>x", b"abbbdacccd", 1)` match CPython; and
  - named compiled `Pattern.sub(rb"\\g<outer>x", b"zzacccdzz")` and `Pattern.subn(rb"\\g<inner>x", b"zzacccdabcbccdzz", 1)` match CPython.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` keeps those bytes rows on the existing shared replacement suite but drops the current `rebar`-only pending behavior for this broader-range open-ended conditional bytes pair; do not fork a second bytes-only suite, another fixture path, or a manifest-local test shim.
- Any new parsing, repeated-span collection, template expansion, or replacement execution semantics live behind `rebar._rebar`; Python changes stay limited to public-surface marshalling, cache/object plumbing, template argument handling, and native result marshalling.
- `reports/correctness/latest.py` is regenerated honestly. Building on the publication state expected after `RBR-0625`, the combined report should move from `1286` total / `1278` passed / `8` `unimplemented` across `111` manifests to `1286` / `1286` / `0`, and `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-replacement-workflows` should move from `16` total / `8` passed / `8` `unimplemented` to `16` / `16` / `0` with mixed `str`/`bytes` coverage.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_replacement_workflows.py --report .rebar/tmp/rbr-0627-nested-broader-range-open-ended-branch-local-backreference-conditional-replacement-bytes-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the implementation bounded to the bytes pair published by `RBR-0625`. Do not broaden into benchmark rows, callable replacements, broader template parsing, deeper grouped execution, another branch-local-backreference family, or stdlib delegation.
- Reuse the existing shared replacement parity suite and correctness fixture. Do not create another bytes-only correctness manifest, another parity suite, or another benchmark family in this run.
- Keep this slice Rust-backed, not Python-only.

## Notes
- Build on `RBR-0625`.
- `ops/tasks/ready/RBR-0625-nested-broader-range-open-ended-branch-local-backreference-conditional-replacement-bytes-pack.md` already pins the exact eight bytes fixture rows, the shared replacement-suite follow-on surface on `tests/python/test_fixture_backed_replacement_parity_suite.py`, and the post-pack scorecard target for this same numbered and named bytes pair.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` already carries the matching `str` replacement-template bundle for `a((b|c){2,})\\2(?(2)d|e)` and `a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)`, so this bytes parity slice can stay on the existing suite once the pack lands instead of inventing another test path.
- `benchmarks/workloads/nested_group_replacement_boundary.py` already publishes the four adjacent `str` benchmark rows for this exact slice as `module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-str`, `module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-first-match-only-b-branch-warm-str`, `pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-purged-str`, and `pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-c-branch-first-match-only-purged-str`, so a later Python-path benchmark catch-up can mirror those rows without another synthesis pass.
- Direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this planning run still raise `NotImplementedError` for both target bytes replacement workflows at `rebar.sub(...)`, so the Rust-backed bytes parity work is not already satisfied in the current checkout.
- A later benchmark follow-on should catch the same bytes pair up on the existing `benchmarks/workloads/nested_group_replacement_boundary.py` surface before deeper grouped execution broadens that family.
