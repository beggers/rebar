# RBR-1193: Implement conditional group-exists quantified callable bytes parity

Status: done
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Reopen the next exact callable-replacement owner-path slice after `RBR-1191` by converting the bounded quantified conditional callable `bytes` workflows from scaffold `NotImplementedError` placeholders to Rust-backed parity before same-family correctness publication, benchmark catch-up, or broader callable-helper expansion widen this family again.

## Pattern Pair
- `rebar.sub(rb"a(b)?c(?(1)d|e){2}", lambda m: m.group(1) + b"x", b"zzabcddzz")`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)d|e){2}").subn(lambda m: m.group("word") + b"x", b"zzaceezz", 1)`

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_callable_replacement_parity_suite.py`

## Acceptance Criteria
- Land the missing quantified conditional callable replacement runtime support for the exact `bytes` owner path in Rust, with Python changes limited to argument normalization, wrapper plumbing, and FFI calls:
  - the numbered module present-path bytes workflow `rebar.sub(rb"a(b)?c(?(1)d|e){2}", lambda m: m.group(1) + b"x", b"zzabcddzz")` now matches `re.sub(...)` instead of raising the scaffold placeholder;
  - the numbered compiled-pattern absent-path bytes workflow `rebar.compile(rb"a(b)?c(?(1)d|e){2}").subn(lambda m: m.group(1) + b"x", b"zzaceezz", 1)` now matches `re.compile(...).subn(...)`, including CPython's bounded absent-capture `TypeError`;
  - the named module present-path bytes workflow `rebar.sub(rb"a(?P<word>b)?c(?(word)d|e){2}", lambda m: m.group("word") + b"x", b"zzabcddzz")` now matches `re.sub(...)`; and
  - the named compiled-pattern absent-path bytes workflow `rebar.compile(rb"a(?P<word>b)?c(?(word)d|e){2}").subn(lambda m: m.group("word") + b"x", b"zzaceezz", 1)` now matches `re.compile(...).subn(...)`, including the matching named absent-capture `TypeError`.
- Keep the work on the existing callable owner path in `tests/python/test_callable_replacement_parity_suite.py` rather than creating a detached parity file, correctness fixture manifest, or benchmark workload:
  - add bounded direct `bytes` parity coverage for numbered and named module/pattern callable `sub()` and `subn()` quantified conditional workflows on the exact pattern pair above;
  - keep the already-landed two-arm, alternation-heavy, and nested conditional callable `bytes` slices green on the same shared suite; and
  - do not widen this run into correctness publication, benchmark manifests, or broader callback helper shapes beyond `match.group(...) + b"x"`.

## Verification
- `cargo build -p rebar-cpython`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and bytes and callable_replacement and module'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and bytes and callable_replacement and pattern'`

## Constraints
- Keep the implementation bounded to the exact quantified conditional callable `bytes` slice above. Leave correctness publication, benchmark catch-up, and broader callable helper expansion for later tasks.
- New compatibility behavior belongs in Rust. Do not solve this by broadening Python-only fallback execution beyond the existing wrapper and bridge responsibilities.
- Do not widen this run into `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`, `benchmarks/workloads/conditional_group_exists_boundary.py`, reports, README text, or tracked ops state prose.

## Notes
- `RBR-1193` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this run; and
  - `rg -n "RBR-1193|RBR-1194" ops/tasks ops/state -g '*.md'` returned no live reservation for either id in this checkout.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest done same-family frontier leaves this exact `bytes` implementation slice concrete after `RBR-1191`, and the narrow owner-path check confirms it is still an implementation prerequisite rather than a publication-only follow-on:
  - `ops/tasks/done/RBR-1191-benchmark-conditional-group-exists-quantified-callable-str-workloads.md` completed the bounded quantified conditional callable `str` benchmark catch-up and explicitly left quantified `bytes` mirrors plus broader callable-helper expansion for later on this owner path;
  - `tests/python/test_callable_replacement_parity_suite.py` still exposes quantified conditional callable direct parity only for `str`, while `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` and `benchmarks/workloads/conditional_group_exists_boundary.py` already anchor the exact quantified numbered and named accepted patterns on the adjacent correctness and benchmark owner paths for later publication;
  - direct public-path probes in this planning run showed `re.sub(...)` and `re.compile(...).subn(...)` on `rb"a(b)?c(?(1)d|e){2}"` and `rb"a(?P<word>b)?c(?(word)d|e){2}"` return the bounded success or `TypeError` outcomes while matching `rebar.sub(...)`, `rebar.subn(...)`, and compiled-entrypoint calls still raise scaffold `NotImplementedError`; and
  - because the runtime is still missing on the exact pattern pair, correctness publication or Python-path benchmark catch-up would be premature until this parity task lands.
- Acceptance-command validation in this planning run:
  - `cargo build -p rebar-cpython` finished successfully;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and bytes and callable_replacement and module'` returned `56 passed, 4719 deselected`; and
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and bytes and callable_replacement and pattern'` returned `64 passed, 4711 deselected`.

## Completion
- Landed bounded quantified conditional callable `bytes` parity on the native owner path by adding compile acceptance plus callable span discovery for `rb"a(b)?c(?(1)d|e){2}"` and `rb"a(?P<word>b)?c(?(word)d|e){2}"` in `/home/ubuntu/rebar/crates/rebar-core/src/lib.rs`, then routing the bytes conditional bridge through `/home/ubuntu/rebar/crates/rebar-cpython/src/lib.rs`.
- Extended `/home/ubuntu/rebar/python/rebar/__init__.py` to allow the exact quantified bytes pair through the existing native callable passthrough set.
- Added direct module and compiled-pattern bytes `sub()`/`subn()` parity coverage in `/home/ubuntu/rebar/tests/python/test_callable_replacement_parity_suite.py` for present-path replacement results and absent-capture `TypeError` parity on the quantified conditional slice.
- Verification in this run:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and bytes and callable_replacement and module'` -> `72 passed, 4735 deselected`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and bytes and callable_replacement and pattern'` -> `80 passed, 4727 deselected`
