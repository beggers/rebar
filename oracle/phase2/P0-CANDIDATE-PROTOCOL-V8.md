# Repaired first-party C candidate: original correctness protocol, version 8

Status: **SOURCE FREEZE ONLY. No candidate has run or qualified.**

This protocol evaluates a privately rebuilt, independently owned C regular-
expression engine against the original frozen CPython 3.14.6 correctness
oracle. It never replaces, removes, approximates, or supplements an original
test. A build, reversible activation, report publication, or passing example
does not establish candidate compatibility.

## Original correctness obligations

The complete denominator remains exactly **13 original suites**, **31,237
counted original cases**, and **13 named private upstream waivers**. The real
CPython debug-only skip remains a skip; no public mismatch, warning, exception,
thread, callback, locale, buffer, scanner, or interpreter obligation is waived.

The only authorized matching evaluator is the immutable original six-family
producer:

`tools/run_owned_six_family_original_p0_producer_v1.py`

SHA-256 `36451c10221857cca8c77fad7533382f4e3969a20a5cdf73c055beea1d315d33`.

Its original C `FamilySpec` and checked-in C owner remain unchanged:

- Adapter: `candidates/vm_candidate.py`, SHA-256
  `b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096`.
- Original source: `candidates/_vm_native.c`, SHA-256
  `bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55`.
- Separately verified privately derived source: SHA-256
  `f44694759174c1c3975423e07095ae91a853e66242c4e55d11836df03a730c4d`,
  exactly 218,308 bytes. This hash does not replace the original family owner.

The interpreter suite must receive the exact **original producer** SHA-256,
not the wrapper or worker SHA-256. A passing interpreter observation must
retain all 128 original cases, 394 genuine interpreter calls, and all 11
created and destroyed interpreters.

## Build and reversible activation

An actual correctness run is forbidden until the independently frozen V8
source build really passes in two fresh private phases, records all 14 actual
compiler and inspection processes, and publishes distinct exact archive and
receipt owners. Both compiled extensions must be complete and byte-identical.

Only the independently frozen, C-only V5 reversible activator may install the
actual V8 compiled extension. Its exact source, protocol, and contract hashes
are pinned independently in the version-eight machine contract. Neither V2,
V3, nor V4 activation is accepted. Activation must authenticate the live native
inode, actual V8 build report and receipt, report, receipt, and recoverable
journal. The original canonical target must be restored exactly in `finally`
before a whole-candidate result is published.

## Complete original recording

Exactly one new, isolated, source-pinned version-six worker runs for each
original suite, in the existing order. Every suite receives the unchanged
matrix, expected records, original source, seed, and reference codec.

A suite worker publishes its entire genuine original record, all mismatches,
and any exceptions as a deterministic streamed gzip owner and a separate,
owner-only durable receipt. Both files are created exclusively, reject links,
and synchronize their file and directory. The aggregate authenticates both
independent inodes, each complete compressed archive, its exact expanded size
and SHA-256, and every complete worker standard-output and standard-error
stream. Failed workers remain failures and are never counted as semantic
mismatches or successful original suites.

The public aggregate report remains strictly bounded to **32 MiB**. Large
original suite data lives in its separately authenticated suite archive, not
in a truncated standard-output stream. Publication success proves evidence
publication only; it never proves matching success.

## Preserved history and boundaries

The unchanged historical overview contains **71 distinct repository evidence
owners** and separately authenticates **76 digest-addressed history paths**.
These denominators are different. Preserve all six first-party engine families,
all 25 original source owners, the failed C++, Rust, Zig, and Go results, and
all prior restored activations.

Source-only tests create, import, activate, compile, and run nothing. Read-only
verification authenticates the frozen original owners but never starts a
correctness worker. The proposed 4,194,304-case final holdout remains **NOT
GENERATED** and **NOT OPENED**. Performance, memory, undefined behavior, and
confidence intervals remain **NOT MEASURED**. No winner is selected.

Only all 13 genuinely passing original suites, exact native ownership,
complete evidence, and verified original-state recovery can qualify the
repaired C candidate.
