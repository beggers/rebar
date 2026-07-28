# Rust: two independent private repairs before a future source build

This is a source freeze. It does not build, run, activate, qualify, or measure
a regular-expression replacement.

The purpose is to make one genuinely first-party Rust implementation ready for
a later, separately authorized correctness experiment. It combines our
existing buffer-order repair with our existing Python public-interface repair
without changing either repair, the original Rust engine, or any tracked
candidate.

## What remains fixed

The reference is CPython 3.14.6 with all 13 original groups, 31,237 counted
checks, and 13 explicitly named private exclusions.

The current published results are version 23: 135 distinct counted evidence
owners and 140 signed history references. Its 30 actual C evidence owners
prove that 13 real C workers ran all 31,237 checks, passed 7,325 checks,
reported 1,262 mismatches, had zero infrastructure failures, and restored the
original C native library. C did not qualify. The original Rust results also
remain unchanged: 2,042 mismatches, 7,461 passing checks, and five failed
groups. No earlier failure is erased or turned into a success.

All nine original Rust files, the immutable goal, the original test matrix,
the complete version-23 chart, the version-9 native builder, and the six
separately published repair files are individually authenticated. The
version-23 graph also provides 138 distinct directly signed evidence-file
paths; these are individually authenticated. The current graph's renderer
and inputs are also independently authenticated, completing an explicit
138-plus-2 signed-path closure of 140. These intermediate categories do not
change the published 135-owner or 140-reference denominators. All four
separately pinned version-22 predecessor graph files are also preserved.

The Rust manifest and lock contain exactly one locally implemented Rust
package and zero outside dependencies. No Python regular-expression engine,
external regular-expression package, other candidate, network, or fallback is
introduced.

## Both private repairs

A future build must use a fresh private root beginning exactly with:

    /tmp/rebar-phase2-native-build-v9-rust-

The version remains V10. The V9 root spelling is intentional: the already
published bridge repair safely accepts only that exact prefix. The separately
published public-interface repair accepts the same root.

Before either repair is applied, both reference-a and reference-b, their
source directories, and their nested candidate directories must exist as
separate owner-only directories with mode 0700.

For each phase, copy exactly seven unchanged Rust files. Leave both of the
following destinations absent:

    source/candidates/rust/py_bridge.c
    source/candidates/rust_candidate.py

Apply each existing first-party repair exactly once. Both use O_CREAT,
O_EXCL, and O_NOFOLLOW and produce an owner-only 0600 file whose complete
contents and inode are independently verified:

    bridge 4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257
    public 81089bab906c9bb511fe0779d8e1ddf735850fce62eaac06ca1e6c678856578c

Each phase must end with seven original files and the two repaired files:
nine independently owned private sources. The tracked originals remain
unchanged.

## A future build is not a correctness result

Only an explicitly pinned later --build may start a compiler. Cargo must use
--release, --locked, --offline, --frozen, an independently owned private
target, isolated CARGO_HOME, and CARGO_NET_OFFLINE. No package is downloaded.

There are exactly 14 real compiler and native-inspection processes per phase,
or 28 real processes across the two phases. Both complete native outputs must
be inspected and compared byte-for-byte across genuinely separate files.
Evidence and durable receipts use the distinct V10 naming. A successful build
still means Rust matching correctness, performance, memory, and undefined
behavior are NOT MEASURED.

The four source-freeze gates are the ordinary and minimal-environment forms
of --self-test and --verify-context. They start no compiler, create no
snapshot, apply no repair, import no candidate, load no native library, open
no holdout, take no timing sample, and select no winner.
