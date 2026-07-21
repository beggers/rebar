# Inline and scoped flags correctness follow-up

All three from-scratch engines now pass the six previously failing official methods for inline/global flags, scoped modes, verbose whitespace/comments, and ASCII/Unicode/LOCALE combinations. The broader pre-timing gate remains **576/576**; its complete result is [flags-qualified.json](flags-qualified.json), SHA-256 `abc11ae7eadfb8cf35012cfede9499343b6b328cef8137c88deca8e8be2a55d3`.

Each independent parser now implements the same observable rules:

- Repeated global flags are accepted only while still at the true start of a pattern, including after ignored whitespace, comments, or earlier global flags. Flags following a real expression, an alternative, or an enclosing group are rejected at the correct position.
- Scoped `a`, `u`, and `L` modes correctly replace one another instead of leaking an outer mode. Bytes `(?u)` is rejected, API/inline ASCII-versus-Unicode or LOCALE conflicts raise the correct exception, and malformed flag groups produce the exact CPython message/position.
- Global verbose flags apply across alternatives and subsequent comments/spaces; ignored text no longer causes accidental literal matching or false “not at start” errors.

Full official-suite reruns improve native C from **110 to 116/144** runnable methods and Python/Rust from **106 to 112/144**, with exactly the same six methods fixed in each engine and no unrelated status changes. Complete records are [native](../../../oracle/cpython-3.14.6/evidence/rebar-flags.json), [Python](../../../oracle/cpython-3.14.6/evidence/ast-flags.json), and [Rust](../../../oracle/cpython-3.14.6/evidence/rust-flags.json). Remaining official crashes/timeouts still block performance claims.

Regression gates are clean: all engines pass the original 2,048 and expanded 8,244 seeded cases plus all 144 broader tasks, native C and Rust pass the expanded/task gates under AddressSanitizer and undefined-behavior or overflow checks, all three pass the no-delegation audit, and release builds are restored afterward.
