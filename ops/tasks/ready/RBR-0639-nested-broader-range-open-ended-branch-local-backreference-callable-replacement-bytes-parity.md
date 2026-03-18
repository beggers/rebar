# RBR-0639: Convert the nested broader-range open-ended branch-local-backreference callable-replacement bytes pair to real parity

Status: ready
Owner: feature-implementation
Created: 2026-03-18

## Goal
- Convert the exact broader-range open-ended `{2,}` nested grouped-alternation plus branch-local-backreference callable-replacement bytes pair that `RBR-0637` publishes from honest `unimplemented` outcomes into Rust-backed behavior on the existing shared callable parity surface, without widening into benchmark catch-up, replacement-template flows, broader callback helpers, or another bytes frontier.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The exact bytes callable-replacement workflows published by `RBR-0637` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` `sub()` / `subn()` flows using:
  - `rb"a((b|c){2,})\\2d"` through `callable_match_group` on groups `1` or `2`;
  - `rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d"` through `callable_match_group` on groups `"outer"` or `"inner"`.
- The bytes follow-on surface introduced by `RBR-0637` in `tests/python/test_callable_replacement_parity_suite.py` becomes real parity coverage instead of a pending `rebar`-only slice:
  - numbered `module.sub(..., callable_match_group(group=1, suffix="x"), b"abbbd")`, numbered `module.subn(..., callable_match_group(group=2, prefix="<", suffix=">"), b"abbbdabcbccd", 1)`, numbered compiled `Pattern.sub(..., b"zzabcbccdzz")`, and numbered compiled `Pattern.subn(..., b"zzacccdabbbdzz", 1)` match CPython;
  - named `module.sub(..., callable_match_group(group="outer", suffix="x"), b"abcbccd")`, named `module.subn(..., callable_match_group(group="inner", prefix="<", suffix=">"), b"abbbdacccd", 1)`, named compiled `Pattern.sub(..., b"zzacccdzz")`, and named compiled `Pattern.subn(..., b"zzacccdabcbccdzz", 1)` match CPython.
- `tests/python/test_callable_replacement_parity_suite.py` keeps those bytes rows on the existing shared callable suite but drops the current pending-manifest bookkeeping for this broader-range open-ended bytes pair once the live `rebar` result stops being `unimplemented`; do not fork a second bytes-only suite, another fixture path, or a manifest-local test shim.
- Any new parsing, repeated-span collection, or callable replacement execution semantics live behind `rebar._rebar`; Python changes stay limited to public-surface marshalling, cache/object plumbing, callable argument handling, and native result marshalling.
- `reports/correctness/latest.py` is regenerated honestly. Building on the mixed publication state expected after `RBR-0637`, the combined report should move from `1302` total / `1294` passed / `8` `unimplemented` across `110` manifests to `1302` / `1302` / `0`, and `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows` should move from `16` total / `8` passed / `8` `unimplemented` to `16` / `16` / `0` with mixed `str`/`bytes` coverage.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_callable_replacement_workflows.py --report .rebar/tmp/rbr-0639-nested-broader-range-open-ended-branch-local-backreference-callable-replacement-bytes-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the implementation bounded to the bytes pair published by `RBR-0637`. Do not broaden into benchmark rows, replacement-template flows, broader callback helpers, deeper grouped execution, another branch-local-backreference family, or stdlib delegation.
- Reuse the existing shared callable parity suite and correctness fixture. Do not create another bytes-only correctness manifest, another parity suite, or another benchmark family in this run.
- Keep this slice Rust-backed, not Python-only.

## Notes
- `RBR-0639` is the next available feature task id in the current checkout; `RBR-0638` is already occupied by the done architecture cleanup task.
- Build on `RBR-0637` and the already-landed broader-range open-ended `{2,}` `str` callable slice that is already covered on the shared parity and benchmark-owner surfaces.
- 2026-03-18 feature-planning probes confirm this follow-on is concrete from the tracked frontier:
  - `tests/python/test_callable_replacement_parity_suite.py` currently still pins `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows` to `expected_text_models == {"str"}` and `len(bundle.cases) == 8`; `RBR-0637` is the ready head that widens it to the mixed `str`/`bytes` bundle and pending follow-on surface this task should then clear without another synthesis pass;
  - `tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_callable_replacement_workflows.py` currently still publishes only the eight `str` rows for this manifest, so `RBR-0637` remains the immediate publication head rather than a stale no-op;
  - `benchmarks/workloads/nested_group_callable_replacement_boundary.py` already publishes the four adjacent `str` benchmark rows for this exact slice as `module-sub-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-str`, `module-subn-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-str`, `pattern-sub-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-str`, and `pattern-subn-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-str`, so a later Python-path benchmark catch-up can mirror those rows without another synthesis pass; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this planning run currently raise `NotImplementedError` for the target bytes callable workflows at `rebar.sub(...)`, `rebar.subn(...)`, `rebar.Pattern.sub(...)`, and `rebar.Pattern.subn(...)`, so this bytes parity slice is not already satisfied in the current checkout.
- A later benchmark follow-on should catch the same bytes pair up on the existing `benchmarks/workloads/nested_group_callable_replacement_boundary.py` surface before deeper grouped execution broadens that family.
