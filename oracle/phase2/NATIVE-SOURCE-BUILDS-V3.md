# Version 3: independently reproducible from-source regex engines

Freeze, commit, and push this complete protocol and its standalone recorder,
[`../../tools/reproduce_phase2_native_builds_v3.py`](../../tools/reproduce_phase2_native_builds_v3.py),
before starting any version-three build. The synthetic `--self-test` is not a
build: it opens no files, starts no compiler or process, creates no directory,
imports no candidate, loads no native library, measures no clock, and never
reads a benchmark or hidden holdout.

The immutable pinned correctness standard remains CPython **3.14.6**:
**31,237** original reference checks, **13** suites, and SHA-256
`cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f`.
A reproducible source build authenticates source and native provenance. It is
not a candidate correctness result, a speed measurement, or permission to
open the final holdout.

## Preserve the actual published findings

Version three authenticates all of the following immutable owners **before
and after** each separately authorized real build. It replays every retained
version-two compiler command, environment, unique process ID, complete output,
versioned ELF stream, two-phase source closure, canonical compressed report,
independently durable receipt, and exact historical status. It neither imports
the earlier recorder as a wrapper nor rewrites any prior evidence.

- Version-two source:
  [`../../tools/reproduce_phase2_native_builds_v2.py`](../../tools/reproduce_phase2_native_builds_v2.py),
  `e822e22cf6a5bbbdc2b634209c6e185ca74ebc55d86828ebea77bb5d44ce3796`.
- Version-two protocol:
  [`NATIVE-SOURCE-BUILDS-V2.md`](NATIVE-SOURCE-BUILDS-V2.md),
  `f383c2ca419c18cf77451c855b53593bb97ea7fa83c90d5d133a80de043aa603`.
- Actual reproducible C result:
  [archive](evidence/native-source-build-v2-c-phase2-v2.json.gz)
  `4d954992312a039daa46a2810e51fc29cfdd2bd49d159dc834f5bf003e456878`;
  [receipt](evidence/native-source-build-v2-c-phase2-v2-publication-receipt.json)
  `e90b4c12a087c0e8864c1627e242be18bd779f9d9693ec711f7dd575288eda24`.
- Actual reproducible Rust result:
  [archive](evidence/native-source-build-v2-rust-phase2-v2.json.gz)
  `69b645c14ca3e566256f5a5b393a6d18554ad347b97b542383db3d86681bb35d`;
  [receipt](evidence/native-source-build-v2-rust-phase2-v2-publication-receipt.json)
  `15580e4441ce651c21800df187fcfaa88ec9336322348a07d84544094d5b050e`.
- Actual Zig reproducibility **failure**:
  [failure archive](evidence/native-source-build-v2-zig-phase2-v2-failures.json.gz)
  `dc5128aaaf8a4d915c57ea8770696db3dc7ca51c89d5a3570cab9d259d070a0e`;
  [failure receipt](evidence/native-source-build-v2-zig-phase2-v2-failures-publication-receipt.json)
  `97e3150e9b68d3031c96ea6e973097687c80163a371f99a67f8b3de08bc0707a`.

A successful durable failure receipt means the real **FAIL** was safely
recorded; it does not mean the Zig build passed. The original two Zig engines
were both **480,040 bytes**, with distinct exact hashes
`b73d43dc4bab42abc1de92e7aaf4a0b145e242ef8407714dc1bef48fc28a7d12`
and
`69a3f024c079b8994c4ffdbf37cbecf59d5afd67c8bcf5200a7331cae66d1f53`.
Their independently built C bridges genuinely matched at **133,656 bytes**,
SHA-256
`c579cf52b767b84ecc3d0a60f837d526978ace4e7739fe4cf51c2d2c8cfd90d9`.
All **15** recorded compiler and ELF-inspection processes completed
successfully. The native Zig debug-line and debug-string sections embed the
distinct absolute `reference-a` and `reference-b` source and cache paths.
The two engines have **no GNU build ID**. Do not describe the failure as a
build-ID difference, missing compiler, candidate mismatch, or bridge failure.

