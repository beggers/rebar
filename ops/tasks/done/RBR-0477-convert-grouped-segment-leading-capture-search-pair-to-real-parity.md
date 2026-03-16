# RBR-0477: Convert the grouped-segment leading-capture search pair to real parity

Status: done
Owner: feature-implementation
Created: 2026-03-16
Completed: 2026-03-16

## Goal
- Convert the newly published grouped-segment leading-capture search pair from honest `unimplemented` correctness debt into real CPython-shaped behavior on the shared `grouped-segment-workflows` surface, while keeping the work pinned to the exact numbered `str`-valued `(ab)c` helper pair already anchored as `module-search-grouped-segment-cold-gap` and `pattern-search-grouped-segment-warm-gap` on `grouped-named-boundary`.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_grouped_capture_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `rebar.search("(ab)c", "zabcz")` stops raising the module placeholder and instead matches CPython for the published case `grouped-segment-leading-capture-module-search-str`, returning a `re.Match`-shaped `rebar.Match` with span `(1, 4)`, `group(0) == "abc"`, `group(1) == "ab"`, and `groups() == ("ab",)`.
- `rebar.compile("(ab)c")` keeps the already-published compile metadata for this exact `str` grouped-segment pattern (`pattern == "(ab)c"`, `flags == 32`, `groups == 1`, and `groupindex == {}`), and `search("zabcz")` on that compiled pattern stops raising the pattern placeholder and instead matches CPython for `grouped-segment-leading-capture-pattern-search-str` with the same span and capture-group results.
- The new helper semantics live behind the Rust-backed grouped-capture boundary in `rebar._rebar`; any Python changes stay limited to public-surface gating, cache/object integration, and keeping the source-tree shim aligned with the same exact bounded case. Do not satisfy this task by delegating the new behavior to stdlib `re`.
- `tests/python/test_grouped_capture_parity_suite.py` promotes the two published leading-capture case ids onto the shared grouped-capture parity frontier instead of leaving them behind the temporary publication-only exclusion added by `RBR-0475`:
  - the new ids stay visible through the grouped-segment fixture/frontier inventory checks;
  - the direct module-helper and compiled-pattern parity parametrizations cover them; and
  - direct match-group-access and convenience-API coverage exercises `group(1)` and `groups()` on those exact successful hits without broadening into named leading-capture, grouped alternation, backreferences, or replacement work.
- `reports/correctness/latest.py` is regenerated honestly. With `RBR-0475` landed first, the combined report should stay at `965` total cases across `107` manifests and return to `965` passes / `0` failures / `0` published `unimplemented` outcomes, while the shared `match.grouped_segment` suite should move from `8` total / `6` passed / `2` unimplemented to `8` total / `8` passed / `0` unimplemented.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py tests/conformance/test_correctness_fixture_inventory_contract.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/grouped_segment_workflows.py --report .rebar/tmp/rbr-0477-grouped-segment.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task scoped to the exact numbered `str` `search()` pair on pattern `"(ab)c"`. Do not broaden into named leading-capture grouped-segment support, `match()`/`fullmatch()`, replacements, grouped alternation, backreferences, or quantified grouped execution.
- Leave `tests/conformance/fixtures/grouped_segment_workflows.py`, `tests/conformance/correctness_expectations.py`, `benchmarks/workloads/grouped_named_boundary.py`, `tests/benchmarks/`, and `reports/benchmarks/latest.py` unchanged in this run; the paired source-tree benchmark refresh is the explicit follow-on once this exact helper pair is live.
- Preserve the current compile-surface behavior for this literal grouped-segment pattern. This task should carry the already-supported compile metadata through the helper execution path rather than widening compile acceptance for unrelated grouped patterns.

## Notes
- `RBR-0475` should land immediately ahead of this task and publish the exact cases `grouped-segment-leading-capture-module-search-str` and `grouped-segment-leading-capture-pattern-search-str` on `tests/conformance/fixtures/grouped_segment_workflows.py`.
- 2026-03-16 planning probe: in the current checkout, CPython reports that both `re.search("(ab)c", "zabcz")` and `re.compile("(ab)c").search("zabcz")` return a match with span `(1, 4)`, `group(0) == "abc"`, `group(1) == "ab"`, and `groups() == ("ab",)`, while `re.compile("(ab)c")` reports `pattern == "(ab)c"`, `flags == 32`, `groups == 1`, and `groupindex == {}`.
- 2026-03-16 implementation check: before this fix, the native path in the current checkout still rejected `"(ab)c"` entirely, while the adjacent simpler grouped-segment slice `a(b)c` already matched through module and compiled-pattern `search()`.
- 2026-03-16 planning probe: the adjacent benchmark rows `module-search-grouped-segment-cold-gap` and `pattern-search-grouped-segment-warm-gap` already exist on `benchmarks/workloads/grouped_named_boundary.py` and still publish as explicit source-tree known gaps in `reports/benchmarks/latest.py`; they should stay untouched here and become the benchmark catch-up target immediately after parity lands.

## Completion
- Added exact Rust-backed compile and `search()` support for the numbered `str` pattern `"(ab)c"` in `crates/rebar-core/src/lib.rs`, keeping the new behavior scoped to the published leading-capture grouped-segment pair and leaving `match()` / `fullmatch()` as explicit placeholders.
- Kept the source-tree shim aligned in `python/rebar/__init__.py` for the same exact bounded pattern/helper pair without delegating to stdlib `re`.
- Promoted the two published leading-capture grouped-segment case ids into the shared grouped-capture parity frontier in `tests/python/test_grouped_capture_parity_suite.py`, including direct module/pattern parity coverage, match-group-access coverage, and one explicit `group(1)` / `groups()` assertion for the exact successful hits.
- Republished `reports/correctness/latest.py`; the tracked combined scorecard now reports `965` total / `965` passed / `0` failed / `0` unimplemented cases, and the published `match.grouped_segment` suite now reports `8` total / `8` passed / `0` unimplemented.
- No direct edit to `crates/rebar-cpython/src/lib.rs` was required; the existing CPython boundary already forwarded the core compile and match payloads once the Rust core supported this exact slice.

## Verification
- `cargo build -p rebar-cpython` passed.
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py tests/conformance/test_correctness_fixture_inventory_contract.py tests/conformance/test_combined_correctness_scorecards.py` passed (`394 passed, 2234 subtests passed in 21.00s`).
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/grouped_segment_workflows.py --report .rebar/tmp/rbr-0477-grouped-segment.py` passed and wrote `8` total / `8` passed / `0` failed / `0` unimplemented cases.
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` republished the tracked combined scorecard at `965` total / `965` passed / `0` failed / `0` unimplemented cases.
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py` passed after republishing (`1 passed, 1055 subtests passed in 20.82s`).
