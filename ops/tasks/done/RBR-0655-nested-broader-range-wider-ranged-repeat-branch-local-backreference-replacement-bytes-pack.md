# RBR-0655: Publish the nested broader-range wider-ranged-repeat branch-local-backreference replacement-template bytes pair

Status: done
Owner: feature-implementation
Created: 2026-03-19
Completed: 2026-03-19

## Goal
- Extend the existing broader `{1,4}` nested grouped-alternation plus branch-local-backreference replacement-template correctness publication with the exact bytes pair on the shared replacement surface, so the frontier reopens on the tracked correctness path before Rust-backed bytes replacement parity and later Python-path benchmark catch-up land.

## Deliverables
- `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_replacement_workflows.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `tests/conformance/correctness_expectations.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_replacement_workflows.py` remains the only correctness manifest for this slice and grows only by the 8 byte-typed counterparts to the already-published `str` cases for:
  - `rb"a((b|c){1,4})\\2d"` with `rb"\\1x"` or `rb"\\2x"`;
  - `rb"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d"` with `rb"\\g<outer>x"` or `rb"\\g<inner>x"`.
- The added bytes cases stay pinned to the exact broader `{1,4}` replacement-template observations already published for the `str` slice:
  - numbered `module.sub(..., rb"\\1x", b"abbd")`, numbered `module.subn(..., rb"\\2x", b"abbbdaccd", 1)`, numbered compiled `Pattern.sub(rb"\\1x", b"zzabcbccdzz")`, and numbered compiled `Pattern.subn(rb"\\2x", b"zzaccdabcbccdzz", 1)`;
  - named `module.sub(..., rb"\\g<outer>x", b"abcbccd")`, named `module.subn(..., rb"\\g<inner>x", b"abbbdaccd", 1)`, named compiled `Pattern.sub(rb"\\g<outer>x", b"zzacccccdzz")`, and named compiled `Pattern.subn(rb"\\g<inner>x", b"zzacccccdabbbdzz", 1)`.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` keeps the shared replacement bundle contract honest after this manifest becomes mixed `str`/`bytes`, updates this manifest from 8 `str` replacement rows to 16 mixed rows with helper counts growing from `2` to `4` for each of `module_call/sub`, `module_call/subn`, `pattern_call/sub`, and `pattern_call/subn`, and keeps the new bytes rows explicit on the shared suite:
  - if the live `rebar` result still reports placeholder behavior for those bytes rows, keep them visible through the existing shared replacement owner by marking this manifest as a pending-bytes follow-on instead of forcing it through the current `str`-only compile-pattern and supplemental replacement partitions; and
  - if the live `rebar` result already matches CPython for those bytes rows, keep the mixed-text manifest landed without adding a bytes-only replacement suite or another manifest-specific parity module.
- `tests/conformance/correctness_expectations.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1318` total / `1318` passed / `0` `unimplemented` across `111` manifests to `1326` total cases across the same `111` manifests;
  - `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-replacement-workflows` moves from `8` total / `8` passed / `0` `unimplemented` with `['str']` text models to `16` total with mixed `str`/`bytes` coverage; and
  - the new bytes cases are reported honestly as either `pass` or `unimplemented` according to the live `rebar` result rather than being dropped from the published scorecard.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_replacement_workflows.py --report .rebar/tmp/rbr-0655-nested-broader-range-wider-ranged-repeat-branch-local-backreference-replacement-bytes.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement new bytes replacement behavior just to make the new cases pass.
- Do not broaden into bytes parity, bytes benchmark rows, the adjacent conditional or callable replacement flows, another branch-local-backreference family, or deeper grouped execution in this run.
- Keep the future parity follow-on anchored to the existing `tests/python/test_fixture_backed_replacement_parity_suite.py` surface and the later benchmark follow-on on the existing `benchmarks/workloads/nested_group_replacement_boundary.py` path.

## Notes
- `RBR-0655` is the next available feature task id in the current checkout; `RBR-0654` is already occupied by the done architecture cleanup task.
- Queue this directly behind `RBR-0653` so the broader `{1,4}` `str` benchmark catch-up closes before the adjacent non-conditional replacement-template bytes publication reopens correctness work on the shared replacement surface.
- 2026-03-19 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `find ops/tasks -maxdepth 2 -type f | rg 'RBR-0655'` returned no matches before this file was added;
  - `tests/python/test_fixture_backed_replacement_parity_suite.py` currently treats `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-replacement-workflows` as `str`-only with 8 selected case ids and `EXPECTED_OPERATION_HELPER_COUNTS`, while the adjacent broader-range open-ended replacement manifest on the same owner already exercises the mixed-text helper-count and text-model path;
  - `tests/conformance/correctness_expectations.py` and `reports/correctness/latest.py` currently publish this manifest at `8` total / `8` passed / `0` `unimplemented` with `text_models == ['str']`, while the combined report stays at `1318` total / `1318` passed / `0` `unimplemented` across `111` manifests;
  - `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_replacement_workflows.py` currently publishes only the 8 `str` replacement-template rows for this exact slice, so the bytes publication step is still missing rather than a stale no-op; and
  - `benchmarks/workloads/nested_group_replacement_boundary.py` already carries the adjacent broader `{1,4}` callable-replacement `str` rows, and the ready `RBR-0653` task already pins the matching non-callable template `str` rows on that same manifest, so later Python-path benchmark catch-up for the bytes pair can stay on the existing shared owner path without another synthesis pass.
- A later parity follow-on should convert the same bytes pair behind `rebar._rebar` on the existing shared replacement surface before the benchmark surface mirrors the four adjacent broader `{1,4}` non-callable `str` rows already queued by `RBR-0653`.

## Completion Note
- 2026-03-19: Added the exact 8 bytes publication rows to `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_replacement_workflows.py`, keeping the manifest on the shared replacement surface and mirroring the existing `str` case ids, helpers, and observations one-for-one.
- 2026-03-19: Updated `tests/python/test_fixture_backed_replacement_parity_suite.py` so this manifest is now a mixed `str`/`bytes` bundle with `4` helper rows each for `module.sub`, `module.subn`, `Pattern.sub`, and `Pattern.subn`, while the live unimplemented bytes slice stays staged as a pending follow-on on the existing grouped replacement owner instead of being forced through the current `str`-only direct parity buckets.
- 2026-03-19: Updated `tests/conformance/correctness_expectations.py` so the mixed-text manifest keeps explicit bytes representative rows alongside the existing `str` representatives on both the feature scorecard table and the combined table.
- 2026-03-19: Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py` (`1124 passed, 1747 subtests passed in 27.54s`), `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_replacement_workflows.py --report .rebar/tmp/rbr-0655-nested-broader-range-wider-ranged-repeat-branch-local-backreference-replacement-bytes.py` (`16` total / `8` passed / `8` `unimplemented`), and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` (`1326` total / `1318` passed / `8` `unimplemented`).
- 2026-03-19: The tracked published scorecard now reports `collection.replacement.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference` at `16` total / `8` passed / `8` `unimplemented` with `text_models == ['bytes', 'str']`, keeping the new bytes rows visible and honest until `RBR-0657` lands parity.
