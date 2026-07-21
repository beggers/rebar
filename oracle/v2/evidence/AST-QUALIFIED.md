# Python backtracker passes the expanded correctness check

The independently written Python backtracker now passes **8,244/8,244** frozen CPython 3.14.6 cases with **45/45 obligations mapped** and zero unexplained failures. The complete generated result is [ast-qualified.json](ast-qualified.json); fixture SHA-256 is `ae6a095bc0cd2b3ba1512a04f0d4fbe57916cf2d5b583fd4ecdda5c2c70a5bb2`.

This closes its 42 preserved gaps from the [initial check](INITIAL.md): bytes-like inputs and replacements, standard object behavior, fixed-width lookbehind references, warnings, and invalid-pattern errors now agree with Python `re`. This remains an independent parser and executor, with no shared matching code or delegation to another engine.

Gates run for this change:

- original oracle: **2,048/2,048 passed**;
- expanded oracle: **8,244/8,244 passed**;
- delegation audit: zero forbidden imports, engine markers, or blocked attempts.

Reproduce with the pinned runtime:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHONPATH=. "$PY" tools/oracle_v2.py verify --module candidates.ast_candidate
PYTHONPATH=. "$PY" tools/audit_candidate.py candidates/ast_candidate.py candidates.ast_candidate
```
