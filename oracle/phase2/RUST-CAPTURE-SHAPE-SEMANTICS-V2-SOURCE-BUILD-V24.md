# Reproduce the first-party corrected Rust bridge without an external engine

Status: **SOURCE FROZEN; ACTUAL NATIVE BUILD IMPLEMENTED BUT NOT RUN;
CORRECTNESS NOT MEASURED.**

This chunk freezes the root-authorized, operational first-party V24 native
build. A source-only check does not run it. An actual build is allowed only
after these three V24 files are committed and pushed, and only when the root
explicitly invokes the independently pinned `--run` or `--build` command.

## Preserve the complete pushed correction

Authenticate and embed every byte of the preceding V23 source-build freeze:

    tools/reproduce_owned_rust_capture_shape_semantics_v2_source_build_v23.py
    d4d27b33423fea02cc74529ea279fe02776447f40c5a8d83022004d2af3f771b

    oracle/phase2/RUST-CAPTURE-SHAPE-SEMANTICS-V2-SOURCE-BUILD-V23.md
    3fb90120ff21a6cafe1f6ce24c7e4d1d08e1327b98b980e69c0eb0295ae48520

    oracle/phase2/rust-capture-shape-semantics-v2-source-build-v23.json
    e4138ea585eefc0a22c254b21f761a2d9795fef4ff914b2368178e7c8e392028

The actual, complete privately overlaid bridge is the existing first-party
source, not a package, engine wrapper, copied artifact, or failed V22 bridge:

    candidates/rust/variants/
      buffer_shape_pickle_findall_captures_semantics_v2/py_bridge.c
    1adb6bcecfa0b2fa80403e1c2caf372916466e8b9d0516980e60aef6a9ac08f0
    178860 bytes

Re-derive it from the complete captured-findall `a0b9…` predecessor. Remove
only the uniquely located, 660-byte outer-length rewrite; preserve the entire
original replacement cache, its original 97-byte replacement branch, the
complete 17-line captured-findall path, and the first-party Rust matching
engine. Reject the known failed `f9bd…` bridge.

Use only the authenticated first-party private adapter bytes:

    d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e
    31934 bytes

Do not execute the old adapter-repair source: it imports standard-library
`re`. Obtain the genuine adapter and all nine original source bytes from the
independently authenticated operational V21, V16, and V9 source lineage.

## Record the real original results

Preserve all 435 V22 obligations, 402 inherited V21 obligations, and the full
96-field real V22 failure receipt:

    7013c42f6309d94e094dd89cc8e9f24fe245c0cba5ca4791d35ffe5fa2b7dad7

The historical candidate failed. Of 31,237 original cases in 13 groups with
13 named private waivers, 14,725 genuinely passed before the 13th group failed.
The 42 managed-buffer, 352 substitution, and 1,624 shape-changing mismatches
make **2,018 an observed lower bound**, not a complete global count.
The global mismatch count remains **NOT MEASURED**.

The actual failing worker was PID 188. It imported one candidate, loaded two
native libraries, recorded zero successfully returned children, zero installed
child guards, and zero executed child cases. Whether a child was transiently
created remains **NOT MEASURED**. Its actual warning counts are one remaining
interpreters warning and 16 destructor warnings. Keep the 8,244 supplemental
and 6,912 separate corrected-reference cases outside the original denominator.

## Actual native build, never a source-only simulation

A root-authorized actual run uses the previously authenticated, operational
first-party V16 controller and genuine V9/V7 compiler kernel. Both independent
private phases, `reference-a` and `reference-b`, run all 14 ordered,
independent real compiler or ELF-inspector processes:

    readelf_version
    gcc_version
    rustc_version
    cargo_version
    build_rust_engine
    build_rust_bridge
    engine_dynamic
    engine_symbols
    bridge_dynamic
    bridge_symbols
    engine_sections
    engine_notes
    bridge_sections
    bridge_notes

A successful build requires 28 genuinely observed, distinct, successful
process IDs. Each phase receives a fresh, private nine-source snapshot with
exactly one complete `1adb…` bridge overlay and one complete `d47…` adapter
overlay. The original verifier must compare the complete independently built
engine ELF bytes and complete independently built bridge ELF bytes. Native
libraries are not loaded and candidate matching is not run.

Use the exact absolute Rust 1.95.0 tools, not the shell default:

    /home/dev-user/.rustup/toolchains/
      1.95.0-x86_64-unknown-linux-gnu/bin/rustc
    /home/dev-user/.rustup/toolchains/
      1.95.0-x86_64-unknown-linux-gnu/bin/cargo
    /usr/bin/x86_64-linux-gnu-gcc-13
    /usr/bin/x86_64-linux-gnu-readelf

Cargo must run `build --release --locked --offline --frozen` against the
private manifest and private target. The Rust package has one first-party
package and **zero external dependencies**. Use the frozen reproducible phase
environment, both source-prefix remaps, `CARGO_NET_OFFLINE=true`, one job,
pinned CPython 3.14.6 headers, GCC 13, ELF hardening, and `$ORIGIN`.

Caller-pin the V24 source, protocol, and contract; the exact 48-character
label `phase2-v24-rust-capture-shape-v2-root-provenance`; the complete V2
bridge and adapter; all three complete V23 build owners; all three passing
phase-one V4 owners; and each of the nine original canonical Rust owners.
No weakly pinned or implicit actual build is allowed.

Actual mode authenticates the original bridge source, original public
adapter, installed original engine, and installed original bridge before and
after the build. A successful publication requires all four complete hashes,
file identities, permissions, and timestamps to remain unchanged. Source-only
mode must not open or probe either installed native file.

Publish actual success and failure into separate freshly created,
no-follow, exclusively written and fsynced V24 archive and publication
receipt paths. A failed build reports its genuine partial process count and
never publishes successful root provenance. Publish the separate root
receipt only after checking a genuine successful 28-process receipt, both
complete independent ELF comparisons, a live owned private 0700 directory,
and all four restored original runtime identities. Never open a historical
archive or the newly written compressed archive.

## Reproduce only the source gates

Use:

    /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

Independently pin the three V24 files. Run `--self-test` and
`--verify-frozen-context` normally and under
`env -i PATH=/usr/bin:/bin LC_ALL=C`, always using `-I -B -S`.

Source mode installs its irreversible deny-default wall before reading any
predecessor. Its bounded hostile controls preserve every V22 obligation and
the complete V23 frozen build; reject changed complete source, the failing
`f9bd…` variant, external packages or matchers, missing actual build pins,
private roots, installed native files, candidate imports, process creation,
clocks, archives, network, and the sealed holdout.

An implemented actual command is not an executed build. Until the root
runs it after push, compiler processes are **0**, candidate workers are
**0**, actual native output hashes and receipt hashes are **NOT MEASURED**,
and the build remains **NOT RUN**. Compatibility, runtime non-delegation,
undefined-behavior safety, performance, memory, confidence intervals,
qualification, and any winner remain **NOT MEASURED**. The proposed
14,155,776-case holdout remains **NOT FROZEN; NOT GENERATED; NOT OPENED**.
