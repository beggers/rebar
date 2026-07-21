# Expanded correctness oracle: initial candidate check

The v2 oracle freezes **8,244** CPython 3.14.6 cases with **45/45 obligations mapped**. Stdlib was generated twice and verified again with **8,244/8,244 passed**, zero invalid successes, and zero false properties. Fixture SHA-256: `ae6a095bc0cd2b3ba1512a04f0d4fbe57916cf2d5b583fd4ecdda5c2c70a5bb2`.

Initial results, before any candidate fixes:

| Implementation | Passed | Failed | Deep-fuzz failures | Main gaps exposed |
| --- | ---: | ---: | ---: | --- |
| `rebar` / native C | 8,202 | 42 | 0 | bytes-like values, generic aliases, representations/copy, inline-flag errors, fixed-width lookbehind references, warnings/deprecations |
| Python backtracker | 8,202 | 42 | 0 | the same public-contract gaps |
| Rust engine | 7,858 | 386 | 343 | the same gaps plus missing named-Unicode escapes in deep fuzz |

The complete failure records and generated charts are [rebar](rebar-initial.json), [Python backtracker](ast_candidate-initial.json), and [Rust](rust_candidate-initial.json). No case is removed or waived because a candidate fails it. These results establish the compatibility work required before the next performance oracle is accepted.

Reproduce the self-check and a representative failure:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHONPATH=. "$PY" tools/oracle_v2.py verify --module re
PYTHONPATH=. "$PY" tools/oracle_v2.py verify --module rebar --case v2.byteslike.bytearray-search
```
