# Current-build correctness and independent ownership: version 26

## Purpose

This is an additive, frozen correctness protocol for `import rebar as re`. It
does not establish a speedup, run a benchmark, open the holdout, change a
candidate, qualify a synthetic result, or replace a preserved historical
failure. Its only producer is `tools/postfinal_current_build_proofs_v26.py`.

The reference remains the pinned, original CPython 3.14.6 correctness oracle
and the frozen original version 8 report validators. Each independently owned
Rust, C, and Zig candidate must separately satisfy all 223,198 original edge
checks in 49 categories and all 393 original deep checks, including all 64
seeded cases. Preserve both independent standard-library references, every
actual failure, the exact original worker command and exit, and its complete
stdout and stderr. A failed or incomplete observation is never a pass.

## The current audit and the historical audit are different

Only the complete, actually published version 23 ownership audit can qualify
current correctness. Its independently frozen source and protocol are:

```text
tools/postfinal_independent_engine_audit_v23.py
a565cff78306e9d21a97fbb301e087db7371273bc4079533517492788f70b1cc
oracle/cpython-3.14.6/POSTFINAL-INDEPENDENT-ENGINE-AUDIT-V23.md
8b3da77ba5a659d72c940cd595726b1d9b000ed7db1fac5027745c37d504f6bd
```

Supply six different actual SHA-256 values externally: `audit_source`,
`audit_protocol`, `base_report`, `base_receipt`, `strict_report`, and
`strict_receipt`. The first two must be the exact version 23 frozen values
above. Never guess, synthesize, replay, or substitute a report or receipt
hash. Independently authenticate the exact, complete, externally pinned bytes
of both actual reports and both actual exclusive-publication receipts before
decoding any of them. Validate each actual receipt against its own exact
report path, externally supplied report digest, original report byte count,
six genuine descriptor lifetime events, all real write calls, and actual file
and parent-directory synchronization. Invoke the actual version 23
`validate_report` on both reports. Require the strict report to bind the
supplied base digest, both reports to expose exactly the same twelve owned
sources and five independently owned native binaries, and both reports to
preserve complete, genuine owner-worker records and process transcripts for
all three independent families. Require the strict independent base owners
to exactly equal the genuine base report owners and the two actual preserved
histories to exactly agree.

The earlier, genuinely failed version 22 proof is historical evidence only:

```text
candidates/audits/POSTFINAL-CURRENT-BUILD-V22-READONLY-INTEGRATION-PREFLIGHT-FAILURE.json
c6e765f142f25667dd0e7dab45ff16a60abcaae6e230ba05acc596a72d304b01
```

Decode its actual frozen, pretty-printed bytes without reserializing them. Its
historical version 21 prerequisites are exactly:

```text
audit_source   ded077962416ada3bddd825d77b2e6785fe3b01184fe5d9058ec17a57b08ea4d
audit_protocol 5a78673c6b23e4781070cf5a2290d5f6cecd402fff77ff388d8795370de93a1f
base_report    4c1de720abb53a5baee56c36a09039e48137e83b2db103cb0d6e77866b496ce4
strict_report  6e742e2e10cde837cb4c39ffe6d1ab12634d672924e109a727e9a558ad22194d
```

These historical pins must never be passed into the current version 23 audit,
and current version 23 report pins must never be passed into the version 22
failure validator. Preserve the complete actual 25-field version 22 incident,
its 27-field authenticated summary, 25 original inline-source lines, and 24
actual combined traceback lines. Its original failed-invocation boundary was
`NOT PRESERVED BY THE FAILED CONTROLLER`; do not invent separate stdout,
stderr, boundary counters, native owners, original correctness workers, or a
passing report. Preserve all genuine version 13, 15, 17, and 19 historical
incidents with their actual 26, 28, 18, and 36 fields. In particular, the
actual version 13 failure stage is
`historical-zig-edge-authentication-before-any-new-native-owner-worker`.

Independently authenticate the exact frozen version 23 read-only integration
observation before accessing either actual current report. Validate its
complete actual method denominators, named private waivers, true historical
version 21 pins, distinct genuine historical failures, exact six descriptor
events, and five zero-effect counters. It has zero actual ownership audits and
zero owner workers: it cannot qualify a candidate or replace either actual
report or its independently pinned receipt.

## Current ownership and original-worker isolation

Run an independently observed, actual version 23 same-family native owner
immediately before and immediately after each original correctness worker.
Preserve each complete, individually validated owner record and its complete
actual process transcript. Require actual matching, all 13 standard-library
matching guards and five native-loader guards, two representation checks, all
16 standard pickling observations, and zero external package or cross-family
delegation.

