# Complete first-party C engine corrections, version 1

Status: **SOURCE FROZEN; NATIVE VARIANT NOT MATERIALIZED, BUILT, OR RUN.**

The C candidate has its own independently authored C matching engine; this
experiment does not wrap an outside package, use Python's regular-expression
engine, reuse another candidate, or fall back to another implementation.

The pinned reference is official CPython 3.14.6. Its unchanged, prospectively
frozen original test suite contains **31,237** checks in **13** groups with
**13** explicitly named private waivers. The separate **8,244** reference
checks do not alter that denominator. The proposed **14,155,776**-case final
holdout remains **NOT GENERATED; NOT OPENED**.

## Preserve the actual failed result

The most recent actual C21 engine source is:

    SHA-256  fe5bd423cb93b982bce79c584f19ad6eb254ab927008b21b37427de9e6ecf3c2
    bytes    221647

Two independently compiled artifacts both had SHA-256
`7a5f8db27154cdcbd4203d727e02c0828ba1f9bf3fa2fdc1a86223ee57825f60`.
Their private source/build directories are not opened. The latest actually
executed C12 candidate failed, and its genuine durable evidence is:

    oracle/phase2/evidence/repaired-c-original-campaign-v12-c-phase2-v21-c-original-match-semantics-original-p0-v12-failures-publication-receipt.json
    SHA-256  a3f4b90b8f289df9dfe49f776266e3c290edb2c21c62713137f501a5f997c21b

Exactly **16,413** original checks passed before five groups recorded **606**
actual differences:

    managed exporter lifetime       16
    public object behavior         248
    replacement behavior           224
    public module behavior         114
    retained scanner lifetime        4
    observed total                 606

The interpreter-isolation group also failed before completing its 128 checks;
the complete difference count is therefore **NOT MEASURED**. Every original
failure, suite denominator, case-vector fingerprint, and compressed evidence
owner is retained. This experiment never opens the compressed evidence.

The corrected V4 runtime guard separately preserves exact first-party native
ownership and requires all eleven genuinely created child interpreters to be
destroyed. It has not yet run on this cumulative C variant.

## Record and reverse a genuinely falsified earlier hypothesis

An earlier committed protocol claimed that every Match pickle protocol from
zero through five must fail. Its source, protocol, and contract remain
immutable:

    tools/apply_owned_c_original_match_semantics_v1.py
    SHA-256  e2a67d418ab531a93bb2f894844a256460ba7fde70a6e1f6fb2ae82eba63b1c6

    oracle/phase2/C-ORIGINAL-MATCH-SEMANTICS-V1.md
    SHA-256  a71e397d87ecd538ee8a1eb218a6dbdf68849cc9598c208ddc83066dc9aec7b9

    oracle/phase2/c-original-match-semantics-v1.json
    SHA-256  6a7a53c77bd20664fed15a61d5ad5c1d7ae5354405e99e8d72427d44ab9f134c

That claim is false. Official CPython 3.14.6 returns its genuine Match
reconstructor for signed C-integer protocols below two, including protocols
zero and one; protocols two and above raise the original Match `TypeError`.
Inputs outside the signed C-integer range raise the original integer overflow
exception. The frozen public-object cohort contains sixteen protocol-zero and
sixteen protocol-one cases, explaining exactly **32** genuine C21 differences.

The new C source restores the original first-party, interpreter-owned Match
reconstructor and upgrades protocol conversion to `PyLong_AsInt`. Copy and
deep-copy identity, one `__index__` call, bool handling, negative values, the
dedicated public method, and the complete previous source evidence survive.

## Preserve original exporter ownership and release timing

The authentic base source compiled replacement templates before acquiring the
subject, correctly implemented one independent nested acquisition per captured
group, and retained original shape/error handling. C21 nevertheless copied the
subject to `bytes` and released its original exporter before matching. That
removed nested exporter events and hid mutation during release.

Remove the eager snapshot, keep the original exporter live through matching,
captured groups, prefix/tail materialization, and empty-separator creation,
then release it **immediately before the final bytes join**. This last detail
is essential: a literal replacement exporter must be probed first, the subject
must be acquired and released next, and only then may bytes joining acquire
the replacement again. No-match, negative-limit, error, cross-domain, and
callable paths retain their previous cleanup behavior. Buffer release remains
idempotent and safe during reentrant exporter callbacks.

This correction targets **16** managed-exporter cases and **224** replacement
cases across these seven independently frozen cohorts, exactly 32 each:

    pep688-stable-subject
    pep688-mutating-subject
    pep688-fixed-hash-subject
    pep688-unhashable-subject
    nested-stable-subject-and-template
    nested-stable-fixed-hash-template
    nested-mutating-unhashable-template

