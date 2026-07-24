# Current-build correctness and ownership: version 14

## Scope

This protocol freezes a new, append-only correctness gate. It does not certify
an existing candidate, open a performance holdout, execute a benchmark, or
change an earlier result.

The producer is `tools/postfinal_current_build_proofs_v14.py`. Its original
correctness engines are the unchanged, independently frozen version 8 edge and
deep validators, accessed through the immutable version 11 and version 12
controllers. The edge denominator remains 223,198 original checks in 49
categories. The deep denominator remains 393 original checks, including all 64
seeded cases and two independently verified standard-library references.

The current-build ownership authority is exactly
`tools/postfinal_independent_engine_audit_v13.py`, with protocol
`oracle/cpython-3.14.6/POSTFINAL-INDEPENDENT-ENGINE-AUDIT-V13.md`. Version 13
has one independently frozen dual-mode producer. Its two independently
generated report paths are:

- `candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V13.json`.
- `candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V13.json`.

No version 13 source, protocol, or report fingerprint may be guessed, copied
from an older build, inferred from a pathname, or treated as a passing report.
Each of the four actual SHA-256 values must be independently published and
supplied explicitly before qualification. The complete actual version 13
validators must authenticate both reports, all three independent families, the
current twelve owned sources and five native ELF files, active standard-library
and external-engine rejection, and genuine native matching.

## Runtime boundary

Production uses only the pinned isolated CPython 3.14.6 executable, `-I -B`,
and the exact verified parent values:

```text
PYTHONDONTWRITEBYTECODE=1
PYTHONHASHSEED=0
PYTHONPATH=/home/dev-user/src/rebar
```

Each original worker receives an explicitly constructed environment containing
only those three values, `LC_ALL=C`, and `PATH=/usr/bin:/bin`. The parent
controller never imports a production candidate. Original candidate work runs
only in the immutable isolated original workers. A timeout, signal, nonzero
exit, oversized stream, missing original archive, changed source or native ELF,
native-owner rejection, or post-run integrity failure is an actual failure.

Immediately before and immediately after every original edge or deep worker,
run and fully validate a newly executed version 13 native-owner worker for the
same family and exact current native fingerprints. Revalidate the complete
version 13 report graph and current family source and native snapshot after the
original worker. An archived worker record, another candidate, the standard
library, `_sre`, or an external regex package cannot supply production
matching.

## Exclusive evidence

All destinations are new, exact, family-specific version 14 paths. Create each
regular file with `O_CREAT | O_EXCL | O_NOFOLLOW`, preserve full canonical
bytes, authenticate the resulting fingerprint, and reread and revalidate the
complete evidence. Never retry or overwrite a version 11, version 12, or
version 14 result.

The edge original and its separate complete owner proof are:

```text
candidates/evidence/rust-v7-edge-oracle-{rust|vm|zig}-postfinal-current-build-v14-qualified-{pass|failures}.json.gz
candidates/evidence/rust-v7-edge-oracle-{rust|vm|zig}-postfinal-current-build-v14-qualified-{pass|failures}-proof.json
```

The deep original and its separate complete owner proof are:

```text
candidates/audits/RUST-V8-DEEP-CONTRACT-{RUST|C|ZIG}-POSTFINAL-CURRENT-BUILD-V14-{PASS|FAILURES}.json.gz
candidates/audits/RUST-V8-DEEP-CONTRACT-{RUST|C|ZIG}-POSTFINAL-CURRENT-BUILD-V14-{PASS|FAILURES}-PROOF.json
```

Use separate version 14 `PRODUCER-CRASH` and
`INVALIDATED-AFTER-OWNER-FAILURE` paths for complete, genuine producer or owner
failures. Preserve actual return codes, signals, timeouts, complete captured
stdout and stderr, original candidate observations when available, all public
mismatches, the independently validated before and after owner records when
available, and the complete current family and all-family source/native
fingerprints. A failing edge or deep original remains a failing original and
can never qualify.

A deep pass additionally requires its own already-published, independently
validated version 14 passing edge archive and complete version 14 edge owner
proof. Both must belong to the same family, exact source and ELF snapshot, and
same authenticated version 13 report pair.

## Failure history

Historical evidence is immutable and is never a qualification of the repaired
build. Preserve and authenticate the real first Rust version 11 producer
failure and invalidated original:

```text
360d430666bfae146eb9abc18cab2bcd9822096f78e6f21ed3b938bb50631c39
9cc30b172575c83b399f680057a6d33ae952e44f920079c3d8c3b67566afb407
```

Preserve and authenticate the complete real Zig version 12 producer failure,
its separate failed retry proof, and its invalidated original:

```text
5c3e07d9f11d5c8244d3d22fc94f287f4f0573423bf38e70b6abc383c96eca90
b5deb6c3ce522fe0dbc3c4e723867ffe830520f0a47a0b72cc5b1d9a0a69ad9d
d7f11c33a010406db1637e0715e72bfebdc13acf21118735b6b1f6e550927865
```

Validate, rather than summarize away, the complete 393-case Zig observation
archive, the original 26 public mismatches, their 18 original and eight seeded
method-introspection breakdown, the actual `re.Pattern` versus `Pattern`
representation difference, the child exit status, and the genuine original
before-owner record. Never mark either incident, an unpaired archive, a
diagnostic, or stdout as a passing version 14 candidate.

## Source-only gate

`--self-test` is a source-only test, not a candidate run. Inherit the complete
frozen version 12 and version 11 source-only controls. Under the frozen
candidate-free boundary, reject candidate and external-engine imports, report
and historical-evidence reads, original workers, subprocesses, temporary
directories, clocks, timing, holdout access, and all filesystem writes.

Use explicitly synthetic values only to test each validator's complete field
binding. Exercise every family, every version 13 pin, all family-specific
paths, complete owner-before and owner-after binding, archive and proof
integrity, original edge and deep denominators, environment binding, failure
preservation, and every required graph field. Poison every durable-proof field
individually. Synthetic observations never qualify any real candidate.

Run source-only tests with the exact pinned interpreter directly and with an
empty environment. Do not execute an edge worker or deep worker, inspect
candidate evidence, authenticate an actual report, or open the holdout during
the source-only phase.

## Qualification and performance

Run qualification only after the independently reviewed version 13 source,
protocol, and both passing current-build reports have been published. Supply
all four real version 13 hashes to every original invocation. A family is
qualified only when its complete actual version 14 original edge, edge owner
proof, original deep, and deep owner proof all independently pass and agree on
the exact same current version 13 audited source/native graph.

The only permitted performance value is `NOT MEASURED`. The only permitted
holdout value is `NOT ACCESSED`. This protocol makes no speed claim, selects no
winner, and does not begin the performance phase.
