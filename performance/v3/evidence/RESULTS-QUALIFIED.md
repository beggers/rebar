# Result types and representations: correctness follow-up

This focused API chunk aligns the match type/module and result normalization with CPython in all three from-scratch engines. It adds no external regex package or shared parser and changes no frozen fixtures or performance denominators.

The native match type now exposes module `re`, matching its already-compatible `<re.Match ...>` representation. Python and Rust results from string/bytes subclasses are normalized to plain `str`/`bytes`, including subclasses that deliberately return subclass instances from slicing. This closes the official representation, `findall`, and `split` type checks while preserving the exact frozen representations.

## Gate results

| Gate | Result |
| --- | --- |
| Original seeded oracle | **PASS** — 2,048/2,048 for native, Python, and Rust |
| Expanded seeded oracle | **PASS** — 8,244/8,244 for native, Python, and Rust |
| Broader pre-timing check | **PASS** — 576/576 comparisons |
| Targeted official methods | **PASS** — 9/9 (three methods × three engines) |
| Result-surface controls | **PASS** — match module/repr and custom string/bytes slicing |
| Native address/undefined-behavior checks | **PASS** — expanded oracle and all 144 tasks |
| Rust address/overflow checks | **PASS** — expanded oracle and all 144 tasks |
| Delegation audit | **PASS** — zero forbidden markers or blocked import attempts in all three engines |
| v3 speed and memory | **NOT MEASURED** — remaining long-input failures still block timing |

The full official rerun passes **142/144** runnable methods for native C and **139/144** for both Python and Rust. The known timeouts and Rust crashes are unchanged; this chunk adds no new crash or timeout. Complete records and the generated chart are linked from the [official compatibility report](../../../oracle/cpython-3.14.6/README.md#result-types-and-representations-follow-up).

Reproduce the focused gate:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHON="$PY" sh tools/build_vm.sh
RUSTFLAGS='-D warnings' sh tools/build_rust.sh

for module in rebar candidates.ast_candidate candidates.rust_candidate; do
  PYTHONPATH=. "$PY" tools/oracle.py verify --module "$module"
  PYTHONPATH=. "$PY" tools/oracle_v2.py verify --module "$module"
  for test in ReTests.test_match_repr ReTests.test_re_findall ReTests.test_re_split; do
    PYTHONPATH=. "$PY" tools/cpython_re_oracle.py verify --module "$module" --test "$test"
  done
done
PYTHONPATH=. "$PY" tools/perf_v3.py verify
```
