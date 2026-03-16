# RBR-0483: Convert the numbered-backreference grouped-segment search pair to real parity

Status: ready
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Convert the newly published numbered-backreference grouped-segment search pair from honest `unimplemented` correctness debt into real CPython-shaped behavior on the shared `numbered-backreference-workflows` surface, while keeping the work pinned to the exact numbered `str` helper pair already anchored as `module-search-numbered-backreference-segment-cold-gap` and `pattern-search-numbered-backreference-prefix-purged-gap` on `numbered-backreference-boundary`.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_simple_backreference_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `rebar.search("(ab)x\\1", "zzabxabzz")` stops raising the module placeholder and instead matches CPython for the published case `numbered-backreference-segment-module-search-str`, returning a `re.Match`-shaped `rebar.Match` with span `(2, 7)`, `group(0) == "abxab"`, `group(1) == "ab"`, and `groups() == ("ab",)`.
- `rebar.compile("x(ab)\\1")` returns CPython-shaped compile metadata for this exact `str` pattern (`pattern == "x(ab)\\1"`, `flags == 32`, `groups == 1`, and `groupindex == {}`), and `search("zzxababzz")` on that compiled pattern stops raising the pattern placeholder and instead matches CPython for `numbered-backreference-prefix-pattern-search-str` with the same span and capture-group results.
- The new helper semantics live behind the Rust-backed grouped-reference boundary in `rebar._rebar`; any Python changes stay limited to public-surface gating, cache/object integration, and keeping the source-tree shim aligned with the same exact bounded case. Do not satisfy this task by delegating the new behavior to stdlib `re`.
- `tests/python/test_simple_backreference_parity_suite.py` promotes the two published grouped-segment case ids onto the shared simple-backreference parity frontier instead of leaving them behind the temporary publication-only exclusion added by `RBR-0481`:
  - the new ids stay visible through the existing fixture/frontier inventory checks;
  - the direct module-helper and compiled-pattern parity parametrizations cover them; and
  - direct match-group-access and convenience-API coverage exercises `group(1)` and `groups()` on those exact successful hits without broadening into named grouped-segment backreferences, branch-local backreferences, alternation, or replacement work.
- `reports/correctness/latest.py` is regenerated honestly. With `RBR-0481` landed first, the combined report should stay at `967` total cases across `107` manifests and return to `967` passes / `0` failures / `0` published `unimplemented` outcomes, while the shared `match.numbered_backreference` suite should move from `5` total / `3` passed / `2` unimplemented to `5` total / `5` passed / `0` unimplemented.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_simple_backreference_parity_suite.py tests/python/test_fixture_parity_support_contract.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/numbered_backreference_workflows.py --report .rebar/tmp/rbr-0483-numbered-backreference.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task scoped to the exact numbered `str` `search()` pair on patterns `"(ab)x\\1"` and `"x(ab)\\1"`. Do not broaden into named grouped-segment backreferences, `match()` / `fullmatch()`, replacements, branch-local backreferences, alternation, or conditional groups.
- Leave `tests/conformance/fixtures/numbered_backreference_workflows.py`, `tests/conformance/correctness_expectations.py`, `benchmarks/workloads/numbered_backreference_boundary.py`, `tests/benchmarks/`, and `reports/benchmarks/latest.py` unchanged in this run; the paired source-tree benchmark refresh is the explicit follow-on once this exact helper pair is live.
- Preserve the current simpler numbered-backreference slice `(ab)\\1`. This task should carry adjacent literal-segment behavior through the existing numbered-backreference helper path rather than widen compile acceptance for unrelated grouped-reference patterns.

## Notes
- `RBR-0481` should land immediately ahead of this task and publish the exact cases `numbered-backreference-segment-module-search-str` and `numbered-backreference-prefix-pattern-search-str` on `tests/conformance/fixtures/numbered_backreference_workflows.py`.
- 2026-03-16 planning probe: CPython reports that `re.search("(ab)x\\1", "zzabxabzz")` returns a match with span `(2, 7)`, `group(0) == "abxab"`, `group(1) == "ab"`, and `groups() == ("ab",)`, while `re.compile("x(ab)\\1").search("zzxababzz")` returns a match with the same span and capture payload.
- 2026-03-16 planning probe: before `RBR-0481`, the current checkout still exposes only the simpler `(ab)\\1` numbered-backreference cases on `numbered-backreference-workflows`, and the grouped-segment helpers `rebar.search("(ab)x\\1", "zzabxabzz")` and `rebar.compile("x(ab)\\1").search("zzxababzz")` still raise the scaffold placeholder instead of matching.
- 2026-03-16 planning probe: the adjacent benchmark rows `module-search-numbered-backreference-segment-cold-gap` and `pattern-search-numbered-backreference-prefix-purged-gap` already exist on `benchmarks/workloads/numbered_backreference_boundary.py` and still publish as explicit source-tree known gaps in `reports/benchmarks/latest.py`; they should stay untouched here and become the benchmark catch-up target immediately after parity lands.
