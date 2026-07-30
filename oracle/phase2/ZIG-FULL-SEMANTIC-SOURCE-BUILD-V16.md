# Independently build the complete first-party Zig candidate twice

Status: **SOURCE FREEZE ONLY. NO COMPILER, CANDIDATE, RUNTIME GUARD,
BENCHMARK, OR HIDDEN TEST HAS BEEN RUN.**

This protocol freezes one future, root-authorized, reproducible source build
of the fully corrected Zig implementation. It combines the exact independently
authored Zig regular-expression parser, compiler, and matching executor with
the complete first-party Python adapter and CPython C-API bridge. No existing
regular-expression package, CPython matching engine, another project engine,
matching fallback, or network download may provide matching.

## Exact independently owned matching sources

```text
first-party Zig engine, 186,915 bytes
candidates/zig/mini_regex.zig
a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28

complete corrected Python adapter, 67,735 bytes
candidates/zig/variants/public_adapter_semantics_v1/zig_candidate.py
7129c63bdfd3c265a44541500238c26a8a5511f8932140de7d06bb49c13f588d

complete corrected CPython C-API bridge, 176,765 bytes
candidates/zig/variants/replacement_event_semantics_v1/py_bridge.c
07337863f6b4a0e749a8d60b2e5704bb961e43dc09bfa85c238f0efa40d3583c
```

The sole native Python-module import is the exact digest-bound bridge call
`PyImport_ImportModule("copyreg")`, which implements the Python-compatible
`Match.__reduce_ex__` behavior for old pickle protocols. It is allowed only
in the bridge, only once, only with the literal `copyreg`, and only after the
complete corrected bridge source digest is verified. The native engine must
never import that symbol. Every other Python importer, `_sre` engine symbol,
existing regex package, native dynamic loader, external regex symbol, and
cross-family engine remains forbidden. The bridge's `_sre.SRE_Scanner` display
name is a required compatibility string, not an imported matching engine.

## Preserve original failures and correct runtime policy

Preserve the independently published Zig V12 original candidate failure:
**4,607** verified passing checks, at least **1,700** actually observed
semantic differences, one incomplete interpreter group, **13** distinct
workers, and all named historical failures. The complete mismatch count is
**NOT MEASURED**. Its plaintext receipt is:

```text
oracle/phase2/evidence/repaired-zig-original-campaign-v12-phase2-v13-zig-guard-clean-v1-original-p0-v12-failures-publication-receipt.json
ce7605be25bbb71e1b06b65b9aa3f79cfd09b39f0ce5f076ed9d986f15ee8de9
```

The unchanged original reference has exactly **31,237** cases, **13** groups,
**13** named private waivers, **73** mapped obligations, and **34** complete
crosswalks. The separate **8,244** reference cases never enter that denominator.

Authenticate the strict version-4 first-party interpreter guard without
executing it or calling its provider proof:

```text
source    5b498643fa730dc09090bdc9e189e2d395cbe41a2b14019937eb251fd38240f3
protocol  835473a98f62c9b2cb0dee61736b6cbbab4460f14d8371597e80933c64721a16
contract  30f5c52d5aadfd6e8a7be7c6f355d9628510384d7fd922bcfb609dfe854acea2
```

The old version-3 guard is preserved only as history; it must not replace the
genuine version-4 native/public live-set interpreter attestation. A future
matching campaign must separately install version 4 before candidate import.

## Two genuinely independent native source builds

The pinned offline stable Zig compiler is
`/tmp/zig-x86_64-linux-0.16.0/zig`, SHA-256
`2317bbb91798556d9d0f38aabdac23db83f0979b25f767259ae474546724087c`.
Authenticate the exact CPython 3.14.6 executable and headers, official Zig
lock, GCC 13, and ELF inspector using the previously frozen V13 source-build
toolchain identities. Do not use `PATH` discovery or download dependencies.

Only an explicitly root-authorized `--build --root-authorized
--frozen-committed-pushed --frozen-commit COMMIT --pushed-commit COMMIT
--label FRESH-LABEL` may create one fresh, mode-`0700` private `/tmp` root.
Build `reference-a` and `reference-b` independently. Each gets three distinct,
mode-`0600` copies of the complete corrected engine, bridge, and adapter.
Each phase runs exactly **13** pinned real processes: three compiler/tool
version inspections, one Zig `ReleaseFast` engine compilation, one optimized
CPython bridge compilation, and eight complete ELF inspections. Thus **26**
real, uniquely identified processes and six distinct source snapshots exist
only after successful execution.

Both engine outputs and both bridge outputs must be byte-identical across
genuinely separate phase inodes. Each bridge must link only its own adjacent
Zig engine and libc, with `$ORIGIN`; the Zig engine links only libc and its
first-party Python Unicode helpers. Preserve every process's complete output,
command, environment, PID, and return code. Publish exactly one exclusive,
fsynced private-root receipt and one independently linked, fsynced actual-build
receipt. Keep a successful root for a separately frozen matching campaign.
On failure, clean only the exact descriptor-verified private root; never touch
the repository, `/tmp`, or another candidate. Preserve an actual build failure.

## Four physically isolated source-only gates

The frozen source and contract may be verified ordinarily and under
`env -i PATH=/usr/bin:/bin LC_ALL=C` using the exact pinned interpreter with
`-I -B -S`. Execute `--verify-frozen-context` and `--self-test` in both
environments, independently supplying all V16 source/protocol/contract pins,
all three V13 build pins, all three V13 campaign pins, all three V4 guard pins,
and the corrected adapter, corrected bridge, original Zig engine, official
toolchain lock, and actual historical failure receipt pins.

Before any predecessor byte is opened, source-only modes install a strict
physical allowlist that excludes every proposal, hidden case, seed, archive,
native object, private root, subprocess, clock, network connection, thread,
candidate import, runtime guard, compiler, canonical mutation, and build
receipt. Explicit hostile controls must reject evidence tampering, omitted
suites, altered historical losses, source substitutions, unsafe `copyreg`
exceptions, weakened symbol exclusions, forged caller pins, escaped root and
label paths, and premature candidate qualification.

Actual Zig native build: **NOT RUN**. Original and broader candidate matching:
**NOT RUN**. Runtime no-delegation: **NOT ESTABLISHED**. Candidate
qualification, undefined behavior, memory, and final performance:
**NOT MEASURED**. Qualified candidates: **0**. Hidden holdout: **NOT OPENED**.
No winner.
