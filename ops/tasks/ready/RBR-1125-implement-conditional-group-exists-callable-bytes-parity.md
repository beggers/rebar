# RBR-1125: Implement conditional group-exists callable bytes parity

Status: ready
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Reopen the next exact callable-replacement owner-path slice after `RBR-1124` by converting the bounded bytes two-arm conditional group-exists callable workflows from scaffold placeholders to Rust-backed parity before any same-family correctness publication or benchmark catch-up widens the frontier.

## Pattern Pair
- `rebar.sub(rb"a(b)?c(?(1)d|e)", lambda m: m.group(1) + b"x", b"zzabcdzz")`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)d|e)").subn(lambda m: m.group("word") + b"x", b"zzacezz", 1)`

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_callable_replacement_parity_suite.py`

## Acceptance Criteria
- Land the missing bytes callable replacement runtime support for the exact two-arm conditional group-exists owner path in Rust, with Python changes limited to argument normalization, wrapper plumbing, and FFI calls:
  - the numbered module bytes present-capture path `rebar.sub(rb"a(b)?c(?(1)d|e)", lambda m: m.group(1) + b"x", b"zzabcdzz")` now matches `re.sub(...)` instead of raising the scaffold placeholder;
  - the numbered module bytes absent-capture count path `rebar.subn(rb"a(b)?c(?(1)d|e)", lambda m: m.group(1) + b"x", b"zzacezz", 1)` now raises the same bounded `TypeError` as CPython when the callback reads the missing group;
  - the named compiled-pattern bytes present-capture path `rebar.compile(rb"a(?P<word>b)?c(?(word)d|e)").sub(lambda m: m.group("word") + b"x", b"zzabcdzz")` now matches `re.compile(...).sub(...)`; and
  - the named compiled-pattern bytes absent-capture count path `rebar.compile(rb"a(?P<word>b)?c(?(word)d|e)").subn(lambda m: m.group("word") + b"x", b"zzacezz", 1)` now raises the same bounded `TypeError` as CPython.
- Keep the work on the existing callable owner path in `tests/python/test_callable_replacement_parity_suite.py` rather than creating a detached parity file, correctness fixture manifest, or benchmark workload:
  - add bounded direct bytes parity coverage for the numbered and named module/pattern `sub()` present-capture workflows on `rb"a(b)?c(?(1)d|e)"` and `rb"a(?P<word>b)?c(?(word)d|e)"`;
  - add bounded direct bytes parity coverage for the matching `subn(count=1)` absent-capture exception workflows on those same numbered and named patterns; and
  - keep the already-landed quantified nested-group callable, quantified nested-group alternation callable, exact branch-local-backreference callable, and quantified branch-local-backreference callable `str` and bytes coverage green on the same file.
- Preserve the existing unsupported boundaries outside this exact slice:
  - do not widen into correctness publication, benchmark manifests, README text, or tracked ops state prose in this run; and
  - keep the already-flagged broader conditional callable bytes follow-ons on the existing shared fixture owner path until later tasks publish them.

## Verification
- `cargo build -p rebar-cpython`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and callable and bytes and module'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and callable and bytes and pattern'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and callable and bytes'`

## Constraints
- Keep the implementation bounded to the exact bytes two-arm conditional group-exists callable slice above. Leave correctness publication, benchmark catch-up, broader conditional callable bytes families, and other callable replacement expansion for later tasks.
- New compatibility behavior belongs in Rust. Do not solve this by expanding Python-only fallback execution beyond the existing wrapper and bridge responsibilities.
- Preserve the current `str` conditional callable behavior and the already-landed bytes callable replacement families while widening only the missing bytes conditional slice above.

## Notes
- `RBR-1125` is the next available unreserved feature task id in this checkout:
  - the highest live task id across `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, and `ops/tasks/blocked/` is `1124`; and
  - `rg -n 'RBR-1125' ops/tasks ops/state -g '*.md'` returned only historical mentions inside prior task notes in this run.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The current head task `RBR-1124` already covers the adjacent quantified branch-local callable benchmark catch-up, so the narrow same-family owner-path scan in this run looked one slice deeper for the surviving post-drain callable frontier and found an implementation prerequisite rather than another publication-only gap:
  - `tests/python/test_callable_replacement_parity_suite.py` still defines `conditional-group-exists-callable-replacement-workflows` with `expected_text_models=STR_ONLY_TEXT_MODELS`, while neighboring callable manifests on the same owner path already require mixed `str`/`bytes`;
  - `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` still defaults to `text_model: "str"` and publishes only the eight exact `str` callable workflows for `a(b)?c(?(1)d|e)` and `a(?P<word>b)?c(?(word)d|e)`;
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and `reports/benchmarks/latest.py` still publish only the `str` callable rows for this exact conditional slice, including the retained `pattern-subn-callable-named-conditional-group-exists-replacement-purged-gap` benchmark anchor; and
  - direct runtime probes in this run showed `rebar.sub(...)`, `rebar.subn(...)`, and the matching compiled-pattern bytes callable paths for those exact conditional patterns still raising scaffold `NotImplementedError`, confirming parity implementation is the next bounded prerequisite before correctness or benchmark catch-up can widen.
