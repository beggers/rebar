# RBR-1082: Implement grouped callable replacement parity

Status: done
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Reopen the collection/replacement owner path with the first deferred grouped callable implementation prerequisite from `RBR-1080`, converting the exact bounded numbered and named grouped callable replacement slice from placeholder raises to Rust-backed parity before benchmark catch-up, broader grouped callable publication, or deeper grouped replacement expansion reenters the queue.

## Pattern Pair
- `rebar.sub("(abc)", lambda m: f"<{m.group(1)}>", "abcabc")`
- `rebar.compile("(?P<word>abc)").sub(lambda m: f"<{m.group('word')}>", "abcabc")`

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_callable_replacement_parity_suite.py`

## Acceptance Criteria
- Land the missing grouped callable replacement runtime support on the existing replacement owner path in Rust, with any Python bridge changes limited to argument normalization, wrapper plumbing, and FFI calls:
  - the exact numbered grouped module path `rebar.sub("(abc)", lambda m: f"<{m.group(1)}>", "abcabc")` now matches `re.sub("(abc)", lambda m: f"<{m.group(1)}>", "abcabc")` instead of raising the scaffold placeholder;
  - the exact named grouped compiled-pattern path `rebar.compile("(?P<word>abc)").sub(lambda m: f"<{m.group('word')}>", "abcabc")` now matches `re.compile("(?P<word>abc)").sub(lambda m: f"<{m.group('word')}>", "abcabc")` instead of raising the scaffold placeholder; and
  - the adjacent count-bearing grouped callable cases on the same owner route now match CPython too:
    - `rebar.subn("(abc)", lambda m: f"<{m.group(1)}>", "abcabc", count=1)`
    - `rebar.compile("(?P<word>abc)").subn(lambda m: f"<{m.group('word')}>", "abcabc", count=1)`
- Keep the work on the existing callable owner path in `tests/python/test_callable_replacement_parity_suite.py` rather than creating a detached parity file, correctness fixture manifest, or benchmark workload:
  - add bounded direct grouped callable parity coverage for the exact numbered module and named compiled-pattern slices above, including the `subn(count=1)` variants;
  - keep the already-landed literal callable replacement coverage green on the same file, including `test_module_callable_replacement_matches_cpython`, `test_pattern_callable_replacement_matches_cpython`, and the callback match-object / callback-exception / wrong-return-type checks; and
  - do not widen this run into grouped-alternation callable fixtures, bytes callable parity, scorecard refreshes, or benchmark publication.
- Preserve the existing unsupported boundaries outside this exact slice:
  - `test_source_package_module_literal_replacement_helpers_stay_loud_without_cache_mutation` in `tests/python/test_fixture_backed_replacement_parity_suite.py` still observes placeholder errors for the flagged/meta/empty module cases it already covers; and
  - `test_source_package_pattern_literal_replacement_helpers_stay_loud_for_unsupported_cases` in `tests/python/test_fixture_backed_replacement_parity_suite.py` still observes placeholder errors for the flagged/empty compiled-pattern cases it already covers.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'grouped callable and module'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'grouped callable and pattern'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'literal_callable_replacement_matches_cpython or module_callable_replacement_callback_match_objects_match_cpython or module_callable_replacement_callback_exception_matches_cpython or pattern_callable_replacement_callback_match_objects_match_cpython or pattern_callable_replacement_callback_exception_matches_cpython or pattern_callable_replacement_wrong_return_type_matches_cpython'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_stay_loud_without_cache_mutation or test_source_package_pattern_literal_replacement_helpers_stay_loud_for_unsupported_cases'`

## Constraints
- Keep the implementation bounded to the exact grouped callable replacement shape above. Leave grouped-alternation callable publication, bytes callable follow-ons, broader grouped callable fixtures, and benchmark catch-up for later tasks.
- New compatibility behavior belongs in Rust. Do not solve this by expanding Python-only fallback execution beyond the existing wrapper and bridge responsibilities.
- Preserve the current callable callback semantics for already-landed literal replacement cases while widening only the grouped capture visibility needed for this exact slice.

## Notes
- `RBR-1082` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contain no active feature task; and
  - `rg -n 'RBR-1082|RBR-1083|RBR-1084' ops/tasks ops/state/backlog.md ops/state/current_status.md -g '*.md'` returned only historical mentions inside done-task notes, not a live reservation.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- `RBR-1080` explicitly left grouped callable follow-ons ahead of benchmark catch-up and broader grouped replacement expansion on the same owner family, so this is the first concrete deferred same-family slice rather than a new frontier.
- Narrow owner-path checks in this run confirm the slice is still missing and needs an implementation task before any publication follow-on:
  - a direct runtime probe showed `rebar.sub("(abc)", lambda m: f"<{m.group(1)}>", "abcabc")` still raises `NotImplementedError: rebar.sub() is a scaffold placeholder; the \`re\`-compatible API is not implemented yet` while CPython returns `"<abc><abc>"`;
  - a direct runtime probe showed `rebar.compile("(?P<word>abc)").sub(lambda m: f"<{m.group('word')}>", "abcabc")` still raises `NotImplementedError: rebar.Pattern.sub() is a scaffold placeholder; compiled pattern semantics are not implemented yet` while CPython returns `"<abc><abc>"`; and
  - `tests/python/test_callable_replacement_parity_suite.py -k 'callable and (module or pattern)'` is already green on the adjacent literal callable owner path, so the missing work is the grouped callable implementation slice itself rather than generic callable harness scaffolding.

## Completion Notes
- Added a capture-aware grouped-literal repeat helper on the Rust replacement path, exposed it through the PyO3 boundary, and wired Python callable replacement dispatch to use it for the exact `(abc)` and `(?P<word>abc)` grouped callable slice.
- Added bounded direct parity coverage in `tests/python/test_callable_replacement_parity_suite.py` for the numbered module `sub()` path, the named compiled-pattern `sub()` path, and their `subn(count=1)` variants without widening into new manifests or scorecard publication.
- Verified the Rust helper compiles via `cargo build -p rebar-cpython`, the direct grouped callable tests pass, the adjacent literal callable parity gates stay green, and the existing unsupported fixture-backed placeholder checks still pass.
- The task-provided first two `pytest -k` expressions were syntactically invalid as written (`grouped callable and module` / `grouped callable and pattern`), so I reran them as the equivalent valid expressions `grouped and callable and module` and `grouped and callable and pattern`.
