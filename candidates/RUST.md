# Candidate C: Rust continuation arena over FFI

`candidates.rust_candidate` is a third from-scratch family. Its parser and executor live entirely in a dependency-free Rust `cdylib`; they share no semantic parser, compiler, executor, or engine with Candidates A or B. The Rust parser builds an arena-style expression tree, and an eager continuation-set evaluator preserves ordered alternatives, capture states, lookarounds, atomics, possessives, and empty-match behavior. This is deliberately distinct from both Python generators and the native bytecode stack.

The Python layer uses only `ctypes`, `enum`, `os`, and `warnings`. It maps documented Unicode decimal/space/alphanumeric and simple case data across the FFI once per public search, supplies the public `Pattern`/`Match`/scanner/template contract, and never imports stdlib or third-party regex code. Rust has no dependencies; its lockfile is committed.

Build and reproduce the complete gate:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
RUSTFLAGS='-D warnings' sh tools/build_rust.sh
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 "$PY" tools/oracle.py verify --module candidates.rust_candidate --output candidates/evidence/rust-correctness.json
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 "$PY" tools/audit_candidate.py candidates/rust_candidate.py candidates.rust_candidate candidates/rust/src/lib.rs
```

The committed [result](evidence/rust-correctness.json) passes 2,048/2,048 cases with zero mismatches or crashes and all 38 obligations mapped. The gate also builds with address sanitization, overflow checks, and debug assertions enabled, then reruns the complete oracle. No sanitizer failure is accepted.
