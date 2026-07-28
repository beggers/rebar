# Build the corrected first-party Rust implementation twice

This is a source freeze, not a build, correctness claim, or speed measurement.
It records how to build the Rust implementation entirely from the project's
own source after correcting the real flag-order failure found in CPython's
original tests. The older build, its failing adapter, and every existing
failure remain independently visible.

## Preserve the actual result

CPython 3.14.6 remains the isolated reference. The frozen correctness
denominator is unchanged: 13 original groups, 31,237 counted checks, and 13
explicitly named private exclusions.

The released version-30 overview contains 149 real evidence files and 154
authenticated history references. The actual Rust result is 1,087 mismatches
and 7,438 passing checks. C has 1,230 mismatches and 7,325 passing checks;
its historical 1,262 mismatches remain recorded. Zig has 2,172 mismatches
and 2,847 passing checks. A separate Zig preflight started no candidate
workers and is not presented as a matching test. No candidate qualifies.

The previous Rust V11 build genuinely ran 28 compiler and binary-inspection
processes and built two independent private phases. Its bridge had SHA-256
`4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257`.
Its public adapter had SHA-256
`81089bab906c9bb511fe0779d8e1ddf735850fce62eaac06ca1e6c678856578c`.
Both the complete compressed evidence archive and independently durable
publication receipt are preserved. The archive is authenticated as raw
compressed bytes and is never decompressed by a source-only gate.

## Correct the actual flag-order error without borrowing an engine

Use the independently frozen first-party bridge repair V1, and use the
independently frozen first-party public-adapter repair V2. The corrected
public source must have exactly 31,464 bytes and SHA-256
`f8afb6c6e020faad3452b59ceb84abc957ee74d1397397008b3178856abe01a5`.
Never substitute the earlier `81089…` adapter. Neither derived source is
installed into the workspace, loaded, imported, or run in this chunk.

The semantic parser, compiler, and execution engine remain the project's own
Rust. The interface remains the project's own C bridge and Python adapter.
The frozen Cargo lock has exactly one project-owned package and no outside
dependency. The implementation may not call `re`, `_sre`, another candidate,
an external regex package, a fallback engine, or a prebuilt native binary.

## Freeze a genuinely independent two-phase build

An actual build is allowed only after an explicit `--build` supplies all nine
original source hashes, the exact corrected bridge hash and byte count, and
the exact corrected public-adapter hash and byte count. Its fresh private
directory must start with:

    /tmp/rebar-phase2-native-build-v9-rust-

Create `reference-a` and `reference-b` as separate owner-only `0700` trees
before either source repair. In each tree, copy seven original files and
create each of the two corrected overlay files exactly once using exclusive,
no-follow `0600` creation. Reauthenticate every complete overlay and every
distinct source inode. Never change an original file.

The V12 implementation owns its snapshot and reproduction checks. It uses
only the pinned V9 and V7 low-level build primitives. It never calls the
V10 or V11 high-level build, stale-history context, old snapshot, or
old-adapter reproduction helpers.

Pin and stream-authenticate the exact installed `rustc`, `cargo`, GCC, and
`readelf` files without running them. A later build must use offline, locked,
frozen Cargo and run exactly these 14 successful, distinct processes in
each independent phase:

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

Compare complete engine and bridge bytes across the genuinely different
phase inodes. A native build does not demonstrate Python compatibility.

A later actual build publishes exactly one fresh, zero-timestamp compressed
report and one independently durable receipt under the distinct
`native-source-build-v12-rust-` prefix. Only after those real files have been
created can the evidence and history totals increase from 149/154 to
151/156. Preserve failed builds as explicitly named failure evidence.

## Source-only gates

Run the source-only self-test and the frozen read-only context in both the
ordinary and empty environments, with pinned CPython's `-I -B` flags and all
three exact V12 owner hashes. The self-test physically blocks filesystem
access, writes, processes, candidate imports, networking, threads, clocks,
native loading, locks, signals, and archive decompression. It exercises
every source owner, both independent phases, all 28 ordered process slots,
the stale adapter, stale denominators, and hostile boundary violations.

Read-only verification authenticates the immutable original goal, the
complete P0 denominator, current released graph, original source owners,
both independently frozen repairs, actual V11 history, low-level source
kernels, and exact compiler files. It never executes a compiler, decompresses
an archive, constructs a private snapshot, writes evidence, reads or stats a
canonical native target, runs a candidate, samples a clock, opens the final
holdout, or selects a winner.

Corrected Rust compatibility, undefined behavior, speed, confidence
intervals, and memory remain **NOT MEASURED**.
