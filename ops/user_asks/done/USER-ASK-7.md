# USER-ASK-7

Status: done
Owner: supervisor
Created: 2026-03-13
Completed: 2026-03-14

## Goal
- Retune the QA/testing agent so it pressures claimed behavior more like an outside test author and treats broad CPython `re` coverage as part of the long-term target.

## Completion Note
- Updated `ops/agents/qa_testing.md` so the QA agent now explicitly treats `rebar` as a black box, targets behavior the repo appears to claim as implemented, and prefers additions that expose fidelity gaps even when those tests fail.
- Tightened the same prompt so imported/adapted CPython `re` coverage is called out as part of the long-term testing target, alongside the repo's own reusable pytest-based coverage.
