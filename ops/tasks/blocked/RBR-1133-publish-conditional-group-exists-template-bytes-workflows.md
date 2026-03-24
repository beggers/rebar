# RBR-1133: Publish conditional group-exists template bytes workflows

Status: blocked
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Catch the exact two-arm conditional group-exists replacement-template bytes slice up on the published correctness owner path once `RBR-1130` lands, so the bounded bytes runtime for `a(b)?c(?(1)d|e)` and `a(?P<word>b)?c(?(word)d|e)` becomes part of the backend-parameterized correctness surface before any same-family Python-path benchmark catch-up widens the frontier.

## Pattern Pair
- `rebar.sub(rb"a(b)?c(?(1)d|e)", rb"\\1x", b"zzabcdzz")`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)d|e)").subn(rb"\\g<word>x", b"zzacezz", 1)`

## Deliverables
- `tests/conformance/fixtures/conditional_group_exists_replacement_template_workflows.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- Extend the existing `conditional-group-exists-replacement-template-workflows` manifest with only the adjacent bytes cases for the exact bounded numbered and named two-arm conditional replacement-template slice that `RBR-1130` is meant to land:
  - add numbered module `sub()` and `subn(count=1)` bytes rows for `rb"a(b)?c(?(1)d|e)"` on the existing present-capture and absent-capture haystacks;
  - add numbered compiled-pattern `sub()` and `subn(count=1)` bytes rows for that same pattern and bounded `rb"\\1x"` template;
  - add named module and compiled-pattern bytes `sub()` / `subn(count=1)` rows for `rb"a(?P<word>b)?c(?(word)d|e)"` with the bounded `rb"\\g<word>x"` template; and
  - keep the task bounded to these adjacent bytes rows instead of widening into callable replacements, alternation-heavy arms, nested conditionals, quantified conditionals, or broader template parsing.
- Keep the work on the existing shared replacement owner path instead of introducing a detached correctness pack or parity file:
  - update `tests/python/test_fixture_backed_replacement_parity_suite.py` only as needed so the `conditional-group-exists-replacement-template-workflows` manifest expects mixed `str`/`bytes` coverage, the mirrored bytes case ids, and the bytes compile patterns for this exact slice;
  - update `tests/conformance/test_combined_correctness_scorecards.py` only as needed so the combined-scorecard representative cases for `conditional-group-exists-replacement-template-workflows` mirror the new bytes rows; and
  - preserve the already-landed `str` conditional replacement-template rows plus the neighboring grouped replacement-template families on the same owner path.
- Regenerate `reports/correctness/latest.py` so the tracked publication reflects the adjacent bytes workflows without widening beyond this exact slice:
  - the conditional replacement-template manifest no longer appears as `collection.replacement.conditional_group_exists.template.str` only;
  - the published manifest now includes the eight new bytes rows alongside the existing eight `str` rows for this exact numbered/named module/pattern `sub()` / `subn(count=1)` slice; and
  - the combined correctness report remains fully passing with no new explicit failures or unimplemented cases.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'conditional and replacement and template and bytes'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'conditional_group_exists_replacement_template_workflows or collection_replacement_conditional_group_exists_template'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the task bounded to correctness publication for the exact bytes two-arm conditional replacement-template slice above. Do not widen into benchmark manifests, broader conditional replacement families, README text, or tracked ops prose in this run.
- Treat `RBR-1130` as the implementation prerequisite. If the bounded bytes runtime support is still missing when this task starts, stop and move the task to `blocked/` instead of faking publication through a Python-only fallback.
- Reuse the existing `conditional-group-exists-replacement-template-workflows` owner path and the shared replacement parity suite instead of creating another manifest or another correctness suite family for the same bounded slice.

## Notes
- `RBR-1133` is the next available unreserved feature task id in this checkout:
  - the highest live task id across `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, and `ops/tasks/blocked/` is `1132`; and
  - `rg -n 'RBR-1133|RBR-1134|RBR-1135' ops/tasks ops/state -g '*.md'` returned no reserved future feature ids in this run before this task was written.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The narrow same-family owner-path check in this run shows correctness publication, not another runtime prerequisite, is the exact surviving post-`RBR-1130` slice:
  - `tests/conformance/fixtures/conditional_group_exists_replacement_template_workflows.py` still defaults to `text_model: "str"` and publishes only the eight exact `str` replacement-template workflows for `a(b)?c(?(1)d|e)` and `a(?P<word>b)?c(?(word)d|e)`;
  - `tests/python/test_fixture_backed_replacement_parity_suite.py` still routes `conditional-group-exists-replacement-template-workflows` through the shared conditional replacement surface without any bytes representative ids on that manifest;
  - `tests/conformance/test_combined_correctness_scorecards.py` still expects only the `str` representative ids for `conditional-group-exists-replacement-template-workflows`; and
  - `reports/correctness/latest.py` still surfaces `collection.replacement.conditional_group_exists.template.str` with no corresponding `.bytes` suite while `benchmarks/workloads/conditional_group_exists_boundary.py` remains `str`-only on the adjacent template rows, confirming that correctness publication is the next exact bounded follow-on and that benchmark catch-up should stay behind it.

## Blocker Notes
- Attempted the bounded publication update, then reverted it after the direct parity gate showed the prerequisite runtime slice is still incomplete in this checkout.
- Verified passing unchanged coverage:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'conditional and replacement and template and bytes'` passed before widening the manifest and still only covers the four already-landed direct bytes cases from `RBR-1130`.
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py` passes unchanged with the current `str`-only publication.
- Verified missing prerequisite support after trying to publish the full eight-case bytes slice:
  - the mirrored numbered compiled-pattern bytes paths and named module-level bytes paths still raise the scaffold placeholder through the shared replacement parity surface;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'conditional and replacement and template and bytes'` failed with `NotImplementedError: rebar.search() is a scaffold placeholder` and matching template-expansion failures as soon as those unpublished bytes rows were routed onto the shared manifest; and
  - a direct probe of `rebar.sub(rb\"a(b)?c(?(1)d|e)\", rb\"\\\\1x\", b\"zzabcdzz\")` from the repo-local Python path still raises the scaffold placeholder in this checkout.
- Follow-up needed before reopening this task:
  - extend the bytes template runtime behind `rebar._rebar` to cover the missing mirrored `pattern` numbered rows and `module` named rows for `a(b)?c(?(1)d|e)` / `a(?P<word>b)?c(?(word)d|e)` with `sub()` and `subn(count=1)`, then rerun this publication task.
