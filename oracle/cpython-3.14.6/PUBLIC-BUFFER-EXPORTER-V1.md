# Original Python buffer-exporter and regex lifetime correctness

Status: **PROSPECTIVE. NO BUFFER REFERENCES OR CANDIDATES HAVE RUN.**
Performance is **NOT MEASURED**. Holdout data is **NOT ACCESSED**.

This is one new, separately frozen correctness category. It does not replace,
rerun, weaken, or change the denominator of either the complete original
CPython tests or the existing public Python regex tests.

## Immutable prerequisites

Use only isolated, pinned CPython **3.14.6**. Authenticate exact complete
bytes before starting any reference worker:

- Original `test_re.py`: `879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2`.
- Original V6 source: `b1522b55b37de2e004b029c128e2e75c3020cda34165bcf0de07cb5ebb3136cb`.
- Original V6 protocol: `8e43ceaa61f6e70e2e1193de71bde8583c101cdbe40bc78d862ae789531aff57`.
- Actual independent V6 reference: `1c0445780b747680ff75ced694a61b43949dc1f7eb81a8e4a8c45cfa9376cebf`.
- V27 public source: `fd0ef1babdb5943d74ef443486805ef6586e46b06eb9d46e4f5b7b650045032b`.
- V27 public protocol: `c8cc917b52affbce8d61ae1ad217835c7c890fe1e1369d211475a7aaf443cd3f`.
- Actual independent public reference: `a2ac2853a6551b9eb95564ee74731c9e7d44998f5ec32ad5aac2259b5b313ad8`.
- Actual public-record fingerprint: `c002fc9e82bb73e592ffa3b5ba73731070004eb892cf85cfcf288fe7693b0aef`.

Python's original suite has **165** source-ordered methods: **152** mandatory
public methods and **13** individually named, genuinely CPython-private
waivers. The original real baseline has **151** public passes and one named
private-debug-condition skip. The existing public suite remains **1,376**
cases, **43** cohorts, and **32** cases per cohort. This category does not
claim that any of those reference results qualify a candidate.

## Freeze the genuine PEP 688 matrix

The immutable **264**-case matrix has SHA-256
`2d9eb4e637387bc89020d2f883f59ff03dd98cbebd2f2aaa2a30dc55d0836891`.
Its four carrier variants are direct mutable, direct read-only, wrapped
mutable, and wrapped read-only. Its 19 real operations are module `search`,
`match`, `fullmatch`, `findall`, `finditer`, `split`, `sub`, and `subn`; the
same eight compiled-pattern operations; compiled `Pattern.scanner`;
match extraction; and public `Scanner.scan`.

Freeze **76** successful-source cases, **76** no-match cases, and **76**
same-exporter repeated-acquisition cases. Add **20** independently observed
replacement/scanner callback failures and **16** independently observed
strong-reference and live iterator, scanner, or match retention cases.
Every operation, carrier, scenario, outcome, Python exception, and exact
event sequence is included in source order. Retention records actual
weak-reference liveness and cleanup; none is predicted.

The fixture is a Python-owned PEP 688 exporter. Its `__buffer__` records
actual acquisition. Its `__release_buffer__` records actual release and
poisons only its own live `bytearray` by overwriting the same number of
bytes. It never frees, unmaps, resizes, or dereferences released memory. A
wrapped `memoryview`, repeated acquisition, scanner, match, or iterator must
retain its actual exporter exactly as the isolated Python references
demonstrate. Cyclic cleanup and weak-reference observations must be actual.

## References and publication

`--self-test` uses synthetic in-memory controls only. It must start no
reference or candidate worker; perform no filesystem read or write; import no
candidate or production controller; sample no clock; and inspect no holdout.
Its output is never a reference, a candidate result, or a speed measurement.

`--self-oracle` is a distinct, root-invoked production action. Only after the
source and this protocol are committed and independently reviewed may it run
exactly two isolated standard-library-only workers, `reference_a` and
`reference_b`. Capture both complete genuine stdout and stderr streams, all
264 actual outcomes and lifetime events, distinct worker results, and exact
ordered-vector equality. Reject stale pins, duplicate JSON keys, missing
records, added cases, changed exception identities, candidate imports, and
any claimed or actual benchmark or holdout access. Decode actual frozen
reference bytes with pinned Python's surrogate-safe JSON decoder; never use
`jq` or lossy text conversion.

Only fresh, exclusively created, separately named success/failure JSON and
receipt destinations under `oracle/cpython-3.14.6/evidence/` are approved.
Every material report is canonical ASCII JSON and records its actual single
write, complete bytes, digest, exact readback, file sync, and directory sync.
Never overwrite a first success or failure. This source does not start a
candidate, build a C fixture, test invalid memory, or publish performance.
