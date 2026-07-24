# Portable additional Python `re` compatibility checks

Status: **Frozen public design and candidate-free checks only.** The
two-reference Python self-comparison and all candidate comparisons are
**NOT RUN**. No speed is measured.

This additive correctness stage retains all **3,584** exact
stage-seven case identities, all eight public obligations, all real
four- and eight-thread tests, both genuine byte locales, all original
Unicode cases, and the original deterministic matrix SHA-256
`0233ca9bc1229b2f905192f9b8ae0c0268b7d23ba3621124192993c6d486f3db`.
The fixed case seed remains `2026072437` in the unchanged
`rebar/python-re/public-contract/v7` matrix domain. Version eight
separately binds its own source, protocol, reports, and observation
domain `rebar/python-re/public-contract/v8`.

| Unchanged public obligation | Cases |
| --- | ---: |
| Public module exports, signatures, flags, and errors | 256 |
| Invalid patterns, warnings, and flag interactions | 256 |
| Every byte in both genuine locales, including compiled-before-switch patterns | 1,024 |
| Bytes, memory views, released and noncontiguous buffers | 256 |
| Pickle, copy, equality, weak references, groups, and real hash behavior | 256 |
| Callbacks, exception propagation, nested matches, and scanners | 256 |
| One compiled pattern shared by synchronized groups of four and eight threads | 256 |
| Bounded indices, large inputs, Unicode, and lone surrogates | 1,024 |
| **Total per isolated implementation** | **3,584** |

## Preserve the real failed experiment

The immutable stage-seven runner has SHA-256
`150abcfc597658f48d64c04053889bd4b299c75ad7413bc1cafa5f864e9e7c25`.
Its unchanged protocol has SHA-256
`b4d719609179dde5f582695393539e7a320c09438e4bc635ca843627ac9d7524`.
Its genuine, exclusively created Python-versus-Python failure has
SHA-256
`765e635745a7e332a1bd22426065c43fd52036d013add0d88d840d8fde1121e0`.

Both pinned, isolated Python processes ran every original case. They
disagreed on exactly **32** rows: the indices `0, 8, 16, …, 248` in
`object-contract`. Every disagreement was a raw numeric hash of the
same kind of compiled pattern. Numeric compiled-pattern hashes are not
a cross-process public contract, even with `PYTHONHASHSEED=0`. All
other **3,552** case records matched. No candidate was started.

Version eight retains all **32** rows. It directly observes whether a
pattern is hashable, whether repeated hashing is stable within its own
process, whether an equal pattern compiled after a public cache purge
has the same hash, and whether either equal pattern retrieves the same
dictionary entry. It never compares raw process-local hash numbers or
claims that unequal objects must have different hashes.

The unchanged failed evidence also contains real isolated Unicode
surrogates. Python can decode its historical JSON, but strict portable
JSON readers correctly reject an unpaired surrogate escape. Version
eight preserves every surrogate-bearing string losslessly using an
explicit tagged UTF-8 `surrogatepass` hexadecimal representation.
Nested values, errors, warnings, match groups, and dictionary keys are
encoded before serialization. Ordinary strings and the original matrix
remain unchanged.

## Prove Python against itself first

The exact current version-five independence reports, all **12** owned
source files, all **five** real native libraries, the **146 × 4** actual
upstream locale results, and all **1,179,648** preceding Python
comparisons remain mandatory. Two distinct, pinned, isolated standard
Python workers must complete all **3,584** cases and produce identical,
portable observations before a candidate can run.

Passing evidence is exclusively created at:

```text
oracle/cpython-3.14.6/evidence/public-contract-v8-self-oracle.json
candidates/evidence/python-re-universal-public-oracle-v8-all.json
```

Every baseline discrepancy, crash, or timeout is durably and
exclusively retained at:

```text
oracle/cpython-3.14.6/evidence/public-contract-v8-self-oracle-failures.json
```

Each independently guarded native failure has its own distinct,
exclusively created report:

```text
candidates/evidence/python-re-universal-public-oracle-v8-rust-failures.json
candidates/evidence/python-re-universal-public-oracle-v8-vm-failures.json
candidates/evidence/python-re-universal-public-oracle-v8-zig-failures.json
```

No stage-seven source, protocol, case, failure, report, or candidate is
modified. A current candidate may load only its independently owned,
source-verified and mapped native library. All third-party matching
libraries, CPython's matcher, cross-family imports, cached module
aliases, and dynamic-loader bypasses remain blocked.

## Run only after freezing and pushing

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/python_re_universal_public_oracle_stage08.py --self-test
```

The self-test imports no candidate, runs no reference or worker, reads
or writes no evidence, takes no timing, and draws no entropy. Freeze,
commit, and push this exact stage-eight source and protocol before the
root process runs either real command:

```sh
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/python_re_universal_public_oracle_stage08.py --self-oracle

PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/python_re_universal_public_oracle_stage08.py --candidate all
```

The passing Python self-oracle is mandatory before any candidate.
Real private ISO-8859-1 and UTF-8 locales are generated and authenticated
inside the production controller. The original six public-method and
two private-class waivers remain unchanged. Performance is
**NOT MEASURED**.
