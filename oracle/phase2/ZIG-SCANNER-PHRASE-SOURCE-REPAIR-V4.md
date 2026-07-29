# Freeze the complete first-party Zig Scanner correction

Status: **SOURCE FROZEN; NOT BUILT; NOT TESTED.**

This is one source-only phase-two candidate feature, authorized only after
the independently published phase-one Python-oracle readiness passed. It
materializes a complete, separately owned Zig Python adapter. It does not
modify the original adapter, Zig parser, compiler, executor, C bridge, public
entrypoint, or any other candidate.

## Retain the actual Python oracle and all failures

Pinned isolated CPython 3.14.6 remains the only correctness oracle. The
published version-four readiness has **73** mapped original obligations,
**31,237** original cases, **13** complete suites, and **13** named private
waivers. Two independent Python reference workers separately passed all
**8,244** supplemental differential, property, and fuzz cases. The 8,244
supplemental cases do not change the 31,237-case original denominator, and
no candidate has run them.

The current, actually pushed version-72 graph has SHA-256:

- Source: `b279901481d2f4f6bc1adeae542d5aacf2453dedbcff88a944a79ce5c8478753`.
- Inputs: `28f235f8bbb7e49de25a1194fa0693e9764d3e5b0ef7a3e5a4da8e273f22eaef`.
- Summary: `2b5dba28961c0842fc15df1afdca49eeb20613df05b31c1bd4a16491f7f9c25b`.
- Image: `eb2708426467a85a6d7ee592c4dde21fc08b57f8a17822a0b60732f44f22e804`.

Its independently authenticated lower bounds are **239** evidence owners
and **244** historical references. They are lower bounds, not a complete
repository census. This source feature adds no actual matching-result owner.

The previous complete Zig original-suite result is **FAIL**: **1,764**
observed differences, **3,711** explicitly verified passing cases, all
**13** distinct workers and suites completed, and zero infrastructure
failures. Its small receipt has SHA-256
`40be94851ae23d8c4a9d2ac759d28231605247a499b0703e727c757d25b2fb96`.
Publication **PASS** means durable publication only. Do not decompress a
matching archive, invent per-suite mismatch counts, subtract failures to
invent passes, report a corrected result, or qualify this candidate.

The same graph preserves the actually completed Rust version-19 native build:
**PASS**, **28** compiler processes, **2** independent phases, verified
private-root provenance, and **NOT RUN** matching. The earlier Rust
version-11 campaign remains blocked without independently verified
private-root provenance. The completed C native build is **PASS** for
**14** compiler processes; its matching remains **NOT RUN**. Neither build
pass is a candidate correctness pass. The latest completed Rust matching
remains **FAIL**, with **1,440** observed differences and **14,853**
explicitly verified passes. The latest completed C matching remains
**FAIL**, with **1,230** observed differences and **7,325** explicitly
verified passes. Never derive passing counts by subtraction.

## Correct exactly one first-party Scanner behavior

The project owns its Zig regular-expression parser, compiler, and matching
executor:

```text
candidates/zig/mini_regex.zig
a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28

candidates/zig/py_bridge.c
67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b

candidates/zig_candidate.py
2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862
```

CPython's Scanner gives each lexicon branch one exposed capture slot. It
raises `RuntimeError("invalid SRE code")` when any individual phrase
requires more capture slots than there are branches. The original owned
Zig adapter already calculates each phrase's capture count, but its
constructor rejects only an empty lexicon.

Replace the one exact 112-byte constructor block with its exact 220-byte
first-party counterpart:

```python
group_count = len(branches)
if not group_count or any(
    local_groups > group_count
    for _body, local_groups in branches
):
    raise RuntimeError("invalid SRE code")
```

The check happens before source assembly and native compilation. The empty
lexicon still raises the same exception. All other complete original
adapter bytes, every capture, replacement, buffer and match lifetime, all
engine and bridge bytes, and the separate duplicate-loader issue are
preserved.

The complete corrected source has exactly **68,530** bytes:

```text
candidates/zig/variants/scanner_phrase_v4/zig_candidate.py
0ab9f56b469df7939af8a221a4deac9351de2162960085ca7fa2d69179480e2b
```

This remains the existing Zig family, not a seventh engine. Python's
`re`, `_sre`, external regex packages, another candidate, fallbacks,
hidden matching answers, and unverified native activation are forbidden.

## Verify the entire frozen original Scanner matrix

Authenticate and reconstruct only the independently owned, pure matrix
syntax in `tools/rust_scanner_differential_v1.py`. Do not import or
execute that module. Preserve all **1,024** source-derived cases,
**32** families, and **32** variants per family:

```text
matrix SHA-256
83a8ad125b36846c1790ca01564305b2ab9714185f972efa838740b7bbf4b55c

all 64 affected source-witness identifiers SHA-256
e1b75493de4be5ea1583e30077737405112b22fdb072cd8b0e38e2770a2959e6
```

The source-derived capture overflow histogram is exactly **32** nested,
**16** numbered, and **16** named cases. Preserve the other **960**
original stimuli. The first archived failure is
`scanner-differential.v1.0160`; the remaining source-derived witnesses
are not claimed to be archive-extracted. The separately observed **620**
verbose-scanner differences remain unrepaired. No original case, warning,
exception, public contract, memory lifetime, supplemental case, or waiver
is dropped.

## Four source-only gates

Supply six independently computed caller pins: the V4 source, protocol,
and all four exact version-72 graph owners. For self-test and context
verification, also independently supply the complete V4 contract hash.

Use only:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B
```

Run `--self-test` and `--verify-frozen-context` once in the ordinary
environment and once with `env -i PATH=/usr/bin:/bin LC_ALL=C`.
The source-only wall physically blocks candidate and standard-regex
imports, native loading, compiler and test processes, matching and
reference archives, temporary files, writes, network, threads, clocks,
locks, signals, the expanded holdout, and performance measurements.

Only a separately frozen and explicitly authorized future build may
compile this variant. Only a later independently authorized complete
candidate campaign may test all original and supplemental obligations.

Corrected Zig native build: **NOT RUN**.
Corrected Zig original matching: **NOT RUN**.
Corrected Zig supplemental matching: **NOT RUN**.
Runtime non-delegation: **NOT ESTABLISHED**.
Qualified candidates: **0**.
Performance, memory, and undefined behavior: **NOT MEASURED**.
Holdout: **NOT OPENED**. Winner: **NOT SELECTED**.
