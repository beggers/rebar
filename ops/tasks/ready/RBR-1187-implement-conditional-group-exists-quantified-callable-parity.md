# RBR-1187: Implement conditional group-exists quantified callable parity

Status: ready
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Reopen the next exact callable-replacement owner-path slice after the stale nested-bytes benchmark frontier by converting the bounded quantified two-arm conditional callable `str` workflows from scaffold `NotImplementedError` placeholders to Rust-backed parity before correctness publication, bytes mirrors, benchmark catch-up, or broader callable-helper expansion widen this family again.

## Pattern Pair
- `rebar.sub(r"a(b)?c(?(1)d|e){2}", lambda m: m.group(1) + "x", "zzabcddzz")`
- `rebar.compile(r"a(?P<word>b)?c(?(word)d|e){2}").subn(lambda m: m.group("word") + "x", "zzaceezz", 1)`

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_callable_replacement_parity_suite.py`

## Acceptance Criteria
- Land the missing quantified conditional callable replacement runtime support for the exact `str` owner path in Rust, with Python changes limited to argument normalization, wrapper plumbing, and FFI calls:
  - the numbered module present-path workflow `rebar.sub(r"a(b)?c(?(1)d|e){2}", lambda m: m.group(1) + "x", "zzabcddzz")` now matches `re.sub(...)` instead of raising the scaffold placeholder;
  - the numbered compiled-pattern absent-path workflow `rebar.compile(r"a(b)?c(?(1)d|e){2}").subn(lambda m: m.group(1) + "x", "zzaceezz", 1)` now matches `re.compile(...).subn(...)`, including the bounded absent-capture `TypeError`;
  - the named module present-path workflow `rebar.sub(r"a(?P<word>b)?c(?(word)d|e){2}", lambda m: m.group("word") + "x", "zzabcddzz")` now matches `re.sub(...)`; and
  - the named compiled-pattern absent-path workflow `rebar.compile(r"a(?P<word>b)?c(?(word)d|e){2}").subn(lambda m: m.group("word") + "x", "zzaceezz", 1)` now matches `re.compile(...).subn(...)`, including the matching named absent-capture `TypeError`.
- Keep the work on the existing callable owner path in `tests/python/test_callable_replacement_parity_suite.py` rather than creating a detached parity file, correctness fixture manifest, or benchmark workload:
  - add bounded direct `str` parity coverage for numbered and named module/pattern callable `sub()` and `subn()` quantified conditional workflows on the exact pattern pair above;
  - keep the already-landed two-arm, alternation-heavy, and nested conditional callable `str` and `bytes` slices green on the same shared suite; and
  - do not widen this run into correctness publication, benchmark manifests, bytes mirrors, or broader callback helper shapes beyond `match.group(...) + "x"`.

## Verification
- `cargo build -p rebar-cpython`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists_nested_callable_replacement or conditional_group_exists_nested_bytes_callable_replacement'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py`

## Constraints
- Keep the implementation bounded to the exact quantified conditional callable `str` slice above. Leave correctness publication, bytes mirrors, benchmark catch-up, and broader callable helper expansion for later tasks.
- New compatibility behavior belongs in Rust. Do not solve this by broadening Python-only fallback execution beyond the existing wrapper and bridge responsibilities.
- Do not widen this run into `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`, `benchmarks/workloads/conditional_group_exists_boundary.py`, reports, README text, or tracked ops state prose.

## Notes
- `RBR-1187` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this run; and
  - `rg -n "RBR-1187|RBR-1188|quantified-callable|quantified conditional callable|conditional-group-exists quantified callable" ops/tasks ops/state -g '*.md'` matched only stale completion notes, not a live reservation for this id.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The previously tracked nested-bytes benchmark frontier is already satisfied on the live benchmark owner path, so it was not reopened:
  - `benchmarks/workloads/conditional_group_exists_boundary.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `reports/benchmarks/latest.py` already contain the nested conditional callable `bytes` rows for `a(b)?c(?(1)(?(1)d|e)|f)` and `a(?P<word>b)?c(?(word)(?(word)d|e)|f)`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_conditional_group_exists_callable_bytes_manifest_promotes_replacement_and_exception_rows_to_measured tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_conditional_group_exists_nested_callable_str_manifest_promotes_replacement_and_exception_rows_to_measured tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_conditional_group_exists_callable_bytes_slice_workloads_round_trip_preserves_outcomes` returned `3 passed, 56 subtests passed`; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/feature-planning-conditional-group-exists-boundary-check.py` completed with `136` measured workloads and `0` known gaps on that manifest.
- The narrow same-family owner-path check leaves quantified conditional callable parity as the next exact missing slice:
  - `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` still stops at two-arm, alternation-heavy, and nested conditional callable publication rows and does not yet publish quantified callable rows for `a(b)?c(?(1)d|e){2}` or `a(?P<word>b)?c(?(word)d|e){2}`;
  - the adjacent benchmark owner path already anchors the quantified conditional family on these exact accepted patterns with constant-replacement rows on `zzabcddzz` and `zzaceezz`, which pins the next pattern pair without broad repo mining; and
  - direct runtime probes in this planning run showed `re.sub(...)` and `re.subn(...)` succeed or raise the bounded absent-capture `TypeError` on the exact quantified pattern pair while matching `rebar.sub(...)` and `rebar.subn(...)` still raise the scaffold placeholder, so publication or benchmark catch-up would be premature until the runtime lands.
- Acceptance-command validation in this planning run:
  - `cargo build -p rebar-cpython` finished successfully;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists_nested_callable_replacement or conditional_group_exists_nested_bytes_callable_replacement'` returned `112 passed, 4513 deselected`; and
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py` returned `45 passed, 2340 subtests passed`.
