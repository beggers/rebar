# Pattern and replacement escapes: correctness follow-up

This focused compatibility chunk fixes seven official CPython `re` methods in each from-scratch engine. It adds no external regex package or shared parser and changes no frozen fixtures or performance denominators.

The corrected behavior covers:

- three-digit octal pattern escapes and their `0o377` limit, including bytes and character classes;
- the distinction between an octal escape and a one/two-digit group reference;
- partial hexadecimal/Unicode escape errors and out-of-range Unicode code points;
- missing, unknown, and multi-character Unicode names;
- invalid class ranges and invalid `\8`/`\9` class escapes;
- replacement octal escapes, group-reference errors, and validation even when there are no matches.

## Gate results

| Gate | Result |
| --- | --- |
| Original seeded oracle | **PASS** — 2,048/2,048 for native, Python, and Rust |
| Expanded seeded oracle | **PASS** — 8,244/8,244 for native, Python, and Rust |
| Broader pre-timing check | **PASS** — 576/576 comparisons |
| Targeted official methods | **PASS** — 21/21 (seven methods × three engines) |
| Native address/undefined-behavior checks | **PASS** — expanded oracle and all 144 tasks |
| Rust address/overflow checks | **PASS** — expanded oracle and all 144 tasks |
| Delegation audit | **PASS** — zero forbidden markers or blocked import attempts in all three engines |
| v3 speed and memory | **NOT MEASURED** — remaining official failures still block timing |

The full official rerun passes **126/144** runnable methods for native C and **122/144** for both Python and Rust. The previous and current results preserve the same two native timeouts, one Python timeout, and three Rust crashes; this chunk adds no new crash or timeout. Complete records and the generated chart are linked from the [official compatibility report](../../../oracle/cpython-3.14.6/README.md#pattern-and-replacement-escapes-follow-up).

Reproduce the focused gate:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHON="$PY" sh tools/build_vm.sh
RUSTFLAGS='-D warnings' sh tools/build_rust.sh

for module in rebar candidates.ast_candidate candidates.rust_candidate; do
  PYTHONPATH=. "$PY" tools/oracle.py verify --module "$module"
  PYTHONPATH=. "$PY" tools/oracle_v2.py verify --module "$module"
  for test in \
    ReTests.test_sub_template_numeric_escape \
    ReTests.test_named_unicode_escapes \
    ReTests.test_sre_character_literals \
    ReTests.test_sre_character_class_literals \
    ReTests.test_sre_byte_literals \
    ReTests.test_sre_byte_class_literals \
    ReTests.test_character_set_errors
  do
    PYTHONPATH=. "$PY" tools/cpython_re_oracle.py verify --module "$module" --test "$test"
  done
done
PYTHONPATH=. "$PY" tools/perf_v3.py verify
```
