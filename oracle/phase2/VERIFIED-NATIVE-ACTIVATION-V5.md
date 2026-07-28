# V5: reversible activation of the independently rebuilt C engine

Status: frozen preparation only. No V8 C build, repaired candidate, candidate
import, native activation, compatibility run, benchmark, or holdout access has
been performed by this activation freeze.

## What this step can and cannot establish

This tool concerns only our original C implementation. It does not use Rust,
Zig, another candidate, Python's `re` or `_sre`, or an external regular
expression package. An activation, if separately requested, is not evidence
that the C engine is compatible or faster. Compatibility must still be
measured against all 13 original CPython 3.14.6 suites and 31,237 case
executions. Speed, memory, confidence intervals, and the unopened 4,194,304-case
final holdout remain **NOT MEASURED**.

The original `candidates/_vm_native.c` remains exactly 218,185 bytes with
SHA-256
`bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55`.
The original `candidates/vm_candidate.py` remains exactly 60,707 bytes with
SHA-256
`b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096`.
Only the separately frozen first-party private repair may create a future C
compiler input of 218,308 bytes with SHA-256
`f44694759174c1c3975423e07095ae91a853e66242c4e55d11836df03a730c4d`.
It must never replace either original repository source.

## Actual native proof, required before any future activation

The caller must independently pin all three V5 activation owners and all
three released V8 source-build owners. An actual activation accepts only a
separately published, passing V8 report and a distinct passing durable
receipt, both independently caller-pinned. Both actual private build phases
must contain independently owned repaired source, the unchanged C adapter, and
complete, byte-identical native ELF output. All 14 real compiler and ELF
inspection processes, both raw ELF parses, independent output inodes,
audited dynamic symbols, and exact output bytes must be verified again.

The sole permitted canonical target is
`candidates/_vm_native.cpython-314-x86_64-linux-gnu.so`. No other family,
fallback, external engine, generated header, prebuilt binary, partial output,
failed-build publication receipt, or unproven replacement is eligible.

## Recovery preserves the original inode

Activation requires a new owner-only `/tmp/rebar-phase2-native-activation-v5-c-`
directory. It first exclusively writes and synchronizes a complete recovery
journal and an intention before creating a random, adjacent, owner-only native
stage. A separate synchronized intention precedes each individual atomic
rename.

If the canonical target originally exists, its exact inode is atomically moved
to a unique adjacent backup in the **same** `candidates` directory. Recovery
moves that very inode back. It restores the original device, inode, owner,
mode, complete bytes, and digest; it never restores a copied substitute. An
originally absent target gets no fabricated backup and recovery removes only
the exact independently journaled promoted inode.

Private source snapshots, adapters, journals, and intentions must be mode
`0600`. Every private phase directory and the actual compiler-produced native
ELF must be mode `0700`. Originals, backups, stages, and promoted outputs must
be ordinary, owner-controlled files with exactly one hard link. Symlinks,
dangling aliases,
directories, unexpected targets, changed user files, and cross-family paths
are rejected. Every individual operation is separately synchronized. These
operations are **not group-atomic**. Recovery reads its caller-pinned journal
and individual intentions and does not require an activation report or
activation receipt.

## Preserved original results

The frozen context independently verifies all 25 original candidate source
owners, all 76 digest-addressed V19 historical references, and all 71 actual
repository evidence owners; 55 owners include the original C++ history. Three
real V4 activations remain historical facts and all three restored their
targets, so the current active-target count is zero. The actual Go campaign
remains a failure with 4,518 semantic mismatches and four infrastructure
failures; its restoration passed. No candidate is qualified.

## Four required source-only gates

Run the effect-blocked, in-memory self-test with the pinned interpreter:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/activate_verified_native_candidate_v5.py --self-test
```

Repeat the same command under `env -i PATH=/usr/bin:/bin`.

Read-only verification requires independently supplied exact SHA-256 pins for
the V5 source, this protocol, and its machine contract, plus the exact released
V8 source, protocol, and machine contract:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/activate_verified_native_candidate_v5.py \
  --verify-frozen-context \
  --activation-source-sha256 V5_SOURCE_SHA256 \
  --activation-protocol-sha256 V5_PROTOCOL_SHA256 \
  --activation-contract-sha256 V5_CONTRACT_SHA256 \
  --build-source-sha256 \
    afc4f8070cb3c1bccf312b77b019cbb6d71f8dcf976f4a2e921e18cc7c063dd4 \
  --build-protocol-sha256 \
    376aae2bdcbeb0c399369c2a15e7e39efb2b1bcce53129a20c229fbbb995cda2 \
  --build-contract-sha256 \
    7f463b70367156d65e73b561629bd1e14ae265b2273afae9b0a984608492019b
```

Repeat this read-only command under `env -i PATH=/usr/bin:/bin`. Neither gate
builds, activates, restores, imports a candidate, opens the holdout, reads a
performance result, starts a compiler, samples a clock, or claims a winner.
