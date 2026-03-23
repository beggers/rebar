## RBR-1114: Implement nested-group alternation branch-local-backreference callable bytes parity

Status: done
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Reopen the next adjacent callable-replacement owner path after `RBR-1112` by converting the exact bounded nested-group alternation plus branch-local-backreference bytes callable slice from str-only publication to Rust-backed parity before any same-family correctness publication, benchmark catch-up, quantified branch-local follow-ons, or broader callable expansion reenters the queue.

## Pattern Pair
- `rebar.sub(rb"a((b|c))\\2d", lambda m: m.group(1) + b"x", b"zzabbdzz")`
- `rebar.compile(rb"a(?P<outer>(?P<inner>b|c))(?P=inner)d").subn(lambda m: b"<" + m.group("inner") + b">", b"abbdaccd", 1)`

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_callable_replacement_parity_suite.py`

## Acceptance Criteria
- Land the missing exact nested-group alternation plus same-branch backreference bytes callable runtime support on the existing replacement owner path in Rust, with any Python bridge changes limited to argument normalization, wrapper plumbing, and FFI calls:
  - the exact numbered module bytes path `rebar.sub(rb"a((b|c))\\2d", lambda m: m.group(1) + b"x", b"zzabbdzz")` now matches `re.sub(rb"a((b|c))\\2d", lambda m: m.group(1) + b"x", b"zzabbdzz")` instead of falling back to scaffold behavior;
  - the exact numbered count-bearing module bytes path `rebar.subn(rb"a((b|c))\\2d", lambda m: b"<" + m.group(2) + b">", b"abbdaccd", 1)` now matches CPython on the bounded first-match-only same-branch replay slice;
  - the exact named compiled-pattern bytes path `rebar.compile(rb"a(?P<outer>(?P<inner>b|c))(?P=inner)d").sub(lambda m: m.group("outer") + b"x", b"abbdaccd")` now matches `re.compile(rb"a(?P<outer>(?P<inner>b|c))(?P=inner)d").sub(lambda m: m.group("outer") + b"x", b"abbdaccd")`; and
  - the exact named compiled-pattern count-bearing bytes path `rebar.compile(rb"a(?P<outer>(?P<inner>b|c))(?P=inner)d").subn(lambda m: b"<" + m.group("inner") + b">", b"abbdaccd", 1)` now matches CPython on that same bounded leading-`b`-branch slice.
- Keep the work on the existing callable owner path in `tests/python/test_callable_replacement_parity_suite.py` rather than creating a detached parity file, correctness fixture manifest, or benchmark workload:
  - add bounded direct exact nested-group alternation plus branch-local-backreference callable bytes parity coverage for the existing numbered module/pattern and named module/pattern slices that mirror `tests/conformance/fixtures/nested_group_alternation_branch_local_backreference_callable_replacement_workflows.py`;
  - keep the already-landed grouped, nested-group, quantified nested-group, and quantified nested-group alternation callable `str` and bytes coverage green on the same file; and
  - do not widen into quantified branch-local backreferences, broader counted repeats, correctness publication, benchmark workloads, README text, or tracked ops state prose in this run.
- Preserve the existing unsupported boundaries outside this exact slice:
  - `tests/python/test_fixture_backed_replacement_parity_suite.py` must still observe placeholder behavior for the flagged/meta/empty helper cases it already covers; and
  - leave the str-only publication and benchmark owner paths for this branch-local-backreference family untouched for later planning passes after parity lands.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'nested_group_alternation_branch_local_backreference and callable and bytes and module'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'nested_group_alternation_branch_local_backreference and callable and bytes and pattern'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'nested_group_alternation_branch_local_backreference and callable'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_stay_loud_without_cache_mutation or test_source_package_pattern_literal_replacement_helpers_stay_loud_for_unsupported_cases'`

## Constraints
- Keep the implementation bounded to the exact bytes callable branch-local-backreference slice above. Leave correctness publication, benchmark catch-up, quantified branch-local bytes follow-ons, broader counted repeats, and wider callable expansion for later tasks.
- New compatibility behavior belongs in Rust. Do not solve this by expanding Python-only fallback execution beyond the existing wrapper and bridge responsibilities.
- Preserve the current callable callback semantics for the already-landed exact and quantified nested callable families while widening only the bytes branch-local capture visibility needed for this exact follow-on.

## Notes
- `RBR-1114` is the next available unreserved feature task id in this checkout:
  - the highest live task id across `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, and `ops/tasks/blocked/` is `1113`; and
  - `rg -n 'RBR-1114|RBR-1115|RBR-1116' ops/tasks ops/state -g '*.md'` returned only historical mentions inside done-task notes in this run.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest same-family feature completion note closed the quantified nested-group alternation bytes benchmark trio and left broader callable follow-ons for later; the narrow owner-path check in this run shows the next exact missing slice is the exact branch-local-backreference bytes implementation prerequisite rather than another publication-only catch-up task:
  - `tests/conformance/fixtures/nested_group_alternation_branch_local_backreference_callable_replacement_workflows.py` still defaults to `text_model: "str"` and publishes only the eight exact `str` callable workflows for `a((b|c))\\2d` and `a(?P<outer>(?P<inner>b|c))(?P=inner)d`;
  - `reports/correctness/latest.py` still reports both `collection.replacement.nested_group_alternation_branch_local_backreference.callable` and `collection.replacement.quantified_nested_group_alternation_branch_local_backreference.callable` with `text_models == ['str']`, while the adjacent broader `collection.replacement.nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference.callable` suite already reports `['bytes', 'str']`;
  - `tests/python/test_callable_replacement_parity_suite.py` currently has no direct bytes parity coverage for the exact nested-group alternation plus branch-local-backreference callable family; and
  - `benchmarks/workloads/nested_group_callable_replacement_boundary.py` plus `reports/benchmarks/latest.py` still include exact and quantified branch-local callable `str` workload ids with no adjacent exact bytes ids on that owner path.
- `ops/state/backlog.md` and the queue-frontier prose in `ops/state/current_status.md` already honestly describe the post-drain frontier for a single ready feature task: no ready feature follow-on currently survives in this checkout, so this run does not need tracked state-prose edits.

## Completion
- Landed exact bytes callable parity for `a((b|c))\\2d` and `a(?P<outer>(?P<inner>b|c))(?P=inner)d` on the Rust/native replacement path by adding bounded bytes compile recognition plus capture-preserving finditer support in `crates/rebar-core/src/lib.rs`, exposing that path through `crates/rebar-cpython/src/lib.rs`, and allowing the exact bytes patterns through the existing Python wrapper passthrough in `python/rebar/__init__.py`.
- Added focused direct module/pattern bytes parity checks in `tests/python/test_callable_replacement_parity_suite.py` for the numbered `sub`/`subn` and named compiled-pattern `sub`/`subn` callable slices without changing the published fixture manifest or benchmark surface.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'nested_group_alternation_branch_local_backreference and callable and bytes and module'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'nested_group_alternation_branch_local_backreference and callable and bytes and pattern'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'nested_group_alternation_branch_local_backreference and callable'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_stay_loud_without_cache_mutation or test_source_package_pattern_literal_replacement_helpers_stay_loud_for_unsupported_cases'`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
- Refreshed `reports/correctness/latest.py` as required for a correctness-behavior change; the tracked artifact totals remain `1629` executed, `1629` passed, `0` failed, and `0` unimplemented, and the tracked diff for that file is timestamp-only because this task did not widen the published fixture surface.
