# Genuine Python regex buffer-exporter lifetime and preserved first failure

Status: **PROSPECTIVE. NO V2 REFERENCES OR CANDIDATES HAVE RUN.**
Performance is **NOT MEASURED**. Holdout data is **NOT ACCESSED**.

## Preserve the actual failed first experiment

The immutable V1 source is
`1f60401fa24717c502e147509d1aa625c05bd1cc3aa27b0d1f6ce84783309af7`;
its protocol is
`30587b78d2752f9e9a1eeeaa4cef89e09ad75ccd39989bd5eb2d84f136c99dad`.
The actual canonical V1 reference failure is
`f38c8b3dd1faaaa6197a1cf4698a51f830398a3d26c3527302607ed0136fb5ae`.
Its separately durable, real, one-write receipt is
`f68612336528f5660805d2bec5a5c2316f891651cdef3a4ee4d3253960c80f82`.

Exactly one actual isolated first worker, `reference_a`, exited with code 1;
its actual stdout contains **zero bytes**. Its exact complete 1,657-byte
stderr has SHA-256
`4f395284262fb5264a734336016e8acfa18d7860ecb55433fa0e0dd670d14f73`.
It published **zero complete reference vectors**. The traceback genuinely
locates V1's premature unconditional buffer-balance assertion. Neither the
failed case identity, zero-acquisition `TypeError`, nor a still-live result is
present in that immutable failure. Never invent any of them.

One separately authorized, explicitly in-memory diagnostic called V1
`execute_case` on **case index 0 only** using pinned CPython's standard
library. This is **not** a reference worker, V1 retry, complete baseline, or
candidate test. `buffer-exporter.v1.000` returned from `module.search` on
the direct mutable carrier. Its actual event sequence acquired and released
the same exporter **twice**; the first genuine same-length release poisoned
`616161` to `212121`, and the actual returned match group was `212121`.
This confirms case zero cannot be asserted to be the unidentified V1 failure.

## Keep every existing correctness obligation

Pin the original 165 upstream methods: **152** public methods and exactly
**13** independently authenticated, individually named CPython-private
waivers. Authenticate the complete genuine two-worker V6 original report
`1c0445780b747680ff75ced694a61b43949dc1f7eb81a8e4a8c45cfa9376cebf`.

Authenticate the unchanged V27 source
`fd0ef1babdb5943d74ef443486805ef6586e46b06eb9d46e4f5b7b650045032b`
and protocol
`c8cc917b52affbce8d61ae1ad217835c7c890fe1e1369d211475a7aaf443cd3f`.
Independently authenticate the actual V19 public reference
`a2ac2853a6551b9eb95564ee74731c9e7d44998f5ec32ad5aac2259b5b313ad8`,
both complete process streams, all **1,376 = 43 × 32** actual records,
record fingerprint
`c002fc9e82bb73e592ffa3b5ba73731070004eb892cf85cfcf288fe7693b0aef`,
and all **64** locale cases and **192** transitions per worker. Decode
canonical surrogate-containing reference bytes with pinned Python; never use
lossy parsers or substitute a copied vector.

## Freeze the exact original 264-case safety matrix

Preserve V1's exact **264** case identities, order, operation descriptors,
carriers, scenarios, and immutable SHA-256
`2d9eb4e637387bc89020d2f883f59ff03dd98cbebd2f2aaa2a30dc55d0836891`.
Keep all 19 module, compiled-pattern, scanner, and match operations on all
four direct/wrapped mutable/read-only carriers: **76** successful-source,
**76** no-match, **76** repeated-acquisition, **20** authentic failing
callback, and **16** weak-reference and cyclic holder cases. No original
public method, PEP 688 case, callback, carrier, or release may be waived.

Record actual ordered acquisition, safe in-place poison, replacement and
scanner callbacks, returned values, exceptions, weak references, garbage
collection, live holders, materialization, and explicit final cleanup. Match,
scanner, iterator, and wrapping memoryviews must remain strongly referenced
until the actual observation says otherwise. Retain genuine matching results
through serialization, then explicitly drop result and carrier references,
record actual cyclic collection, and check balanced acquisitions and releases
only **after** authentic final cleanup. Permit zero acquisitions only for an
actually observed, fully recorded `builtins.TypeError` on an unsupported
direct exporter. Never dereference freed data, resize backing storage,
manufacture a release, or classify a harness error as a regex result.

## Candidate-free isolated controls and durable evidence

The standalone `--self-test` runs no reference, candidate, exporter, buffer
case, collector, process, thread, timer, regex matcher, evidence read, write,
locale change, or performance/holdout inspection. It preserves **67** unique
positive controls and **259** genuinely distinct rejected forged matrix,
weak-reference, phase, inode, syscall, cleanup, first-failure, receipt,
source-path, stream, and no-effect attempts. Every one of the **15** actual
outside-effect counters remains zero; intercepted attack attempts are reported
separately. Run both CLI and direct API in ordinary and empty isolated
environments. A source-only self-test is never an executed reference or a
candidate qualification.

Only after root separately commits and pushes this source and protocol may
`--self-oracle` run exactly two new pinned standard-library-only workers.
Record their distinct actual process identities, complete stdout/stderr,
every original case and cleanup, identical full ordered vectors, and the
actual first failing case and completed prefix on any failure. V2 exclusively
creates only its four new success/failure report-and-receipt destinations.
Open each exact approved evidence parent and basename descriptor-relatively,
without following symlinks; journal intended syscalls before each operation;
capture first and all real cleanup failures; require a single complete
write, same-inode readback, file synchronization, directory synchronization,
and truthful actual receipts. Never alter or reuse a V1 path.
