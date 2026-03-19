# RBR-0657: Convert the nested broader-range wider-ranged-repeat branch-local-backreference replacement-template bytes pair to real parity

Status: done
Owner: feature-implementation
Created: 2026-03-19
Completed: 2026-03-19

## Goal
- Convert the exact broader `{1,4}` nested grouped-alternation plus branch-local-backreference replacement-template bytes pair that the adjacent correctness publication slice adds from honest `unimplemented` outcomes into Rust-backed behavior on the existing shared replacement parity surface, without widening into benchmark catch-up, callable replacement, or another grouped frontier.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The exact bytes replacement-template workflows on the shared correctness surface stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` `sub()` / `subn()` flows using:
  - `rb"a((b|c){1,4})\\2d"` with `rb"\\1x"` or `rb"\\2x"`;
  - `rb"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d"` with `rb"\\g<outer>x"` or `rb"\\g<inner>x"`.
- The shared replacement follow-on surface becomes real parity coverage instead of a pending-bytes slice:
  - numbered `module.sub(..., rb"\\1x", b"abbd")` and `module.subn(..., rb"\\2x", b"abbbdaccd", 1)` match CPython;
  - numbered compiled `Pattern.sub(rb"\\1x", b"zzabcbccdzz")` and `Pattern.subn(rb"\\2x", b"zzaccdabcbccdzz", 1)` match CPython;
  - named `module.sub(..., rb"\\g<outer>x", b"abcbccd")` and `module.subn(..., rb"\\g<inner>x", b"abbbdaccd", 1)` match CPython; and
  - named compiled `Pattern.sub(rb"\\g<outer>x", b"zzacccccdzz")` and `Pattern.subn(rb"\\g<inner>x", b"zzacccccdabbbdzz", 1)` match CPython.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` keeps those bytes rows on the existing shared replacement suite but drops the pending-bytes follow-on behavior for this broader `{1,4}` manifest; do not fork a second bytes-only suite, another fixture path, or a manifest-local test shim.
- Any new parsing, repeated-span collection, template expansion, or replacement execution semantics live behind `rebar._rebar`; Python changes stay limited to public-surface marshalling, cache/object plumbing, template argument handling, and native result marshalling.
- `reports/correctness/latest.py` is regenerated honestly. Building on the mixed-text publication state expected after `RBR-0655`, the combined report should move from `1326` total / `1318` passed / `8` `unimplemented` across `111` manifests to `1326` / `1326` / `0`, and `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-replacement-workflows` should move from `16` total / `8` passed / `8` `unimplemented` to `16` / `16` / `0` with mixed `str`/`bytes` coverage.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_replacement_workflows.py --report .rebar/tmp/rbr-0657-nested-broader-range-wider-ranged-repeat-branch-local-backreference-replacement-bytes-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the implementation bounded to the bytes pair published by `RBR-0655`. Do not broaden into benchmark rows, callable replacements, broader template parsing, deeper grouped execution, another branch-local-backreference family, or stdlib delegation.
- Reuse the existing shared replacement parity suite and correctness fixture. Do not create another bytes-only correctness manifest, another parity suite, or another benchmark family in this run.
- Keep this slice Rust-backed, not Python-only.

## Notes
- `RBR-0657` is the next available feature task id in the current checkout; `RBR-0656` is already occupied by the done architecture cleanup task in `ops/tasks/done/`.
- Build on `RBR-0655`.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` already carries the matching `str` replacement-template bundle for `a((b|c){1,4})\\2d` and `a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d`, so this bytes parity slice can stay on the existing shared suite once `RBR-0655` lands instead of inventing another test path.
- `benchmarks/workloads/nested_group_replacement_boundary.py` already publishes the four adjacent `str` benchmark rows for this exact slice as `module-sub-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str`, `module-subn-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str`, `pattern-sub-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-str`, and `pattern-subn-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-str`, so a later Python-path benchmark catch-up can mirror those rows without another synthesis pass.
- 2026-03-19 feature-planning probes confirm this follow-on is concrete from the tracked frontier:
  - the ready `RBR-0655` task already pins the exact patterns, replacement templates, haystacks, and shared replacement owner path for the eight bytes rows this parity slice needs to convert;
  - `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_replacement_workflows.py` currently still contains only the 8 `str` rows, and `tests/python/test_fixture_backed_replacement_parity_suite.py` still treats this manifest as `str`-only with 8 selected case ids and the default `EXPECTED_OPERATION_HELPER_COUNTS`, so `RBR-0655` remains the immediate publication head rather than a stale no-op;
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this planning run still raise `NotImplementedError` for all eight target bytes workflows at `rebar.sub(...)`, `rebar.subn(...)`, `rebar.compile(...)`, `rebar.Pattern.sub(...)`, and `rebar.Pattern.subn(...)`, so the Rust-backed bytes parity work is not already satisfied in the current checkout; and
  - `reports/correctness/latest.py` currently publishes `1318` total / `1318` passed / `0` `unimplemented` across `111` manifests, with `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-replacement-workflows` still at `8` total / `8` passed / `0` `unimplemented` and `['str']` coverage, so `RBR-0655` is the bounded step that will widen this owner to the expected mixed `16`-case publication before this parity slice clears the new bytes rows.
- A later benchmark follow-on should catch the same bytes pair up on the existing `benchmarks/workloads/nested_group_replacement_boundary.py` surface before deeper grouped execution broadens that family.

## Completion Note
- 2026-03-19: Wired the broader `{1,4}` numbered and named bytes replacement-template pair through the native replacement path by allowing those two bytes patterns through the Python template passthrough gate, adding the missing Rust bytes span collector for this exact slice, and teaching the CPython bridge to use it for template expansion.
- 2026-03-19: Updated the shared replacement parity suite so this manifest is fully mixed-text on the existing owner instead of staging bytes as a pending follow-on, and refreshed the published bytes fixture notes so the regenerated scorecard no longer describes these rows as still queued behind `RBR-0657`.
- 2026-03-19: Verified with `cargo build -p rebar-cpython`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py` (`1160 passed, 1747 subtests passed in 27.33s`), and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_replacement_workflows.py --report .rebar/tmp/rbr-0657-nested-broader-range-wider-ranged-repeat-branch-local-backreference-replacement-bytes-parity.py` (`16` total / `16` passed / `0` `unimplemented`).
- 2026-03-19: Regenerated the tracked published correctness scorecard with `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`; the tracked artifact now reports `1326` total / `1326` passed / `0` `unimplemented` overall, and `collection.replacement.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference` at `16` total / `16` passed / `0` `unimplemented` with `text_models == ['bytes', 'str']`.
