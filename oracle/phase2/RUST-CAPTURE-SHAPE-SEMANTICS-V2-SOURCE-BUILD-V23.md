# Freeze the complete from-scratch Rust correction before building it

Status: **COMPLETE FIRST-PARTY V2 SOURCE MATERIALIZED; NATIVE BUILD NOT RUN;
CORRECTNESS NOT MEASURED.**

This chunk creates and authenticates a complete new, independently owned Rust
bridge source. It does not alter an existing candidate, import a matcher,
start a compiler, build a native library, execute a test worker, read an
archive, create a private build directory, open the final holdout, or claim a
faster or compatible replacement.

## The actual new first-party source

The new file is:

    candidates/rust/variants/
      buffer_shape_pickle_findall_captures_semantics_v2/py_bridge.c

Its genuinely materialized, complete SHA-256 and byte count are:

    1adb6bcecfa0b2fa80403e1c2caf372916466e8b9d0516980e60aef6a9ac08f0
    178860 bytes

Authenticate the exact complete predecessor without modifying it:

    candidates/rust/variants/
      buffer_shape_pickle_findall_captures_v1/py_bridge.c
    a0b9e7fbfc92da4c3b97608cf156fb0ca2f94fb5358901b7b6baa0a819fffc8a
    179520 bytes

Within the uniquely bounded `rust_restore_original_template_error` function,
remove exactly the already frozen 660-byte `OUTER_LENGTH_REWRITE`. Derive
the entire new file again from the pinned original and require byte-for-byte
equality with the actual materialized variant. Keep the entire
`rust_replacement_cache` byte-identical, including its 97-byte original
replacement branch. Never introduce the previously tested and failing
384-byte replacement branch from the `f9bd…` bridge.

Preserve the complete original 17-line two-capture fast path. Authenticate
all nine canonical Rust source owners, including the original matching engine:

    candidates/rust/src/lib.rs
    c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d

The existing canonical bridge, public adapter, and installed native targets
remain unchanged. Authenticate the native originals only through their exact
previous public receipt; do not open or probe an installed shared library.
Do not import the adapter repair: its historic source imports the standard
library `re`. Authenticate its entire frozen public source and derive its
future private-snapshot identity from the independently frozen V16 and V3
documents instead:

    corrected private adapter
    d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e
    31934 bytes

## Preserve what the actual original campaign established

Authenticate and embed the complete factually corrected original-campaign
freeze, its complete 435 V22 obligations and 402 inherited V21 obligations,
and the entire 96-field actual V22 failure receipt:

    actual failure receipt
    7013c42f6309d94e094dd89cc8e9f24fe245c0cba5ca4791d35ffe5fa2b7dad7

The historical publication passed; the historical candidate failed. All 13
original groups started, 12 completed, and 14,725 cases were verified as
passing. Exactly 42 managed-buffer, 352 replacement, and 1,624 shape-changing
differences were fully observed. Their 2,018 sum is a lower bound, not the
global mismatch count. That count remains NOT MEASURED.

Worker 188 genuinely imported one candidate and loaded two native libraries.
It recorded no successfully returned child interpreters, installed child
guards, or executed child cases; whether a native child was transiently
created before its guard failed is NOT MEASURED. Preserve its one
remaining-interpreters warning and 16 destructor warnings, scoped to that
actual worker alone.

Retain exactly 31,237 original cases, 13 groups, and 13 named private
waivers. Keep the 8,244-case differential reference and distinct 6,912-case
corrected reference outside the original denominator. The new materialized
variant has not run any original case.

## Freeze the real offline build requirements

Reuse only the exactly authenticated original V9 first-party compiler
kernel and V16 native-build policy. The locked Rust package has one local
package and zero external crates. An actual later build must use the exact
absolute Rust 1.95.0 toolchain:

    /home/dev-user/.rustup/toolchains/
      1.95.0-x86_64-unknown-linux-gnu/bin/rustc
    /home/dev-user/.rustup/toolchains/
      1.95.0-x86_64-unknown-linux-gnu/bin/cargo
    /usr/bin/x86_64-linux-gnu-gcc-13
    /usr/bin/x86_64-linux-gnu-readelf

Do not substitute the shell's default Rust version. The uniquely frozen
future build label is:

    phase2-v23-rust-capture-shape-v2-root-provenance

Build two distinct fresh phases, `reference-a` and `reference-b`. Each must
run all 14 ordered version, compilation, dynamic-section, symbols, sections,
and notes roles; a genuine success requires 28 real distinct successful
processes and complete byte equality of both independent engine files and
both independent bridge files.

Use the private-phase Cargo invocation:

    PINNED_CARGO build
      --manifest-path PHASE/source/candidates/rust/Cargo.toml
      --release --locked --offline --frozen
      --target-dir PHASE/target

Use GCC 13 with the frozen `-pthread -std=c11 -shared -fPIC -O3 -Wall
-Wextra -Werror` hardening, reproducible source-prefix maps, pinned CPython
3.14.6 headers, the privately overlaid authenticated `1adb…` bridge, the
first-party Rust engine, and a `$ORIGIN` runpath.

Set `CARGO_NET_OFFLINE=true`, disable Cargo incremental builds, use one
Cargo job, set `LC_ALL=LANG=C`, `TZ=UTC`, `SOURCE_DATE_EPOCH=1`, both
cross-phase remapping flags, and independent phase-local `TMPDIR`, Cargo
homes, targets, and source snapshots. No standard-library matcher, `_sre`,
external regular-expression engine or Rust crate, cross-candidate engine,
network access, or matching fallback is allowed.

An actual build requires a separately committed and pushed freeze and
explicit root authorization. Until a complete and genuine 28-process
implementation is provided, both `--run` and `--build` fail before wall
installation, private-root creation, candidate access, or compilation.

## Reproduce only the source freeze

Use the official isolated CPython 3.14.6 interpreter:

    /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

Independently pin the new source-build controller, protocol, and canonical
machine contract. Run both source-only modes normally and with
`env -i PATH=/usr/bin:/bin LC_ALL=C`:

    python3.14 -I -B -S
      tools/reproduce_owned_rust_capture_shape_semantics_v2_source_build_v23.py
      --self-test --source-sha256 SOURCE_SHA256
      --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

    python3.14 -I -B -S
      tools/reproduce_owned_rust_capture_shape_semantics_v2_source_build_v23.py
      --verify-frozen-context --source-sha256 SOURCE_SHA256
      --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

The verifier installs its physical, deny-by-default wall before loading any
predecessor. It permits only complete, exact, tracked, no-follow public
evidence and the explicitly pinned first-party source files. Its hostile
controls reject a substituted `a0`, a copied failed `f9`, modified `1adb`, a
lost 17-line fast path, rewritten original losses, invented physical child
creation, an unpinned Rust toolchain, extra crates, native compilation,
direct I/O, private roots, compressed archives, candidate imports, clocks,
network, and holdout access.

The corrected source file exists; its native build does not. Native engine
and bridge hashes, new build and root receipts, runtime matching
independence, compatibility, undefined-behavior safety, speed, memory,
confidence intervals, and qualification remain **NOT MEASURED**. The
14,155,776-case proposed final comparison remains **NOT FROZEN; NOT
GENERATED; NOT OPENED**. No winner exists.
