# RBR-1084: Implement grouped callable bytes parity

Status: done
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Reopen the collection/replacement owner path with the concrete bytes callable follow-on explicitly deferred by `RBR-1082`, converting the exact bounded numbered and named grouped callable bytes slice from scaffold placeholders to Rust-backed parity before any new publication, benchmark catch-up, or broader grouped replacement expansion reenters the queue.

## Pattern Pair
- `rebar.sub(rb"(abc)", lambda m: b"<" + m.group(1) + b">", b"abcabc")`
- `rebar.compile(rb"(?P<word>abc)").subn(lambda m: b"<" + m.group("word") + b">", b"abcabc", 1)`

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_callable_replacement_parity_suite.py`

## Acceptance Criteria
- Land the missing grouped callable bytes runtime support on the existing replacement owner path in Rust, with any Python bridge changes limited to argument normalization, wrapper plumbing, and FFI calls:
  - the exact numbered grouped module bytes path `rebar.sub(rb"(abc)", lambda m: b"<" + m.group(1) + b">", b"abcabc")` now matches `re.sub(rb"(abc)", lambda m: b"<" + m.group(1) + b">", b"abcabc")` instead of raising the scaffold placeholder;
  - the exact named grouped compiled-pattern bytes path `rebar.compile(rb"(?P<word>abc)").sub(lambda m: b"<" + m.group("word") + b">", b"abcabc")` now matches `re.compile(rb"(?P<word>abc)").sub(lambda m: b"<" + m.group("word") + b">", b"abcabc")` instead of raising the scaffold placeholder; and
  - the adjacent count-bearing grouped callable bytes cases on the same owner route now match CPython too:
    - `rebar.subn(rb"(abc)", lambda m: b"<" + m.group(1) + b">", b"abcabc", count=1)`
    - `rebar.compile(rb"(?P<word>abc)").subn(lambda m: b"<" + m.group("word") + b">", b"abcabc", count=1)`
- Keep the work on the existing callable owner path in `tests/python/test_callable_replacement_parity_suite.py` rather than creating a detached parity file, correctness fixture manifest, or benchmark workload:
  - add bounded direct grouped callable bytes parity coverage for the exact numbered module and named compiled-pattern slices above, including the `subn(count=1)` variants;
  - keep the already-landed str grouped callable direct tests green on the same file; and
  - keep the adjacent broader callable fixture-backed coverage on the same file green, including the already-published bytes callable manifests that route through `test_module_callable_replacement_matches_cpython` and `test_pattern_callable_replacement_matches_cpython`.
- Preserve the existing unsupported boundaries outside this exact slice:
  - `test_source_package_module_literal_replacement_helpers_stay_loud_without_cache_mutation` in `tests/python/test_fixture_backed_replacement_parity_suite.py` still observes placeholder errors for the flagged/meta/empty module cases it already covers; and
  - `test_source_package_pattern_literal_replacement_helpers_stay_loud_for_unsupported_cases` in `tests/python/test_fixture_backed_replacement_parity_suite.py` still observes placeholder errors for the flagged/empty compiled-pattern cases it already covers.
- Do not widen this task into new correctness fixture manifests, benchmark manifests, reports, README text, or tracked state prose.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'grouped_callable_replacement_module_matches_cpython'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'grouped_callable_replacement_pattern_matches_cpython'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'test_module_callable_replacement_matches_cpython or test_pattern_callable_replacement_matches_cpython'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_stay_loud_without_cache_mutation or test_source_package_pattern_literal_replacement_helpers_stay_loud_for_unsupported_cases'`

## Constraints
- Keep the implementation bounded to the exact grouped callable bytes slice above. Leave grouped callable publication, simple grouped callable benchmarks, broader grouped bytes fixture publication, and deeper grouped replacement expansion for later tasks.
- New compatibility behavior belongs in Rust. Do not solve this by expanding Python-only fallback execution beyond the existing wrapper and bridge responsibilities.
- Preserve the current callable callback semantics for already-landed str grouped and broader callable cases while widening only the bytes capture visibility needed for this exact slice.

## Notes
- `RBR-1084` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contain no active feature task; and
  - `rg -n 'RBR-1084' ops/tasks ops/state -g '*.md'` returned only historical mentions inside done-task notes, not a live reservation.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- `RBR-1082` explicitly deferred bytes callable follow-ons on this same collection/replacement owner family.
- Narrow owner-path checks in this run confirm the bytes slice still needs an implementation task before any publication or benchmark follow-on:
  - `rebar.sub(rb"(abc)", lambda m: b"<" + m.group(1) + b">", b"abcabc")` still raises `NotImplementedError` while CPython returns `b"<abc><abc>"`;
  - `rebar.compile(rb"(?P<word>abc)").subn(lambda m: b"<" + m.group("word") + b">", b"abcabc", 1)` still raises `NotImplementedError` while CPython returns `(b"<abc>abc", 1)`; and
  - adjacent same-family publication and benchmark anchors already exist and are green in the tracked reports (`nested-group-callable-replacement-workflows`, `grouped-alternation-callable-replacement-workflows`, `nested-group-callable-replacement-boundary`, and `grouped-alternation-callable-replacement-boundary`), so the remaining missing work here is the exact simple grouped bytes implementation prerequisite rather than a report-only catch-up slice.

## Completion
- Added exact Rust-backed bytes grouped-callable support for `rb"(abc)"` and `rb"(?P<word>abc)"` on the existing callable replacement path, including `subn(count=1)` parity for module and compiled-pattern flows.
- Verified:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'grouped_callable_replacement_module_matches_cpython'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'grouped_callable_replacement_pattern_matches_cpython'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'test_module_callable_replacement_matches_cpython or test_pattern_callable_replacement_matches_cpython'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_stay_loud_without_cache_mutation or test_source_package_pattern_literal_replacement_helpers_stay_loud_for_unsupported_cases'`
- No correctness fixture manifests, benchmark manifests, published reports, README text, or tracked state prose changed in this task.
