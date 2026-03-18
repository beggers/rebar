# RBR-0607: Publish the nested broader-range wider-ranged-repeat branch-local-backreference bytes pair

Status: done
Owner: feature-implementation
Created: 2026-03-18
Completed: 2026-03-18

## Goal
- Extend the existing broader `{1,4}` nested grouped-alternation plus branch-local-backreference correctness publication with the exact bytes pair on the existing branch-local parity surface, so the frontier reopens on the tracked correctness path before Rust-backed bytes parity and later Python-path benchmark catch-up land.

## Deliverables
- `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_workflows.py`
- `tests/python/test_branch_local_backreference_parity_suite.py`
- `tests/conformance/correctness_expectations.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_workflows.py` remains the only correctness manifest for this slice and grows only by the 14 byte-typed counterparts to the already-published `str` cases for:
  - `rb"a((b|c){1,4})\\2d"`
  - `rb"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d"`
- The added bytes cases stay pinned to the exact broader `{1,4}` branch-local observations already published for the `str` slice:
  - numbered compile metadata, module `search()` lower-bound `b`-branch success on `b"zzabbdzz"` and lower-bound `c`-branch success on `b"zzaccdzz"`, compiled `Pattern.fullmatch()` second-iteration `b`-branch success on `b"abbbd"`, compiled `Pattern.fullmatch()` fourth-repetition mixed-branches success on `b"abcbccd"`, and compiled `Pattern.fullmatch()` no-match cases on `b"abcd"` and `b"abbbbbbd"`;
  - named compile metadata, module `search()` lower-bound `c`-branch success on `b"zzaccdzz"` and lower-bound `b`-branch success on `b"zzabbdzz"`, compiled `Pattern.fullmatch()` second-iteration mixed-branches success on `b"abccd"`, compiled `Pattern.fullmatch()` upper-bound all-`c` success on `b"acccccd"`, and compiled `Pattern.fullmatch()` no-match cases on `b"abcbcd"` and `b"accccccd"`.
- `tests/python/test_branch_local_backreference_parity_suite.py` keeps the shared fixture-bundle contract honest after the manifest becomes mixed `str`/`bytes`, updates the nested broader `{1,4}` branch-local-backreference bundle expectations from `2` compile / `4` module / `8` pattern `str` cases to `4` / `8` / `16` with mixed text-model coverage, introduces one direct bytes follow-on anchor for this manifest, and routes the manifest's bytes rows through that anchor instead of silently widening the generic shared buckets.
- The new nested broader `{1,4}` branch-local-backreference bytes follow-on anchor in `tests/python/test_branch_local_backreference_parity_suite.py` stays explicitly unsupported for `rebar` pending the later bytes parity follow-on, keeps the lower-bound, upper-bound, mixed-branches, and no-match texts above visible on the parity path, and does not fork a second bytes-only suite.
- `tests/conformance/correctness_expectations.py` and `reports/correctness/latest.py` are regenerated honestly. With the live checkout still lacking this bytes pair behind `rebar._rebar`, the combined report should move from `1244` total / `1244` passed / `0` `unimplemented` across `111` manifests to `1258` / `1244` / `14`, and `match.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference` should publish `28` total / `14` passed / `14` `unimplemented` with mixed `str`/`bytes` coverage.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_workflows.py --report .rebar/tmp/rbr-0607-nested-broader-range-wider-ranged-repeat-branch-local-backreference-bytes.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement new bytes runtime behavior just to make the new cases pass.
- Do not broaden into bytes parity, bytes benchmark rows, the open-ended nested branch-local-backreference bytes follow-on, or another branch-local-backreference family in this run.
- Keep the future parity follow-on anchored to the existing `tests/python/test_branch_local_backreference_parity_suite.py` surface.

## Notes
- Queue this directly behind `RBR-0605` so the bounded `+` nested-group branch-local-backreference bytes benchmark catch-up closes before the broader `{1,4}` nested branch-local-backreference bytes publication reopens correctness work on the same shared parity surface.
- 2026-03-18 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_workflows.py` currently contains `14` case ids and `0` bytes rows;
  - `tests/python/test_branch_local_backreference_parity_suite.py` currently treats `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-workflows` as `str`-only with `2` compile / `4` module / `8` pattern cases and exposes no direct bytes follow-on anchor for this manifest;
  - `tests/conformance/correctness_expectations.py` and `reports/correctness/latest.py` currently publish `match.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference` at `14` total / `14` passed / `0` `unimplemented` with `text_models == ['str']`, while the combined report stays at `1244` total / `1244` passed / `0` `unimplemented` across `111` manifests;
  - `benchmarks/workloads/nested_group_alternation_boundary.py` already publishes the three adjacent `str` benchmark rows for this exact broader `{1,4}` slice as `module-search-numbered-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-lower-bound-b-branch-warm-str`, `module-compile-named-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-warm-str`, and `pattern-fullmatch-named-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-upper-bound-all-c-purged-str`, so a later Python-path benchmark catch-up can mirror those rows without another synthesis pass; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this planning run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`.
- A later parity follow-on should convert the same bytes pair behind `rebar._rebar` on the existing branch-local-backreference parity surface before the benchmark surface mirrors the three adjacent `str` rows already published on `benchmarks/workloads/nested_group_alternation_boundary.py`.

## Completion Note
- 2026-03-18: Added the 14 bytes mirrors for `rb"a((b|c){1,4})\\2d"` and `rb"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d"` to `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_workflows.py`, keeping this manifest as the only correctness publication surface for the broader `{1,4}` nested branch-local-backreference slice.
- Updated `tests/python/test_branch_local_backreference_parity_suite.py` so the manifest is now a mixed `str`/`bytes` bundle with `4` compile / `8` module / `16` pattern rows, and routed its new bytes rows through one explicit direct bytes follow-on anchor that stays marked unsupported on the `rebar` backend pending the later bytes parity task.
- Refreshed `tests/conformance/correctness_expectations.py` and republished `reports/correctness/latest.py`; the tracked report now shows the combined correctness surface at `1258` total / `1244` passed / `14` unimplemented, while `match.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference` now shows `28` total / `14` passed / `14` unimplemented with `['bytes', 'str']` coverage.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_workflows.py --report .rebar/tmp/rbr-0607-nested-broader-range-wider-ranged-repeat-branch-local-backreference-bytes.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.
