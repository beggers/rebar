# Freeze a from-scratch C build with recoverable root provenance

This is an independently reproducible source freeze, not a native build,
compatibility result, benchmark, or candidate qualification. Use only the
isolated, no-bytecode, pinned CPython **3.14.6**.

## What already happened

The existing version-16 first-party C build genuinely completed **14**
compiler and native-inspection roles in **two** independently reproduced
phases. Its small actual publication receipt is
`16794f5b1487b76a909a176948f4bbac8ed3108768f3127e27c44f9f392ae3d6`.
That receipt does **not** establish its private build-root path, device,
inode, or individual native outputs. Its archive is never opened.

The historical C compatibility result remains **FAIL**: **1,230** actual
differences and **7,325** independently verified passing observations in
the unchanged **31,237**-case, **13**-group original test. Compilation
does not make that candidate compatible.

The latest actual Rust compatibility result remains **FAIL**: **13**
workers started, **eight** groups completed, **12,942** checks verified,
and **five** infrastructure failures. The total semantic mismatch count
and underlying cause are **NOT MEASURED** and **NOT ESTABLISHED**. A
destructor warning is not evidence that it caused the failure.

The independent Rust version-19 build genuinely completed **28**
compiler and native-inspection processes. Its actual build receipt is
`27fbe6ec2077b05c1f8fe0b340f962d8d8f637b893c57d381108c9ed606cd0dc`;
its separately durable private-root receipt is
`de13207235055665c605cce1b88a8f2127f291b84a5954119a033c7f4e9a3c99`.
Neither the Rust engine nor any of its parser, compiler, executor,
matching operations, build roots, or archives is reused by C.

## The exact C implementation

The unchanged, independently written C parser and matching engine are
derived from `candidates/_vm_native.c`, SHA-256
`bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55`.
The actual Python integration is `candidates/vm_candidate.py`, SHA-256
`b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096`.
There is no `candidates/c_candidate.py`.

The complete, previously authenticated corrected C source is
`candidates/c/variants/subject_buffer_ownership_v1/vm_native.c`,
**222,212** bytes, SHA-256
`8131aea768a122308716b8a67903794aa03f2fed2e2022f53bb6aa7b7e10e962`.
Authenticate the original C source, real adapter, all four feature
owners, and the immutable C version-16 source, protocol, contract, and
actual small build receipt. Do not read installed native modules or
historical compressed reports.

Calling or wrapping Python `re`, `_sre`, an external regular-expression
package, Rust `regex`, PCRE, RE2, another candidate, an external
process, a network service, a hidden fallback, or stored oracle answers
is forbidden. Both actual C source and Python adapter must pass the
independent first-party token and syntax audits before a later build.
Runtime non-delegation remains **NOT ESTABLISHED** until separately
tested in a live candidate worker.

## Authenticate the actual current state

Bind all four complete, committed version-86 graph owners:

    tools/render_candidate_current_overview_v86.py
    49c529c7f8b695c501dd03f9d35056c2853c73fcd36425718d8bfceb599b1a7d

    docs/evidence/candidate-current-overview-v86.inputs.json
    42c534652a350eada8704581ebf8aa52c77687b6904e9fb486f03c2f117cbe6c

    docs/evidence/candidate-current-overview-v86.json
    ed728687e919410e6e9dae22ad3c976aa900d7a857f85231aaa93d0fc674f7cc

    docs/evidence/candidate-current-overview-v86.svg
    4bbf196a48997dbee3ea6b966d9a4eefce860962861675ad202506f685a80e55

Their **277** evidence owners and **282** historical references are
authenticated lower bounds, not repository-wide totals. Preserve all
six independently written engine families, the complete **31,237**
original checks, all **13** named private waivers, and the separate
**8,244** checks passed by each of **two** actual Python reference
workers. Do not merge the two test denominators. No candidate has
passed both suites or qualified.

The version-86 graph still records its original **4,194,304** planned
final cases as **NOT GENERATED**. Preserve that graph's denominator;
the newer **14,155,776**-case comparison is a separate, subsequently
published proposal, not a silently revised graph or an actual test.

Preserve the current expanded **14,155,776**-case final-comparison
proposal without opening or generating it. Its three public owner
hashes, in source, protocol, and contract order, are:

    3dd9abcbd7a87486186ee8da804de595e65d79020a3fe33413d0157dde4f3309
    818f1636d87ae721912f04a3fc8294ac04a59dff4a272319aa29a393f52a4fd4
    676aac4f48c9404f5253c89b692efde5c425170f8d9f152b4f85b3e2a5225a76

