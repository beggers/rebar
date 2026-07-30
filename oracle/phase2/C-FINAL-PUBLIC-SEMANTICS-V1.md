# Final independently observed C compatibility corrections

The unchanged, committed complete C correctness run executed all **13**
frozen original groups with **31,237** cases and **13** separate workers. It
verified **22,798** checks and preserved every one of the remaining **224**
semantic differences. No worker crashed or timed out. Its public receipt is:

    oracle/phase2/evidence/repaired-c-original-campaign-v15-c-phase2-v23-c-complete-semantics-original-p0-v15-failures-publication-receipt.json
    SHA-256 6adea6a4da59bb0c63c54006991257b46149c4447a82bb1cd6b8810e6bee5b43

The compressed, complete public evidence has SHA-256
`9864dd38761bcb23008973bde471c8911e18234fe7162ad11a2a1893c118a102`.
The freeze controller preserves that fingerprint but never opens the archive.
Separate read-only forensics authenticated and replayed all **224** individual
records. The complete, nonoverlapping observed partition is:

| Original Python group | Independently observed defect | Cases |
| --- | --- | ---: |
| Original CPython tests | Unknown compiled flags and inverted public flags | 2 |
| Public types | Declaration-ordered flag objects | 48 |
| Public types | Equal string/bytes subclasses compare unequal | 96 |
| Public surface | Declaration-ordered public flag objects | 14 |
| Public surface | Indexed-only flags incorrectly accepted | 64 |
| Total | Four first-party semantic corrections | **224** |

The public-type flag failures are four disjoint 12-case cohorts covering flag
membership, zero and combinations, unknown bits, and both `repr` and `str`.
The equality cohort has 48 string-subclass and 48 bytes-subclass records. The
64 indexed-flag surface records are evenly split across unknown compiled flags
and mixed/inverted indexed flags; each incorrectly successful actual record
also exposes the wrong unknown-flag compiled-pattern representation.

## Correct public and compiled-pattern flags independently

Python flag objects describe known flags in **class declaration order**:

    repr(re.ASCII | re.IGNORECASE)
    re.ASCII|re.IGNORECASE

Compiled patterns independently describe the same flags in **numeric bit
order**:

    repr(re.compile("a", re.ASCII | re.IGNORECASE))
    re.compile('a', re.IGNORECASE|re.ASCII)

Unknown-only public flag objects use decimal:

    repr(re.RegexFlag(0x123000))
    re.RegexFlag(1191936)

Unknown-only compiled pattern flags use hexadecimal:

    repr(re.compile("a", 0x123000))
    re.compile('a', 0x123000)

The independently written C native factory deliberately discards the Python
`Pattern` class-body namespace. Adding a Python `Pattern.__repr__` therefore
cannot change its native representation. Instead, create an independently
written private flag type whose representation is numeric-order and
hexadecimal. Temporarily expose that private type to the existing first-party
native configuration, which retains its own strong reference. Restore the
original public flag class in an exception-safe `finally` before continuing.
The public type retains its exact module identity, aliases, declaration order,
and `repr`/`str` semantics. The unchanged native compiled-pattern formatter
retains its existing quoting, **200-character** truncation, implicit-Unicode
mask, and independently owned matching engine.

## Preserve equal pattern identity and consistent hashing

The first-party native pattern identity currently includes the concrete source
type. A string subclass and an equal ordinary string therefore compare unequal;
the same defect affects bytes subclasses. Canonicalize only that identity's
type component to the base Python string or bytes type. Keep the source value
and flags unchanged. The same native identity function is used by both rich
comparison and hashing, so equal base/subclass patterns keep identical hashes
while bytes and strings remain distinct. No native parser, compiler, executor,
scanner, capture, replacement, or lifetime rule is changed.

## Reject unsupported indexed-only flags in Python's order

An object implementing `__index__` but not bitwise `&` is not a supported
regular-expression flag. Python raises:

    TypeError: unsupported operand type(s) for &: 'IndexedFlag' and 'int'

