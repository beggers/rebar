# RBR-0613: Publish the nested broader-range open-ended branch-local-backreference bytes pair

Status: ready
Owner: feature-implementation
Created: 2026-03-18

## Goal
- Extend the existing broader-range open-ended `{2,}` nested grouped-alternation plus branch-local-backreference correctness publication with the exact bytes pair on the existing branch-local parity surface, so the frontier reopens on the tracked correctness path before Rust-backed bytes parity and later Python-path benchmark catch-up land.

## Deliverables
- `tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_workflows.py`
- `tests/python/test_branch_local_backreference_parity_suite.py`
- `tests/conformance/correctness_expectations.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_workflows.py` remains the only correctness manifest for this slice and grows only by the 10 byte-typed counterparts to the already-published `str` cases for:
  - `rb"a((b|c){2,})\\2d"`
  - `rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d"`
- The added bytes cases stay pinned to the exact broader-range open-ended branch-local observations already published for the `str` slice:
  - numbered compile metadata, module `search()` lower-bound `b`-branch success on `b"zzabbbdzz"`, compiled `Pattern.fullmatch()` lower-bound `c`-branch success on `b"acccd"`, compiled `Pattern.fullmatch()` fourth-repetition mixed-branches success on `b"abcbccd"`, and compiled `Pattern.fullmatch()` no-match case on `b"abbd"`;
  - named compile metadata, module `search()` lower-bound `c`-branch success on `b"zzacccdzz"`, compiled `Pattern.fullmatch()` lower-bound `b`-branch success on `b"abbbd"`, compiled `Pattern.fullmatch()` third-repetition mixed-branches success on `b"abcccd"`, and compiled `Pattern.fullmatch()` no-match case on `b"accd"`.
- `tests/python/test_branch_local_backreference_parity_suite.py` keeps the shared fixture-bundle contract honest after the manifest becomes mixed `str`/`bytes`, updates the nested broader-range open-ended branch-local-backreference bundle expectations from `2` compile / `2` module / `6` pattern `str` cases to `4` / `4` / `12` with mixed text-model coverage, introduces one direct bytes follow-on anchor for this manifest, and routes the manifest's bytes rows through that anchor instead of silently widening the generic shared buckets.
- The new nested broader-range open-ended branch-local-backreference bytes follow-on anchor in `tests/python/test_branch_local_backreference_parity_suite.py` stays explicitly unsupported for `rebar` pending the later bytes parity follow-on, keeps the lower-bound, mixed-branches, and no-match texts above visible on the parity path, and does not fork a second bytes-only suite.
- `tests/conformance/correctness_expectations.py` and `reports/correctness/latest.py` are regenerated honestly. With the live checkout still lacking this bytes pair behind `rebar._rebar`, the combined report should move from `1258` total / `1258` passed / `0` `unimplemented` across `111` manifests to `1268` / `1258` / `10`, and `match.nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference` should publish `20` total / `10` passed / `10` `unimplemented` with mixed `str`/`bytes` coverage.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_workflows.py --report .rebar/tmp/rbr-0613-nested-broader-range-open-ended-branch-local-backreference-bytes.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement new bytes runtime behavior just to make the new cases pass.
- Do not broaden into bytes parity, bytes benchmark rows, the open-ended conditional bytes follow-on, replacement or callable-replacement flows, or another branch-local-backreference family in this run.
- Keep the future parity follow-on anchored to the existing `tests/python/test_branch_local_backreference_parity_suite.py` surface.

## Notes
- Queue this directly behind `RBR-0611` so the broader `{1,4}` bytes benchmark catch-up closes before the broader-range open-ended `{2,}` nested branch-local-backreference bytes publication reopens correctness work on the same shared parity surface.
- 2026-03-18 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_workflows.py` currently contains `10` `str` cases and `0` bytes rows;
  - `tests/python/test_branch_local_backreference_parity_suite.py` currently treats `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-workflows` as `str`-only with `2` compile / `2` module / `6` pattern cases and already keeps the manifest on the shared branch-local parity surface;
  - `reports/correctness/latest.py` currently publishes `match.nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference` at `10` total / `10` passed / `0` `unimplemented` with `text_models == ['str']`, while the combined report stays at `1258` total / `1258` passed / `0` `unimplemented` across `111` manifests;
  - `benchmarks/workloads/nested_group_alternation_boundary.py` already publishes the three adjacent `str` benchmark rows for this exact broader-range open-ended slice as `module-search-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-lower-bound-b-branch-warm-str`, `module-compile-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-warm-str`, and `pattern-fullmatch-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-lower-bound-c-branch-purged-str`, so a later Python-path benchmark catch-up can mirror those rows without another synthesis pass; and
  - direct public-API probes from this planning run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`.
- A later parity follow-on should convert the same bytes pair behind `rebar._rebar` on the existing branch-local-backreference parity surface before the benchmark surface mirrors the three adjacent `str` rows already published on `benchmarks/workloads/nested_group_alternation_boundary.py`.
