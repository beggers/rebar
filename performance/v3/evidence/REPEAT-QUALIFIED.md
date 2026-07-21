# Repeated-pattern syntax: correctness follow-up

This focused parser chunk fixes the two official CPython methods covering "nothing to repeat" and "multiple repeat" errors. Each from-scratch parser now recognizes a valid brace quantifier both at the start of an expression and after an existing quantifier; ordinary unmatched or non-numeric braces still behave as literals. It adds no external regex package or shared parser and changes no frozen fixtures or performance denominators.

All **136** upstream combinations of `*`, `+`, `?`, `{1,2}`, lazy, and possessive forms now match CPython's error message and position in each engine. Seven literal-brace controls also remain valid.

## Gate results

| Gate | Result |
| --- | --- |
| Original seeded oracle | **PASS** — 2,048/2,048 for native, Python, and Rust |
| Expanded seeded oracle | **PASS** — 8,244/8,244 for native, Python, and Rust |
| Broader pre-timing check | **PASS** — 576/576 comparisons |
| Targeted official methods | **PASS** — 6/6 (two methods × three engines) |
| Exhaustive repeat combinations | **PASS** — 136/136 for each engine, plus seven literal controls |
| Native address/undefined-behavior checks | **PASS** — expanded oracle and all 144 tasks |
| Rust address/overflow checks | **PASS** — expanded oracle and all 144 tasks |
| Delegation audit | **PASS** — zero forbidden markers or blocked import attempts in all three engines |
| v3 speed and memory | **NOT MEASURED** — remaining official failures still block timing |

The full official rerun passes **128/144** runnable methods for native C and **124/144** for both Python and Rust. The known timeouts and Rust crashes are unchanged; this chunk adds no new crash or timeout. Complete records and the generated chart are linked from the [official compatibility report](../../../oracle/cpython-3.14.6/README.md#repeated-pattern-syntax-follow-up).

Reproduce the focused gate:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHON="$PY" sh tools/build_vm.sh
RUSTFLAGS='-D warnings' sh tools/build_rust.sh

for module in rebar candidates.ast_candidate candidates.rust_candidate; do
  PYTHONPATH=. "$PY" tools/oracle.py verify --module "$module"
  PYTHONPATH=. "$PY" tools/oracle_v2.py verify --module "$module"
  PYTHONPATH=. "$PY" tools/cpython_re_oracle.py verify --module "$module" --test ReTests.test_nothing_to_repeat
  PYTHONPATH=. "$PY" tools/cpython_re_oracle.py verify --module "$module" --test ReTests.test_multiple_repeat
done
PYTHONPATH=. "$PY" tools/perf_v3.py verify
```
