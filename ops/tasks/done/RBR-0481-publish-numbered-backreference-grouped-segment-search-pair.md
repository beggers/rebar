# RBR-0481: Publish the numbered-backreference grouped-segment search pair on the shared numbered-backreference correctness surface

Status: done
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Extend the published correctness scorecard with the exact numbered-backreference grouped-segment search pair already exposed as explicit source-tree benchmark gaps on `numbered-backreference-boundary`, while keeping the work on the ordinary `numbered-backreference-workflows` correctness path before Rust-backed parity or benchmark catch-up revisit those broader grouped-reference shapes.

## Deliverables
- `tests/conformance/fixtures/numbered_backreference_workflows.py`
- `tests/conformance/correctness_expectations.py`
- `tests/python/test_simple_backreference_parity_suite.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/numbered_backreference_workflows.py` grows only by the minimal two numbered `str` workflow cases needed to publish the exact grouped-segment pair already anchored on the benchmark surface:
  - `numbered-backreference-segment-module-search-str` for `rebar.search("(ab)x\\1", "zzabxabzz")`
  - `numbered-backreference-prefix-pattern-search-str` for `rebar.compile("x(ab)\\1").search("zzxababzz")`
- Keep both new cases pinned to the existing `numbered-backreference-workflows` correctness surface. Do not create a new correctness manifest, do not add named variants, and do not broaden into alternation, conditional, nested, or replacement backreference work in this run.
- `tests/python/test_simple_backreference_parity_suite.py` and `tests/python/test_fixture_parity_support_contract.py` keep the published frontier contract honest for the new grouped-segment pair without pretending that direct parity already exists:
  - the new case ids are visible through the existing simple-backreference fixture inventory and whole-manifest contract checks; and
  - until real support lands, they stay out of the direct search-result and supplemental-miss parametrizations that currently require successful `rebar` numbered-backreference behavior.
- `tests/conformance/correctness_expectations.py` updates the `numbered-backreference-workflows` representative-case set so both new grouped-segment case ids stay visible in the combined publication instead of landing as unpublished tail cases.
- `reports/correctness/latest.py` is regenerated honestly. With the current checkout still raising scaffold placeholders for both exact grouped-segment backreference helpers, the combined report should move from `965` total cases / `965` passes / `0` unimplemented to `967` total cases / `965` passes / `2` unimplemented while keeping `0` explicit failures and `107` manifests, and the shared `match.numbered_backreference` suite should move from `3` total / `3` passed / `0` unimplemented to `5` total / `3` passed / `2` unimplemented.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_simple_backreference_parity_suite.py tests/python/test_fixture_parity_support_contract.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/numbered_backreference_workflows.py --report .rebar/tmp/rbr-0481-numbered-backreference.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement grouped-segment numbered-backreference helper behavior, do not touch `benchmarks/workloads/numbered_backreference_boundary.py`, `tests/benchmarks/`, or `reports/benchmarks/latest.py`, and do not broaden into named grouped-segment backreferences or branch-local backreference support.
- Keep the work anchored to the exact existing benchmark gap pair. This task should make those two helpers visible as honest correctness debt, not rename or replace the benchmark rows that already track them.

## Notes
- `RBR-0479` should land immediately ahead of this task and clear the unrelated grouped-segment leading-capture benchmark pair from `grouped-named-boundary`, leaving this numbered-backreference grouped-segment publication slice as the concrete surviving follow-on in the ready queue.
- 2026-03-16 planning probe: the tracked benchmark manifest `benchmarks/workloads/numbered_backreference_boundary.py` already carries the exact gap rows `module-search-numbered-backreference-segment-cold-gap` and `pattern-search-numbered-backreference-prefix-purged-gap`, pinned to patterns `"(ab)x\\1"` and `"x(ab)\\1"` with haystacks `"zzabxabzz"` and `"zzxababzz"`.
- 2026-03-16 planning probe: in the current checkout, CPython reports that `re.search("(ab)x\\1", "zzabxabzz")` returns a match with span `(2, 7)`, `group(0) == "abxab"`, `group(1) == "ab"`, and `groups() == ("ab",)`, while `re.compile("x(ab)\\1").search("zzxababzz")` returns a match with span `(2, 7)`, `group(0) == "xabab"`, `group(1) == "ab"`, and `groups() == ("ab",)`.
- 2026-03-16 planning probe: in the current checkout, `rebar.search("(ab)x\\1", "zzabxabzz")` and `rebar.compile("x(ab)\\1").search("zzxababzz")` both still raise `NotImplementedError: rebar.compile() is a scaffold placeholder; the \`re\`-compatible API is not implemented yet`.
- The immediate follow-on after this publication should stay on the same exact pair: first Rust-backed parity for the published grouped-segment numbered-backreference helpers, then source-tree benchmark catch-up against the already-existing `numbered-backreference-boundary` gap rows.

## Completion
- 2026-03-16: Added the exact publication-only grouped-segment numbered-backreference search pair to `tests/conformance/fixtures/numbered_backreference_workflows.py` and kept both ids visible in `tests/conformance/correctness_expectations.py` without widening the manifest beyond the requested two `str` cases.
- 2026-03-16: Updated `tests/python/test_simple_backreference_parity_suite.py` and `tests/python/test_fixture_parity_support_contract.py` so the whole-manifest inventory and contract checks see the new ids, while direct search-result and supplemental-miss parametrizations still stay limited to the already-supported numbered-backreference search pair.
- 2026-03-16: Republished `reports/correctness/latest.py`; the tracked combined scorecard now reads `967` total cases / `965` passed / `0` failed / `2` unimplemented, and `match.numbered_backreference` now reads `5` total / `3` passed / `0` failed / `2` unimplemented.
- 2026-03-16: Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_simple_backreference_parity_suite.py tests/python/test_fixture_parity_support_contract.py tests/conformance/test_combined_correctness_scorecards.py` (`121 passed, 1057 subtests passed in 25.27s`), `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/numbered_backreference_workflows.py --report .rebar/tmp/rbr-0481-numbered-backreference.py` (`5` total / `3` passed / `2` unimplemented), and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` (`967` total / `965` passed / `2` unimplemented).
