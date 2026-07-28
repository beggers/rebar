# Test each independent engine in real Python subinterpreters

This protocol is frozen before importing or running a candidate. It closes a
specific gap in the published 31,237-case Python-compatibility standard: the
128 genuinely executed subinterpreter cases cannot be passed by testing an
engine in the main interpreter.

The controller is `tools/run_owned_candidate_subinterpreters_v1.py` and its
machine-readable protocol is `oracle/phase2/candidate-subinterpreters-v1.json`.
Every actual invocation must independently supply and verify the exact SHA-256
of the controller, that JSON protocol, and this explanation. These digests are
caller-pinned to avoid claiming an impossible circular self-hash.

The sole Python reference is the pinned CPython 3.14.6 producer
`tools/python_re_subinterpreter_oracle_v2.py`, SHA-256
`54735efb77a099feb2dd076723d3a93d81415226b9b9213307c32cc0f38c52c8`.
Its exact 11,378-byte interpreter program is SHA-256
`9d136a708a438c1f8060c047d89d415c4854ffaeeee9af2fb2d8619f2f0ed07d`.
Its original source-ordered 128-case matrix is SHA-256
`edda77658c5eef9746c6d4769734c69e40db4c9d986171fa63799093f4cb62d3`.
The complete original Python reference vector is SHA-256
`450fccc859099ca78aec725911b6195695cd932ad281af931ca7945cec8c51e8`.

The published Phase 2 candidate protocol,
`oracle/phase2/p0-candidate-protocol-v1.json`, is SHA-256
`7ca70c9d4ae7491ae2b9b9a660c8c72efcee629708103ac7654f31353fa7cd0c`.
Its frozen candidate runner is SHA-256
`c8378cd59a3b4dfaf75609c5b06f5a5ec20114d428e8e06ccc0f12ceec2076b8`.
The original objective remains SHA-256
`e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`.

## What an actual candidate must do

A candidate run must use one isolated, pinned `python3.14 -I -B` worker and
the real public `concurrent.interpreters` API. It must create and destroy
exactly **11 genuine subinterpreters**. Two independent, simultaneously live
interpreters, A and B, each execute every original case in the real order
**A, B, A**. The eight independently fresh interpreter cases, one A
execution after B closes, and one newly created C execution are also required.
This is exactly **394 actual matching-case `Interpreter.exec()` calls**.
The 11 separate interpreter initialization calls and 11 guard-cleanup calls
are reported separately; they do not change the 128-case denominator.
A real correctness worker has a 180-second timeout and a separately bounded
15-second kill-and-reap cleanup. These are correctness safeguards, not
performance measurements.

Each actual case must pass a real bounded operating-system pipe, retain every
writer/reader event, genuinely read to EOF, close both descriptors, preserve
the full record, and retain the actual matching-interpreter identity.
Preserve all three complete 128-record A/B/A vectors, all eight fresh records,
the A-after-B-close record, the C record, all interpreter IDs and original
seeds, every exception and failure, the original live-interpreter set, the
worker's actual process ID, and the unchanged process locale.

## Prevent Python-regex and foreign-engine delegation

Run the independently frozen source audit and verify the selected family's
published, actually reproduced **version-2** native-source build proof before
starting a candidate. The historical **version-1 recorder, which never
authorizes a candidate,** is
`tools/reproduce_phase2_native_builds_v1.py`, SHA-256
`e4cee196fcd6ff0908f46c26ef66363aa059e3003f2e89b302df10f35f9a3afd`;
its protocol is SHA-256
`33c495f6852155130c92af73422b7a6c6aae26b1c7012e65e2ddddab028064a2`.
A preexisting native binary is not a source-build proof.

