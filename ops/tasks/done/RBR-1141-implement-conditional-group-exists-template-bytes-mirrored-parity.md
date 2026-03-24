# RBR-1141: Implement conditional group-exists template bytes mirrored parity

Status: done
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Land the missing mirrored bytes replacement-template runtime for the bounded two-arm conditional group-exists owner path so `RBR-1133` can publish the full mixed-text correctness slice and `RBR-1135` can reopen the adjacent Python-path benchmark catch-up without another synthesis pass.

## Pattern Pair
- `rebar.compile(rb"a(b)?c(?(1)d|e)").sub(rb"\\1x", b"zzabcdzz")`
- `rebar.subn(rb"a(?P<word>b)?c(?(word)d|e)", rb"\\g<word>x", b"zzacezz", 1)`

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`

## Acceptance Criteria
- Land the exact missing bytes replacement-template runtime support for the mirrored entrypoints that still block the shared conditional replacement owner path:
  - numbered compiled-pattern bytes `sub()` present-capture and `subn(count=1)` absent-capture parity for `rb"a(b)?c(?(1)d|e)"` with `rb"\\1x"`;
  - named module-level bytes `sub()` present-capture and `subn(count=1)` absent-capture parity for `rb"a(?P<word>b)?c(?(word)d|e)"` with `rb"\\g<word>x"`; and
  - preserve the already-landed numbered module-level and named compiled-pattern bytes template cases so the full numbered/named plus module/pattern matrix is ready for `RBR-1133`.
- Keep the work on the existing shared replacement owner path rather than creating a detached parity file or publication manifest:
  - extend `tests/python/test_fixture_backed_replacement_parity_suite.py` with only the four missing mirrored bytes cases for this exact bounded slice;
  - update `python/rebar/__init__.py` only as needed so those mirrored entrypoints route into the native bytes template path instead of the scaffold placeholder; and
  - update the Rust core / CPython bridge only as needed to make those exact bytes template flows match CPython rather than broadening into callable replacements, alternation-heavy arms, nested conditionals, quantified conditionals, or broader template parsing.
- Leave correctness publication and benchmark catch-up to the already-written follow-ons once this prerequisite lands:
  - do not modify `tests/conformance/fixtures/conditional_group_exists_replacement_template_workflows.py`, `reports/correctness/latest.py`, `benchmarks/workloads/conditional_group_exists_boundary.py`, or `reports/benchmarks/latest.py` in this run; and
  - keep the task bounded to the runtime prerequisite that reopens `RBR-1133` and then `RBR-1135`.

## Verification
- `cargo build -p rebar-cpython`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'module-named-bytes-sub-template-present-capture or module-named-bytes-subn-template-absent-capture or pattern-numbered-bytes-sub-template-present-capture or pattern-numbered-bytes-subn-template-absent-capture'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'conditional and replacement and template and bytes'`

## Constraints
- Keep the implementation bounded to the missing mirrored bytes replacement-template slice for `a(b)?c(?(1)d|e)` and `a(?P<word>b)?c(?(word)d|e)`. Do not widen into correctness publication, benchmark manifests, README text, or tracked ops prose in this run.
- New compatibility behavior belongs in Rust. Do not solve this by expanding Python-only fallback execution beyond wrapper plumbing and native entrypoint selection.
- Reuse the existing shared conditional replacement parity suite instead of inventing a second owner path for the same bounded matrix.

## Notes
- `RBR-1141` is the next available unreserved feature task id in this checkout:
  - the highest live task id across `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, and `ops/tasks/blocked/` is `1140`; and
  - `rg -n 'RBR-1141' ops/tasks ops/state -g '*.md'` only matched a historical reservation note inside `ops/tasks/done/RBR-1140-collapse-grouped-quantified-trace-builders-onto-shared-parity-support.md`, not a live task reservation.
- The newest blocked same-family task exposes this exact prerequisite:
  - `ops/tasks/blocked/RBR-1133-publish-conditional-group-exists-template-bytes-workflows.md` still reports the missing mirrored numbered compiled-pattern and named module-level bytes template rows on this owner path;
  - `ops/tasks/blocked/RBR-1135-catch-up-conditional-group-exists-template-bytes-benchmarks.md` still depends on `RBR-1133`, so benchmark catch-up should stay behind publication on this family; and
  - `tests/python/test_fixture_backed_replacement_parity_suite.py` currently covers only four direct bytes template cases for this slice: numbered module `sub()` / `subn(count=1)` and named compiled-pattern `sub()` / `subn(count=1)`, leaving the mirrored half of the matrix unimplemented.
- The narrow same-family owner-path check in this run confirms this task is the smallest concrete prerequisite instead of a broader new frontier:
  - `tests/conformance/fixtures/conditional_group_exists_replacement_template_workflows.py` still publishes only the eight `str` rows for `conditional-group-exists-replacement-template-workflows`;
  - `tests/python/test_fixture_backed_replacement_parity_suite.py` keeps the conditional bytes template direct coverage bounded to the four already-landed cases above; and
  - `ops/state/current_status.md` and `ops/state/backlog.md` both already record that no ready feature follow-on survives beyond the blocked publication and benchmark pair, so restoring this mirrored runtime half is the exact step that reopens the post-drain frontier.

## Completion Note
- Closed by extending `tests/python/test_fixture_backed_replacement_parity_suite.py` with the four mirrored bytes case IDs for the existing conditional replacement owner path and updating the frontier assertions to cover the full numbered/named plus module/pattern matrix.
- The native bytes template runtime was already behaving with CPython parity in this checkout for the mirrored compiled-numbered and module-named entrypoints, so no Rust or wrapper changes were required in this run.
- Verified with `cargo build -p rebar-cpython`, the four-case narrow pytest selector, and the broader `conditional and replacement and template and bytes` parity selector.
