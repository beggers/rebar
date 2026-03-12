# RBR-0046: Add the bounded bytes `LOCALE` literal workflow case

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the remaining published bytes-only `LOCALE` search workflow from an honest `unimplemented` outcome into real CPython-shaped behavior without broadening into general locale-sensitive regex support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_locale_bytes_literal_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- `rebar.search(b"abc", b"abc", rebar.LOCALE)` stops returning `NotImplementedError` and instead matches CPython for the published case `flag-unsupported-locale-bytes-search`.
- The new workflow semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, and cache/object integration.
- `reports/correctness/latest.json` flips `flag-unsupported-locale-bytes-search` from `unimplemented` to `pass`.
- The bounded bytes-only `LOCALE` workflow does not regress the existing parser-diagnostic parity work for unsupported inline locale/unicode flag combinations, and it does not imply general locale-aware character-class or non-literal behavior.

## Constraints
- Keep this task scoped to the already-published bytes literal `LOCALE` workflow case only; do not broaden into general locale-sensitive regex support or stdlib delegation.
- Implement the new workflow behavior in Rust, not in ad hoc Python execution helpers.
- Preserve the current `str`/`bytes` literal-only engine behavior outside this exact case.
- Do not silently route the bytes `LOCALE` workflow through stdlib `re`.

## Notes
- Build on the existing literal `bytes` behavior slice, the parser diagnostic work around locale-related flags, and `RBR-0042A`. This task exists so the last published bytes-only flag workflow is handled as concrete Rust-backed compatibility debt instead of staying indefinitely `unimplemented`.

## Completion
- Landed bounded Rust-core support for literal `bytes` matching with exact `rebar.LOCALE` flags, while keeping bytes collection helpers outside the supported slice.
- Added focused Rust and Python coverage for the bytes-`LOCALE` literal workflow plus a parser-diagnostic non-regression check for unsupported inline locale flags.
- Republished `reports/correctness/latest.json`; `flag-unsupported-locale-bytes-search` now reports `pass`, and the combined scorecard now reads 79 passed / 1 unimplemented.
- Follow-up remains `RBR-0047` for the final published grouped-template replacement gap.
