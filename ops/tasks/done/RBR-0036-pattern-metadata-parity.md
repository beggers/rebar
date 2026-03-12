# RBR-0036: Fix compiled-pattern metadata parity for the supported literal slice

Status: done
Owner: supervisor
Created: 2026-03-12
Completed: 2026-03-12

## Goal
- Eliminate the remaining explicit correctness failures in compiled `Pattern` metadata for the currently supported literal-only `str` and `bytes` slice.

## Deliverables
- `python/rebar/__init__.py`
- `tests/python/test_pattern_object_scaffold.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- For supported literal-only compiled patterns, the observed metadata fields already covered by the correctness harness match CPython for representative `str` and `bytes` cases, including the existing `IGNORECASE` metadata observations.
- The existing pattern-object correctness pack flips the three current explicit metadata failures (`pattern-object-str-metadata`, `pattern-object-str-ignorecase-metadata`, and `pattern-object-bytes-ignorecase-metadata`) to passing comparisons in `reports/correctness/latest.json`.
- The task preserves the current literal-only behavior contract from `RBR-0023` and `RBR-0024`: supported metadata should become correct, while unsupported pattern methods, flags, and non-literal parsing paths remain loud gaps rather than silent delegation to stdlib `re`.
- Cache identity and compiled-pattern reuse stay intact for the supported subset; metadata parity fixes must not regress the observable cache/purge behavior already covered by unit tests.

## Constraints
- Keep this task scoped to compiled-pattern metadata parity for the existing literal-only slice; do not broaden into collection helpers, replacement behavior, or general regex parsing.
- Do not delegate compiled-pattern metadata to stdlib `re` or swap in raw `re.Pattern` objects behind the shim.
- Preserve compatibility with both `str` and `bytes` scaffolds and the environment-gated native smoke path from `RBR-0010`.

## Notes
- Build on `RBR-0019`, `RBR-0022`, `RBR-0023`, and `RBR-0024`; this task existed to convert the current known-wrong pattern metadata cases into true compatibility wins before broader feature work resumed.

## Completion
- Retired by the supervisor after `RBR-0035` landed. The exported-helper metadata and constructor-guard cleanup also fixed the previously published compiled-pattern metadata mismatches as a direct side effect.
- `reports/correctness/latest.json` now reports `80` executed, `60` passed, `0` failed, and `20` unimplemented cases, so there is no remaining explicit compiled-pattern metadata debt for this task to close.
- The milestone front moves directly to `RBR-0037` through `RBR-0042`, where the remaining visible correctness debt is concentrated in published parser-matrix cases.
