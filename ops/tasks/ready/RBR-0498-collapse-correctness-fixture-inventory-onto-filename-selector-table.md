# RBR-0498: Collapse correctness fixture inventory onto one filename-rooted selector table

Status: ready
Owner: architecture-implementation
Created: 2026-03-16

## Goal
- Remove the remaining open-coded correctness fixture path arithmetic so the correctness harness owns one filename-rooted selector table like the benchmark harness, while preserving the exact published full-suite fixture ordering and every focused selector's current membership.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/python/test_fixture_parity_support_contract.py`

## Acceptance Criteria
- `python/rebar_harness/correctness.py` stops storing the published full-suite inventory as a giant tuple of `REPO_ROOT / "tests" / "conformance" / "fixtures" / ...` `Path` objects. Instead:
  - the published full-suite inventory and the focused selector inventories live in one filename-only selector table;
  - `select_correctness_fixture_paths(...)` resolves selector-owned filenames through `CORRECTNESS_FIXTURES_ROOT`;
  - `DEFAULT_FIXTURE_PATHS` remains derived from `select_correctness_fixture_paths(PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR)`; and
  - the subset helpers that currently filter `_PUBLISHED_FULL_SUITE_FIXTURE_PATHS` operate on selector-owned filenames rather than prebuilt `Path` objects.
- Preserve the current published full-suite selector exactly:
  - `select_correctness_fixture_paths(PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR)` still returns `109` paths;
  - the first filename remains `parser_matrix.py`;
  - the last filename remains `conditional_group_exists_callable_replacement_workflows.py`; and
  - the filename-order digest `sha256("\n".join(path.name for path in paths).encode())` remains `4a9cef3163e096784b33fb00337ca038e56d92cfe4cac5c7876620f9ec76c166`.
- Preserve focused-selector behavior exactly:
  - every existing correctness selector constant still resolves only paths under `CORRECTNESS_FIXTURES_ROOT`;
  - the focused selector filename expectations in `tests/python/test_fixture_parity_support_contract.py` stay unchanged; and
  - that test module adds or keeps one explicit contract for the published full-suite selector count/order digest above so future fixture additions have one obvious inventory touchpoint.
- Delete the remaining open-coded published fixture path arithmetic:
  - after the cleanup, `rg -n 'REPO_ROOT\\s*/\\s*"tests"\\s*/\\s*"conformance"\\s*/\\s*"fixtures"\\s*/' python/rebar_harness/correctness.py` returns no matches.
- Verification passes with:
  - ```bash
    PYTHONPATH=python ./.venv/bin/python - <<'PY'
    from hashlib import sha256
    from rebar_harness.correctness import (
        DEFAULT_FIXTURE_PATHS,
        PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR,
        select_correctness_fixture_paths,
    )

    paths = select_correctness_fixture_paths(PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR)
    assert paths == DEFAULT_FIXTURE_PATHS
    payload = "\n".join(path.name for path in paths).encode()
    print(f"count={len(paths)}")
    print(f"first={paths[0].name}")
    print(f"last={paths[-1].name}")
    print(f"sha256={sha256(payload).hexdigest()}")
    PY
    ```
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/conformance/test_correctness_scorecard_registry_contract.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/grouped_alternation_replacement_workflows.py --report .rebar/tmp/rbr-0498-correctness-selector-inventory.py`
  - `rg -n 'REPO_ROOT\\s*/\\s*"tests"\\s*/\\s*"conformance"\\s*/\\s*"fixtures"\\s*/' python/rebar_harness/correctness.py`

## Constraints
- Keep this cleanup structural only. Do not change files under `tests/conformance/fixtures/`, do not change `reports/correctness/latest.py`, benchmark harness code, README text, or tracked project-state files.
- Prefer the benchmark harness shape already used in `python/rebar_harness/benchmarks.py` over adding a new registry module, package-discovery layer, or filesystem `glob()`-driven published order.
- Preserve the current published full-suite ordering explicitly. The goal is to delete duplicated path plumbing, not to infer a new order from the filesystem.

## Notes
- `RBR-0416` centralized correctness selectors, but the published full-suite correctness inventory still lives as a long tuple of repeated `Path` constructions inside `python/rebar_harness/correctness.py`. The benchmark harness already keeps the equivalent inventory as a filename-rooted selector table in `python/rebar_harness/benchmarks.py`; this is the correctness-side mirror cleanup.
- The runtime reporting surfaces are slightly behind the live queue: `.rebar/runtime/dashboard.md` was rendered at `fad99bcd6cbac74ccfc255ffe1754402206ea19d` and still reports `ready: 1` / `blocked: 0`, while the live checkout is clean at `3fbbcbfc67787ec0f4ca78bf7e4e221bbecccf5a` with `0` ready and `1` blocked task. JSON counts remain zero in the live checkout (`git ls-files '*.json' | wc -l = 0`, `rg --files -g '*.json' | wc -l = 0`), so this run stayed on post-JSON harness simplification rather than queue/state repair.
- 2026-03-16 architecture probes from the current checkout:
  - The published full-suite selector probe prints `count=109`, `first=parser_matrix.py`, `last=conditional_group_exists_callable_replacement_workflows.py`, and `sha256=4a9cef3163e096784b33fb00337ca038e56d92cfe4cac5c7876620f9ec76c166`.
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/conformance/test_correctness_scorecard_registry_contract.py` passes (`104 passed, 139 subtests passed in 0.61s`).
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/grouped_alternation_replacement_workflows.py --report .rebar/tmp/rbr-0498-correctness-selector-inventory.py` currently succeeds and reports `{"executed_cases": 8, "failed_cases": 0, "passed_cases": 8, "skipped_cases": 0, "total_cases": 8, "unimplemented_cases": 0}`.
  - `rg -n 'REPO_ROOT\\s*/\\s*"tests"\\s*/\\s*"conformance"\\s*/\\s*"fixtures"\\s*/' python/rebar_harness/correctness.py` currently returns matches, which is the exact cleanup target for this task.
