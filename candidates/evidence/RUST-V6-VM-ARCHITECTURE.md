# Independent Rust engine

The Rust candidate is a complete, independently written replacement for Python's regular-expression engine. Its parser, compiler, bytecode, ordered backtracking, Unicode tables, and Python interface belong to this project. It has no third-party Rust dependencies, does not import or call Python's `re` or `_sre`, does not use another candidate, and does not contain the previous interpreter or an alternative execution fallback.

This checkpoint establishes correctness. Speed on the frozen **10,312-case** unseen benchmark is **NOT MEASURED**.

## What changed

- Compile expressions into mandatory native bytecode and discard the parse tree.
- Preserve Python's left-to-right backtracking, captures, lookarounds, conditionals, atomic groups, and possessive and large counted repetitions.
- Use bounded inline state, capture rollback, lazily extended repetitions, and the project's own portable and runtime-detected vector search.
- Borrow Python's actual byte and one-, two-, and four-byte Unicode storage rather than copying complete subjects.
- Generate character properties and case-folding from pinned CPython **3.14.6** and its Unicode data.
- Use the required native CPython bridge for compiled operations, vectors, scanners, match objects, collection, splitting, and replacement. Replacement callbacks are collected and joined in Python's exact order; object identity, buffers, garbage collection, and exact error metadata remain observable.
- Remove the previous `ctypes` production bridge, optional engine loading, retained syntax-tree executor, and Python matching fallbacks. The isolated profiling tool loads its instrumented native library directly.

## Correctness

Every reference below is generated using the pinned Python and independently reproduced against the actual rebuilt Rust candidate.

| Gate | Passing checks | Unexplained failures |
| --- | ---: | ---: |
| Frozen version-2 correctness | 8,244 | 0 |
| Complete frozen version-3 correctness | 44,084 | 0 |
| Earlier performance answers | 12,432 | 0 |
| Expanded benchmark answers | 20,624 | 0 |
| Official CPython tests | 144; two recorded skips | 0 |
| Full Unicode and seeded real operations | 4,494,555 | 0 |
| Extended captures, windows, and matching paths | 72,248 | 0 |
| Public Python interface | 1,198 | 0 |
| Deep replacement and buffer behavior | 11,266 | 0 |
| Group-name and error metadata | 420 | 0 |
| Native interface and object lifetime | 738 | 0 |
| Isolated crash and malformed-input cases | 254 | 0 |
| Isolated deep recursion and allocation cases | 348 | 0 |

The two official skips are the original, explicitly documented locale-dependent tests. These gates cover partly overlapping behavior; their counts are not added together or described as distinct independent operations.

Before the final character-class fix, the Unicode gate exposed **277** failing operations and the extended-path gate exposed **21**. They arose because four Python Unicode whitespace characters were omitted when preparing a class for a wide subject. The exact [failing Unicode cases](rust-v6-unicode-c0-f33-baseline.json.gz), [original Rust source](rust-v6-unicode-c0-f33-core-before.rs.gz), [failing-source manifest](rust-v6-unicode-c0-f33-baseline-manifest.json), [corrected full result](rust-v6-unicode-c0-f33-fixed.json.gz), and [corrected-source manifest](rust-v6-unicode-c0-f33-fixed-manifest.json) are retained. The correction uses the same pinned Unicode properties already proven across the full Unicode plane; byte and ASCII modes remain unchanged.

The original matching-path, invalid-name, safety, depth, and public-interface controls are separately retained in `rust-v6-c0-prefx-*.json.gz`. No crashes, timeout, mismatch, or skip is waived.

## Source identity

- Engine: `f529040ab9082eedf80ba9c39b407def3edf9520a9a1fc8d70cb6e8399f7723f`.
- Native bridge: `36f91d6e6970b508ad6a9fe4299055b0538917b1c2a751840e9b3accc24dbc9e`.
- Python surface: `a6394022bf647f8992f01f73e9fc1a02dd7178734948cc2dc4e5ed9dcf7b6a35`.
- Generated Unicode source: `f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af`.

## Reproduce

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
RUSTFLAGS='-D warnings' PYTHON="$PY" sh tools/build_rust.sh
cargo fmt --manifest-path candidates/rust/Cargo.toml -- --check

PYTHONPATH=. "$PY" tools/oracle_v2.py verify \
  --module candidates.rust_candidate --output /tmp/rebar-rust-v2.json
PYTHONPATH=. "$PY" tools/oracle_v3.py verify \
  --module candidates.rust_candidate --output /tmp/rebar-rust-v3.json
PYTHONPATH=. "$PY" tools/cpython_re_oracle.py verify \
  --module candidates.rust_candidate --output /tmp/rebar-rust-cpython.json
PYTHONPATH=. "$PY" tools/perf_v7.py verify \
  --module candidates.rust_candidate --output /tmp/rebar-rust-v7.json
PYTHONPATH=. "$PY" tools/rust_replacement_adversarial.py \
  --module candidates.rust_candidate --deep --output /tmp/rebar-rust-replacement.json.gz
PYTHONPATH=. "$PY" tools/audit_candidate.py \
  candidates/rust_candidate.py candidates.rust_candidate candidates/rust/src/lib.rs
```

This checkpoint does not establish benchmark speed, memory rankings, a new winner, or any advantage over Python or the existing Zig engine. All of those results are **NOT MEASURED** until the already-committed performance protocol is run in full.
