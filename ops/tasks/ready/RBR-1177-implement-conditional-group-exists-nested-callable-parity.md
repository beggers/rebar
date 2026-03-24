# RBR-1177: Implement conditional group-exists nested callable parity

Status: ready
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Reopen the next exact callable-replacement owner-path slice after `RBR-1175` by converting the bounded nested two-arm conditional callable workflows from scaffold `NotImplementedError` placeholders to Rust-backed parity before any same-family correctness publication, benchmark catch-up, quantified conditional callable follow-ons, or broader callable-helper expansion widen this family again.

## Pattern Pair
- `rebar.sub(r"a(b)?c(?(1)(?(1)d|e)|f)", lambda m: m.group(1) + "x", "zzabcdzz")`
- `rebar.compile(r"a(?P<word>b)?c(?(word)(?(word)d|e)|f)").subn(lambda m: m.group("word") + "x", "zzacfzz", 1)`

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_callable_replacement_parity_suite.py`

## Acceptance Criteria
- Land the missing nested conditional callable replacement runtime support for the exact `str` owner path in Rust, with Python changes limited to argument normalization, wrapper plumbing, and FFI calls:
  - the numbered module present-path `rebar.sub(r"a(b)?c(?(1)(?(1)d|e)|f)", lambda m: m.group(1) + "x", "zzabcdzz")` now matches `re.sub(...)` instead of raising the scaffold placeholder;
  - the numbered compiled-pattern absent-path `rebar.compile(r"a(b)?c(?(1)(?(1)d|e)|f)").subn(lambda m: m.group(1) + "x", "zzacfzz", 1)` now matches `re.compile(...).subn(...)`, including CPython's bounded absent-capture `TypeError`;
  - the named module present-path `rebar.sub(r"a(?P<word>b)?c(?(word)(?(word)d|e)|f)", lambda m: m.group("word") + "x", "zzabcdzz")` now matches `re.sub(...)`; and
  - the named compiled-pattern absent-path `rebar.compile(r"a(?P<word>b)?c(?(word)(?(word)d|e)|f)").subn(lambda m: m.group("word") + "x", "zzacfzz", 1)` now matches `re.compile(...).subn(...)`, including the matching named absent-capture `TypeError`.
- Keep the work on the existing callable owner path in `tests/python/test_callable_replacement_parity_suite.py` rather than creating a detached parity file, correctness fixture manifest, or benchmark workload:
  - add bounded direct parity coverage for the numbered and named module/pattern callable `sub()` and `subn()` nested conditional workflows above;
  - cover both present-capture success and absent-capture `TypeError` observations across the bounded numbered and named matrix that a follow-on correctness publication would need on this same owner path; and
  - keep the already-landed simple and alternation-heavy conditional callable slices green on the same file.
- Keep the slice pinned to the current nested conditional owner-path frontier:
  - do not widen this run into correctness publication, benchmark manifests, bytes mirrors, quantified conditional callable follow-ons, or broader callback helper shapes beyond `match.group(...) + "x"`;
  - reuse the existing nested conditional spellings already anchored by the adjacent conditional replacement and benchmark owner paths instead of introducing another conditional family; and
  - preserve the current behavior of the surrounding callable-replacement suite outside this bounded nested conditional slice.

## Verification
- `cargo build -p rebar-cpython`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py::test_conditional_group_exists_alternation_callable_replacement_group_access_matches_cpython tests/python/test_callable_replacement_parity_suite.py::test_conditional_group_exists_alternation_callable_replacement_absent_capture_typeerror_matches_cpython`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py::CorrectnessScorecardRegistryContractTest::test_mixed_text_feature_scorecards_mirror_representative_bytes_rows tests/conformance/test_combined_correctness_scorecards.py::CorrectnessScorecardRegistryContractTest::test_combined_scorecard_mixed_text_manifests_cover_both_representative_text_models`

## Constraints
- Keep the implementation bounded to the exact nested conditional callable `str` slice above. Leave correctness publication, benchmark catch-up, bytes mirrors, quantified conditional callable follow-ons, and broader callable helper expansion for later tasks.
- New compatibility behavior belongs in Rust. Do not solve this by broadening Python-only fallback execution beyond the existing wrapper and bridge responsibilities.
- Do not widen this run into `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`, `benchmarks/workloads/conditional_group_exists_boundary.py`, reports, README text, or tracked ops state prose.

## Notes
- `RBR-1177` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this run; and
  - `rg -n "RBR-1177|nested conditional callable|conditional-group-exists.*nested.*callable" ops/tasks ops/state -g '*.md'` matched only historical mentions inside completed task files, not a live reservation for this id.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest done same-family frontier leaves this exact implementation slice concrete after `RBR-1175`:
  - `ops/tasks/done/RBR-1175-benchmark-conditional-group-exists-alternation-callable-bytes-workloads.md` completed the bounded bytes benchmark catch-up and explicitly left nested conditional callable follow-ons and quantified conditional callable follow-ons for later on this owner path;
  - the adjacent owner-path files already pin the next exact nested spellings as `a(b)?c(?(1)(?(1)d|e)|f)` and `a(?P<word>b)?c(?(word)(?(word)d|e)|f)` in `tests/conformance/fixtures/conditional_group_exists_nested_replacement_workflows.py` and `benchmarks/workloads/conditional_group_exists_boundary.py`, while the quantified `a(b)?c(?(1)d|e){2}` slice remains the next later same-family follow-on instead of the immediate frontier;
  - `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` is still the only conditional callable publication manifest in this checkout, so the next bounded callable follow-on should stay on that owner path rather than inventing a new callable family; and
  - direct runtime probes in this planning run showed the exact nested conditional module and compiled-pattern calls above still raise scaffold `NotImplementedError` on `rebar` while CPython either succeeds on the present-arm paths or raises the expected bounded `TypeError` on the absent-capture paths, so correctness publication or benchmark catch-up would be premature until the runtime lands.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists_alternation_callable_replacement_group_access_matches_cpython or conditional_group_exists_alternation_callable_replacement_absent_capture_typeerror_matches_cpython or conditional_group_exists_alternation_bytes_callable_replacement_group_access_matches_cpython or conditional_group_exists_alternation_bytes_callable_replacement_absent_capture_typeerror_matches_cpython'` returned `64 passed, 4186 deselected`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py::CorrectnessScorecardRegistryContractTest::test_mixed_text_feature_scorecards_mirror_representative_bytes_rows tests/conformance/test_combined_correctness_scorecards.py::CorrectnessScorecardRegistryContractTest::test_combined_scorecard_mixed_text_manifests_cover_both_representative_text_models` returned `2 passed, 51 subtests passed`; and
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... PY` direct probes showed `rebar.sub(...)` / `rebar.compile(...).subn(...)` still raise scaffold `NotImplementedError` for both exact nested conditional spellings above while `re` already returns `zzbxzz` on the present paths and the expected `TypeError` on the absent-capture paths.
