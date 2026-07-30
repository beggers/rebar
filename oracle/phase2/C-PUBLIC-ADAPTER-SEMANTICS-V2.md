# Corrected root-only first-party C adapter experiment V2

Status: **SOURCE FROZEN; V1 FAILURE PRESERVED; V2 VARIANT NOT MATERIALIZED.**

The complete previous V1 source freeze remains immutable:

    tools/apply_owned_c_public_adapter_semantics_v1.py
    SHA-256  4604e145a6c5d135f690cb8ab2f869be33456e20f9ad27acc193f93fb1beaddb

    oracle/phase2/C-PUBLIC-ADAPTER-SEMANTICS-V1.md
    SHA-256  fe36c0ebba88d61375146bf22eb339456b86bf07f01ed8e0d64abe2c2562696a

    oracle/phase2/c-public-adapter-semantics-v1.json
    SHA-256  e0a794cf149b03880355e4660a669ebee4bca86efd937f09c3acfc79992afa6a

Its genuine, already-pushed root-only application failed before any candidate
source was read or variant target was created:

    oracle/phase2/evidence/c-public-adapter-semantics-v1-preapplication-failure.json
    SHA-256  d82ed4077f0b16310c7650bbe6c6f7c47f301d2d3a8f1f720c0958effc3788fa
    bytes    845
    device   2064
    inode    525054

The exact failed frozen and pushed commit was
`ccf7f71aba1df44b203a0b4d40b339feb7be8292`. Its recorded error is
`require complete independent controls before root-only candidate access`.

V1 used the expression:

```python
need(semantic_controls() and transform(synthetic_source()), message)
```

The first dictionary is truthy, so the expression evaluates to the second
nonempty `bytes` object. However, `need` explicitly requires
`condition is True`: a truthy bytes object is not the `True` singleton. The
four ordinary/sterile V1 source gates passed because they did not execute this
root-only branch. The failure proves no candidate was run, no output target
was created, no compatibility result changed, and no speed was measured.

V2 performs the independent controls as explicit values and computes a real
boolean before calling the exact same `need` guard:

```python
controls = semantic_controls()
synthetic = transform(synthetic_source())
ready = (
    type(controls) is dict
    and type(controls.get("semantic_checks")) is int
    and controls["semantic_checks"] >= 200
    and type(synthetic) is bytes
    and len(synthetic) > 0
)
need(ready, message)
need(type(ready) is bool and ready is True, regression_message)
```

The complete actual root-authorization control path now runs during every
source self-test and source verification. An explicit hostile case confirms
that giving the original nonempty bytes to `need` still fails. Only after this
identical, boolean-authenticated path has completed may a separately
authorized coordinator read the exact canonical candidate source once.

## Preserve every previous candidate result

The latest C12 result remains an authentic failed candidate:

    oracle/phase2/evidence/repaired-c-original-campaign-v12-c-phase2-v21-c-original-match-semantics-original-p0-v12-failures-publication-receipt.json
    SHA-256  a3f4b90b8f289df9dfe49f776266e3c290edb2c21c62713137f501a5f997c21b

Exactly **16,413** of the frozen **31,237** original checks have been verified;
all **606** observed differences remain preserved; the child-interpreter test
still failed before completion; the exact overall difference total is
**NOT MEASURED**. The 13 original groups, the 13 named private waivers,
the unmodified Python reference, and the full failure partition remain intact:

    managed buffer lifetime       16
    public object behavior       248
    substitution behavior        224
    public module behavior       114
    retained scanner lifetime      4
    total observed               606

The authenticated C21 first-party build remains unchanged:

    oracle/phase2/evidence/native-source-build-v21-c-phase2-v21-c-original-match-semantics-publication-receipt.json
    SHA-256  9475dd0c441a0440136f12425f94e6a4244e4cdc52d49f803e891f6663a647df

    oracle/phase2/evidence/native-source-build-v21-c-phase2-v21-c-original-match-semantics-root-provenance-receipt.json
    SHA-256  8f913d623bf5bb4aec3669e9b3daa882df16aad6f2f1bc3db1f02f4988a8afa2

Its independently authored C source digest is
`fe5bd423cb93b982bce79c584f19ad6eb254ab927008b21b37427de9e6ecf3c2`;
both independently built native outputs have digest
`7a5f8db27154cdcbd4203d727e02c0828ba1f9bf3fa2fdc1a86223ee57825f60`.

The unchanged canonical adapter is:

    candidates/vm_candidate.py
    SHA-256  b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096
    bytes    60707
    device   2064
    inode    428074

The predicted exact corrected bytes are identical to V1, but are written only
to a completely fresh, exclusive V2 path:

    candidates/c/variants/public_adapter_semantics_v2/vm_candidate.py
    SHA-256  4a62cb318592600d53e5ed6b9f8b9edf4edf2068fb2453892ca2130bb203410a
    bytes    61663

The seven reversible corrections still implement all standard public flag
aliases and module identity, exact flag ordering and unknown values,
`PatternError.__module__`, exact subclass cache identity, 512-entry LRU and
256-entry FIFO caches, uncached `DEBUG` compilations, and complete `purge`.
The known **330** disjoint public adapter failures and eight additional public
alias/module obligations are unchanged. No extra test cases are invented, no
outside matching package is wrapped, and the first-party native C engine is
not replaced, run, or borrowed from another candidate.

## Source gates and separately authorized root application

A deny-default descriptor wall and audit hook are installed before any owner
read. Source verification opens exactly ten immutable plaintext files: the
three V2 owners, the three original V1 owners, the real V1 failure receipt,
the C12 candidate failure receipt, and the two C21 build receipts. It never
opens the canonical candidate, a native binary, a private build root, a
compressed archive, the frozen oracle, any final-test data, or a network.
Self-test opens no workspace owner.

Run both ordinary checks:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_c_public_adapter_semantics_v2.py --self-test

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_c_public_adapter_semantics_v2.py \
  --verify-source --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
```

Repeat both under `env -i PATH=/usr/bin:/bin LC_ALL=C`. Each successful gate
confirms that the actual root preauthorization path has passed and that the
specific V1 truthy-bytes regression was independently rejected.

After the exact three V2 source owners are committed and pushed, only the root
coordinator may request the exclusive V2 adapter materialization:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_c_public_adapter_semantics_v2.py \
  --apply --root-authorized \
  --frozen-commit PUSHED_FROZEN_COMMIT \
  --pushed-commit PUSHED_FROZEN_COMMIT \
  --source-sha256 SOURCE_SHA256 --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256
```

The sole permitted mutation is one new exclusive `0700` V2 directory and one
new exclusive `0600` adapter file; both are descriptor-relative, nofollow,
flushed, and read back with the exact predicted digest. The failed V1 target
is never created, no existing candidate or user file changes, and the V1
source freeze and failure receipt remain immutable.

Candidate matching and compatibility remain **NOT MEASURED**. Runtime
non-delegation remains **NOT ESTABLISHED**. No candidate build, execution,
performance trial, qualification, or winner selection occurs in this phase.
