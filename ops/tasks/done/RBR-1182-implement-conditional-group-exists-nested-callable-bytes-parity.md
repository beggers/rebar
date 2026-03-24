# RBR-1182: Implement conditional group-exists nested callable bytes parity

Status: done
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Reopen the next exact callable-replacement owner-path slice after `RBR-1181` by converting the bounded bytes nested two-arm conditional callable workflows from scaffold `NotImplementedError` placeholders to Rust-backed parity before any same-family correctness publication, benchmark catch-up, quantified conditional callable follow-ons, or broader callable-helper expansion widen this family again.

## Pattern Pair
- `rebar.sub(rb"a(b)?c(?(1)(?(1)d|e)|f)", lambda m: m.group(1) + b"x", b"zzabcdzz")`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)(?(word)d|e)|f)").subn(lambda m: m.group("word") + b"x", b"zzacfzz", 1)`

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_callable_replacement_parity_suite.py`

## Acceptance Criteria
- Land the missing bytes callable-replacement runtime support for the exact nested conditional owner path in Rust, with Python changes limited to argument normalization, wrapper plumbing, and FFI calls:
  - the numbered module present-path bytes workflow `rebar.sub(rb"a(b)?c(?(1)(?(1)d|e)|f)", lambda m: m.group(1) + b"x", b"zzabcdzz")` now matches `re.sub(...)` instead of raising the scaffold placeholder;
  - the numbered compiled-pattern absent-path bytes workflow `rebar.compile(rb"a(b)?c(?(1)(?(1)d|e)|f)").subn(lambda m: m.group(1) + b"x", b"zzacfzz", 1)` now matches `re.compile(...).subn(...)`, including CPython's bounded absent-capture `TypeError`;
  - the named module present-path bytes workflow `rebar.sub(rb"a(?P<word>b)?c(?(word)(?(word)d|e)|f)", lambda m: m.group("word") + b"x", b"zzabcdzz")` now matches `re.sub(...)`; and
  - the named compiled-pattern absent-path bytes workflow `rebar.compile(rb"a(?P<word>b)?c(?(word)(?(word)d|e)|f)").subn(lambda m: m.group("word") + b"x", b"zzacfzz", 1)` now matches `re.compile(...).subn(...)`, including the matching named absent-capture `TypeError`.
- Keep the work on the existing callable owner path in `tests/python/test_callable_replacement_parity_suite.py` rather than creating a detached parity file, correctness fixture manifest, or benchmark workload:
  - add bounded direct bytes parity coverage for the numbered and named module/pattern callable `sub()` and `subn()` nested conditional workflows above;
  - keep the already-landed simple and alternation-heavy conditional callable bytes slices plus the adjacent nested `str` callable slice green on the same file; and
  - do not widen this run into correctness publication, benchmark manifests, quantified conditional callable follow-ons, or broader callback helper shapes beyond `match.group(...) + b"x"`.

## Verification
- `cargo build -p rebar-cpython`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and bytes and callable_replacement and module'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and bytes and callable_replacement and pattern'`

## Constraints
- Keep the implementation bounded to the exact bytes nested conditional callable slice above. Leave correctness publication, benchmark catch-up, quantified conditional callable follow-ons, and broader callable helper expansion for later tasks.
- New compatibility behavior belongs in Rust. Do not solve this by broadening Python-only fallback execution beyond the existing wrapper and bridge responsibilities.
- Do not widen this run into `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`, `benchmarks/workloads/conditional_group_exists_boundary.py`, reports, README text, or tracked ops state prose.

## Notes
- `RBR-1182` is the next available reserved feature task id in this checkout:
  - `ops/state/backlog.md` already reserved `RBR-1182` for this same bounded bytes nested callable parity slice; and
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this run.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest done same-family frontier leaves this exact bytes implementation slice concrete after `RBR-1181`, and the narrow owner-path check confirms it is still an implementation prerequisite rather than another publication-only follow-on:
  - `ops/tasks/done/RBR-1181-benchmark-conditional-group-exists-nested-callable-str-workloads.md` completed the bounded nested conditional callable `str` benchmark catch-up and explicitly left bytes mirrors plus quantified conditional callable follow-ons for later on this owner path;
  - `tests/python/test_callable_replacement_parity_suite.py` already covers the nested conditional callable `str` module/pattern paths plus adjacent bytes alternation callable paths on the shared callable suite, but it does not yet exercise this exact nested bytes pair;
  - `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` and `reports/correctness/latest.py` still stop at the nested callable `str` publication rows for this spelling; and
  - `benchmarks/workloads/conditional_group_exists_boundary.py` and `reports/benchmarks/latest.py` still measure only the nested callable `str` rows for this spelling, so correctness publication or benchmark catch-up would be premature until the runtime lands.
- Direct public-path probes in this planning run confirmed the missing runtime behavior on the exact bounded bytes slice:
  - `re.sub(rb"a(b)?c(?(1)(?(1)d|e)|f)", lambda m: m.group(1) + b"x", b"zzabcdzz")` returned `b"zzbxzz"` while the matching `rebar.sub(...)` call still raised `NotImplementedError`;
  - `re.subn(rb"a(b)?c(?(1)(?(1)d|e)|f)", lambda m: m.group(1) + b"x", b"zzacfzz", 1)` raised the expected bounded `TypeError` while the matching `rebar.subn(...)` call still raised `NotImplementedError`.
- Acceptance-command validation in this planning run:
  - `cargo build -p rebar-cpython` finished successfully;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and bytes and callable_replacement and module'` returned `32 passed, 4383 deselected`; and
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and bytes and callable_replacement and pattern'` returned `40 passed, 4375 deselected`.

## Completion
- Landed bounded bytes nested conditional callable parity on the native owner path by adding compile acceptance and callable span discovery for `rb"a(b)?c(?(1)(?(1)d|e)|f)"` and `rb"a(?P<word>b)?c(?(word)(?(word)d|e)|f)"` in `crates/rebar-core/src/lib.rs` and wiring the bytes conditional bridge through `crates/rebar-cpython/src/lib.rs`.
- Extended `python/rebar/__init__.py` to allow the exact nested bytes pair through the existing native callable passthrough set.
- Added direct module and compiled-pattern bytes `sub()`/`subn()` parity coverage in `tests/python/test_callable_replacement_parity_suite.py` for present-path replacement results and absent-capture `TypeError` parity on the nested conditional slice.
- Verification in this run:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and bytes and callable_replacement and module'` -> `48 passed, 4399 deselected`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and bytes and callable_replacement and pattern'` -> `56 passed, 4391 deselected`
