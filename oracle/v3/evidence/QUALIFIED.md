# Large correctness holdout: all three engines qualified

The new **35,840-case** holdout found real compatibility gaps before timing. After independent fixes, the native C, Python, and Rust engines each pass **44,084/44,084** frozen correctness cases with zero mismatches, crashes, or release-build timeouts. The fixture and denominator are unchanged.

![Large correctness holdout and final results](qualified-correctness.svg)

| Engine | First holdout check | Final complete check | New focused checks |
| --- | ---: | ---: | ---: |
| Native C / `rebar` | 35,828/35,840 | **44,084/44,084** | **89,280/89,280** |
| Python | 35,839/35,840 | **44,084/44,084** | **89,280/89,280** |
| Rust | 35,839/35,840 | **44,084/44,084** | **89,280/89,280** |

The complete initial results are retained for [native C](native-initial.json), [Python](python-initial.json), and [Rust](rust-initial.json); the final results are [native C](native-qualified.json), [Python](python-qualified.json), and [Rust](rust-qualified.json). These are comparisons with the frozen CPython fixture, not estimates.

## What the holdout caught

- **Bounded separators:** the native delimiter-search shortcut incorrectly rejected a match when more than the allowed number of non-separator characters preceded a delimiter. Python `re` can start at the suffix of that run. The native path now starts at the latest valid position and leaves the general matcher to check the full expression.
- **Final newlines in configuration-style patterns:** the native multiline shortcut included a final newline after a comment, and could give a different result when trailing whitespace was allowed to consume a newline. It now ends commented lines correctly and returns the ambiguous no-comment case to the general executor.
- **Negated byte sets with locale-aware, case-insensitive matching:** all three independent engines differed from CPython for multi-item negated sets such as `rb"[^x\\n]"` under `IGNORECASE | LOCALE`. CPython tests the locale case alternatives after applying set negation; the single-literal form has different behavior. Each engine now implements that distinction in its own matcher.

The focused regression control adds **89,280** deterministic comparisons: **82,944** bounded-separator calls, **576** final-newline/configuration calls, and **5,760** locale-negated-set calls across APIs, flags, text/bytes/buffers, and module/compiled surfaces. Its seed is `2026072909`; the [complete result](regression-controls.json) has zero failures. Combined with the earlier controls, the engines now pass **155,313** focused differential checks.

The optimized builds pass the frozen one-second-per-case gate. Instrumented native safety checks use a separately recorded **20-second** per-case allowance because two intentionally difficult backtracking cases exceed one second only with address/undefined-behavior instrumentation; this does not change the frozen release oracle or hide a release timeout. The instrumented [native](native-sanitized.json) and [Rust](rust-sanitized.json) results each pass **35,840/35,840**, and the [instrumented focused control](regression-sanitized.json) passes **89,280/89,280**, with zero address, undefined-behavior, or overflow reports. The runnable upstream results for [native](native-upstream.json), [Python](python-upstream.json), and [Rust](rust-upstream.json) each pass **144/144** with zero failures, crashes, or timeouts. The **576/576** performance pre-check and all no-delegation audits are clean.

The expanded performance holdout is **NOT MEASURED** in this correctness chunk.

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHON="$PY" sh tools/build_vm.sh
PYTHON="$PY" RUSTFLAGS='-D warnings' sh tools/build_rust.sh
PYTHONPATH=. "$PY" tools/oracle_v3.py verify --module rebar
PYTHONPATH=. "$PY" tools/oracle_v3.py verify --module candidates.ast_candidate
PYTHONPATH=. "$PY" tools/oracle_v3.py verify --module candidates.rust_candidate
PYTHONPATH=. "$PY" tools/holdout_regression_controls.py --output /tmp/holdout-regression.json
```
