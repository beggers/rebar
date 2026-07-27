# Python regular-expression buffer and exporter correctness

Status: **FROZEN DESIGN; NO V4 REFERENCE HAS RUN; NO CANDIDATE HAS RUN.**
Performance is **NOT MEASURED**. Final or hidden examples are **NOT ACCESSED**.

This is an additional correctness category, not a benchmark. It asks whether
Python's regular-expression operations correctly acquire, retain and release a
real Python 3.14.6 PEP 688 buffer exporter. It never replaces, predicts,
waives or changes another original Python test.

## Independently frozen prerequisites

Run only the isolated, no-bytecode stable CPython **3.14.6** executable:

`255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016`.

Authenticate the complete original-suite V5 policy source:

`8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce`.

Keep the **165** original, source-ordered CPython methods: **152** mandatory
public methods and the same **13** individually named genuinely private
waivers. The original baseline has **151** public passes and one genuine
debug-condition skip. Keep the independent original two-reference report
`1c0445780b747680ff75ced694a61b43949dc1f7eb81a8e4a8c45cfa9376cebf`.

Keep the complete **1,376 = 43 × 32** independently frozen public examples.
Authenticate the public-suite source
`fd0ef1babdb5943d74ef443486805ef6586e46b06eb9d46e4f5b7b650045032b`,
protocol
`c8cc917b52affbce8d61ae1ad217835c7c890fe1e1369d211475a7aaf443cd3f`,
actual complete two-process report
`a2ac2853a6551b9eb95564ee74731c9e7d44998f5ec32ad5aac2259b5b313ad8`,
and actual record fingerprint
`c002fc9e82bb73e592ffa3b5ba73731070004eb892cf85cfcf288fe7693b0aef`.
Preserve both actual process streams, all **64** locale cases and **192**
transitions per reference worker. Decode surrogate-containing JSON using
the authenticated original Python producer's strict, duplicate-key-rejecting
decoder; never use a lossy external parser or copied reference vector.

## Preserve both actual historical failures

V1 source:
`1f60401fa24717c502e147509d1aa625c05bd1cc3aa27b0d1f6ce84783309af7`.
V1 protocol:
`30587b78d2752f9e9a1eeeaa4cef89e09ad75ccd39989bd5eb2d84f136c99dad`.
V1 actual failure:
`f38c8b3dd1faaaa6197a1cf4698a51f830398a3d26c3527302607ed0136fb5ae`.
V1 separately published receipt:
`f68612336528f5660805d2bec5a5c2316f891651cdef3a4ee4d3253960c80f82`.
The actual first process produced empty standard output and **1,657** bytes
of standard error with hash
`4f395284262fb5264a734336016e8acfa18d7860ecb55433fa0e0dd670d14f73`.
Its failed case is **NOT CAPTURED**. Never invent a missing case or vector.

V2 source:
`1db0c95669adc369e8113398576d1d3436018c1f58f1ba0facd2816adf4758cc`.
V2 protocol:
`a34f68399982b6ecf45a443664d290132a463dd6824d2bf797e8a470eb0c3458`.
V2 actual failure:
`33396962dbe4144fcec37d1941d3147c163273ee83592a53fe09aad61c87fea6`.
V2 separately published receipt:
`f81d87020e2ba5d8f7adf956ecfdbede12c3d3cf0639a290fa054e6f3fe70603`.
Preserve and revalidate the actual **214,865-byte** failed-worker output with
hash `74e436ee7dba5f368999f4138daddf819df928c6017d131417d471564bff210b`,
all **256** genuinely completed, source-ordered cases, and their fingerprint
`fb1c8ff92780c739c7ac5fc168923a344b33933c7f1ae593d5b45296479ff023`.
The actual failed case is exactly `buffer-exporter.v1.256`: direct mutable
`pattern.scanner`, a deliberately fixture-created owner/holder cycle, two
observed acquisitions and one observed release. Preserve the complete
intermediate live owner and carrier. This historical fixture failure is not
proof of incorrect Python matching.

The V3 source and design were prospective and incomplete. Neither supplies
an executed reference, qualifying result or completed publication. V4 is a
complete independently executable controller and does not depend on V3.

## Exact original 264-case matrix

Keep **every** original case identifier, order, scenario, operation and
carrier. The exact immutable **264-case** fingerprint is
`2d9eb4e637387bc89020d2f883f59ff03dd98cbebd2f2aaa2a30dc55d0836891`.

The four carriers are direct mutable, direct read-only, wrapped mutable and
wrapped read-only. Cover all **19** module, compiled-pattern, scanner and
match operations. Preserve **76** successful cases, **76** no-match cases,
**76** repeated-acquisition cases, **20** actual failing callback cases and
**16** live-holder cases. This is one exact original denominator; no
unexecuted case, approximation or extra scenario may silently replace it.

Record every actual operation, returned value, exact Python exception and
callback, ordered acquisition, release and same-length poison, match,
iterator, scanner, weak reference and initial/final garbage collection. Keep
an actual returned object alive through complete materialization. Do not
resize storage, inspect released storage, manufacture buffer events, alter
candidate state or silently classify a harness error as matching behavior.

If first garbage collection leaves the owner alive, break only the exact
`cyclic_holder` attribute that this exact fixture installed, after
authenticating both owner type and original holder identity. Record the
actual first-collection live state before breaking it, then record genuine
final collection and balanced release. Never clear native matcher internals,
global caches, foreign references or unrelated attributes.

Canonicalize the module of **only** the exact V4-owned
`CallbackProbeError` class to
`tools.python_re_buffer_exporter_oracle_v4`. Preserve the real class,
module, arguments, message and event for every other exception, including
same-name user-defined exceptions and subclasses. This prevents
script-versus-import test artifacts without weakening user-visible behavior.

## Synthetic-only control and two real references

`--self-test` is strictly in-memory, reversible and source-only. Require
at least **300** distinct positive and adversarial controls and zero actual
file reads, writes, directory scans, clocks, locale changes, threads,
processes, regex matches, native loads, buffer construction, case execution,
garbage collection, candidate imports, benchmark reads or final examples.
Report blocked attack attempts separately. Verify ordinary and empty
environments produce identical canonical output.

`--self-oracle` is a separate, later, explicitly source- and
protocol-pinned root action. Only after V4 protocol and source are committed,
pushed and reviewed may it authenticate the pinned CPython executable,
original V5 source, original V1/V2 failures, and original public reference.
Start exactly two isolated standard-library-only processes,
`reference_a` and `reference_b`; prove their distinct real PIDs, retain
both complete stdout/stderr, validate all **264** outcomes from both, compare
full source-ordered vectors, and preserve every first failure and complete
already-observed prefix. Do not predict reference outcomes.

Publish only the four fresh V4 success/failure archive and receipt paths under
`oracle/cpython-3.14.6/evidence/`. Archive complete canonical reports
with lossless reproducible `gzip` (level 9, zero timestamp), and separately
publish the full authenticated canonical receipt. Open every root and
evidence-path component descriptor-relatively with `O_DIRECTORY` and
`O_NOFOLLOW`; exclusively create each basename with `O_EXCL`. Record each
syscall before execution. Require exact bounded bytes, authentic inode,
single complete write, full same-inode readback, and both file and parent
directory synchronization. Remove an incomplete output only after proving it
is the exact newly created inode; never remove a fully published report.
Preserve first and all cleanup/publication errors. No V4 action builds,
imports or qualifies a candidate, measures performance, opens a holdout,
or changes another frozen denominator.
