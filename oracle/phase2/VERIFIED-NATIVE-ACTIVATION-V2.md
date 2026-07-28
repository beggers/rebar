# Crash-safe activation of independently built native regex engines

Freeze, commit, and push this protocol and
[`../../tools/activate_verified_native_candidate_v2.py`](../../tools/activate_verified_native_candidate_v2.py)
before activating a native candidate. The tool is a standalone, source-only
verified successor: it does not import the earlier activator, a build recorder,
a candidate, an extension, or an outside regular-expression engine. Its
`--self-test` is synthetic. A passing self-test is not a source build, a
candidate import, a correctness result, or a speed measurement.

The immutable reference remains stable CPython 3.14.6: all **31,237** original
checks across **13** independently passed suites. The expanded final holdout
remains **NOT GENERATED; NOT OPENED**. Candidate correctness and speed are
**NOT MEASURED** by this protocol.

## Two exact, explicitly selected build versions

Every real command supplies `--build-version 2` or `--build-version 3`. A
version is never guessed, rewritten, or accepted using another version's
source, protocol, report, receipt, private-root prefix, compiler commands,
source closure, or GNU symbol evidence.

Version 2 uses only:

- Source `tools/reproduce_phase2_native_builds_v2.py`, SHA-256
  `e822e22cf6a5bbbdc2b634209c6e185ca74ebc55d86828ebea77bb5d44ce3796`.
- Protocol `NATIVE-SOURCE-BUILDS-V2.md`, SHA-256
  `f383c2ca419c18cf77451c855b53593bb97ea7fa83c90d5d133a80de043aa603`.
- Report schema `rebar-phase2-independent-native-source-build-v2` and roots
  `/tmp/rebar-phase2-native-build-v2-FAMILY-UNIQUE`.
- Genuine reproducible C archive
  `4d954992312a039daa46a2810e51fc29cfdd2bd49d159dc834f5bf003e456878`
  and receipt
  `e90b4c12a087c0e8864c1627e242be18bd779f9d9693ec711f7dd575288eda24`.
- Genuine reproducible Rust archive
  `69b645c14ca3e566256f5a5b393a6d18554ad347b97b542383db3d86681bb35d`
  and receipt
  `15580e4441ce651c21800df187fcfaa88ec9336322348a07d84544094d5b050e`.

Version 3 uses only:

- Source `tools/reproduce_phase2_native_builds_v3.py`, SHA-256
  `c33d8e89c4b86f06e7cc06ecef9bca7052af86191d2e09ac89e665500147ba6f`.
- Protocol `NATIVE-SOURCE-BUILDS-V3.md`, SHA-256
  `273e5de944b661ec1f5cfbe3a26bcabc2e9b8c04353891fcfb822b07955eace3`.
- Report schema `rebar-phase2-independent-native-source-build-v3` and roots
  `/tmp/rebar-phase2-native-build-v3-FAMILY-UNIQUE`.
- Genuine reproducible Zig archive
  `485fcf3434d2c46088f8e358ce43a34aee63e3f4aacb878e63109279afb2c46c`
  and receipt
  `050f0156647c90ed03ebffe7d530e0a9f56d605f3728df618c85dc2f8ae570e8`.
- Exactly one compiler-native `-fstrip` in each actual Zig engine command;
  distinct source, temporary, local-cache, global-cache, and output directories;
  all **15** genuine compiler and ELF-inspection processes; and complete
  authenticated versioned GNU dynamic-symbol streams.

The original version-2 Zig result is a **genuine failure**, not an acceptable
engine. Preserve its archive
`dc5128aaaf8a4d915c57ea8770696db3dc7ca51c89d5a3570cab9d259d070a0e`,
receipt `97e3150e9b68d3031c96ea6e973097687c80163a371f99a67f8b3de08bc0707a`,
both different source-built engine hashes, and all 15 actual successful
compiler/inspector processes. Its receipt's `status = PASS` means only that
the **failure was durably published**. A qualifying native build requires all
three of `report.status = PASS`, `receipt.status = PASS`, and
`receipt.build_status = PASS`.

Before any promotion or recovery, independently reread and authenticate all
three original V2 archives and receipts. Reparse every genuine process and
complete ELF stream: **8 C**, **16 Rust**, and **15 failed Zig**, for exactly
**39** preserved processes. A V3 record must preserve exactly those actual
three historical outcomes. Never call a GNU version-index token such as `(2)`
a native symbol; preserve the recorded falsification of the original V1
symbol parser.

## Seven exact identity fields; independent durability evidence

A no-follow file reader returns exactly these seven typed identity fields:

```text
relative, path, sha256, size_bytes, device, inode, mode
```

A published intention also records four separately authenticated durability
facts:

```text
exclusive_creation
same_inode_readback_verified
file_fsync_completed
directory_fsync_completed
```

Its original `write_calls` must be a real positive `int`, not `True`, `False`,
zero, a float, or a string. Compare the seven identity fields separately from
the additional durability metadata. Comparing a bare file-owner dictionary
with the richer published intention falsely rejected the actual original C
run before **zero** of its 31,237 candidate checks; retain that recorded
failure and do not repeat it. The authenticated activation report and distinct
receipt supply the genuine durable flags. A later disk read cannot invent a
past fsync.

