# Safe ownership of compiled Rust regular expressions V1

Status: **SOURCE FROZEN; VARIANT NOT MATERIALIZED; NOT BUILT; NOT RUN.**

The existing independently written Rust engine already passes all **31,237**
original checks and all **10,434** broader public checks. Its last fully
correct measured public build runs at **1.2424347186648022× Python** across
**416** cases; **252** cases are faster, **164** are slower, and all **14**
substantial slowdowns remain visible. This safety experiment does not claim a
new correctness, speed, memory, or runtime-safety measurement.

The existing static source-and-binary independence audit covers an older Rust
build, not the exact current engine and bridge. Its audited engine begins
`3c952a1a` and its bridge begins `ee63273f`; neither is this exact build.
It is preserved as historical evidence only. Static independence and live
runtime independence for the exact current or proposed build are both **NOT
ESTABLISHED** and require a new same-build source and native-binary audit.
The newly added ownership code itself adds no matching dependency or
delegation; this narrow source-change observation is not a whole-build audit.

Source inspection proves a possible lifetime error. The current Python pattern
destructor immediately frees a raw Rust engine pointer. A replacement callback
can call `match.re.__del__()` while substitution still needs that pointer;
calling a pattern destructor while its scanner or iterator remains alive has
the same problem. An observed crash or actual undefined behavior is **NOT
MEASURED**. The issue is established from the authenticated source paths, not
by executing the candidate.

This freeze composes directly on the actually materialized first-party literal
acceleration bridge and leaves its Rust engine and Python adapter untouched:

```text
literal bridge  e4ee92d9d651600d94cf371f6437638b639b3418103cb20044fbdd26a60d5d57
actual receipt  48fbc982f5e490bc44e7fc0e2c0d25a88e2187371b75ed86ffc6042f41d185e6
Rust engine     7ec7dc9815bec10c3149123ddc5045f575c3cd45731531bd81e0b888362a9136
Python adapter  f7ad42db903e7f9f096f9c9460eb6605ac42932a40323a9ff9eb47e88a386227
target          candidates/rust/variants/native_handle_lease_v1/py_bridge.c
```

Each compiled native engine receives one private Python capsule. The capsule
destructor is the sole owner allowed to free that engine. The existing adapter
continues to clear its pattern reference when explicitly destroyed, but its
native `free` call only validates the capsule; it does not destroy engines
retained by a running match, callback, scanner, or iterator. Every native
entry point authenticates the exact capsule name before reading its pointer.

Both normal and scanner compilation transfer ownership exactly once. If
creating the capsule fails, the still-unowned raw engine is released once. If
later tuple construction fails, the capsule destructor performs the release;
no separate raw free remains. Existing active calls already hold a strong
capsule reference while user callbacks run. Scanners and iterators acquire
their own strong capsule reference before exposing their raw pointer; cleanup
clears the pointer before dropping that reference. Repeated explicit pattern
finalizers and repeated `Match.re` wrappers cannot double-free an engine.

The private capsule contains no Python references, cannot participate in a
Python object-reference cycle, and is deliberately omitted from scanner and
iterator GC traversal. This preserves their externally observable
`gc.get_referents` behavior. Independent capsules do not share ownership
between Python interpreters. Literal acceleration, public types, callback
results, reference ownership, and every existing Rust boundary remain intact.

An independent exhaustive synthetic lifetime model covers **32,768** callback
action sequences, nested callbacks, repeated explicit destructors, callbacks
raising errors, multiple scanners and iterators after pattern destruction,
independent interpreter lifetimes, invalid capsule owners, and both compiled
ownership-transfer failure families. It runs no candidate or matching engine.

The permanent deny-default source wall authenticates every permitted source
and public evidence owner by exact device, inode, owner, permissions, link
count, size, and SHA-256. Source gates cannot inspect hidden tests, proposal
metadata, private roots, native binaries, raw timing trials, or writable
descriptors. Only root may create one fresh `0700` variant directory and one
exclusive, no-follow `0600` bridge source file after all three freeze files
have been committed and pushed.

Ordinary and sterile source-only gates:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_native_handle_lease_v1.py \
  --verify-source --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_native_handle_lease_v1.py \
  --self-test --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
```

Repeat both commands under `env -i PATH=/usr/bin:/bin LC_ALL=C`.

Root-only source materialization after committing and pushing the whole freeze:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_native_handle_lease_v1.py \
  --apply --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256 \
  --frozen-commit PUSHED_COMMIT --pushed-commit PUSHED_COMMIT \
  --root-authorized --frozen-committed-pushed
```

Actual post-change compatibility, adversarial runtime behavior, undefined
behavior, speed, memory, live independence, qualification, and hidden-test
performance remain **NOT MEASURED** until separately authorized real runs.