The mutating-subject and nested-mutating/unhashable groups additionally expose
the changed replacement result. All original captures, mutation, replacement
hash behavior, nested flags, event order, exceptions, and public case records
remain independently frozen.

## Match original scanner garbage-collection visibility

CPython's retained scanner has two strong original-subject references but
exposes neither subject edge to cyclic garbage-collection traversal. Its only
traversed objects are the scanner's heap type and compiled Pattern. The C21
scanner incorrectly traversed both its direct subject and owned buffer object,
allowing garbage collection to break the retained owner cycle prematurely.

Remove both traversal edges without removing either strong reference. Keep GC
tracking, the type and Pattern traversal, `done` before release, clearing view
ownership before reentrant release, original buffer release before clearing
the subject/Pattern, and the existing untracking/free/type-decref order.

The four exact failing cases are `buffer-exporter.v1.256` through `.259`:
direct and wrapped carriers, each mutable and read-only. Direct carriers have
two acquisitions and two releases; wrapped carriers have one acquisition and
one release. The exporter stays alive after the first post-drop collection,
and the final release occurs only when the authentic fixture cycle is broken.

## Cumulative candidate composition and measurement boundary

The already materialized, independently corrected public Python adapter is:

    candidates/c/variants/public_adapter_semantics_v2/vm_candidate.py
    SHA-256  4a62cb318592600d53e5ed6b9f8b9edf4edf2068fb2453892ca2130bb203410a
    bytes    61663

Its real exclusive application receipt has SHA-256
`e3e63acfde8f1eef32f81d48bddc613fb386880a5f1974b898e36b211ab55476` and
accounts for **330** distinct public-adapter differences. The new C source
targets the remaining **276** known engine differences:

    16 managed + 32 Match pickle + 224 replacement + 4 scanner = 276
    330 public adapter + 276 native engine = 606 preserved observations

The authenticated committed first-party input is:

    candidates/c/variants/subject_buffer_ownership_v1/vm_native.c
    SHA-256  8131aea768a122308716b8a67903794aa03f2fed2e2022f53bb6aa7b7e10e962
    bytes    222212
    device   2064
    inode    524723

During separately authorized root-only application, reconstruct and verify the
exact actually tested C21 source first. Apply exactly seven unique reversible
native source changes and exclusively materialize:

    candidates/c/variants/complete_native_semantics_v1/vm_native.c
    SHA-256  0654fe3a970760cc3efb08d819c8a4d8abadb152c35f370e662123e4de20e31f
    bytes    221557

No existing candidate source or compiled engine is changed. Candidate
correctness, runtime non-delegation, undefined behavior, memory, and speed
remain **NOT MEASURED** until independently built, guarded, and tested against
the unchanged complete original correctness oracle. No winner is selected.

## Source gates and separately authorized exclusive materialization

A deny-default audit hook and descriptor wall activate before any owner read.
Self-test reads no workspace file. Source verification authenticates exactly
sixteen immutable plaintext owners: the three new source-freeze files, the
three preserved false-hypothesis files, the three corrected public-adapter
files, its actual application receipt, the three corrected V4 guard files,
the real C12 failure receipt, and both C21 build receipts.

Neither mode opens a candidate source, compiled/native artifact, private build
root, compressed archive, final-case proposal, benchmark, network, clock,
compiler, reference process, matcher, or another candidate. The genuine
root-only semantic authorization path runs in every source gate, including a
direct control for the previously observed truthy-bytes authorization bug.

Run each of these checks both normally and under
`env -i PATH=/usr/bin:/bin LC_ALL=C`:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_c_complete_native_semantics_v1.py --self-test

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_c_complete_native_semantics_v1.py \
  --verify-source --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
```

Only after the exact three owners are independently frozen, committed, and
pushed may the root coordinator request one exclusive new `0700` directory
and one exclusive new `0600` C source file:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_c_complete_native_semantics_v1.py \
  --apply --root-authorized \
  --frozen-commit PUSHED_FROZEN_COMMIT \
  --pushed-commit PUSHED_FROZEN_COMMIT \
  --source-sha256 SOURCE_SHA256 --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256
```

Materialization reads the unchanged first-party C input exactly once only
after all sixteen immutable plaintext owners and the identical root-only
semantic authorization path succeed. The new source is durable, digest-bound,
nofollow, descriptor-relative, and read back before successful return. It is
not compiled, imported, benchmarked, or executed by this controller.
