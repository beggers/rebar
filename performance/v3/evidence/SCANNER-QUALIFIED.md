# Public scanner: correctness follow-up

This focused API chunk adds the missing public `Scanner` tokenizer independently to all three from-scratch engines and exposes it through `import rebar as re`. It adds no external regex package or shared parser and changes no frozen fixtures or performance denominators.

The scanner selects the first matching token rule, sets the callback match, supports constant and skipped actions, preserves the unmatched remainder, accepts string/byte patterns and flags, and stops when the first matching rule is zero-length. Differential controls also cover captures, anchors, and lookahead.

## Gate results

| Gate | Result |
| --- | --- |
| Original seeded oracle | **PASS** — 2,048/2,048 for native, Python, and Rust |
| Expanded seeded oracle | **PASS** — 8,244/8,244 for native, Python, and Rust |
| Broader pre-timing check | **PASS** — 576/576 comparisons |
| Official scanner method | **PASS** — 3/3 engines |
| Scanner differential controls | **PASS** — callbacks/captures, constants/skips, bytes, flags, remainder, anchors/lookahead, and zero-length stop |
| Native address/undefined-behavior checks | **PASS** — expanded oracle and all 144 tasks |
| Rust address/overflow checks | **PASS** — expanded oracle and all 144 tasks |
| Delegation audit | **PASS** — zero forbidden markers or blocked import attempts in all three engines |
| v3 speed and memory | **NOT MEASURED** — remaining official failures still block timing |

The full official rerun passes **137/144** runnable methods for native C and **133/144** for both Python and Rust. The known timeouts and Rust crashes are unchanged; this chunk adds no new crash or timeout. Complete records and the generated chart are linked from the [official compatibility report](../../../oracle/cpython-3.14.6/README.md#public-scanner-follow-up).

Reproduce the focused gate:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHON="$PY" sh tools/build_vm.sh
RUSTFLAGS='-D warnings' sh tools/build_rust.sh

for module in rebar candidates.ast_candidate candidates.rust_candidate; do
  PYTHONPATH=. "$PY" tools/oracle.py verify --module "$module"
  PYTHONPATH=. "$PY" tools/oracle_v2.py verify --module "$module"
  PYTHONPATH=. "$PY" tools/cpython_re_oracle.py verify --module "$module" --test ReTests.test_scanner
done
PYTHONPATH=. "$PY" tools/perf_v3.py verify
```
