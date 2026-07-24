# Durable, independently verified Python regex compatibility

Status: **Prospective.** No stage-seventeen reference, candidate, benchmark,
or timing has run. The independently published source, protocol, and real
stage-fifteen failure report are pinned below. A missing, changed, or
substituted failure proof stops every real stage-seventeen mode before any
reference or candidate worker starts.

The reference is unmodified, pinned CPython 3.14.6. Rust, C, and Zig must
each use its separately owned native matcher; neither another candidate,
the standard Python matcher, nor a third-party regex package is a fallback.

## Preserve the actual failed experiment

The original stage-fifteen source and protocol remain frozen:

```text
tools/python_re_universal_public_oracle_stage15.py
fc288f0771462a850d5ac4859ba05fe3731953e7160419ddcdbf98e8563ac580

oracle/cpython-3.14.6/PUBLIC-CONTRACT-V15.md
546c5e6152310eda173e182011cb13ab359e0960018b76cd6ce18c7b6006d691

oracle/cpython-3.14.6/evidence/public-contract-v15-self-oracle.json
755cb818f59259bb5adb05a93782afc3eef12e001c41a976ba4b9258ae54ac01
```

The retained first report describes two real, independently completed
3,584-case Python workers. Both actual arrays and both complete worker
reports exist and agree. However, its four recorded hashes are
`0d6a74b1f923436c14569bfdd84431e4251f3bb8dd3129fbbcaf82a47f906b94`,
while its own independent portable validator computes
`7a3bed83093800085fe1bd084820108142929f60e37632b3c24a02c6a4584d72`
from the persisted arrays. Serializing surrogate-bearing observations and
then applying a portable codec a second time changed the hash. The stored
claim of `PASS` is therefore **FALSIFIED**. No stage-fifteen candidate ran.
Do not change, discard, recreate, or qualify this report.

Require the independently published truthful failure:

```text
tools/python_re_universal_public_oracle_stage15_failure.py
07a522f263cd9e0baad022f91988d034b3cde3013b143bd1f9a77174fa0b58b6

oracle/cpython-3.14.6/PUBLIC-CONTRACT-V15-FAILURE.md
6aa2b8e5bcd6867af60c570d19508a67e0094eedca4ab815266e0f91e2c83b03

oracle/cpython-3.14.6/evidence/public-contract-v15-reference-failures.json
cb71e1a44549c7c76c3bf08900e6107d2b49e789e5002afc725d1e9df0c92880
```

The corrected source and protocol first passed an actual, no-write check
against the preserved complete original. The root controller then recorded
the truthful failure exactly once. Validate the published report, the
preserved real arrays, both failed validator contexts, all four real recorded
and independently recomputed hashes, all recorded surrogate cases, and the
genuinely unrun candidates.

## Freeze the same 3,584 public obligations

Retain the exact original case identities, operations, inputs, callbacks,
errors, warnings, locale switches, buffers, native guards, public
signatures, real four- and eight-thread groups, and Unicode boundaries.
Change only the explicitly declared deterministic cohort seeds.

```text
seed: 2026072485
domain: rebar/python-re/public-contract/v17
matrix SHA-256:
e1c6ccf6cbb057f3e3cb708c1b4efe2a175bc77d6eda5e127cae18e5455cfa47
```

| Preserved Python behavior | Cases |
| --- | ---: |
| Public exports, signatures, flags, and exceptions | 256 |
| Invalid patterns, warnings, and flags | 256 |
| All bytes, both real locales, and changed locales | 1,024 |
| Bytes, memory views, and buffer lifetime | 256 |
| Pattern, match, copying, pickle, and groups | 256 |
| Replacement callbacks, reentry, and scanning | 256 |
| Real shared-pattern thread groups | 256 |
| Position limits and Unicode boundaries | 1,024 |
| Total actual cases per candidate | **3,584** |

Independently authenticate both current V7 native-ownership audits, all
12 owned sources, all five rebuilt binaries, all 584 actual successful
official V3 method records, the genuine preserved first official Rust
failure, and all four actually passing stage-fourteen generic-alias proofs.

## Use one stable hash for the bytes actually stored

Canonicalize normalized JSON exactly once using one frozen plain-JSON
encoder and one frozen SHA-256 implementation. First compute the actual
bytes that will be written. Parse those exact bytes without writing them;
require that parsing and serializing them again returns the identical
bytes. Compute every worker and reference hash from this actual, parsed,
durable representation.

Before an exclusive output is created, validate the complete parsed
document both inside and outside every temporary worker context. Repeat
validation with the independent, context-free public validator. Reject
double-escaped text, twice-wrapped surrogate envelopes, switched digest
implementations, altered worker records, changed case identities,
different context results, and substituted current provenance.

Preserve both genuine complete 3,584-row Python worker reports and both
actual arrays. Preserve every actual answer from all three independent
candidates. The reference contains **7,168** real Python observations;
the candidate report contains **10,752** real native observations.

Authorize only the following six distinct one-use output paths:

```text
oracle/cpython-3.14.6/evidence/public-contract-v17-self-oracle.json
oracle/cpython-3.14.6/evidence/public-contract-v17-self-oracle-failures.json
candidates/evidence/python-re-universal-public-oracle-v17-all.json
candidates/evidence/python-re-universal-public-oracle-v17-rust-failures.json
candidates/evidence/python-re-universal-public-oracle-v17-vm-failures.json
candidates/evidence/python-re-universal-public-oracle-v17-zig-failures.json
```

First execute only source-level, no-file, no-worker synthetic controls:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/python_re_universal_public_oracle_stage17.py --self-test
```

Commit and push the complete protocol and source before the root controller
starts two real references. Commit and push a genuinely passing complete
reference before starting any candidate.

The 3,584 frozen cases are broad, but do not establish every possible
module export, cache eviction, scanner edge, replacement, or concurrent
cache operation. Require a separate complete public-surface experiment
before claiming universal replacement compatibility. Holdout speed,
memory, regression rankings, and a winner are **NOT MEASURED**.
