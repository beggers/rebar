# RBR-0471: Convert the IGNORECASE|ASCII literal helper pair to real parity

Status: ready
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Convert the newly published `IGNORECASE|ASCII` literal helper pair from honest `unimplemented` correctness debt into real CPython-shaped behavior on the shared `literal-flag-workflows` surface, while keeping the work pinned to the exact `str`-valued `search()` pair already anchored as known gaps on `literal-flag-boundary`.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_literal_flag_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `rebar.search("abc", "ABC", rebar.IGNORECASE | rebar.ASCII)` stops raising the module placeholder and instead matches CPython for the published case `flag-module-search-ignorecase-ascii-str-hit`, returning a `re.Match`-shaped `rebar.Match` with span `(0, 3)` and `group(0) == "ABC"`.
- `rebar.compile("abc", rebar.IGNORECASE | rebar.ASCII)` keeps the already-published compile metadata for this exact `str` literal (`pattern == "abc"`, `flags == 258`, `groups == 0`, and `groupindex == {}`), and `search("ABC")` on that compiled pattern stops raising the pattern placeholder and instead matches CPython for `flag-pattern-search-ignorecase-ascii-str-hit` with span `(0, 3)`.
- The new workflow semantics live behind the Rust-backed literal-match boundary in `rebar._rebar`; any Python changes stay limited to public-surface gating, cache/object integration, and keeping the source-tree shim aligned with the same exact bounded case. Do not satisfy this task by delegating the new behavior to stdlib `re`.
- `tests/python/test_literal_flag_parity_suite.py` promotes the two published ASCII case ids onto the shared literal-flag parity frontier instead of leaving them behind the temporary placeholder-only guard:
  - the new ids are added to `TARGET_FIXTURE_CASE_IDS`, the selected-case bundle expectations, and the direct test buckets; and
  - the module and compiled-pattern parity parametrizations cover them directly, while `flag-unsupported-nonliteral-ignorecase-search` remains the only delegated literal-flag case.
- The focused placeholder coverage in `tests/python/test_literal_flag_parity_suite.py` stops expecting `NotImplementedError` for the exact `IGNORECASE|ASCII` helper pair but continues to keep unrelated unsupported flag slices, such as the existing non-literal `findall()` debt, loud and honest.
- `reports/correctness/latest.py` is regenerated honestly. With `RBR-0468` landed first, the combined report should stay at `963` total cases across `107` manifests and return to `963` passes / `0` failures / `0` published `unimplemented` outcomes, while the shared `literal.flag.workflow` suite should move from `13` total / `11` passed / `2` unimplemented to `13` total / `13` passed / `0` unimplemented.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_literal_flag_parity_suite.py tests/conformance/test_correctness_fixture_inventory_contract.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/literal_flag_workflows.py --report .rebar/tmp/rbr-0471-literal-flags.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task scoped to the exact published `str` literal helper pair on `search()`. Do not broaden into `match()`/`fullmatch()`, bytes `ASCII`, collection or replacement helpers, inline-flag combinations, non-literal metacharacter cases, or general flag-combination support.
- Leave `tests/conformance/fixtures/literal_flag_workflows.py`, `tests/conformance/correctness_expectations.py`, `benchmarks/workloads/literal_flag_boundary.py`, `tests/benchmarks/`, and `reports/benchmarks/latest.py` unchanged in this run; the paired source-tree benchmark refresh is the explicit follow-on once this exact helper pair is live.
- Preserve the current compile-surface behavior for this literal pattern. This task should carry the already-supported compile metadata through the helper execution path rather than widening compile acceptance for other ASCII-flag combinations.

## Notes
- `RBR-0468` should land immediately ahead of this task and publish the exact cases `flag-module-search-ignorecase-ascii-str-hit` and `flag-pattern-search-ignorecase-ascii-str-hit` on `tests/conformance/fixtures/literal_flag_workflows.py`.
- 2026-03-16 planning probe: in the current checkout, CPython reports `re.compile("abc", re.IGNORECASE | re.ASCII).flags == 258`, `groups == 0`, and `groupindex == {}`, and both `re.search("abc", "ABC", re.IGNORECASE | re.ASCII)` and the compiled-pattern `search("ABC")` return a match with span `(0, 3)`.
- 2026-03-16 planning probe: `rebar.compile("abc", rebar.IGNORECASE | rebar.ASCII)` already returns compile metadata with `flags == 258`, `groups == 0`, and `groupindex == {}`, but `rebar.search("abc", "ABC", rebar.IGNORECASE | rebar.ASCII)` still raises `NotImplementedError: rebar.search() is a scaffold placeholder; the \`re\`-compatible API is not implemented yet` and `rebar.compile("abc", rebar.IGNORECASE | rebar.ASCII).search("ABC")` still raises `NotImplementedError: rebar.Pattern.search() is a scaffold placeholder; compiled pattern semantics are not implemented yet`.
- 2026-03-16 planning probe: the adjacent benchmark rows `module-search-ignorecase-ascii-cold-gap` and `pattern-search-ignorecase-ascii-warm-gap` already exist on `benchmarks/workloads/literal_flag_boundary.py` and still publish as explicit source-tree known gaps in `reports/benchmarks/latest.py`; they should stay untouched here and become the benchmark catch-up target immediately after parity lands.
