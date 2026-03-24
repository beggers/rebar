# RBR-1130: Implement conditional group-exists template bytes parity

Status: ready
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Reopen the next exact same-owner replacement follow-on after `RBR-1128` by converting the bounded bytes two-arm conditional group-exists replacement-template workflows into Rust-backed parity before any same-family correctness publication or Python-path benchmark catch-up widens the frontier.

## Pattern Pair
- `rebar.sub(rb"a(b)?c(?(1)d|e)", rb"\\1x", b"zzabcdzz")`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)d|e)").subn(rb"\\g<word>x", b"zzacezz", 1)`

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`

## Acceptance Criteria
- Land the missing bytes replacement-template runtime support for the exact two-arm conditional group-exists owner path in Rust, with Python changes limited to argument normalization, wrapper plumbing, and FFI calls:
  - the numbered module bytes present-capture path `rebar.sub(rb"a(b)?c(?(1)d|e)", rb"\\1x", b"zzabcdzz")` now matches `re.sub(...)` instead of raising the scaffold placeholder;
  - the numbered module bytes absent-capture count path `rebar.subn(rb"a(b)?c(?(1)d|e)", rb"\\1x", b"zzacezz", 1)` now matches CPython by expanding the missing group to `b""` instead of rejecting the bytes template path;
  - the named compiled-pattern bytes present-capture path `rebar.compile(rb"a(?P<word>b)?c(?(word)d|e)").sub(rb"\\g<word>x", b"zzabcdzz")` now matches `re.compile(...).sub(...)`; and
  - the named compiled-pattern bytes absent-capture count path `rebar.compile(rb"a(?P<word>b)?c(?(word)d|e)").subn(rb"\\g<word>x", b"zzacezz", 1)` now matches CPython by keeping the bounded empty named-group expansion on bytes payloads.
- Keep the work on the existing shared replacement owner path in `tests/python/test_fixture_backed_replacement_parity_suite.py` rather than creating a detached parity file, correctness fixture manifest, or benchmark workload:
  - add bounded direct bytes parity coverage for the numbered and named module/pattern `sub()` present-capture workflows on `rb"a(b)?c(?(1)d|e)"` and `rb"a(?P<word>b)?c(?(word)d|e)"`;
  - add bounded direct bytes parity coverage for the matching `subn(count=1)` absent-capture workflows on those same numbered and named patterns, keeping the expected empty `\\1` / `\\g<word>` expansion explicit; and
  - preserve the already-landed `str` conditional replacement-template behavior plus the neighboring mixed-text grouped replacement-template surfaces on the same shared parity file.
- Preserve the existing unsupported boundaries outside this exact slice:
  - do not widen into correctness publication, benchmark manifests, README text, or tracked ops state prose in this run; and
  - leave bytes publication plus benchmark catch-up for `conditional-group-exists-replacement-template-workflows` and `conditional-group-exists-boundary` to later tasks once this exact runtime prerequisite lands.

## Verification
- `cargo build -p rebar-cpython`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'conditional and replacement and bytes'`

## Constraints
- Keep the implementation bounded to the exact bytes two-arm conditional group-exists replacement-template slice above. Leave correctness publication, benchmark catch-up, callable replacements, alternation-heavy arms, nested conditionals, quantified conditionals, and broader template parsing for later tasks.
- New compatibility behavior belongs in Rust. Do not solve this by expanding Python-only fallback execution beyond wrapper plumbing and native entrypoint selection.
- Preserve the current `str` conditional replacement-template behavior and the already-landed mixed-text grouped replacement-template families while widening only the missing bytes conditional slice above.

## Notes
- `RBR-1130` is the next available unreserved feature task id in this checkout:
  - the highest live task id across `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, and `ops/tasks/blocked/` is `1129`; and
  - `rg -n 'RBR-1130' ops/tasks ops/state -g '*.md'` returned no matches in this run before this task was written.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The narrow same-family owner-path scan in this run shows the exact bytes template implementation prerequisite is the surviving post-`RBR-1128` slice:
  - `tests/conformance/fixtures/conditional_group_exists_replacement_template_workflows.py` still defaults to `text_model: "str"` and publishes only the eight exact `str` replacement-template workflows for `a(b)?c(?(1)d|e)` and `a(?P<word>b)?c(?(word)d|e)`;
  - `tests/python/test_fixture_backed_replacement_parity_suite.py` still routes the `conditional-group-exists-replacement` surface through `str_case_pattern` and keeps `conditional-group-exists-replacement-template-workflows` on a `str`-only shared replacement path;
  - `reports/correctness/latest.py` still surfaces `collection.replacement.conditional_group_exists.template.str` with no corresponding `.bytes` suite, while `benchmarks/workloads/conditional_group_exists_boundary.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still keep the adjacent minimal template slice `str`-only; and
  - `python/rebar/__init__.py` still omits `rb"a(b)?c(?(1)d|e)"` and `rb"a(?P<word>b)?c(?(word)d|e)"` from `_NATIVE_TEMPLATE_BYTES_PATTERNS`, confirming the exact bytes template runtime prerequisite is still missing and that a publication-only follow-on would be premature.
