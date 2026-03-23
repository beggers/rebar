# RBR-1095: Implement nested-group callable bytes parity

Status: done
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Reopen the next adjacent callable-replacement owner path after `RBR-1092` by converting the exact bounded nested-group bytes callable slice from scaffold placeholders to Rust-backed parity before any correctness publication, benchmark catch-up, or broader grouped callable replacement expansion reenters the queue.

## Pattern Pair
- `rebar.sub(rb"a((b))d", lambda m: b"<" + m.group(1) + b">", b"abdabd")`
- `rebar.compile(rb"a(?P<outer>(?P<inner>b))d").subn(lambda m: b"<" + m.group("inner") + b">", b"abdabd", 1)`

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_callable_replacement_parity_suite.py`

## Acceptance Criteria
- Land the missing nested-group callable bytes runtime support on the existing replacement owner path in Rust, with any Python bridge changes limited to argument normalization, wrapper plumbing, and FFI calls:
  - the exact numbered nested-group module bytes path `rebar.sub(rb"a((b))d", lambda m: b"<" + m.group(1) + b">", b"abdabd")` now matches `re.sub(rb"a((b))d", lambda m: b"<" + m.group(1) + b">", b"abdabd")` instead of raising the scaffold placeholder;
  - the exact named nested-group compiled-pattern bytes path `rebar.compile(rb"a(?P<outer>(?P<inner>b))d").sub(lambda m: b"<" + m.group("outer") + b">", b"abdabd")` now matches `re.compile(rb"a(?P<outer>(?P<inner>b))d").sub(lambda m: b"<" + m.group("outer") + b">", b"abdabd")` instead of raising the scaffold placeholder; and
  - the adjacent count-bearing nested-group callable bytes cases on the same owner route now match CPython too:
    - `rebar.subn(rb"a((b))d", lambda m: b"<" + m.group(2) + b">", b"abdabd", count=1)`
    - `rebar.compile(rb"a(?P<outer>(?P<inner>b))d").subn(lambda m: b"<" + m.group("inner") + b">", b"abdabd", count=1)`
- Keep the work on the existing callable owner path in `tests/python/test_callable_replacement_parity_suite.py` rather than creating a detached parity file, correctness fixture manifest, or benchmark workload:
  - add bounded direct nested-group callable bytes parity coverage for the exact numbered module and named compiled-pattern slices above, including the `subn(count=1)` variants;
  - keep the already-landed simple grouped callable str and bytes direct tests green on the same file; and
  - keep the adjacent broader fixture-backed callable coverage on the same file green without widening into new correctness publication or benchmark rows in this run.
- Preserve the existing unsupported boundaries outside this exact slice:
  - `test_source_package_module_literal_replacement_helpers_stay_loud_without_cache_mutation` in `tests/python/test_fixture_backed_replacement_parity_suite.py` still observes placeholder errors for the flagged/meta/empty module cases it already covers; and
  - `test_source_package_pattern_literal_replacement_helpers_stay_loud_for_unsupported_cases` in `tests/python/test_fixture_backed_replacement_parity_suite.py` still observes placeholder errors for the flagged/empty compiled-pattern cases it already covers.
- Do not widen this task into correctness fixture publication, benchmark manifests, reports, README text, or tracked state prose.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'nested_group and callable and bytes and module'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'nested_group and callable and bytes and pattern'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'grouped_callable_replacement_module_matches_cpython or grouped_callable_replacement_pattern_matches_cpython or test_module_callable_replacement_matches_cpython or test_pattern_callable_replacement_matches_cpython'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_stay_loud_without_cache_mutation or test_source_package_pattern_literal_replacement_helpers_stay_loud_for_unsupported_cases'`

## Constraints
- Keep the implementation bounded to the exact nested-group callable bytes slice above. Leave correctness publication, benchmark catch-up, grouped alternation follow-ons, and broader nested callable replacement expansion for later tasks.
- New compatibility behavior belongs in Rust. Do not solve this by expanding Python-only fallback execution beyond the existing wrapper and bridge responsibilities.
- Preserve the current callable callback semantics for the already-landed simple grouped callable slice while widening only the bytes nested-group capture visibility needed for this exact follow-on.

## Notes
- `RBR-1095` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/done/` currently runs through `RBR-1094`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contain no live feature task file; and
  - `rg -n 'RBR-1095|RBR-1096|RBR-1097' ops/tasks ops/state -g '*.md'` returned no live reservation in this run.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- `RBR-1092` explicitly left broader grouped callable replacement expansion for later work on this same owner family, and the first adjacent omitted slice on that owner path is the bounded nested-group bytes callable implementation prerequisite.
- Narrow owner-path checks in this run confirm that publication or benchmark catch-up would be premature and that the missing work is the exact nested-group bytes implementation slice instead:
  - `tests/conformance/fixtures/nested_group_callable_replacement_workflows.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `reports/correctness/latest.py` still publish only the str rows for `nested-group-callable-replacement-workflows`, with no `module-sub-callable-nested-group-numbered-bytes`, `module-subn-callable-nested-group-numbered-bytes`, `pattern-sub-callable-nested-group-named-bytes`, or `pattern-subn-callable-nested-group-named-bytes` ids;
  - `benchmarks/workloads/nested_group_callable_replacement_boundary.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `reports/benchmarks/latest.py` likewise contain no adjacent bytes workload ids for the simple nested-group callable slice on that existing benchmark owner path;
  - an exact `.venv` public-path probe showed `rebar.sub(rb"a((b))d", lambda m: b"<" + m.group(1) + b">", b"abdabd")` still raises `NotImplementedError: rebar.sub() is a scaffold placeholder; the \`re\`-compatible API is not implemented yet`; and
  - the already-landed simple grouped callable slice still matches CPython on the same `.venv` public path, including `tests/python/test_callable_replacement_parity_suite.py -k 'grouped_callable_replacement_module_matches_cpython or grouped_callable_replacement_pattern_matches_cpython'`, so the next bounded missing work is this exact nested-group bytes implementation prerequisite rather than another report-only catch-up task.

## Completion Note
- Added exact bytes nested-capture support on the callable replacement owner path in Rust and exposed it through the PyO3 boundary so `rb"a((b))d"` and `rb"a(?P<outer>(?P<inner>b))d"` now reach Rust-backed callable `sub()`/`subn()` parity instead of the scaffold placeholder.
- Extended `tests/python/test_callable_replacement_parity_suite.py` with the bounded direct module and compiled-pattern bytes callback cases that read `group(1)`, `group(2)`, `group("outer")`, and `group("inner")`, and kept the existing grouped-callable and unsupported-loud boundaries green.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'nested_group and callable and bytes and module'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'nested_group and callable and bytes and pattern'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'grouped_callable_replacement_module_matches_cpython or grouped_callable_replacement_pattern_matches_cpython or test_module_callable_replacement_matches_cpython or test_pattern_callable_replacement_matches_cpython'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_stay_loud_without_cache_mutation or test_source_package_pattern_literal_replacement_helpers_stay_loud_for_unsupported_cases'`
