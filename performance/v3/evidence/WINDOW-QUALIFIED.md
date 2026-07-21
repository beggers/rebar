# Window and multiline correctness follow-up

The broader pre-timing gate now passes **576/576 comparisons** for stdlib and all three from-scratch engines. The complete result is [window-qualified.json](window-qualified.json), SHA-256 `abc11ae7eadfb8cf35012cfede9499343b6b328cef8137c88deca8e8be2a55d3`. The original eight failures remain preserved in [initial-correctness.json](initial-correctness.json).

Two compatibility fixes close every newly exposed case:

- Compiled-pattern scanners now accept `string`, `pos`, and `endpos`, preserve the search window on every call, and report the original window in returned matches. Native compiled methods also accept their documented keyword forms for search/match/fullmatch/findall/finditer/split/sub/subn.
- The native executor no longer assumes greedy whitespace before multiline `$` is deterministic. Whitespace can consume a newline, so the executor must be able to backtrack to the earlier line ending. This restores first-line configuration matches and the smaller `^([^\\n]*?)\\s*$` regression case.

The official CPython keyword-parameter test now passes in every engine. Full official-suite reruns improve native C from **98 to 99/144** runnable methods and Python/Rust from **94 to 95/144**, with no new crashes or timeouts. Remaining official failures are preserved in the [native](../../../oracle/cpython-3.14.6/evidence/rebar-window.json), [Python](../../../oracle/cpython-3.14.6/evidence/ast-window.json), and [Rust](../../../oracle/cpython-3.14.6/evidence/rust-window.json) records.

Regression gates are clean: all engines pass the original 2,048 and expanded 8,244 seeded cases, native C and Rust pass the expanded and 144-task gates under AddressSanitizer/undefined-behavior or overflow checks, and all three pass the no-delegation audit. Release builds are restored after the sanitizer runs.

The v3 performance result remains **NOT MEASURED** until the official compatibility gate is clean.
