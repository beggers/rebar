# Freeze the next Rust correctness test without inventing a repaired build

Status: **SOURCE FROZEN; CORRECTED BUILD AND ORIGINAL CAMPAIGN NOT RUN.**

This is a prospective correctness campaign for a Rust regular-expression
implementation built from scratch. It does not wrap a package, delegate to
Python's `re`, reuse another candidate's matcher, run a candidate, or claim a
corrected build exists. Actual running, worker creation, and recovery remain
blocked until a real corrected first-party source, native build, and root
receipt have been separately committed and independently authenticated.

## Keep the actual results intact

The complete published V22 original-test receipt is 47,336 bytes:

    7013c42f6309d94e094dd89cc8e9f24fe245c0cba5ca4791d35ffe5fa2b7dad7

Publication succeeded; the candidate **failed**. Thirteen real workers
attempted all 13 original groups. Twelve groups completed, nine passed, and
exactly 14,725 original cases were verified as passing. The observed
differences were 42 managed-buffer cases, 352 replacement cases, and 1,624
shape-changing-buffer cases. Their sum, 2,018, is only a lower bound. The
128-case interpreter group never completed, so the total mismatch count is
**NOT MEASURED**.

The actual failing interpreter worker was process 188. Its genuine history
includes one candidate import and two native-library loads; the source-only
V23 verifier must not erase those historical facts. It recorded no
successfully returned child interpreters, installed child guards, or executed
child cases; whether a native child was transiently created before the guard
failed is NOT MEASURED. Its complete diagnostic contains one
remaining-interpreters warning and 16 destructor warnings, scoped solely to
that worker. The actual nested failure is:

    244b82a3f2ea842d2e154214b5094b08b8ec7fa3ea17b54a3a86734d3f1d442c

Preserve the entire 435-field V22 contract, not a selected subset, including
all 402 inherited V21 obligations:

    source   e88f242835781e9b70efa18e68a7b06b0b9368e91320ed596995ef0e16370c61
    protocol c6a2a5db9c9c27974c29af01b3d7f7042bae73e254c638fe27813505ef11f396
    contract f1c021049e4bb173be8d47339920354e02c8c0194aead877b8474a128b5e158a

Embed the complete 96-field V22 failure receipt and the complete prior V20
failure receipt. V20 verified 15,749 passing cases and observed 240
replacement and 1,056 shape differences. Its complete mismatch total is also
**NOT MEASURED**.

## Describe the correction without pretending to build it

Authenticate the complete independently frozen V2 symbolic correction:

    source   e285d0c39950f7ffc5929f0c5f5a0708b8c3e8878b655255cb29e1b0725233c2
    protocol 999e8cdf9f7a7b0fbaca67759d8c0a13f49c7ca10c753539010d11681a1aaa8d
    contract cafb121e38ed738c51d30978a22ddf788eafd729b2a145a8f3564ea97412e673

The already tested `f9bd…` bridge is known to fail. Its 384-byte replacement
branch contains a 287-byte over-broad early-return guard. The proposed change
restores the authenticated 97-byte original branch while retaining the
separate 660-byte outer-length correction. This gives only conditional anchor
arithmetic:

    179,520 - 660 = 179,147 - 287 = 178,860

No whole corrected source is read or materialized. Its actual byte count,
whole-file hash, native-engine hash, native-bridge hash, build receipt,
root receipt, candidate correctness, memory, and speed are **NOT MEASURED**.
Never present 178,860 as an observed source size. Never pass off the old
`f9bd…` build as repaired.

The original correctness boundary remains exactly 31,237 cases in 13 groups,
with 13 named private waivers. Keep the 8,244-case differential reference and
the distinct 6,912-case corrected reference outside the original denominator.
All 13 future V23 groups are **NOT RUN**. The future genuine child requirement
is 11 interpreters, 394 case calls, and 416 total calls; no V23 child has been
created or executed.

## Authenticate first-party isolation

Authenticate the entire operational V3 runtime guard and the exact public
V2 guard and V5 producer owners without executing those controllers:

    V3 guard source   03f051e428ee31bb671d8ced82f02d7a9fe3520f24191aba78d2e8a0697202c2
    V3 guard protocol d3437b642d322ccccf12851981555cb596ff7f9c5a12e0a6a389d6b80b5a068a
    V3 guard contract 31e9a5d2754b5b4b273d4fc30d6a27967e495b57684fdd1e9306bbac3b2caaa7

Preserve all 14 required native-owner fields and forbid standard-library
matching, `_sre`, external regular-expression packages, cross-candidate
engines, and fallback. Runtime non-delegation remains **NOT ESTABLISHED**
until a real candidate runs under the independently attested guard.

Install a new physical, deny-by-default V23 audit wall before reading the
first predecessor byte. Permit only the three V23 public files, three frozen
V2 files, 18 previously frozen public plaintext owners, and the exact nine
V3-guard, V2-guard, and V5-producer owners. Read each complete owner through
tracked, no-follow descriptors and verify its device, inode, owner, mode,
length, link count, and independently supplied hash.

Reject direct Python and native file opens, foreign descriptors, metadata
probes, candidate paths, historical variant captures, private roots,
compressed archives, phase-three proposals, hidden holdouts, traversal,
clocks, entropy, network, native loading, subprocesses, and untrusted dynamic
execution. Do not instantiate or execute the older V22 campaign or its source
wall. Reuse only the independently authenticated public V2 controller under
the stricter new wall.

## Reproduce the source-only checks

Use the independently pinned CPython 3.14.6 with `-I -B -S` and supply each
frozen source, protocol, and contract hash independently:

    python3.14 -I -B -S tools/run_owned_repaired_rust_original_campaign_v23.py
      --self-test --source-sha256 SOURCE_SHA256
      --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

    python3.14 -I -B -S tools/run_owned_repaired_rust_original_campaign_v23.py
      --verify-frozen-context --source-sha256 SOURCE_SHA256
      --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

Run both with the ordinary environment and with
`env -i PATH=/usr/bin:/bin LC_ALL=C`. The self-test inherits all 240 authentic
V2 controls and separately rejects removal or alteration of every one of the
435 V22 obligations and alteration of every one of the 96 actual failure
fields. It rejects false candidate success, fabricated corrected hashes,
rewritten historical native loads, forged child execution, weakened guard
owners, extra evidence, hidden holdouts, and forbidden matchers.

`--run`, `--worker`, and `--recover` deterministically fail before wall
installation, file access, candidate access, or metadata access:

    actual V23 rejected: corrected V2 native build and authenticated
    root receipt not yet available

The proposed 14,155,776-case expanded holdout is **NOT FROZEN; NOT GENERATED;
NOT OPENED**. Performance, confidence intervals, rankings, regressions,
memory, qualification, and a winner are **NOT MEASURED**. A successful
source-only check establishes an honest reproducible freeze; it does not
establish a repaired candidate.
