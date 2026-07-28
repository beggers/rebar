# Freeze the evidence-backed Zig scanner correction

This freezes one change to a first-party Zig implementation. It does not build,
load, or run an engine. It does not change an original candidate file. The
complete corrected candidate is **NOT MEASURED**.

## The observed problem

The first actual failing public scanner example is
`rust-public-practice.v1.0031`. Python's scanner exposes the complete branch
match `alpha42` as group 1, with span `[0, 7]`. The first Zig repair instead
exposes its nested `alpha` capture, with span `[0, 5]`.

The previous V1 source overlay replaced the original unconditional branch
assignment with a conditional assignment. When a nested capture already occupies
the branch slot, the condition prevents the required whole match from replacing
it. V2 reverses exactly that 246-byte conditional block and restores the exact
190-byte unconditional original. Nested captures in other slots, range checks,
branch selection, the final group number, the Zig engine, buffer handling,
substitution, and all other source bytes remain unchanged.

The defective, privately derived V1 bridge is 173,082 bytes:

    a5ab490d0cfcbba295b68f3f738a1c6371ef3314e9a6c01cdcc0bb5978e3b148

The corrected bridge is byte-for-byte the original 173,026-byte
`candidates/zig/py_bridge.c`:

    67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b

The removed conditional block is 246 bytes:

    7a7fa3a9a16d9dae07e74845984bbd36d17309c1f06ddb091d6d3986b4e27177

The restored whole-branch block is 190 bytes:

    42009e889c83ee06194f14223b629bb221326ce7a3ebf3efe09f5d1a76344978

The exact previous source, protocol, and contract remain present and unchanged.
V2 reconstructs both transitions in memory; verification never materializes a
candidate file.

## Keep the actual results visible

The unchanged correctness reference is stable CPython 3.14.6, 31,237 frozen
checks, 13 test groups, and 13 explicitly named private waivers. The historical
V30 graph preserves 149 distinct evidence files and 154 digest-addressed
references. A subsequently completed Rust source build added exactly two genuine
evidence files. The current totals are therefore 151 evidence files and 156
references. The historical and current counts are not interchangeable.

The new Rust archive contains a successful source build, not a compatibility
result. Its compressed bytes are verified without decompression:

    840a6403699fec44d4f725f737fc9538c997b818a48d167398ad1b95cbb9828d

Compressed size: 108,325 bytes. Its separate 2,109-byte publication receipt is:

    1cd7e538098711ddac017ee3375d302d4b1ba4e6da52d10d2a524103db500a2f

The receipt independently proves the transition from 149 evidence files and 154
references to 151 files and 156 references. Its successful result means that the
new Rust implementation was built. Matching with that build remains
**NOT MEASURED**.

The last actually tested Zig candidate still **FAILS**: 2,172 differences,
2,847 individually passing checks, 13 genuine matching workers, all 13 test
groups complete, and no infrastructure failures. Its first attempted run
started zero matching workers. The latest actually tested Rust and C candidates
still have 1,087 and 1,230 differences respectively. A receipt's successful
publication does not
mean a candidate passed. Zero candidates are qualified.

V2 authenticates the original matching result using its small, independently
pinned publication receipt and the complete version-19-through-version-30 graph
chain. The historical chain contains exactly 124 oracle evidence references and
30 experiment references. The two genuine new Rust build records increase those
counts to 126 oracle references and 30 experiment references. Verification
hashes only the exact pinned compressed Rust build archive; it never decompresses
that archive and never opens a compressed matching-failure archive, native
library, hidden test, benchmark file, or compiler executable.

No external regular-expression package, Python regular-expression engine, other
candidate, candidate wrapper, compiler process, network, clock, or matching
worker is used. The planned 4,194,304-case final comparison is **NOT GENERATED**
and **NOT OPENED**. Speed, confidence, memory, undefined behavior, and corrected
candidate compatibility are **NOT MEASURED**. There is no winner.

## Independently pinned source-only gates

Use only:

    /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B

Independently supply the exact SHA-256 of all three V2 files. Run each source
self-test twice, once in the ordinary environment and once using
`env -i PATH=/usr/bin:/bin LC_ALL=C`:

    python -I -B tools/apply_owned_zig_scanner_capture_source_repair_v2.py \
      --self-test \
      --source-sha256 SOURCE_SHA256 \
      --protocol-sha256 PROTOCOL_SHA256 \
      --contract-sha256 CONTRACT_SHA256

Run the same two environments with `--verify-frozen-context` in place of
`--self-test`. Replace `python` with the exact absolute interpreter above.

The source-only test proves the historical `[0, 5]` branch, the restored
`[0, 7]` branch, and preservation of an independently positioned nested
`[0, 5]` capture. Hostile controls reject incorrect blocks, source hashes,
unsafe private roots, overwritten destinations, stale historical counts claimed
as current, duplicate build owners, altered publication evidence, candidate and
native imports, unauthorized compressed archives, external engines, holdout
access, network, workers, and performance clocks.

## Future private application

`--apply` is a separate future operation and is not run by this freeze. When
explicitly authorized, its only destination is a new, exclusive mode-0600 file
inside one of two distinct owner-only mode-0700 phase trees:

    /tmp/rebar-phase2-zig-scanner-capture-source-build-v2-PRIVATE/
      reference-a/source/candidates/zig/py_bridge.c

The same rules apply to `reference-b`. Both phase directories must exist, have
distinct real directory identities, and belong to the current user. Writes use
`O_CREAT | O_EXCL | O_NOFOLLOW`, verify the same inode and its complete SHA-256,
and synchronize the file and its containing directory. The original candidate,
original engine, original adapter, previous experiment, all native libraries,
and the final holdout must remain unchanged.
