# RBR-1120: Implement quantified nested-group alternation branch-local-backreference callable bytes parity

Status: ready
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Reopen the next adjacent callable-replacement owner path after `RBR-1118` by converting the exact bounded quantified nested-group alternation plus same-branch backreference bytes callable slice from scaffold placeholders to Rust-backed parity before any same-family correctness publication, benchmark catch-up, or broader callable-replacement expansion reenters the queue.

## Pattern Pair
- `rebar.sub(rb"a((b|c)+)\2d", lambda m: m.group(1) + b"x", b"abbd")`
- `rebar.compile(rb"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d").subn(lambda m: b"<" + m.group("inner") + b">", b"abbbdaccd", 1)`

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_callable_replacement_parity_suite.py`

## Acceptance Criteria
- Land the missing quantified nested-group alternation plus same-branch backreference bytes callable runtime support on the existing replacement owner path in Rust, with any Python bridge changes limited to argument normalization, wrapper plumbing, and FFI calls:
  - the exact numbered module bytes path `rebar.sub(rb"a((b|c)+)\2d", lambda m: m.group(1) + b"x", b"abbd")` now matches `re.sub(rb"a((b|c)+)\2d", lambda m: m.group(1) + b"x", b"abbd")` instead of raising the scaffold placeholder;
  - the exact numbered count-bearing module bytes path `rebar.subn(rb"a((b|c)+)\2d", lambda m: b"<" + m.group(2) + b">", b"abbbdaccd", 1)` now matches CPython on the same bounded repeated-branch first-match-only slice;
  - the exact named compiled-pattern bytes path `rebar.compile(rb"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d").sub(lambda m: m.group("outer") + b"x", b"accd")` now matches `re.compile(rb"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d").sub(lambda m: m.group("outer") + b"x", b"accd")` instead of raising the scaffold placeholder; and
  - the exact named compiled-pattern count-bearing bytes path `rebar.compile(rb"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d").subn(lambda m: b"<" + m.group("inner") + b">", b"abbbdaccd", 1)` now matches CPython on that same bounded first-match-only slice.
- Keep the work on the existing callable owner path in `tests/python/test_callable_replacement_parity_suite.py` rather than creating a detached parity file, correctness fixture manifest, or benchmark workload:
  - add bounded direct quantified nested-group alternation plus branch-local-backreference callable bytes parity coverage for the exact numbered module/pattern and named module/pattern slices above, including the `subn(count=1)` variants;
  - keep the already-landed grouped, nested-group, quantified nested-group, quantified nested-group alternation, and exact nested-group alternation branch-local-backreference callable `str` and bytes coverage green on the same file; and
  - do not widen into correctness publication, benchmark manifests, reports, README text, or tracked ops state prose in this run.
- Preserve the existing unsupported boundaries outside this exact slice:
  - `test_source_package_module_literal_replacement_helpers_stay_loud_without_cache_mutation` in `tests/python/test_fixture_backed_replacement_parity_suite.py` still observes placeholder errors for the flagged/meta/empty module cases it already covers; and
  - `test_source_package_pattern_literal_replacement_helpers_stay_loud_for_unsupported_cases` in `tests/python/test_fixture_backed_replacement_parity_suite.py` still observes placeholder errors for the flagged/empty compiled-pattern cases it already covers.

## Verification
- `cargo build -p rebar-cpython`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'quantified_nested_group_alternation_branch_local_backreference and callable and bytes and module'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'quantified_nested_group_alternation_branch_local_backreference and callable and bytes and pattern'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'quantified_nested_group_alternation_branch_local_backreference and callable'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_stay_loud_without_cache_mutation or test_source_package_pattern_literal_replacement_helpers_stay_loud_for_unsupported_cases'`

## Constraints
- Keep the implementation bounded to the exact quantified nested-group alternation plus same-branch backreference bytes callable slice above. Leave correctness publication, benchmark catch-up, broader counted repeats, and deeper callable-replacement expansion for later tasks.
- New compatibility behavior belongs in Rust. Do not solve this by expanding Python-only fallback execution beyond the existing wrapper and bridge responsibilities.
- Preserve the current callable callback semantics for the already-landed quantified nested-group alternation and exact branch-local-backreference families while widening only the bytes quantified branch-local capture visibility needed for this exact follow-on.

## Notes
- `RBR-1120` is the next available unreserved feature task id in this checkout:
  - the highest live task id across `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, and `ops/tasks/blocked/` is `1119`; and
  - `rg -n 'RBR-1120|RBR-1121|RBR-1122' ops/tasks ops/state -g '*.md'` returned no matches in this run.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest same-family feature completion note explicitly leaves quantified branch-local callable expansion for later, and the narrow owner-path check in this run shows the next exact missing slice is an implementation prerequisite rather than another publication-only catch-up task:
  - `ops/tasks/done/RBR-1118-catch-up-nested-group-alternation-branch-local-backreference-callable-bytes-benchmarks.md` closes the exact branch-local callable bytes benchmark quartet and leaves same-family quantified branch-local callable expansion for later planning;
  - `tests/conformance/fixtures/quantified_nested_group_alternation_branch_local_backreference_callable_replacement_workflows.py` already anchors the adjacent quantified callable correctness owner path but still defaults to `text_model: "str"` and publishes only the eight exact `str` workflows for `a((b|c)+)\2d` and `a(?P<outer>(?P<inner>b|c)+)(?P=inner)d`;
  - `reports/correctness/latest.py` still reports `collection.replacement.quantified_nested_group_alternation_branch_local_backreference.callable` with `text_models == ['str']`, while broader same-family branch-local callable suites already publish mixed `bytes`/`str`;
  - `benchmarks/workloads/nested_group_callable_replacement_boundary.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `reports/benchmarks/latest.py` already carry the adjacent quantified branch-local callable `str` workload quartet on the existing benchmark owner path, with no adjacent bytes rows yet present; and
  - direct public-path probes in this run showed `rebar.sub(rb"a((b|c)+)\2d", lambda m: m.group(1) + b"x", b"abbd")`, `rebar.subn(rb"a((b|c)+)\2d", lambda m: b"<" + m.group(2) + b">", b"abbbdaccd", 1)`, `rebar.compile(rb"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d").sub(lambda m: m.group("outer") + b"x", b"accd")`, and `rebar.compile(rb"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d").subn(lambda m: b"<" + m.group("inner") + b">", b"abbbdaccd", 1)` still raise scaffold `NotImplementedError`.
- `ops/state/backlog.md` and the queue-frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on currently survives after the likely same-cycle drain, so this one-task refill does not need tracked state-prose changes.
