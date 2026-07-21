# Groups, lookarounds, and references: correctness follow-up

This focused compatibility chunk fixes eight official CPython `re` methods in each from-scratch engine, including all **403** historical patterns. It adds no external regex package or shared parser and changes no frozen fixtures or performance denominators.

The corrected behavior covers:

- numeric and named references to an open group;
- forward conditional references in lookahead, with final validation when a group never appears;
- numeric, named, conditional, and nested references defined in the same lookbehind;
- invalid conditional and replacement names, including non-ASCII decimal characters and byte-name error text;
- empty/unterminated names, malformed extensions, extra conditional branches, and repeating a global-flag group;
- the complete upstream historical syntax, match, and replacement corpus.

## Gate results

| Gate | Result |
| --- | --- |
| Original seeded oracle | **PASS** — 2,048/2,048 for native, Python, and Rust |
| Expanded seeded oracle | **PASS** — 8,244/8,244 for native, Python, and Rust |
| Broader pre-timing check | **PASS** — 576/576 comparisons |
| Targeted official methods | **PASS** — 24/24 (eight methods × three engines) |
| Historical corpus | **PASS** — all 403 patterns in each engine |
| Native address/undefined-behavior checks | **PASS** — expanded oracle and all 144 tasks |
| Rust address/overflow checks | **PASS** — expanded oracle and all 144 tasks |
| Delegation audit | **PASS** — zero forbidden markers or blocked import attempts in all three engines |
| v3 speed and memory | **NOT MEASURED** — remaining official failures still block timing |

The full official rerun passes **136/144** runnable methods for native C and **132/144** for both Python and Rust. The known timeouts and Rust crashes are unchanged; this chunk adds no new crash or timeout. Complete records and the generated chart are linked from the [official compatibility report](../../../oracle/cpython-3.14.6/README.md#groups-lookarounds-and-references-follow-up).

Reproduce the focused gate:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHON="$PY" sh tools/build_vm.sh
RUSTFLAGS='-D warnings' sh tools/build_rust.sh

for module in rebar candidates.ast_candidate candidates.rust_candidate; do
  PYTHONPATH=. "$PY" tools/oracle.py verify --module "$module"
  PYTHONPATH=. "$PY" tools/oracle_v2.py verify --module "$module"
  for test in \
    ReTests.test_symbolic_groups_errors \
    ReTests.test_symbolic_refs_errors \
    ReTests.test_re_groupref_exists_errors \
    ReTests.test_re_groupref \
    ReTests.test_misc_errors \
    ReTests.test_lookahead \
    ReTests.test_lookbehind \
    ExternalTests.test_re_tests
  do
    PYTHONPATH=. "$PY" tools/cpython_re_oracle.py verify --module "$module" --test "$test"
  done
done
PYTHONPATH=. "$PY" tools/perf_v3.py verify
```
