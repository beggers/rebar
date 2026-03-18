# RBR-0595: Publish the quantified-alternation branch-local-backreference bytes pair

Status: done
Owner: feature-implementation
Created: 2026-03-18

## Goal
- Extend the existing bounded `{1,2}` quantified-alternation-plus-branch-local-backreference correctness publication with the exact bytes pair on the existing branch-local parity surface, so the frontier reopens on the tracked correctness path before Rust-backed bytes parity and later Python-path benchmark catch-up land.

## Deliverables
- `tests/conformance/fixtures/quantified_alternation_branch_local_backreference_workflows.py`
- `tests/python/test_branch_local_backreference_parity_suite.py`
- `tests/conformance/correctness_expectations.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/quantified_alternation_branch_local_backreference_workflows.py` remains the only correctness manifest for this slice and grows only by the ten byte-typed counterparts to the already-published `str` cases for:
  - `rb"a((b|c)\\2){1,2}d"`
  - `rb"a(?P<outer>(?P<inner>b|c)(?P=inner)){1,2}d"`
- The added bytes cases stay pinned to the exact bounded branch-local observations already published for the `str` slice:
  - numbered compile metadata, module `search()` lower-bound `b`-branch success on `b"zzabbdzz"`, compiled `Pattern.fullmatch()` lower-bound `c`-branch success on `b"accd"`, compiled `Pattern.fullmatch()` second-repetition `b`-branch success on `b"abbbbd"`, and compiled `Pattern.fullmatch()` no-match on `b"abcd"`;
  - named compile metadata, module `search()` lower-bound `c`-branch success on `b"zzaccdzz"`, compiled `Pattern.fullmatch()` second-repetition `c`-branch success on `b"accccd"`, compiled `Pattern.fullmatch()` second-repetition mixed-branch success on `b"abbccd"`, and compiled `Pattern.fullmatch()` no-match on `b"abcd"`.
- `tests/python/test_branch_local_backreference_parity_suite.py` keeps the shared fixture-bundle contract honest after the manifest becomes mixed `str`/`bytes`, updates the quantified-alternation-branch-local-backreference bundle expectations from `2` compile / `2` module / `6` pattern `str` cases to `4` / `4` / `12` with mixed text-model coverage, introduces one direct bytes follow-on anchor for this manifest, and routes the manifest's bytes rows through that anchor instead of silently widening the generic shared buckets.
- The new quantified-alternation branch-local-backreference bytes follow-on anchor in `tests/python/test_branch_local_backreference_parity_suite.py` stays explicitly unsupported for `rebar` pending the later bytes parity follow-on, keeps the lower-bound, second-repetition, mixed-branch, and no-match texts above visible on the parity path, and does not fork a second bytes-only suite.
- `tests/conformance/correctness_expectations.py` and `reports/correctness/latest.py` are regenerated honestly. With the live checkout still lacking this bytes pair behind `rebar._rebar`, the combined report should move from `1224` total / `1224` passed / `0` `unimplemented` across `111` manifests to `1234` / `1224` / `10`, and `match.quantified_alternation_branch_local_backreference` should publish `20` total / `10` passed / `10` `unimplemented` with mixed `str`/`bytes` coverage.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/quantified_alternation_branch_local_backreference_workflows.py --report .rebar/tmp/rbr-0595-quantified-alternation-branch-local-backreference-bytes.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement new bytes runtime behavior just to make the new cases pass.
- Do not broaden into bytes parity, bytes benchmark rows, another quantified-alternation manifest, or another branch-local-backreference family in this run.
- Keep the future parity follow-on anchored to the existing `tests/python/test_branch_local_backreference_parity_suite.py` surface.

## Notes
- Queue this directly behind `RBR-0593` so the conditional bytes benchmark catch-up closes before quantified-alternation branch-local-backreference bytes publication reopens correctness work on the same quantified-alternation family.
- 2026-03-18 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `tests/conformance/fixtures/quantified_alternation_branch_local_backreference_workflows.py` currently contains `10` case ids and `0` bytes rows;
  - `tests/python/test_branch_local_backreference_parity_suite.py` currently treats `quantified-alternation-branch-local-backreference-workflows` as `str`-only and exposes no bytes follow-on anchor;
  - `tests/conformance/correctness_expectations.py` and `reports/correctness/latest.py` currently publish `match.quantified_alternation_branch_local_backreference` at `10` total / `10` passed / `0` `unimplemented` with `text_models == ['str']`, while the combined report stays at `1224` total / `1224` passed / `0` `unimplemented` across `111` manifests;
  - `benchmarks/workloads/quantified_alternation_boundary.py` already publishes the six adjacent `str` benchmark rows for this exact numbered and named pair as `module-search-numbered-quantified-alternation-branch-backref-cold-str`, `module-compile-numbered-quantified-alternation-branch-backref-cold-str`, `pattern-fullmatch-numbered-quantified-alternation-branch-backref-second-repetition-purged-str`, `module-compile-named-quantified-alternation-branch-backref-warm-str`, `module-search-named-quantified-alternation-branch-backref-lower-bound-c-branch-warm-str`, and `pattern-fullmatch-named-quantified-alternation-branch-backref-second-repetition-purged-str`, so a later Python-path benchmark catch-up can mirror those rows without another synthesis pass; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this planning run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`.
- A later parity follow-on should convert the same bytes pair behind `rebar._rebar` on the existing branch-local-backreference parity surface before the benchmark surface mirrors the six adjacent `str` rows already published on `benchmarks/workloads/quantified_alternation_boundary.py`.

## Completion Notes
- 2026-03-18: Extended `tests/conformance/fixtures/quantified_alternation_branch_local_backreference_workflows.py` by exactly ten bytes rows, mirroring the published numbered and named `str` compile/module/pattern observations for the bounded `{1,2}` branch-local-backreference pair without widening into runtime implementation work.
- 2026-03-18: Updated `tests/python/test_branch_local_backreference_parity_suite.py` so the shared fixture-bundle contract now accepts the mixed `str`/`bytes` manifest, the shared compile/module/pattern buckets keep only the supported `str` rows, and one explicit bytes follow-on anchor covers the new rows while remaining `rebar`-unsupported pending the later bytes parity task.
- 2026-03-18: Regenerated `tests/conformance/correctness_expectations.py` expectations and republished `reports/correctness/latest.py`; the tracked report now publishes `match.quantified_alternation_branch_local_backreference` at `20` total / `10` passed / `10` `unimplemented` with `text_models == ['bytes', 'str']`, and the combined report at `1234` total / `1224` passed / `10` `unimplemented` across `111` manifests.
- 2026-03-18 verification:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py` (`303 passed, 14 skipped, 1359 subtests passed in 29.56s`)
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/quantified_alternation_branch_local_backreference_workflows.py --report .rebar/tmp/rbr-0595-quantified-alternation-branch-local-backreference-bytes.py` (`20` total / `10` passed / `10` `unimplemented`)
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` (`1234` total / `1224` passed / `10` `unimplemented`)
