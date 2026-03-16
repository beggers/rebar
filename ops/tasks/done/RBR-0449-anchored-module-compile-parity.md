# RBR-0449: Convert the anchored module.compile literal slice to real parity on the public compile path

Status: done
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Convert the newly published `module.compile("^abc$")` correctness slice from an honest `unimplemented` result into real `rebar.compile()` behavior on the public Python-facing path, while keeping the scope pinned to that exact anchored `str` compile case before the adjacent `module_boundary.py` benchmark rows are measured.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_module_surface_scaffold.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `rebar.compile("^abc$")` no longer raises the scaffold placeholder in the live source-tree path; it returns a `re.Pattern`-shaped `rebar.Pattern` object with CPython-matching compile metadata for that exact `str` pattern:
  `pattern == "^abc$"`, `flags == 32`, `groups == 0`, and `groupindex == {}`.
- The implementation stays bounded to the exact published anchored literal compile slice:
  add support only for the `str` pattern `^abc$` on the public `compile()` path, and do not broaden this run into bytes mirrors, flag variants, anchored search/match/fullmatch execution, grouped anchors, cache/purge-only work, or new benchmark rows.
- The narrow support lands behind the Rust boundary, not as a stdlib delegation shortcut:
  extend the Rust core/native compile boundary for this exact shape and keep `python/rebar/__init__.py` limited to public-surface marshalling, cache plumbing, and FFI hookup.
- `tests/python/test_module_surface_scaffold.py` grows only by the minimal module-surface assertions needed to lock the anchored compile metadata down on the shared public helper surface and to keep non-anchored metacharacter inputs such as `"[ab]c"` loudly unsupported.
- The existing published correctness case `workflow-compile-str-anchored-literal` in `tests/conformance/fixtures/module_workflow_surface.py` flips from `unimplemented` to `pass` without adding another fixture manifest or another manifest-local wrapper path.
- `reports/correctness/latest.py` is regenerated honestly and moves to `958` total cases across `107` manifests with `958` passes, `0` failures, and `0` `unimplemented`, while the `module-workflow-surface` slice moves to `11` total cases with `11` passes.
- Verification passes with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_surface_scaffold.py tests/conformance/test_correctness_fixture_inventory_contract.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0449-anchored-module-compile.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.

## Constraints
- Leave `benchmarks/workloads/module_boundary.py`, `tests/benchmarks/benchmark_expectations.py`, and `reports/benchmarks/latest.py` unchanged in this run; the three adjacent `module-compile-literal-{cold,warm,purged}` rows are the explicit `RBR-0450` benchmark catch-up follow-on once this parity slice lands.
- Keep the scope bounded to compile metadata only. Do not turn this task into a general anchored-regex execution milestone.

## Notes
- Before this run, direct verification in the current checkout showed `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... rebar.compile("^abc$") ... PY` raising `NotImplementedError: rebar.compile() is a scaffold placeholder; the \`re\`-compatible API is not implemented yet`.
- Before this run, the published correctness artifact exposed the same gap as `workflow-compile-str-anchored-literal` with `comparison == "unimplemented"` in `reports/correctness/latest.py`.
- The adjacent benchmark publication still carries the three matching `module-compile-literal-{cold,warm,purged}` rows on the shared `module-boundary` manifest, each still published as `status == "unimplemented"` in `reports/benchmarks/latest.py`.
- Completed 2026-03-16: extended the Rust compile classifier so the native boundary now reports `^abc$` as a compiled `str` pattern at normalized `UNICODE` flags without broadening into anchored execution or other metacharacter support, and added the anchored compile-metadata assertion to `tests/python/test_module_surface_scaffold.py`.
- Verified publication from the tracked report artifact: `workflow-compile-str-anchored-literal` is now `comparison == "pass"`, the `module.workflow` suite for `module-workflow-surface` is `11` total cases with `11` passes and `0` `unimplemented`, and the combined summary is `958` total cases with `958` passes, `0` failures, and `0` `unimplemented`.
- Verified with `cargo build -p rebar-cpython`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_surface_scaffold.py tests/conformance/test_correctness_fixture_inventory_contract.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0449-anchored-module-compile.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.