At this controller's freeze, **one** actual two-phase source build has already
completed: C, label `phase2-v1`. Its published archive is SHA-256
`b7844048cde986cae25ec4dafadfbb6dc560f4ea86108b908fe074176423f2e2`, and
its publication receipt is SHA-256
`7736349d1e8dce83e47fdf741a4e34fb313d4d370a11a2d5563dba4468e55002`.
The two fresh builds reproduce extension SHA-256
`ed57383dad99ce311664d165635fa300f3894df6b4816b5f54801d0e68263697`,
size 163,136 bytes. Rust and Zig source builds are **NOT RUN**. This source
build imported and ran zero candidates and created zero subinterpreters.

A successful source-build archive does **not** activate a native binary. A
candidate remains blocked until its actual project-native engine and bridge
both have the exact hash and size proven by its two freshly built outputs.
A stale, preexisting, or differently built project binary fails before any
candidate import or interpreter creation. Installing an authenticated
source-built output is a separate, explicitly reviewed chunk.

The historical version-1 build **cannot authorize a candidate**. Its ELF
symbol audit incorrectly interprets versioned undefined-symbol suffixes such
as `(2)`; this could conceal a forbidden external matcher. An actual run
requires the separately frozen **version-2** recorder and protocol, a real
version-2 selected-family archive and durable receipt, correct versioned
undefined-symbol checks, and two byte-identical freshly built outputs.
The frozen version-2 recorder is SHA-256
`e822e22cf6a5bbbdc2b634209c6e185ca74ebc55d86828ebea77bb5d44ce3796`;
its protocol is SHA-256
`f383c2ca419c18cf77451c855b53593bb97ea7fa83c90d5d133a80de043aa603`.
At this controller's freeze, its status is
`V2_PUBLISHED_NO_FAMILY_BUILDS`: **zero** version-2 family builds have run,
and their future archives, receipts, activations, and candidate results are
**NOT MEASURED**. An actual invocation must supply the exact published
recorder, protocol, selected-family archive, and receipt SHA-256. No
version-1 proof, existing shared library, guessed future digest, or proposed
activation can start a candidate worker or create an interpreter.

The independently verified native artifacts must also be activated through a
separately frozen, **reversible canonical activation**. First, preserve every
existing candidate binary, with its exact bytes, hash, and identity, in a new
owner-only (`0700`) no-symlink directory named
`/tmp/rebar-phase2-verified-native-activation-v1-FAMILY-*`. Atomically
install only the exact two-phase version-2-built binaries at the genuine
candidate's canonical repository paths; require a complete backup journal,
durable activation receipt, hash-and-inode verification, and rollback.

Use the original, unchanged canonical V5, V4, V3, V2, and V1 matcher guards.
Never copy, relocate, rebind `ROOT`, monkeypatch, or weaken their source,
runtime, module-origin, or original-matcher checks. A preexisting repository
binary is never proof: only the exact receipt-bound, source-built, reversibly
activated replacement may be imported. Require the independently pinned
activation source, protocol, report, and receipt before any worker or
interpreter starts. At this controller's freeze, canonical activation is
`REQUIRED_NOT_PUBLISHED` and no candidate has been activated.

Explicitly pin all actual source owners, the exact adapter, the genuine
native engine, and the native Python bridge. The public candidate `c` means
the independent audit's `c_vm` family and the actual
`candidates.vm_candidate` adapter. Only C's real engine and bridge may be
the same owned binary. Zig may load only its exact authenticated owned
engine and approved symbols.

Inside **each** actual interpreter, before importing the candidate, load and
authenticate the frozen original V5 matcher guard. Enter the real
warning-safe guard and then the real `chosen_original_guard`. Keep both
context managers alive until the interpreter's actual cleanup. Authenticate
the selected adapter, bridge, engine, every source-owner hash, and the
interpreter-local native module state. Call the genuine continuous identity
guard immediately before and after every matching observation.

