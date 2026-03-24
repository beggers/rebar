# RBR-1171: Implement conditional group-exists alternation callable bytes parity

Status: done
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Reopen the next exact callable-replacement owner-path slice after `RBR-1169` by converting the bounded bytes alternation-heavy conditional group-exists callable workflows from scaffold `NotImplementedError` placeholders to Rust-backed parity before any same-family correctness publication, benchmark catch-up, nested callable follow-on, or quantified callable follow-on widens this family again.

## Pattern Pair
- `rebar.sub(rb"a(b)?c(?(1)(de|df)|(eg|eh))", lambda m: m.group(1) + b"x", b"zzabcdezz")`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))").subn(lambda m: m.group("word") + b"x", b"zzacehzz", 1)`

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_callable_replacement_parity_suite.py`

## Acceptance Criteria
- Land the missing bytes callable replacement runtime support for the exact alternation-heavy conditional group-exists owner path in Rust, with Python changes limited to argument normalization, wrapper plumbing, and FFI calls:
  - the numbered module present-first-arm bytes path `rebar.sub(rb"a(b)?c(?(1)(de|df)|(eg|eh))", lambda m: m.group(1) + b"x", b"zzabcdezz")` now matches `re.sub(...)` instead of raising the scaffold placeholder;
  - the numbered module present-second-arm count bytes path `rebar.subn(rb"a(b)?c(?(1)(de|df)|(eg|eh))", lambda m: m.group(1) + b"x", b"zzabcdfzz", 1)` now matches `re.subn(...)`;
  - the numbered compiled-pattern absent-first-arm bytes path `rebar.compile(rb"a(b)?c(?(1)(de|df)|(eg|eh))").sub(lambda m: m.group(1) + b"x", b"zzacegzz")` now matches `re.compile(...).sub(...)`;
  - the numbered compiled-pattern absent-second-arm count bytes path `rebar.compile(rb"a(b)?c(?(1)(de|df)|(eg|eh))").subn(lambda m: m.group(1) + b"x", b"zzacehzz", 1)` now matches `re.compile(...).subn(...)`; and
  - the same four module/pattern workflows now also match CPython for the named bytes spelling `rb"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))"` with `match.group("word")`.
- Keep the work on the existing callable owner path in `tests/python/test_callable_replacement_parity_suite.py` rather than creating a detached parity file, correctness fixture manifest, or benchmark workload:
  - add bounded direct bytes parity coverage for the numbered and named module/pattern callable `sub()` and `subn()` alternation-heavy workflows above;
  - keep the current simple two-arm conditional callable slice, including the published present, absent-exception, and `count=-1` str/bytes workflows, green on the same file; and
  - do not widen this run into correctness publication, benchmark manifests, str-path changes, nested conditional callable follow-ons, quantified conditional callable follow-ons, or broader callback helper shapes beyond `match.group(...) + b"x"`.

## Verification
- `cargo build -p rebar-cpython`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and bytes and callable_replacement and module'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and bytes and callable_replacement and pattern'`

## Constraints
- Keep the implementation bounded to the exact bytes alternation-heavy callable conditional slice above. Leave correctness publication, benchmark catch-up, nested callable follow-ons, quantified callable follow-ons, and broader callable helper expansion for later tasks.
- New compatibility behavior belongs in Rust. Do not solve this by broadening Python-only fallback execution beyond the existing wrapper and bridge responsibilities.
- Preserve the already-landed simple two-arm conditional callable behavior plus the recently landed str alternation-heavy callable behavior while widening only the missing bytes alternation-heavy conditional callable slice above.

## Notes
- `RBR-1171` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this run; and
  - `rg -n 'RBR-1171|RBR-1172|conditional group-exists alternation callable bytes|alternation-callable-bytes' ops/tasks ops/state -g '*.md'` matched only historical mentions inside completed task files, not a live reservation for this id.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest done same-family frontier leaves bytes mirrors as the next concrete deferred slice after `RBR-1169`, and the narrow owner-path check in this run confirms that this is an implementation prerequisite rather than another publication-only follow-on:
  - `ops/tasks/done/RBR-1169-benchmark-conditional-group-exists-alternation-callable-str-workloads.md` completed the bounded str benchmark catch-up and explicitly left bytes mirrors, nested callable follow-ons, and quantified callable follow-ons for later on this owner path;
  - `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` and `reports/correctness/latest.py` now publish only the eight str alternation-heavy callable rows for `a(b)?c(?(1)(de|df)|(eg|eh))` and `a(?P<word>b)?c(?(word)(de|df)|(eg|eh))`, with no adjacent bytes mirror rows yet present;
  - `benchmarks/workloads/conditional_group_exists_boundary.py` and `reports/benchmarks/latest.py` now measure only the eight str alternation-heavy callable workloads on the existing benchmark owner path, with no bytes mirror rows yet present there either; and
  - direct public-path probes in this run showed the exact bytes module and compiled-pattern calls above still raise scaffold `NotImplementedError` on `rebar` while CPython either succeeds on the present-arm paths or raises the expected bounded `TypeError` on the absent-capture paths, so correctness publication or benchmark catch-up would be premature until the runtime lands.
- Acceptance-command validation in this planning run:
  - `cargo build -p rebar-cpython` finished successfully;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and bytes and callable_replacement and module'` returned `16 passed, 4040 deselected`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and bytes and callable_replacement and pattern'` returned `24 passed, 4032 deselected`; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/feature-planning-conditional-callable-current.py` returned `32 executed / 32 passed`, confirming the current published callable owner path is otherwise stable before this bytes implementation prerequisite lands.
- `ops/state/backlog.md` and the queue-frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on currently survives after the likely same-cycle drain, so this one-task refill does not need tracked state-prose changes.

## Completion
- Completed 2026-03-24.
- Landed bounded Rust-backed bytes callable replacement parity for `rb"a(b)?c(?(1)(de|df)|(eg|eh))"` and `rb"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))"` across module and compiled-pattern `sub()`/`subn()` flows by extending the bytes conditional compile/finditer slice, the Python bytes callable passthrough allowlist, and the existing parity suite.
- Published correctness and benchmark scorecards were intentionally unchanged for this task; `reports/correctness/latest.py` was not republished.
- Verified with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and bytes and callable_replacement and module'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and bytes and callable_replacement and pattern'`
