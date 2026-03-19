# RBR-0661: Publish the nested broader-range wider-ranged-repeat branch-local-backreference callable-replacement bytes pair

Status: done
Owner: feature-implementation
Created: 2026-03-19
Completed: 2026-03-19

## Goal
- Extend the existing broader `{1,4}` nested grouped-alternation plus branch-local-backreference callable-replacement correctness publication with the exact bytes pair on the shared callable parity surface, so the frontier reopens on the tracked correctness path before any Rust-backed bytes follow-on and later Python-path benchmark catch-up land.

## Deliverables
- `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_callable_replacement_workflows.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_callable_replacement_workflows.py` remains the only correctness manifest for this slice and grows only by the 8 byte-typed counterparts to the already-published `str` cases for:
  - `rb"a((b|c){1,4})\\2d"` through `callable_match_group` on groups `1` or `2`;
  - `rb"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d"` through `callable_match_group` on groups `"outer"` or `"inner"`.
- The added bytes cases stay pinned to the exact broader `{1,4}` callable-replacement observations already published for the `str` slice:
  - numbered `module.sub(..., callable_match_group(group=1, suffix=b"x"), b"abbd")`, numbered `module.subn(..., callable_match_group(group=2, prefix=b"<", suffix=b">"), b"abbbdaccd", 1)`, numbered compiled `Pattern.sub(..., b"zzabcbccdzz")`, and numbered compiled `Pattern.subn(..., b"zzaccdabcbccdzz", 1)`;
  - named `module.sub(..., callable_match_group(group="outer", suffix=b"x"), b"abcbccd")`, named `module.subn(..., callable_match_group(group="inner", prefix=b"<", suffix=b">"), b"abbbdaccd", 1)`, named compiled `Pattern.sub(..., b"zzacccccdzz")`, and named compiled `Pattern.subn(..., b"zzacccccdabbbdzz", 1)`.
- `tests/python/test_callable_replacement_parity_suite.py` keeps the shared callable-replacement owner honest after this manifest becomes mixed `str`/`bytes`, adds manifest-spec coverage for `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows`, updates this manifest from 8 `str` rows to 16 mixed rows with helper counts growing from `2` to `4` for each of `module_call/sub`, `module_call/subn`, `pattern_call/sub`, and `pattern_call/subn`, and keeps the new bytes rows explicit on the shared suite:
  - if the live `rebar` result still reports placeholder behavior for those bytes rows, represent them through `pending_rebar_case_ids` instead of forcing them through the current compile, no-match, near-miss, or return-type-error partitions; and
  - if the live `rebar` result already matches CPython for those bytes rows, keep the mixed-text manifest landed without adding a bytes-only callable suite or another manifest-specific parity module.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1326` total / `1326` passed / `0` `unimplemented` across `111` manifests to `1334` total cases across the same `111` manifests;
  - `collection.replacement.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference.callable` moves from `8` total / `8` passed / `0` `unimplemented` with `['str']` text models to `16` total with mixed `str`/`bytes` coverage; and
  - the new bytes cases are reported honestly as either `pass` or `unimplemented` according to the live `rebar` result rather than being dropped from the published scorecard.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_callable_replacement_workflows.py --report .rebar/tmp/rbr-0661-nested-broader-range-wider-ranged-repeat-branch-local-backreference-callable-replacement-bytes.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement new bytes callable-replacement behavior just to make the new cases pass.
- Do not broaden into bytes parity, bytes benchmark rows, the adjacent replacement-template flows, broader callback semantics, another branch-local-backreference family, or deeper grouped execution in this run.
- Keep the future parity follow-on anchored to the existing `tests/python/test_callable_replacement_parity_suite.py` surface and the later benchmark follow-on on the existing `benchmarks/workloads/nested_group_callable_replacement_boundary.py` path.

## Notes
- `RBR-0661` is the next available feature task id in the current checkout; `RBR-0660` is already occupied by the done architecture cleanup task in `ops/tasks/done/`.
- Queue this directly behind `RBR-0659` so the broader `{1,4}` non-callable replacement-template bytes benchmark catch-up lands before the adjacent callable bytes publication reopens correctness work on the same shared nested-group replacement frontier.
- 2026-03-19 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_callable_replacement_workflows.py` currently contains the 8 published `str` rows for this manifest and no bytes rows;
  - `tests/python/test_callable_replacement_parity_suite.py` currently references this manifest in `PATTERN_RETURN_TYPE_ERROR_EXPECTED_MANIFEST_IDS`, but it has no dedicated `CallableManifestSpec` entry yet and therefore still treats the published bundle as a default 8-case `str`-only owner in its shape contract;
  - `tests/conformance/test_combined_correctness_scorecards.py` currently publishes only the 4 representative `str` cases for this manifest;
  - `reports/correctness/latest.py` currently publishes `collection.replacement.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference.callable` at `8` total / `8` passed / `0` `unimplemented` with `text_models == ['str']`, while the combined report stays at `1326` total / `1326` passed / `0` `unimplemented` across `111` manifests; and
  - `benchmarks/workloads/nested_group_callable_replacement_boundary.py` already publishes the four adjacent `str` benchmark rows for this exact slice as `module-sub-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str`, `module-subn-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-mixed-branches-first-match-only-warm-str`, `pattern-sub-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-str`, and `pattern-subn-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-str`, so a later Python-path benchmark catch-up can mirror those rows without another synthesis pass.
- A later parity follow-on should convert the same bytes pair behind `rebar._rebar` on the existing shared callable parity surface before the benchmark surface mirrors those four adjacent `str` rows already published on `benchmarks/workloads/nested_group_callable_replacement_boundary.py`.

## Completion Note
- 2026-03-19: Added the eight broader `{1,4}` bytes callable-replacement mirrors to `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_callable_replacement_workflows.py`, keeping this as the only correctness manifest for the slice and pinning the bytes callbacks to the published numbered and named module/compiled-`Pattern` observations with true bytes prefixes and suffixes.
- 2026-03-19: Updated `tests/python/test_callable_replacement_parity_suite.py` so the shared callable owner now expects `16` mixed `str`/`bytes` rows, counts `4` cases for each `module_call/sub`, `module_call/subn`, `pattern_call/sub`, and `pattern_call/subn`, and marks the eight new bytes case ids as `pending_rebar_case_ids` because the live `rebar` callable path still raises scaffold `NotImplementedError` for them.
- 2026-03-19: Updated `tests/conformance/test_combined_correctness_scorecards.py` so the combined and nested broader-range scorecard representative-case tables mirror the new bytes rows alongside the existing `str` representatives.
- 2026-03-19: Regenerated the tracked published correctness artifact at `reports/correctness/latest.py`; the tracked report now publishes `1334` total / `1326` passed / `8` `unimplemented` overall across `111` manifests, and `collection.replacement.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference.callable` now publishes `16` total / `8` passed / `8` `unimplemented` with `text_models == ['bytes', 'str']`.
- 2026-03-19: Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py` (`1776 passed, 40 skipped, 1760 subtests passed`), `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_callable_replacement_workflows.py --report .rebar/tmp/rbr-0661-nested-broader-range-wider-ranged-repeat-branch-local-backreference-callable-replacement-bytes.py` (`16` total / `8` passed / `8` `unimplemented`), and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` (`1334` total / `1326` passed / `8` `unimplemented`).