The proposal is **NOT FROZEN**, **NOT GENERATED**, **NOT OPENED**, and
**NOT RUN**. Its earlier **4,194,304**-case proposal remains unchanged.

## Prove source-only verification has no external effects

Bootstrap only the exact matcher-free Rust version-19 auditing and
canonical-JSON source. It is an auditing helper, not a matching
implementation. Install its restrictive physical audit wall before
reading any C version-18 context. The allowlist contains only exact,
immutable, separately pinned public source, graph, contract, and small
receipt owners. It contains no `.so`, archive, candidate import,
private build root, generated final case, compiler, network, or clock.

Do not execute the old C version-16 controller during source-only
verification: its ordinary `argparse` import would import `re` and
`_sre`. Load it only during a separately authorized future native build.
Synthetic controls must reject borrowed roots, incorrect `/tmp` device
assumptions, duplicate phase and artifact owners, reordered or
duplicated processes, external matchers, candidate imports, native
loading, old archives, hidden holdouts, source mutations, clocks,
threads, network, subprocesses, and real temporary roots. Synthetic
phase and native records are always labeled synthetic.

Replace the uppercase placeholders with the exact final three owner
hashes. Run each of the four mandatory source-only gates:

    /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B -S tools/reproduce_owned_c_subject_buffer_source_build_v18.py --self-test --source-sha256 SOURCE_SHA256 --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

    /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B -S tools/reproduce_owned_c_subject_buffer_source_build_v18.py --verify-frozen-context --source-sha256 SOURCE_SHA256 --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

    env -i PATH=/usr/bin:/bin /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B -S tools/reproduce_owned_c_subject_buffer_source_build_v18.py --self-test --source-sha256 SOURCE_SHA256 --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

    env -i PATH=/usr/bin:/bin /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B -S tools/reproduce_owned_c_subject_buffer_source_build_v18.py --verify-frozen-context --source-sha256 SOURCE_SHA256 --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

## A later, separately authorized real build

A native build is forbidden until all four source-only gates have
passed, all three new owners have been independently reviewed,
documented, committed, and pushed, and root explicitly authorizes one
actual build. Only then use the unique label
`phase2-v18-c-subject-buffer-root-provenance`, independently caller-pin
the exact phase-one owners, the unopened proposal, both canonical C
source owners, and the complete corrected **222,212**-byte C source.

The genuine immutable C version-16 compiler kernel must create a new
owner-private `/tmp/rebar-phase2-native-build-v8-c-*` root, with two
distinct **0700** phases. Its exact seven real process roles per phase
are `readelf_version`, `gcc_version`, `build_c_extension`,
`extension_dynamic`, `extension_symbols`, `extension_sections`, and
`extension_notes`. Require **14** distinct real process identifiers,
**four** exclusively written **0600** C-source and adapter owners,
and **two** independently owned, byte-identical C extension files.

Before any compiler process, authenticate the complete contents and
identities of all **five** frozen toolchain owners: Python **3.14.6**,
its `Python.h` and `patchlevel.h`, GCC **13**, and GNU `readelf`.
Record their actual SHA-256 fingerprints, byte counts, devices,
inodes, and executable states in both genuine new receipts. Do not run
the historical whole-repository verification or open historical
archives to establish these compiler identities.

Capture the actual private-root device and inode from a live
`O_DIRECTORY | O_NOFOLLOW` descriptor in the original successful
reproducibility callback. `/tmp` and the repository can be on
different filesystems; never substitute repository device **2064**
for an observed root device. Keep that descriptor open while the
original compiler verifies both complete native files, then recheck
its identity. Never enumerate `/tmp`, inspect a previous root, infer a
root from a historical receipt, or load a native module.

Publish the genuine canonical build success or failure first using
exclusive, no-follow, owner-private, file- and directory-synchronized
evidence. After and only after authenticating a genuine **PASS**
receipt and both first-party no-delegation source audits, publish one
separately durable, exclusively created root-provenance receipt. A
failed build preserves its actual failure; it never creates root
provenance. Both genuine new receipts must preserve the latest Rust
result as **12,942** verified cases and **five** infrastructure
failures; older **1,440** differences and **14,853** verified cases may
appear only when explicitly labeled historical. Successful compilation
proves only reproducibility and
private-root ownership, not candidate correctness, live independence,
memory safety, or speed.

Build: **NOT RUN**. Candidate matching: **NOT RUN**. Correctness:
**NOT MEASURED**. Live runtime independence: **NOT ESTABLISHED**.
Qualified candidates: **0**. Speed, memory, confidence intervals, and
undefined behavior: **NOT MEASURED**. Final holdout: **NOT FROZEN**,
**NOT GENERATED**, **NOT OPENED**. Winner: **NOT SELECTED**.
