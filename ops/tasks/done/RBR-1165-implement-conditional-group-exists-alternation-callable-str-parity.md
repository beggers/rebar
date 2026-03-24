# RBR-1165: Implement conditional group-exists alternation callable str parity

Status: done
Owner: feature-implementation
Created: 2026-03-24
Completed: 2026-03-24

## Goal
- Reopen the next exact callable-replacement owner-path slice after `RBR-1163` by converting the bounded `str` alternation-heavy conditional group-exists callable workflows from scaffold `NotImplementedError` placeholders to Rust-backed parity before any same-family correctness publication or benchmark catch-up widens this family again.

## Pattern Pair
- `rebar.sub(r"a(b)?c(?(1)(de|df)|(eg|eh))", lambda m: m.group(1) + "x", "zzabcdezz")`
- `rebar.compile(r"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))").subn(lambda m: m.group("word") + "x", "zzacehzz", 1)`

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_callable_replacement_parity_suite.py`

## Acceptance Criteria
- Land the missing `str` callable replacement runtime support for the exact alternation-heavy conditional group-exists owner path in Rust, with Python changes limited to argument normalization, wrapper plumbing, and FFI calls:
  - the numbered module present-first-arm path `rebar.sub(r"a(b)?c(?(1)(de|df)|(eg|eh))", lambda m: m.group(1) + "x", "zzabcdezz")` now matches `re.sub(...)` instead of raising the scaffold placeholder;
  - the numbered module present-second-arm count path `rebar.subn(r"a(b)?c(?(1)(de|df)|(eg|eh))", lambda m: m.group(1) + "x", "zzabcdfzz", 1)` now matches `re.subn(...)`;
  - the numbered compiled-pattern absent-first-arm path `rebar.compile(r"a(b)?c(?(1)(de|df)|(eg|eh))").sub(lambda m: m.group(1) + "x", "zzacegzz")` now matches `re.compile(...).sub(...)`;
  - the numbered compiled-pattern absent-second-arm count path `rebar.compile(r"a(b)?c(?(1)(de|df)|(eg|eh))").subn(lambda m: m.group(1) + "x", "zzacehzz", 1)` now matches `re.compile(...).subn(...)`;
  - the same four module/pattern workflows now also match CPython for the named spelling `r"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))"` with `match.group("word")`.
- Keep the work on the existing callable owner path in `tests/python/test_callable_replacement_parity_suite.py` rather than creating a detached parity file, correctness fixture manifest, or benchmark workload:
  - add bounded direct `str` parity coverage for the numbered and named module/pattern callable `sub()`/`subn()` alternation-heavy workflows above;
  - keep the current simple two-arm conditional callable slice, including the published present, absent-exception, and `count=-1` str/bytes workflows, green on the same file; and
  - do not widen this run into correctness publication, benchmark manifests, bytes alternation-heavy callable mirrors, nested conditional callable follow-ons, quantified conditional callable follow-ons, or broader callback helper shapes beyond `match.group(...) + "x"`.

## Verification
- `cargo build -p rebar-cpython`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py::test_module_callable_replacement_callback_match_objects_match_cpython`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py::test_callable_replacement_cases_stay_aligned_with_published_fixture tests/python/test_callable_replacement_parity_suite.py::test_conditional_group_exists_negative_count_bytes_cases_mirror_str_cases`

## Constraints
- Keep the implementation bounded to the exact `str` alternation-heavy callable conditional slice above. Leave correctness publication, benchmark catch-up, bytes mirrors, nested conditional callable follow-ons, quantified conditional callable follow-ons, and broader callable helper expansion for later tasks.
- New compatibility behavior belongs in Rust. Do not solve this by broadening Python-only fallback execution beyond the existing wrapper and bridge responsibilities.
- Preserve the already-landed simple two-arm conditional callable behavior and surrounding callable replacement families while widening only the missing alternation-heavy conditional callable slice above.

## Notes
- `RBR-1165` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this run; and
  - `rg -n 'RBR-1165' ops/tasks ops/state -g '*.md'` matched only historical mentions inside completed task files, not a live reservation for this id.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest done same-family frontier does not leave another publication-only slice ready after `RBR-1163`; it leaves only broader callable follow-ons, so this planning run performed one narrow same-owner scan of the adjacent conditional replacement path before seeding work:
  - `tests/conformance/fixtures/conditional_group_exists_alternation_replacement_workflows.py` is the smallest neighboring conditional replacement fixture that already pins the full numbered/named module/pattern `str` alternation matrix for `a(b)?c(?(1)(de|df)|(eg|eh))` and `a(?P<word>b)?c(?(word)(de|df)|(eg|eh))`;
  - the adjacent nested and quantified constant-replacement fixtures are broader same-family slices, so alternation-heavy callable support is the first exact missing conditional callable expansion on this owner route; and
  - no adjacent callable correctness fixture or benchmark workload currently publishes this alternation-heavy callable slice.
- Direct runtime probes in this planning run confirmed that this is an implementation prerequisite rather than a publication-only follow-on:
  - `PYTHONPATH=python ./.venv/bin/python` probes for the already-published simple callable slice `a(b)?c(?(1)d|e)` and `a(?P<word>b)?c(?(word)d|e)` matched CPython for both module and compiled-pattern callable replacement paths; but
  - matching probes for `a(b)?c(?(1)(de|df)|(eg|eh))` and `a(?P<word>b)?c(?(word)(de|df)|(eg|eh))` still raised scaffold `NotImplementedError` on this branch for both module and compiled-pattern callable replacement paths, so correctness publication or benchmark catch-up would be premature.
- Acceptance-command validation in this planning run:
  - `cargo build -p rebar-cpython` finished successfully;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py::test_module_callable_replacement_callback_match_objects_match_cpython` returned `224 passed`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py::test_callable_replacement_cases_stay_aligned_with_published_fixture tests/python/test_callable_replacement_parity_suite.py::test_conditional_group_exists_negative_count_bytes_cases_mirror_str_cases` returned `11 passed`; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/feature-planning-conditional-callable-current.py` returned `24 executed / 24 passed`, confirming the current published callable owner path is otherwise stable.

## Completion
- Extended `crates/rebar-cpython/src/lib.rs` so the generic str conditional callable `finditer` bridge falls through from the simple two-arm helper to the already-landed alternation-heavy conditional span discovery helper instead of reporting `unsupported`.
- Added bounded direct parity coverage in `tests/python/test_callable_replacement_parity_suite.py` for the numbered and named alternation-heavy conditional callable `sub()`/`subn()` module and compiled-pattern workflows, including present-arm `match.group(...) + "x"` success paths and absent-arm `TypeError` parity paths.
- Left `python/rebar/__init__.py` unchanged; the existing wrapper/FFI path handled the slice once the native bridge reported support.
- Verification:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists_alternation_callable_replacement'` -> `16 passed`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py::test_module_callable_replacement_callback_match_objects_match_cpython` -> `224 passed`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py::test_callable_replacement_cases_stay_aligned_with_published_fixture tests/python/test_callable_replacement_parity_suite.py::test_conditional_group_exists_negative_count_bytes_cases_mirror_str_cases` -> `11 passed`
- Published scorecards were not republished in this run, so `reports/correctness/latest.py` did not change.
