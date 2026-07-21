# Rust engine passes the expanded correctness check

The independently written Rust/FFI engine now passes **8,244/8,244** frozen CPython 3.14.6 cases with **45/45 obligations mapped** and zero unexplained failures. The complete generated result is [rust-qualified.json](rust-qualified.json); fixture SHA-256 is `ae6a095bc0cd2b3ba1512a04f0d4fbe57916cf2d5b583fd4ecdda5c2c70a5bb2`.

This closes all 386 preserved gaps from the [initial check](INITIAL.md). In addition to the public-contract fixes needed by the other engines, Rust now accepts any documented `\\N{...}` Unicode character name: Python's Unicode database resolves the name, and the original pattern positions plus resolved values cross the FFI for Rust's own parser and executor. No names or expected answers are hardcoded.

Gates run for this change:

- original oracle: **2,048/2,048 passed**;
- expanded oracle: **8,244/8,244 passed**;
- Rust build with warnings denied and formatting checked: **PASS**;
- AddressSanitizer, overflow checks, and debug assertions: **8,244/8,244 passed**, no report;
- delegation audit: zero forbidden imports, engine markers, or blocked attempts.

Reproduce with the pinned runtime:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
RUSTFLAGS='-D warnings' sh tools/build_rust.sh
PYTHONPATH=. "$PY" tools/oracle_v2.py verify --module candidates.rust_candidate
PYTHONPATH=. "$PY" tools/audit_candidate.py candidates/rust_candidate.py candidates.rust_candidate candidates/rust/src/lib.rs
```
