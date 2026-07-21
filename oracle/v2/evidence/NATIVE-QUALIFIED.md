# Native C passes the expanded correctness check

The public `import rebar as re` candidate now passes **8,244/8,244** frozen CPython 3.14.6 cases with **45/45 obligations mapped** and zero unexplained failures. The complete generated result is [rebar-qualified.json](rebar-qualified.json); fixture SHA-256 is `ae6a095bc0cd2b3ba1512a04f0d4fbe57916cf2d5b583fd4ecdda5c2c70a5bb2`.

This closes the 42 preserved gaps from the [initial check](INITIAL.md): byte arrays and memory views now work as inputs and replacements, public object behavior matches `re`, fixed-width lookbehind references compile correctly, and the same warnings and invalid-pattern errors are produced. The native hot paths still read bytes-like input directly.

Gates run for this change:

- original oracle: **2,048/2,048 passed**;
- expanded stdlib self-check: **8,244/8,244 passed**;
- expanded native check: **8,244/8,244 passed**;
- AddressSanitizer and UndefinedBehaviorSanitizer: **8,244/8,244 passed**, no report;
- delegation audit: zero forbidden imports, engine markers, or blocked attempts.

Reproduce with the pinned runtime:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHON="$PY" sh tools/build_vm.sh
PYTHONPATH=. "$PY" tools/oracle_v2.py verify --module rebar
PYTHONPATH=. "$PY" tools/audit_candidate.py candidates/vm_candidate.py candidates.vm_candidate candidates/_vm_native.c
```