Retain and independently authenticate the original version-one C result and
its corrected complete GNU symbol stream exactly as required by the preserved
version-two protocol. Its historical versioned-symbol parser remains
**falsified**; it is not a qualifying version-three result.

## Evidence-supported correction

The exact official pinned Zig **0.16.0** compiler documents
`-fstrip` as “Omit debug symbols.” Add exactly this compiler-native option
to both otherwise unchanged, independently owned Zig engine commands:

```text
/tmp/zig-x86_64-linux-0.16.0/zig build-lib
  <fresh phase-owned source>/candidates/zig/mini_regex.zig
  -dynamic -lc -O ReleaseFast -fstrip
  -fallow-shlib-undefined -fsoname=_zig_probe.so
  --cache-dir <fresh phase-owned local cache>
  --global-cache-dir <fresh phase-owned global cache>
  -femit-bin=<fresh phase-owned native>/_zig_probe.so
```

Do not run an after-the-fact binary stripper. Never share source, temporary,
native-output, local-cache, or global-cache paths between the two phases.
Keep complete-byte equality, exact-size equality, all exported and undefined
versioned symbols, independently verified dynamic dependencies, `$ORIGIN`,
both distinct fresh native outputs, exact anti-delegation checks, and all
preserved hostile controls. Reject an omitted or duplicate strip option,
`-fno-strip`, another phase's cache, reused source or output, an unapproved
build ID, extra commands, outside regex packages, process delegation, and a
foreign compiler.

The C and Rust source closures, offline toolchain pins, release settings,
exact official Zig archive and lock, Python headers and ABI, historical
symbol-stream parser, bounded process logs, no-network restrictions, and
all actual failure-preservation obligations are unchanged.

## Strictly separate version-three outputs

Use schema `rebar-phase2-independent-native-source-build-v3` and a newly
created mode-0700 root under:

```text
/tmp/rebar-phase2-native-build-v3-FAMILY-
```

Write exactly one exclusive, canonical, synchronized archive and one
separately exclusive synchronized publication receipt:

```text
native-source-build-v3-FAMILY-LABEL.json.gz
native-source-build-v3-FAMILY-LABEL-publication-receipt.json
```

Preserve a real failure, never overwrite a passing path:

```text
native-source-build-v3-FAMILY-LABEL-failures.json.gz
native-source-build-v3-FAMILY-LABEL-failures-publication-receipt.json
```

Every family source must be explicitly pinned using one
`--owned-source-sha256 RELATIVE/PATH=SHA256` per independently owned file.
Pass the **actual** SHA-256 of the published version-three recorder as
`--source-sha256` and this published protocol as `--protocol-sha256`.
Reject stale, missing, duplicate, cross-family, or mutable source pins.
Separately reject version-two recorder, protocol, schema, and evidence pins
when selecting a version-three build result.

## Current integration boundary

The already frozen
[`../../tools/activate_verified_native_candidate_v1.py`](../../tools/activate_verified_native_candidate_v1.py)
and
[`../../tools/run_frozen_p0_candidate_v3.py`](../../tools/run_frozen_p0_candidate_v3.py)
intentionally accept **only** the exact version-two native build source,
protocol, schema, evidence paths, and private-root prefix. They do **not**
accept a version-three build record. Do not activate a version-three artifact
through either frozen consumer; do not relabel a version-three build as
version two; do not edit or relax either frozen gate. A separately frozen,
committed, and pushed compatible activation and full correctness gate are
required before a V3-built candidate can be executed or qualified.

## Safe source-only reproduction

Run both synthetic checks without a candidate, compiler, archive read, file
write, timer, network, or final holdout:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/reproduce_phase2_native_builds_v3.py --self-test

env -i PATH=/usr/bin:/bin \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/reproduce_phase2_native_builds_v3.py --self-test
```

The exact source and this protocol must first be committed and pushed.
An actual version-three source build is **NOT RUN**. Candidate correctness,
candidate speed, memory, expanded holdout, and a winner are **NOT MEASURED**.
