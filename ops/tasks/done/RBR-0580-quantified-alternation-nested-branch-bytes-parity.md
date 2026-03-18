# RBR-0580: Convert the quantified-alternation nested-branch bytes pair to real parity

Status: done
Owner: feature-implementation
Created: 2026-03-18

## Goal
- Convert the exact bounded `{1,2}` quantified-alternation nested-branch bytes pair from honest `unimplemented` outcomes into Rust-backed behavior on the existing quantified-alternation parity surface, without widening into benchmark catch-up or another bytes frontier.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_quantified_alternation_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `rebar.compile(rb"a((b|c)|de){1,2}d")` and `rebar.compile(rb"a(?P<word>(b|c)|de){1,2}d")` no longer raise the scaffold placeholder; compile metadata and visible `word` capture details match CPython through the public `rebar` API.
- The direct bytes follow-on anchor on `tests/python/test_quantified_alternation_parity_suite.py` becomes real parity coverage instead of a `rebar`-only unsupported follow-on:
  - numbered `module.search()` matches CPython for the lower-bound inner-branch hit `b"zzabdzz"`;
  - numbered compiled `Pattern.fullmatch()` matches CPython for the lower-bound literal-branch success `b"aded"`, the second-repetition mixed-branches success `b"abded"`, and the no-match `b"abde"`;
  - named `module.search()` matches CPython for the lower-bound literal-branch hit `b"zzadedzz"`;
  - named compiled `Pattern.fullmatch()` matches CPython for the lower-bound inner-branch success `b"acd"`, the second-repetition mixed-branches success `b"adebd"`, and the no-match `b"adeb"`.
- `tests/python/test_quantified_alternation_parity_suite.py` keeps that direct bytes anchor on the existing quantified-alternation suite but drops the current `rebar` unsupported gating for these two patterns; do not fork a second bytes-only suite or fixture path.
- Any new parsing or execution semantics live behind `rebar._rebar`; Python changes stay limited to public-surface marshalling, cache/object plumbing, and native result handling.
- `reports/correctness/latest.py` is regenerated honestly. Building on the publication state expected after the nested-branch bytes pack lands, the combined report should move from `1200` total / `1190` passed / `10` `unimplemented` across `111` manifests to `1200` / `1200` / `0`, and `match.quantified_alternation_nested_branch` should move from `20` total / `10` passed / `10` `unimplemented` to `20` / `20` / `0` with mixed `str`/`bytes` coverage.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/quantified_alternation_nested_branch_workflows.py --report .rebar/tmp/rbr-0580-quantified-alternation-nested-branch-bytes-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the implementation bounded to the published bytes pair. Do not broaden into benchmark rows, bounded quantified-alternation bytes work, broader-range quantified-alternation bytes work, open-ended quantified-alternation bytes work, conditional bytes work, branch-local-backreference bytes work, backtracking-heavy bytes work, or another bytes family.
- Reuse the existing parity suite and correctness fixture. Do not create another bytes-only correctness manifest, another parity suite, or another benchmark family in this run.
- Keep this slice Rust-backed, not Python-only.

## Notes
- Build on `RBR-0578`.
- 2026-03-18 feature-planning probes confirm this follow-on is concrete from the tracked frontier:
  - `ops/tasks/ready/RBR-0578-quantified-alternation-nested-branch-bytes-pack.md` already pins the exact ten bytes fixture rows, the direct bytes follow-on surface on `tests/python/test_quantified_alternation_parity_suite.py`, and the post-pack scorecard target for this same numbered and named bytes pair;
  - `tests/conformance/fixtures/quantified_alternation_nested_branch_workflows.py` currently contains `10` case ids and `0` bytes rows, while `tests/python/test_quantified_alternation_parity_suite.py` still keeps the nested-branch bundle at `2` compile / `2` module / `6` pattern `str` cases with no nested-branch bytes follow-on anchor yet, so the Rust-backed parity work is still sequenced behind the publication task;
  - `benchmarks/workloads/quantified_alternation_boundary.py` already publishes the six adjacent nested-branch `str` benchmark rows for this exact pair, so a later Python-path benchmark catch-up can mirror those rows without another synthesis pass; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this planning run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`, so the Rust-backed bytes parity work is not already satisfied in the current checkout.
- A later benchmark follow-on should catch the same bytes pair up on the existing quantified-alternation benchmark surface before another quantified-alternation bytes family broadens the frontier.

## Completion
- Added a bounded bytes nested-branch path in `crates/rebar-core/src/lib.rs`, so `rebar._rebar` now compiles and executes `rb"a((b|c)|de){1,2}d"` and `rb"a(?P<word>(b|c)|de){1,2}d"` with CPython-matching group metadata, group spans, and `lastindex`/`lastgroup` behavior.
- Updated `tests/python/test_quantified_alternation_parity_suite.py` so the existing nested-branch bytes follow-on anchor now runs against `rebar` instead of marking that pair unsupported.
- Regenerated `reports/correctness/latest.py`; the tracked combined scorecard now publishes `1200` total / `1200` passed / `0` unimplemented cases, and `match.quantified_alternation_nested_branch` now publishes `20` total / `20` passed / `0` unimplemented cases.
- Verified with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/quantified_alternation_nested_branch_workflows.py --report .rebar/tmp/rbr-0580-quantified-alternation-nested-branch-bytes-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
