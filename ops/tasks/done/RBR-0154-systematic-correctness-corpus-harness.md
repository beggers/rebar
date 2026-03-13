# RBR-0154: Add a deterministic systematic correctness-corpus harness

Status: done
Owner: implementation
Created: 2026-03-13
Completed: 2026-03-13

## Goal
- Strengthen confidence in already-landed regex slices by adding a reusable, deterministic correctness-harness path that can expand compact feature specs into broader CPython-vs-`rebar` test matrices instead of relying only on hand-written fixture growth.

## Deliverables
- `python/rebar_harness/correctness.py`
- `python/rebar_harness/systematic_corpus.py`
- `tests/conformance/fixtures/systematic_feature_corpus.json`
- `tests/conformance/test_systematic_feature_corpus.py`
- `docs/testing/correctness-plan.md`

## Acceptance Criteria
- The correctness harness gains a deterministic expansion path where a compact feature spec can generate multiple concrete CPython-vs-`rebar` observations without writing a separate Python test body for every module-versus-compiled, numbered-versus-named, or present-versus-absent variant.
- The first published harness slice for this machinery covers at least two already-landed feature families with materially different control flow, including one capture-oriented workflow and one conditional workflow, so the mechanism proves it is not limited to trivial literals.
- The generated cases run as normal tracked tests under `tests/conformance/` and fail loudly when `rebar` regresses relative to CPython for a supposedly landed slice.
- The generation path is deterministic and versioned. Do not add randomized fuzzing, flaky data sources, or a second long-running agent in this task.
- This task strengthens test infrastructure only. It must not broaden regex support, silently delegate new behavior to stdlib `re`, or replace the existing published correctness-report contract.

## Constraints
- Keep the first slice bounded enough for one implementation-agent run and a normal local test loop.
- Reuse the current differential-harness conventions and fixture style instead of inventing a disconnected testing framework.
- Do not turn this task into a full benchmark or native-path expansion project.

## Notes
- This task is the local queue translation of the remote-only `USER-ASK-5` request while git history is still diverged from `origin/main`.
- Prefer deterministic corpus amplification for already-landed slices before considering property-based or fuzz follow-ons.
- Completed by adding a versioned `systematic_feature_corpus` generator path in `python/rebar_harness/systematic_corpus.py`, wiring that expansion into `python/rebar_harness/correctness.py`, publishing a first compact manifest that expands optional-group and nested explicit-empty-else conditional slices into 18 deterministic cases, adding `tests/conformance/test_systematic_feature_corpus.py`, updating the correctness plan, refreshing the affected combined-report tests, and republishing `reports/correctness/latest.json` at 45 manifests / 322 passing cases in this checkout.
