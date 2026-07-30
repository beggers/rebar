# Combined first-party Rust search and compiler improvements

This is one independently frozen Rust source experiment. It combines two
previously materialized, from-scratch improvements without borrowing Python's
regular-expression engine, another candidate, or an external package.

The first existing improvement removes the extra copy of a pattern before Rust
parses it and avoids allocating alternatives when a pattern has no actual
alternative. Its frozen model checks 960 parser outcomes, including 42
scanner-specific distinctions, plus 40 separate source-lifetime checks. The second
existing improvement uses Rust-owned, fixed-position byte requirements to skip
positions that cannot possibly match. Its independent model checks 11,328
ordered searches across 18 expression families.

The two previously frozen transformations commute. Applying the seven exact
compiler substitutions to the existing search variant produces byte-for-byte
the same source as applying the complete search transformation to the existing
compiler variant:

```text
combined lib.rs
SHA-256 c627012d0ce8d1e2cc3c70301956a060eecc6656f82137b219e44ec905f235ee
bytes   189423

unchanged first-party search.rs
SHA-256 4d332a2af446550e29ac81369f8629b47be344f8274b0e83d6d1e2f44ebb8ae7
bytes   24305
```

The source verifier authenticates both complete previous source-freeze triples,
both actual materialization receipts, all three existing derived sources, the
original Rust sources, its zero-dependency Cargo manifest and lock, the safe
changing-buffer bridge, the successful two-build safety receipt, the complete
previous 1,352-difference Rust failure, and all 416 public correctness results
with their 1,664 preserved paired timing rows. Every old substitution must
occur exactly once, every substituted span must be disjoint, both complete
transformation orders must agree, and the entire result must reverse exactly.

The existing 960- and 11,328-case independent models are rerun. A new combined
model additionally checks ordered alternatives, overlapping and bounded
searches, opposite byte densities, high bytes, ordinary and scanner parsing,
scoped flag entry and restoration, nested flag scopes, and anchor ownership
after the borrowed parser input has been released. Synthetic verbose flags are
mapped to Rust's actual verbose bit, never accidentally to its locale bit.

An always-on, deny-default descriptor and audit wall is installed before any
owner is read. It rejects unapproved source or native files, candidate imports,
subprocesses, clocks, descriptor aliases, mutable files, hidden cases, and the
final comparison. Exactly one metadata-only inspection confirms the existing
141,557,760-case proposal; its contents are never opened. Source-only modes
cannot open a target directory or create any file.

Only the root coordinator may apply the already committed and pushed source
freeze. Root must provide the exact source, protocol, and contract hashes, two
matching full pushed-commit hashes, and both explicit authorization switches.
The wall remains active while a pinned parent directory is opened, one fresh
private child directory is created, and exactly two fresh files are written
with `O_CREAT | O_EXCL | O_NOFOLLOW`. Both files, their private directory, and
their parent are synchronized. A partial failure is preserved and can never
silently overwrite or restart the same experiment.

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_combined_search_compiler_fastpath_v1.py \
  --verify-source --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_combined_search_compiler_fastpath_v1.py \
  --self-test --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_combined_search_compiler_fastpath_v1.py \
  --apply --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256 \
  --frozen-commit PUSHED_COMMIT --pushed-commit PUSHED_COMMIT \
  --root-authorized --frozen-committed-pushed
```

This freeze does not compile or execute a candidate. The original correctness
denominator remains 31,237; the separate previous Rust result remains 15,877
verified cases with 1,352 differences. Corrected-candidate compatibility,
speed, memory, confidence, and undefined behavior are **NOT MEASURED**. The
final test remains **NOT FROZEN**, **NOT GENERATED**, and **NOT OPENED**.
