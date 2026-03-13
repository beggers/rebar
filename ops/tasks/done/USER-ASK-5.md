# USER-ASK-5

Status: done
Owner: supervisor
Created: 2026-03-13
Completed: 2026-03-13

## Goal
- Make test growth systematic instead of relying on a few hand-picked regex strings, so landed behavior has stronger evidence behind it than narrow special cases.

## Completion Note
- Translated the remote-only request into `RBR-0154` instead of adding a second always-on worker immediately.
- Landed `RBR-0154-systematic-correctness-corpus-harness`, which added `python/rebar_harness/systematic_corpus.py`, deterministic corpus expansion wiring in `python/rebar_harness/correctness.py`, a versioned `tests/conformance/fixtures/systematic_feature_corpus.json`, and `tests/conformance/test_systematic_feature_corpus.py`.
- The current harness can now amplify compact feature specs into multiple numbered/named, module/compiled-`Pattern`, and present/absent variants, so the published correctness corpus grows in a reusable way as new slices land.
- Deferred property-based or fuzz follow-ons remain a possible future extension, but the current durable direction is to keep expanding deterministic corpus generation alongside each newly supported regex slice.
