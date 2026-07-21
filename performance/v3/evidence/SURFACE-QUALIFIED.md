# Public API surface correctness follow-up

All three from-scratch engines now pass the 11 previously failing official methods for public flags, pattern/match objects, argument errors, warnings, and weak references. The broader pre-timing gate remains **576/576**; its complete result is [surface-qualified.json](surface-qualified.json), SHA-256 `abc11ae7eadfb8cf35012cfede9499343b6b328cef8137c88deca8e8be2a55d3`.

The compatibility fixes are observable to normal users:

- `RegexFlag` now prints canonical names, combinations, inverted values, and unknown bits like Python. Long pattern representations are bounded, and unknown compile flags remain visible and no longer collide with the engines' private bytes-mode bit.
- `groupindex` is read-only, patterns support weak references, and match-group arguments correctly accept objects implementing `__index__` while preserving `IndexError` for invalid groups.
- Module-level `split`, `sub`, and `subn` report duplicate/extra arguments exactly and place deprecation/FutureWarning locations at the calling file, including calls through helper APIs.

Full official-suite reruns improve native C from **99 to 110/144** runnable methods and Python/Rust from **95 to 106/144**, with exactly the same 11 methods fixed in each engine and no unrelated status changes. Complete records are [native](../../../oracle/cpython-3.14.6/evidence/rebar-surface.json), [Python](../../../oracle/cpython-3.14.6/evidence/ast-surface.json), and [Rust](../../../oracle/cpython-3.14.6/evidence/rust-surface.json). Remaining official crashes/timeouts still block performance claims.

Regression gates are clean: all engines pass the original 2,048 and expanded 8,244 seeded cases plus all 144 broader tasks, native C and Rust pass the expanded/task gates under AddressSanitizer and undefined-behavior or overflow checks, all three pass the no-delegation audit, and release builds are restored afterward.
