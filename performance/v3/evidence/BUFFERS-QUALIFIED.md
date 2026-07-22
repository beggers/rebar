# Buffer and input safety: correctness follow-up

This focused API/safety chunk adds CPython-compatible buffer handling independently to all three from-scratch engines. It adds no external regex package or shared parser and changes no frozen fixtures or performance denominators.

The corrected behavior covers arbitrary contiguous buffer exporters (including empty and multi-byte `array` values), byte-length windows and slicing, non-contiguous-view rejection, invalid-input error text, mutable-buffer locking for live iterators, and safe match access after a byte buffer shrinks. The native C path now clamps saved spans before reading, eliminating the prior out-of-bounds read.

## Gate results

| Gate | Result |
| --- | --- |
| Original seeded oracle | **PASS** — 2,048/2,048 for native, Python, and Rust |
| Expanded seeded oracle | **PASS** — 8,244/8,244 for native, Python, and Rust |
| Broader pre-timing check | **PASS** — 576/576 comparisons |
| Targeted official buffer methods | **PASS** — 12/12 (four methods × three engines) |
| Public-API differential controls | **PASS** — 120/120 across eight operations and five buffer kinds |
| Native address/undefined-behavior checks | **PASS** — expanded oracle, all 144 tasks, and all four targeted buffer methods |
| Rust address/overflow checks | **PASS** — expanded oracle, all 144 tasks, and all four targeted buffer methods |
| Delegation audit | **PASS** — zero forbidden markers or blocked import attempts in all three engines |
| v3 speed and memory | **NOT MEASURED** — remaining official failures still block timing |

The full official rerun passes **141/144** runnable methods for native C and **136/144** for both Python and Rust. The known timeouts and Rust crashes are unchanged; this chunk adds no new crash or timeout. Complete records and the generated chart are linked from the [official compatibility report](../../../oracle/cpython-3.14.6/README.md#buffer-and-input-safety-follow-up).

Reproduce the focused gate:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHON="$PY" sh tools/build_vm.sh
RUSTFLAGS='-D warnings' sh tools/build_rust.sh

for module in rebar candidates.ast_candidate candidates.rust_candidate; do
  PYTHONPATH=. "$PY" tools/oracle.py verify --module "$module"
  PYTHONPATH=. "$PY" tools/oracle_v2.py verify --module "$module"
  for test in ReTests.test_bug_29444 ReTests.test_bug_40736 ReTests.test_empty_array ReTests.test_keep_buffer; do
    PYTHONPATH=. "$PY" tools/cpython_re_oracle.py verify --module "$module" --test "$test"
  done
done
PYTHONPATH=. "$PY" tools/perf_v3.py verify
```
