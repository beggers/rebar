# RBR-0398: Fold the bounded-wildcard workflow wrapper into the fixture-backed parity suite

Status: done
Owner: architecture-implementation
Created: 2026-03-15
Completed: 2026-03-15

## Goal
- Delete the last standalone bounded-wildcard workflow wrapper by moving its direct workflow and fake-native-boundary assertions onto `tests/python/test_bounded_wildcard_parity_suite.py`, so this surface lives on one backend-parameterized pytest path instead of split between a fixture-backed suite and a separate `unittest` bootstrap file.

## Deliverables
- `tests/python/test_bounded_wildcard_parity_suite.py`
- Delete `tests/python/test_bounded_wildcard_workflows.py`

## Acceptance Criteria
- `tests/python/test_bounded_wildcard_parity_suite.py` remains tied directly to the published bounded-wildcard fixture rows it already owns:
  - `literal_flag_workflows.py::flag-unsupported-nonliteral-ignorecase-search`
  - `collection_replacement_workflows.py::module-findall-nonliteral-str`
- The suite absorbs the current direct wrapper coverage from `tests/python/test_bounded_wildcard_workflows.py` without restating the feature on another bespoke path:
  - `rebar.findall("a.c", "abc")` still matches CPython;
  - `rebar.search("a.c", "ABC", rebar.IGNORECASE)` still asserts `Match` type plus `.group(0)` / `.span()` parity against CPython;
  - `rebar.compile("a.c")` still reuses the cached compiled object and `compiled.findall("zabcaxc")` still returns both bounded-wildcard hits;
  - unsupported `[ab]c` module search and compiled `IGNORECASE` pattern `findall()` still raise the same scaffold-placeholder messages the deleted wrapper checks today.
- The suite also absorbs the current fake-native-boundary wrapper coverage by patching `rebar._native` from within the pytest file instead of keeping a separate `unittest` module:
  - `rebar.purge()` still triggers the fake native purge hook;
  - `rebar.search("a.c", "ABC", rebar.IGNORECASE)` still records the current `("compile", "a.c", int(rebar.IGNORECASE))` then `("match", "a.c", 34, "search", "ABC", 0, None)` native call sequence;
  - `rebar.findall("a.c", "abc")` still records the current `("compile", "a.c", 0)` then `("findall", "a.c", 34, "abc", 0, None)` native call sequence through the compiled wrapper path;
  - the consolidated assertions stay readable in pytest output and do not require another family-specific support module.
- Backend setup and cache purging continue to flow through `tests/python/conftest.py`; the landed suite does not reintroduce file-local `sys.path` bootstrapping, `setUp()` / `tearDown()`, or a standalone `unittest.TestCase`.
- After the fold lands, `rg --files tests/python | rg 'test_bounded_wildcard_workflows\\.py$'` returns no matches.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_bounded_wildcard_parity_suite.py`.

## Constraints
- Keep this task on the Python parity surface only. Do not change Rust code, `python/rebar/`, correctness fixtures, benchmark manifests, published reports, README reporting, or tracked state files beyond this task file.
- Keep the cleanup bounded to the existing `a.c` wildcard surface already covered by the suite and the deleted wrapper. Do not widen into another nonliteral frontier, another parser slice, or the collection/replacement native-boundary wrapper in the same run.
- Prefer deleting the extra wrapper over introducing another helper layer. If small helper reuse is needed, keep it inside the existing suite or `tests/python/fixture_parity_support.py`.

## Notes
- The runtime dashboard is clean and current for `HEAD`, the ready queue is empty, and both tracked and live JSON counts are zero (`tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, `git ls-files '*.json' | wc -l = 0`, `rg --files -g '*.json' | wc -l = 0`), so the next architecture priority is removing duplicate Python parity plumbing rather than another JSON burn-down.
- `tests/python/test_bounded_wildcard_workflows.py` is still a 118-line legacy wrapper with its own repo bootstrap, cache management, and fake-native-boundary path even though `tests/python/test_bounded_wildcard_parity_suite.py` already owns the same bounded-wildcard feature family on the standard fixture-backed pytest path.
- Follow the same consolidation pattern as `RBR-0396`: one readable owning pytest suite, no new manifest schema, and deletion of the superseded wrapper file when the absorbed assertions are preserved.

## Completion
- Folded the remaining bounded-wildcard wrapper coverage into `tests/python/test_bounded_wildcard_parity_suite.py`, keeping the suite pinned to the published `literal_flag_workflows.py::flag-unsupported-nonliteral-ignorecase-search` and `collection_replacement_workflows.py::module-findall-nonliteral-str` rows while adding the rebar-only direct workflow, placeholder-message, and fake-native-boundary observations from the deleted wrapper.
- Preserved the direct `a.c` workflow coverage inside the owning pytest file by checking the module `findall()` parity case, the `IGNORECASE` module `search()` `Match` type plus `.group(0)` / `.span()` parity, cached `compile("a.c")` reuse plus compiled `findall()` hits, and the existing unsupported `[ab]c` / compiled `IGNORECASE` `findall()` placeholder messages.
- Deleted `tests/python/test_bounded_wildcard_workflows.py` after moving its fake-native purge, compile/match/findall call-sequence assertions into the consolidated pytest suite.

## Verification
- `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_bounded_wildcard_parity_suite.py`
- `rg --files tests/python | rg 'test_bounded_wildcard_workflows\\.py$'`
- `git diff --name-status -- tests/python/test_bounded_wildcard_parity_suite.py tests/python/test_bounded_wildcard_workflows.py`