Read and rehash the current twelve-source, five-native graph only inside the
frozen historical read-only effect guard. Require exactly zero candidate
imports, native workers, subprocesses, filesystem writes, and clock samples
within each graph check. Use this guard only for its actual effect counters;
the independently validated version 23 graph alone qualifies current
ownership. Reauthenticate both actual version 23 reports and their receipts
before and after the original worker and reject any changed source, native
binary, preserved history, or ownership report.

Run each original worker using the exact pinned original CPython executable
with `-I -B`. Validate the actual parent `PYTHONDONTWRITEBYTECODE=1`,
`PYTHONHASHSEED=0`, and exact project `PYTHONPATH`. The isolated child receives
only those explicitly intended values, `LC_ALL=C`, and `PATH=/usr/bin:/bin`.
Retain the exact observed command, timeout, signal, exit, stdout, and stderr.
Never import a production candidate in this controller.

## Fresh, version-specific correctness evidence

The only permitted original edge archive and owner proof are:

```text
candidates/evidence/rust-v7-edge-oracle-{rust|vm|zig}-postfinal-current-build-v26-qualified-{pass|failures}.json.gz
candidates/evidence/rust-v7-edge-oracle-{rust|vm|zig}-postfinal-current-build-v26-qualified-{pass|failures}-proof.json
```

The only permitted deep archive and owner proof are:

```text
candidates/audits/RUST-V8-DEEP-CONTRACT-{RUST|C|ZIG}-POSTFINAL-CURRENT-BUILD-V26-{PASS|FAILURES}.json.gz
candidates/audits/RUST-V8-DEEP-CONTRACT-{RUST|C|ZIG}-POSTFINAL-CURRENT-BUILD-V26-{PASS|FAILURES}-PROOF.json
```

Producer crashes and completed originals invalidated by a later owner failure
have distinct, fresh version 26 `PRODUCER-CRASH` and
`INVALIDATED-AFTER-OWNER-FAILURE` paths. Preflight all six possible output
paths for the selected family and mode before any native-owner or original
worker starts. Never overwrite, retry, rename, delete, or silently reuse an
existing result. A deep pass must authenticate its own complete, unchanged,
same-family passing version 26 edge archive and version 26 owner proof, with
the identical current graph and all six identical actual version 23 pins.

## Exact and independently owned publication

Version 26 owns its real publisher; it must not call a prior proof
controller's publisher. Accept only bounded exact bytes, a finite strict
canonical JSON object, or a matching exact object-and-bytes pair. Verify the
complete strict, unique-key canonical round trip.

Each of the four artifact purposes owns an independent, unaliased, exact
18-field receipt. Record every `actual_write_calls` request before attempting
the real write and then record its actual returned byte count. Do not lose a
pending attempted write, and do not retry a zero, negative, oversized,
boolean, or failing return. Preserve every genuine partial-write
continuation. Require an actual directory descriptor, verified nonsymlink
directory identity, descriptor-relative `O_EXCL`, `O_NOFOLLOW`, and
`O_CLOEXEC`, complete bytes, file `fsync`, file close, parent-directory
`fsync`, parent close, exact full-byte reread, SHA-256, and, for proof
documents, canonical strict JSON reread.

Reject raw bytes, malformed JSON, or noncanonical JSON for the proof artifact
before any directory open or write. Every attempted owner proof must record
that its canonical JSON document was expected; a validated owner proof must
record that its complete strict canonical reread genuinely succeeded.

A durable proof can only be written after the actual complete original
archive has passed every required publication transition. Preserve the first
real publication failure, every completed transition, and truthful cleanup
observations. Keep the first genuine publication error and every subsequent
failed descriptor-cleanup close as separate, ordered actual observations;
never retry a consumed descriptor. A completed but subsequently invalidated
original is retained
at its distinct nonqualifying path. Never present stdout, a partial file, an
unpaired archive, a historical failure, a synthetic syscall, or a read-only
integration observation as a candidate correctness proof.

## Candidate-free controls

The independently runnable ordinary, isolated, direct, and environment-clean
self-tests inherit all 8,330 passing version 24 controls and add version 26
controls for separate historical/current pin domains, strict graph and report
authentication, all three families, both modes, both outcomes, all four
publication purposes, each exact receipt field, unaliased write ledgers,
partial and invalid writes, canonical publication, and failure stages. Use
only pure in-memory synthetic syscall doubles. Source-only controls must
import no candidates, execute no workers or subprocesses, read no historical
evidence or ownership reports, write no files, sample no clocks, and never
access a benchmark or holdout. Their results never qualify a candidate.

Performance is **NOT MEASURED**. The holdout is **NOT ACCESSED**. A future
result is not known until a genuinely executed, independently owned original
worker and both actual native owners pass and the complete archive and proof
have been independently and durably published.