The current first-party adapter incorrectly applies `int(flags)` before its
first bitwise operation. After normal cache lookup, first reject non-string
patterns, then perform the genuine first `VERBOSE` bitwise check on the
original flag object, and only then retain the existing integer conversion.
This preserves invalid-pattern exception priority, cache-key hashing priority,
normal integer and `RegexFlag` inputs, and the exact unsupported-flag error.

## Independently pinned first-party inputs and prospective outputs

The already corrected public C adapter remains immutable:

    candidates/c/variants/public_adapter_semantics_v2/vm_candidate.py
    SHA-256 4a62cb318592600d53e5ed6b9f8b9edf4edf2068fb2453892ca2130bb203410a
    bytes   61663
    inode   525120

The already corrected first-party native engine source remains immutable:

    candidates/c/variants/complete_native_semantics_v1/vm_native.c
    SHA-256 0654fe3a970760cc3efb08d819c8a4d8abadb152c35f370e662123e4de20e31f
    bytes   221557
    inode   525629

After separate committed-and-pushed root authorization, exclusively create:

    candidates/c/variants/final_public_semantics_v1/vm_candidate.py
    SHA-256 e91819b1d6b399954b3384519fdfddb6ccd6d4e4099a34e06d702c9959a79193
    bytes   62209

    candidates/c/variants/final_public_semantics_v1/vm_native.c
    SHA-256 99f45846551705379ccd7365333995ee68fe25e10d101655a17ad45c5e13a5e6
    bytes   221715

Both new files are mode `0600`, created without following symbolic links in a
fresh mode-`0700` directory, independently hashed, read back, and synchronized.
No existing candidate or user-owned file is edited.

## Four strict source-only gates

Use only pinned CPython **3.14.6**, with `-I -B -S`. Ordinary self-test and
source verification must both pass, followed by identical self-test and source
verification with `env -i PATH=/usr/bin:/bin LC_ALL=C LANG=C TZ=UTC`.

Each self-test requires all three source/protocol/contract hashes but opens
**zero files**. Verification authenticates exactly four public plaintext files:
the source, this protocol, the frozen contract, and the complete C15 public
receipt. It opens **zero candidate files**, compressed archives, private build
roots, hidden cases, retired or prospective holdouts, native engines,
benchmarks, or final-test metadata.

The permanent descriptor wall guards both `os` and its underlying native
`posix` aliases. At least 40 independent hostile controls reject inherited
descriptors, unauthorized paths, metadata, symlinks, mutation, subprocesses,
dynamic execution, regular-expression imports, and timing. Exhaustive synthetic
controls check **20,481** public flag values, **16,385** compiled-pattern flag
values, **96** base/subclass equality and hash identities, unknown values,
negative/inverted flags, all aliases, indexed flags, invalid-pattern precedence,
and existing long-pattern truncation. No candidate is executed by any gate.

After these gates pass and the exact source, protocol, and contract have been
committed and pushed, only the root coordinator may separately authorize:

    python3.14 -I -B -S tools/apply_owned_c_final_public_semantics_v1.py \
      --apply --root-authorized --frozen-committed-pushed \
      --frozen-commit PUSHED_COMMIT --pushed-commit PUSHED_COMMIT \
      --source-sha256 SOURCE_SHA256 --protocol-sha256 PROTOCOL_SHA256 \
      --contract-sha256 CONTRACT_SHA256

Application opens exactly two pinned first-party candidate inputs after all
authorization and controls. It creates exactly one new directory and two
exclusive immutable source files. It does not compile, import, run, or time a
candidate. A separately frozen independent native build and both complete
correctness suites are still required.

Correctness of the proposed corrected candidate: **NOT MEASURED**. Runtime
independence: **NOT ESTABLISHED**. Performance, memory, and undefined
behavior: **NOT MEASURED**. Qualified candidates: zero. No winner.
