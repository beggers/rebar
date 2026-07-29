# Build the corrected from-scratch Rust engine reproducibly

Status: **SOURCE FROZEN; NATIVE BUILD NOT RUN; CORRECTNESS NOT MEASURED.**

This version prepares an independently auditable native build of the existing
first-party Rust regular-expression engine and its own CPython bridge. It does
not wrap an external regular-expression package, compile during source-only
verification, activate a candidate, run matching, or open the final benchmark.

## What has actually already happened

The pushed version-21 native build genuinely completed **two** independent
source phases and all **28** real compiler and binary-inspection processes.
Only its two small, published plaintext build and root-provenance receipts are
read. Their SHA-256 hashes are:

```text
bc3ebdc835ef6a89d351c4541863274d410e2685d35eacdc9668f4bf3a474102
73cee9c0a4f44d113da96b505eb0e9224577584b75c347e6fd351995d1d09a4e
```

The latest actual version-20 original compatibility campaign attempted all
**13** groups, completed **12**, proved **15,749** passing cases, reported
**240** fully observed substitution differences and **1,056** changing-buffer
differences, and recorded **one** separately visible worker failure. All four
original Rust targets were restored. The global mismatch count is still **NOT
MEASURED** because the subinterpreter group did not complete. The separately
preserved older version-19 result completed eight groups and verified 12,942
passes. Neither failure is overwritten or misrepresented as the other.

The latest actual version-20 public failure receipt is:

```text
ad9e04aa3595a4e44a5bbc12b6413fde08b926c9e73b23aa6b3eedacd35e4a36
```

## What the next build will compile

The immediate first-party version-21 bridge has SHA-256
`a0b9e7fbfc92da4c3b97608cf156fb0ca2f94fb5358901b7b6baa0a819fffc8a`.
The independently frozen semantic correction derives the complete next bridge
in memory:

```text
corrected bridge SHA-256  f9bd2d3c8406e4b2c703ce96f42964ee15941611e22447b12acc9b54fac98055
corrected bridge bytes    179147
```

Only the independently owned `rust_restore_original_template_error` and
`rust_replacement_cache` change. The real Rust parser, compiler, matching
engine, original subject ownership, existing 17-line captured-result fast path,
callable replacement handling, zero-width matching, and the corrected public
Python adapter remain intact. The source verifies the exact reference
`subject SIMPLE, subject SIMPLE, replacement FULL_READONLY` ordering and
strict reverse release order.

The nine original source owners are individually authenticated. The Rust
package has one package and zero external crates. Each future private build
phase uses `--release --locked --offline --frozen`, a fresh owned source
snapshot, the complete corrected bridge, the actual corrected adapter, and
the original engine. Both independent phases must produce byte-identical
native engine and bridge artifacts. All **28** distinct processes and all
compiler, symbol, dynamic-section, and complete-ELF roles must actually pass.

A future successful build proves reproducible native compilation and root
provenance **only**. It does not prove Python compatibility, runtime matching
independence, undefined-behavior safety, or speed. The actual matching tests
remain a separate gate.

## Safe, independently reproducible source-only gates

Use exactly the frozen stable CPython 3.14.6 interpreter:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
```

Independently hash the three new files:

```text
tools/reproduce_owned_rust_capture_shape_semantics_source_build_v22.py
oracle/phase2/RUST-CAPTURE-SHAPE-SEMANTICS-SOURCE-BUILD-V22.md
oracle/phase2/rust-capture-shape-semantics-source-build-v22.json
```

Run both exact source-only modes with three independent pins:

```text
python3.14 -I -B -S \
  tools/reproduce_owned_rust_capture_shape_semantics_source_build_v22.py \
  --self-test --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

python3.14 -I -B -S \
  tools/reproduce_owned_rust_capture_shape_semantics_source_build_v22.py \
  --verify-frozen-context --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
```

Repeat both under `env -i PATH=/usr/bin:/bin LC_ALL=C`. The irreversible audit
must physically reject compilation, matcher imports, candidate execution,
dynamic native loading, any compressed evidence, private build roots, source
writes, clocks, network, fabricated historical results, altered buffer flags,
omitted native source owners, and hidden benchmark data.

Only a later, explicitly root-authorized invocation of `--build`, supplying
the exact complete nine-source authority and every independently frozen hash,
may create the two actual private phases. A genuine failure is preserved. A
genuine success exclusively creates and synchronizes a separate public build
receipt and a separate root-provenance receipt; it restores and verifies all
nine canonical source identities.

The **31,237** original cases in **13** groups remain separate from the
additional **8,244** differential cases. The **14,155,776**-case speed
comparison remains **NOT GENERATED and NOT OPENED**. Correctness, speed,
memory, confidence, undefined behavior, and qualification of this new native
variant remain **NOT MEASURED**. No winner exists.