The recovery directory must be a fresh, same-owner, no-follow, mode-0700 root:

```text
/tmp/rebar-phase2-verified-native-activation-v2-FAMILY-UNIQUE
```

Its recovery journal, intention, backup, report, and receipt are separately
created, owner-only, mode-0600, synchronized files. Compiled source outputs
are **not** required to have mode 0600 or 0755. Preserve each originally
present canonical binary's exact actual permission mode; use 0755 only for a
genuinely originally absent executable. An existing canonical binary is
rollback evidence only; it is never proof of how the candidate was built.

## Individually crash-safe canonical promotion

The only permitted targets are:

```text
C:    candidates/_vm_native.cpython-314-x86_64-linux-gnu.so
Rust: candidates/_rust_engine.so
      candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so
Zig:  candidates/_zig_probe.so
      candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so
```

Before touching a target, authenticate the immutable objective, frozen full
oracle, original guard sources, exact build-version owner closure, original
historical evidence, exact caller-pinned passing archive and receipt, all
actual compiler commands and environment, all GNU dynamic-symbol streams, and
both matching source-phase binaries on distinct real inodes.

Write, fsync, and reread every exact original native backup. Exclusively write
and fsync the complete pre-promotion recovery journal. Stage the genuine
source-built bytes in a fresh adjacent file, preserve the exact original
mode, and recheck the real staged hash, size, device, and inode. Exclusively
write and fsync its mode-0600, per-role staged-inode intention; fsync the
recovery directory. Only then use a directory-descriptor-bound, same-directory
atomic replacement and synchronize the candidate directory.

Rust and Zig each have two **individually** atomic promotions. Do not claim
that replacing two files is group-atomic. A process killed after either
replacement can recover from the original journal without an activation
report or receipt. Recovery authenticates the unchanged original sources,
all 39 actual preserved history processes, the exact passing versioned build,
both real source-phase binaries, staged intention, canonical inode, and
owner-only backups before changing anything. It restores verified roles in
reverse order, preserves original modes, and never overwrites or removes a
changed or unrelated user file.

## Explicit pinned commands

After this source and protocol have independently been committed and pushed,
activate only with actual observed hashes and source-owner pins:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/activate_verified_native_candidate_v2.py --activate \
  --family FAMILY --build-version 2-OR-3 \
  --build-label ACTUAL-LABEL --build-root ACTUAL-PRIVATE-BUILD-ROOT \
  --activation-source-sha256 ACTUAL-ACTIVATION-SOURCE-SHA256 \
  --activation-protocol-sha256 ACTUAL-ACTIVATION-PROTOCOL-SHA256 \
  --build-source-sha256 EXACT-SELECTED-BUILD-SOURCE-SHA256 \
  --build-protocol-sha256 EXACT-SELECTED-BUILD-PROTOCOL-SHA256 \
  --build-report-sha256 EXACT-PASSING-ARCHIVE-SHA256 \
  --build-receipt-sha256 EXACT-PASSING-RECEIPT-SHA256 \
  --native-engine-sha256 ACTUAL-ENGINE-SHA256 \
  --native-bridge-sha256 ACTUAL-BRIDGE-SHA256 \
  --native-engine-bytes ACTUAL-ENGINE-BYTES \
  --native-bridge-bytes ACTUAL-BRIDGE-BYTES \
  --owned-source-sha256 RELATIVE/PATH=EXACT-SHA256
```

Repeat `--owned-source-sha256` exactly once for every family-owned source.
For C, engine and bridge arguments both denote its one extension. A genuine
reportless restart requires only:

```text
--recover --family FAMILY --build-version 2-OR-3 \
--activation-root EXACT-PRIVATE-ACTIVATION-ROOT \
--activation-source-sha256 EXACT-ACTIVATION-SOURCE-SHA256 \
--activation-protocol-sha256 EXACT-ACTIVATION-PROTOCOL-SHA256 \
--recovery-journal-sha256 EXACT-PREPROMOTION-JOURNAL-SHA256
```

`--restore` with these journal-pinned arguments is an exact alias for
`--recover`. After successful publication, a separately report-pinned
`--restore` instead takes the same family, build-version, private root,
activation source and protocol arguments, plus
`--activation-report-sha256` and `--activation-receipt-sha256`.

## Reproduce the source-only safety gate

Neither command reads a candidate, archive, native binary, benchmark, or
holdout. Both actively block file operations, imports, subprocesses, threads,
network connections, environment access, and clocks:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/activate_verified_native_candidate_v2.py --self-test

env -i PATH=/usr/bin:/bin \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/activate_verified_native_candidate_v2.py --self-test
```

The synthetic gate covers all three language families, both exact build
versions, both fresh phases, all original permission modes, originally absent
targets, cross-version source/schema/archive substitutions, all exact compiler
commands and environments, actual GNU version parsing, all seven typed owner
fields, all four durability flags, positive typed write counts, archive and
receipt failures, original Zig failure classification, and reportless crash
recovery.

**Current status:** the protocol is source-only. Version-two activation,
restoration, recovery, actual candidate execution, final holdout, speed,
memory, and winner selection remain **NOT MEASURED**.
