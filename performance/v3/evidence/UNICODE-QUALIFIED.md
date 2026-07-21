# Unicode case-equivalence correctness follow-up

All three from-scratch engines now pass the three previously failing official case-insensitivity methods for literals, character sets, and ranges. The broader pre-timing gate remains **576/576**; its complete result is [unicode-qualified.json](unicode-qualified.json), SHA-256 `abc11ae7eadfb8cf35012cfede9499343b6b328cef8137c88deca8e8be2a55d3`.

The semantic correction is important for real users:

- Ranges now test valid case variants of the input character instead of folding the two range endpoints. This makes `[9-A]` correctly reject `_`, keeps `[9-a]` matching it, and preserves punctuation/non-letter boundaries in Latin, Cyrillic, and astral ranges.
- The independent C, Python, and Rust executors now cover CPython's special case-equivalence closures, including dotted/dotless I, long-s, Kelvin, `В/в/ᲀ`, `ﬅ/ﬆ`, and `ß/ẞ`. ASCII and bytes mode stay ASCII-only.

Full official-suite reruns improve native C from **116 to 119/144** runnable methods and Python/Rust from **112 to 115/144**, with exactly the same three methods fixed in each engine and no unrelated status changes. Complete records are [native](../../../oracle/cpython-3.14.6/evidence/rebar-unicode.json), [Python](../../../oracle/cpython-3.14.6/evidence/ast-unicode.json), and [Rust](../../../oracle/cpython-3.14.6/evidence/rust-unicode.json). Remaining official crashes/timeouts still block performance claims.

Regression gates are clean: all engines pass the original 2,048 and expanded 8,244 seeded cases plus all 144 broader tasks, native C and Rust pass the expanded/task gates under AddressSanitizer and undefined-behavior or overflow checks, all three pass the no-delegation audit, and release builds are restored afterward.
