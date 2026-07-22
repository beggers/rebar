# Long repeats, lookbehind, and overflow: correctness follow-up

This focused compatibility/safety chunk closes every remaining official CPython `re` failure in all three from-scratch engines. It adds no external regex package or shared parser and changes no frozen fixtures or performance denominators.

The native bytecode engine now emits compact single-character runs and fixed-width capture layouts instead of unrolling large counts. The Python and Rust engines use independent iterative paths for repeated single-character expressions, alternatives, and capture groups, preserving greedy/lazy/possessive order and the final capture. Positive fixed-width lookbehind can safely skip impossible starting positions. Oversized repeat counts and lookbehind widths raise the same errors as CPython, and Rust character sets now preserve valid surrogate code points.

## Gate results

| Gate | Result |
| --- | --- |
| Original seeded oracle | **PASS** — 2,048/2,048 for native, Python, and Rust |
| Expanded seeded oracle | **PASS** — 8,244/8,244 for native, Python, and Rust |
| Broader pre-timing check | **PASS** — 576/576 comparisons |
| Full official CPython suite | **PASS** — 144/144 runnable methods in every engine; zero failures, crashes, or timeouts |
| Long-pattern differential controls | **PASS** — 3,060/3,060 comparisons, seed `20260721` |
| Native address/undefined-behavior checks | **PASS** — expanded oracle, all 144 tasks, and targeted long-input methods |
| Rust address/overflow checks | **PASS** — expanded oracle, all 144 tasks, and targeted long-input/surrogate methods |
| Delegation audit | **PASS** — zero forbidden markers or blocked import attempts in all three engines |
| v3 speed and memory | **NOT MEASURED** — correctness qualification is complete; timing is the next experiment |

The generated chart and complete method records are linked from the [official compatibility report](../../../oracle/cpython-3.14.6/README.md#long-repeats-lookbehind-and-overflow-follow-up). The deterministic control output is [long-repeat-controls.json](../../../oracle/cpython-3.14.6/evidence/long-repeat-controls.json), SHA-256 `f08c10053d3c16a3fa56b4d21f91dee0eedda637171670e06beaad4860b0e644`.

Reproduce the focused gate:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHON="$PY" sh tools/build_vm.sh
RUSTFLAGS='-D warnings' sh tools/build_rust.sh

for module in rebar candidates.ast_candidate candidates.rust_candidate; do
  PYTHONPATH=. "$PY" tools/oracle.py verify --module "$module"
  PYTHONPATH=. "$PY" tools/oracle_v2.py verify --module "$module"
  PYTHONPATH=. "$PY" tools/cpython_re_oracle.py verify --module "$module"
done
PYTHONPATH=. "$PY" tools/perf_v3.py verify
PYTHONPATH=. "$PY" tools/long_repeat_controls.py --output /tmp/long-repeat-controls.json
```
