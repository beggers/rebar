# RBR-0619: Publish the nested broader-range open-ended branch-local-backreference conditional bytes pair

Status: done
Owner: feature-implementation
Created: 2026-03-18
Completed: 2026-03-18

## Goal
- Extend the existing broader-range open-ended `{2,}` nested grouped-alternation plus branch-local-backreference conditional correctness publication with the exact bytes pair on the existing branch-local parity surface, so the frontier reopens on the tracked correctness path before Rust-backed bytes parity and later Python-path benchmark catch-up land.

## Deliverables
- `tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_workflows.py`
- `tests/python/test_branch_local_backreference_parity_suite.py`
- `tests/conformance/correctness_expectations.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_workflows.py` remains the only correctness manifest for this slice and grows only by the 10 byte-typed counterparts to the already-published `str` cases for:
  - `rb"a((b|c){2,})\\2(?(2)d|e)"`
  - `rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)"`
- The added bytes cases stay pinned to the exact broader-range open-ended conditional branch-local-backreference observations already published for the `str` slice:
  - numbered compile metadata, module `search()` lower-bound `b`-branch success on `b"zzabbbdzz"`, compiled `Pattern.fullmatch()` lower-bound `c`-branch success on `b"acccd"`, compiled `Pattern.fullmatch()` mixed-branches success on `b"abcbccd"`, and compiled `Pattern.fullmatch()` no-match case on `b"abcbcc"`;
  - named compile metadata, module `search()` lower-bound `c`-branch success on `b"zzacccdzz"`, compiled `Pattern.fullmatch()` lower-bound `b`-branch success on `b"abbbd"`, compiled `Pattern.fullmatch()` mixed-branches success on `b"abcbccd"`, and compiled `Pattern.fullmatch()` no-match case on `b"abbd"`.
- `tests/python/test_branch_local_backreference_parity_suite.py` keeps the shared fixture-bundle contract honest after the manifest becomes mixed `str`/`bytes`, updates the nested broader-range open-ended conditional branch-local-backreference bundle expectations from `2` compile / `2` module / `6` pattern `str` cases to `4` / `4` / `12` with mixed text-model coverage, introduces one direct bytes follow-on anchor for this manifest, and routes the manifest's bytes rows through that anchor instead of silently widening the generic shared buckets.
- The new nested broader-range open-ended conditional branch-local-backreference bytes follow-on anchor in `tests/python/test_branch_local_backreference_parity_suite.py` stays explicitly unsupported for `rebar` pending the later bytes parity follow-on, keeps the lower-bound, mixed-branches, and no-match texts above visible on the parity path, and does not fork a second bytes-only suite.
- `tests/conformance/correctness_expectations.py` and `reports/correctness/latest.py` are regenerated honestly. With the live checkout still lacking this bytes pair behind `rebar._rebar`, the combined report should move from `1268` total / `1268` passed / `0` `unimplemented` across `111` manifests to `1278` / `1268` / `10`, and `match.nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional` should publish `20` total / `10` passed / `10` `unimplemented` with mixed `str`/`bytes` coverage.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_workflows.py --report .rebar/tmp/rbr-0619-nested-broader-range-open-ended-branch-local-backreference-conditional-bytes.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement new bytes runtime behavior just to make the new cases pass.
- Do not broaden into bytes parity, bytes benchmark rows, replacement or callable-replacement flows, another branch-local-backreference family, or deeper grouped execution in this run.
- Keep the future parity follow-on anchored to the existing `tests/python/test_branch_local_backreference_parity_suite.py` surface and the later benchmark follow-on on the existing `benchmarks/workloads/branch_local_backreference_boundary.py` path.

## Notes
- Queue this directly behind `RBR-0617` so the broader `{2,}` plain branch-local-backreference bytes benchmark catch-up closes before the broader-range open-ended `{2,}` conditional bytes publication reopens correctness work on the same shared branch-local parity surface.
- 2026-03-18 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_workflows.py` currently contains `10` `str` cases and `0` bytes rows;
  - `tests/python/test_branch_local_backreference_parity_suite.py` currently treats `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-workflows` as `str`-only with `2` compile / `2` module / `6` pattern cases and exposes no direct bytes follow-on anchor for this manifest;
  - `reports/correctness/latest.py` currently publishes `match.nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional` at `10` total / `10` passed / `0` `unimplemented` with `text_models == ['str']`, while the combined report stays at `1268` total / `1268` passed / `0` `unimplemented` across `111` manifests;
  - `benchmarks/workloads/branch_local_backreference_boundary.py` already publishes the six adjacent `str` benchmark rows for this exact broader-range open-ended conditional slice as `module-compile-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-cold-str`, `module-search-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-str`, `pattern-fullmatch-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-mixed-branches-purged-str`, `module-compile-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-warm-str`, `module-search-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-warm-str`, and `pattern-fullmatch-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-purged-str`, so a later Python-path benchmark catch-up can mirror those rows without another synthesis pass; and
  - direct public-API probes from this planning run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`.
- A later parity follow-on should convert the same bytes pair behind `rebar._rebar` on the existing branch-local-backreference parity surface before the benchmark surface mirrors the six adjacent `str` rows already published on `benchmarks/workloads/branch_local_backreference_boundary.py`.

## Completion Notes
- 2026-03-18: Added the ten bytes counterparts for `rb"a((b|c){2,})\\2(?(2)d|e)"` and `rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)"` to `tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_workflows.py`, keeping the published lower-bound, mixed-branches, and no-match observations aligned with the existing `str` slice.
- 2026-03-18: Updated `tests/python/test_branch_local_backreference_parity_suite.py` so the manifest is now an explicit mixed `str`/`bytes` bundle with `4` compile, `4` module, and `12` pattern rows, and added one direct bytes follow-on anchor for this manifest that skips `rebar` pending the later bytes parity task while keeping the bytes texts visible on the parity path.
- 2026-03-18: Expanded the relevant representative-case expectations in `tests/conformance/correctness_expectations.py` and republished `reports/correctness/latest.py`. The tracked report now shows `match.nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional` at `20` total / `10` passed / `10` `unimplemented` with `['bytes', 'str']`, and the combined published report at `1278` total / `1268` passed / `10` `unimplemented`.
- 2026-03-18 verification:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py` (`452 passed, 14 skipped, 1491 subtests passed in 26.24s`)
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_workflows.py --report .rebar/tmp/rbr-0619-nested-broader-range-open-ended-branch-local-backreference-conditional-bytes.py` (`20` total / `10` passed / `10` `unimplemented`)
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` (`1278` total / `1268` passed / `10` `unimplemented`)