The frozen V5 guard temporarily points its interpreter-local public `re`
import slot at the **hash-authenticated chosen candidate**. This is neither
an import of Python's matcher nor a claim that the candidate is `re`: the
candidate's real module name, `__file__`, loader, bridge, native type and
source owners must still identify `candidates.rust_candidate`,
`candidates.vm_candidate`, or `candidates.zig_candidate`. The original
CPython `re` and `_sre` matcher identities stay quarantined. Calls to the
original matcher, external regex engines, sibling engines, unowned native
libraries, foreign subprocesses, or a replaced guard fail the case. Restore
both authentic guards before closing each interpreter.

## Exact lossless reference-to-candidate identity projection

The authentic Python-reference records contain two reference-only fields:
`candidate_imports: 0` and `stdlib_origin_verified: true`. An independently
loaded candidate must not claim either. Remove **only** those two root
fields, and replace them with authenticated candidate-specific provenance.

Preserve every original value in the matching observation. Rename exactly
these seven implementation-identity keys; reject a missing or duplicate key,
a collided target, a changed value, or a forged candidate owner:

| Original Python field | Actual candidate field |
| --- | --- |
| `actual_stdlib_reimport` | `actual_engine_reimport` |
| `match_is_stdlib_match` | `match_is_engine_match` |
| `module_identity` | `engine_sysmodules_identity_verified` |
| `pattern_is_stdlib_pattern` | `pattern_is_engine_pattern` |
| `reimported_origin_verified` | `engine_reimported_origin_verified` |
| `stdlib_owner` | `engine_sysmodules_owner_verified` |
| `stdlib_re_module` | `engine_module_name_verified` |

Every mapped candidate value is measured from its actual independently
imported adapter, native pattern, native match, module entry, loader, and
source. The complete 128-case projected original reference, using the genuine
producer's compact ASCII JSON **without** a trailing newline, is SHA-256
`cf5633c8dc1038d650603eee421371285d0e32f6446190ce728590f1f5c55021`.
The original vector digest is never relabeled as the candidate digest.

Generate the candidate observation program by applying uniquely verified,
whole-context edits to the exact hash-pinned original `INTERPRETER_PROGRAM`.
The complete derived program is exactly 12,759 UTF-8 bytes and SHA-256
`147b09bcda37678b9ac4f2f050a22eb5435c7703cbce33247e9287e62e514f71`.
Never globally replace `re`, `_stdlib_re_origin`, cohort names, outcomes,
exception types, callbacks, flags, cache operations, or cleanup. Parse the
resulting source and authenticate its exact derived hash before executing it.

## Complete durable results

Publish complete passing or failing results to new, exclusively created
`oracle/phase2/evidence/` paths:

```text
owned-candidate-subinterpreters-v1-FAMILY-LABEL.json.gz
owned-candidate-subinterpreters-v1-FAMILY-LABEL-publication-receipt.json
owned-candidate-subinterpreters-v1-FAMILY-LABEL-failures.json.gz
owned-candidate-subinterpreters-v1-FAMILY-LABEL-failures-publication-receipt.json
```

Use bounded deterministic gzip, exact compressed and original SHA-256,
no-follow exclusive files, same-inode readback, file and directory syncing,
and a complete failure-safe publication receipt. Never overwrite existing
evidence. Preserve nonzero process returns, signals, timeouts, full child
standard output and error, original exceptions, completed matching prefixes,
failed interpreter names, partial pipes, actual guard violations and every
cleanup failure. A failed native subinterpreter import is an actual failure,
not permission to retry in the main interpreter.

The source-only `--self-test` starts **zero** workers, creates **zero**
interpreters, imports **zero** candidates, and reads or writes **zero**
actual files. It performs no garbage collection, timing, native build,
benchmark, hidden-case access, or holdout access. It must positively test
the complete matrix, lifecycle, seven-key projection, deterministic original
program transformation, exact owner families and genuine failure evidence,
and reject hostile substitutions and every attempted real external effect.

Until each family has a separately published real source-build proof and the
parent authorizes candidate execution, actual candidate subinterpreter
results remain **NOT MEASURED**. This source freeze is not a passing
candidate, and does not authorize the performance holdout.
