# First-party C18 original correctness campaign, version 6

## Scope and honest status

This is a frozen, explicitly runnable correctness experiment for the
first-party C regular-expression engine. Freezing this protocol, checking its
source, or rendering its machine contract does not run the engine, qualify a
candidate, measure performance, or open a holdout. Until the separately pinned
actual command is run, C18 candidate correctness is **NOT MEASURED**.

CPython 3.14.6, invoked with `-I -B -S`, is the frozen oracle. The denominator
is exactly 31,237 genuine original observations across these complete suites:

| Original suite | Cases |
| --- | ---: |
| `original_bounded_v5` | 151 |
| `public_v3` | 864 |
| `scanner_v3` | 1,024 |
| `buffer_v3` | 768 |
| `managed_v1` | 1,024 |
| `scanner_verbose_v1` | 2,854 |
| `public_types_v1` | 6,912 |
| `substitution_v2` | 5,120 |
| `shape_v2` | 10,240 |
| `public_surface_v19` | 1,376 |
| `subinterpreter_v2` | 128 |
| `pep688_v4` | 264 |
| `threaded_pattern_v1` | 512 |
| Total | 31,237 |

The separately published 8,244-case differential references are not candidate
executions and are never added to this denominator. The proposed
14,155,776-case performance holdout is **NOT GENERATED; NOT OPENED**. Speed,
memory, confidence intervals, and undefined behavior are **NOT MEASURED**.

## Authenticated build, source, and references

The campaign requires the independently frozen C18 build source, protocol, and
machine contract. It independently authenticates both small, already published
C18 build and root-provenance receipts. They prove 14 genuine toolchain
processes, two genuinely separate source phases, four distinct private phase
source owners, and two distinct, byte-identical native outputs. A successful
build means reproducible native compilation and root provenance only; it is
not a regex correctness result.

The original canonical C source is
`bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55`.
The separately source-owned and actually compiled corrected variant is
`8131aea768a122308716b8a67903794aa03f2fed2e2022f53bb6aa7b7e10e962`.
The unchanged first-party Python adapter is
`b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096`.
The genuine C18 combined native engine and bridge is
`f3794f963819a9af3798c1d97f32edcbc2a117f9ed20c56ec554a605de82eeae`,
163,504 bytes. The frozen V5 producer remains unmodified on disk: the worker
constructs an exact, authenticated corrected-source C family in memory so the
observed source really is the source that produced the tested native output.

Passing phase-one V4 authorizes candidate evaluation. The independently frozen
phase-one V1 manifest
`cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f`
provides the actual archived original reference vectors to the unmodified V5
direct-suite observer. It does not replace the V4 authorization. In
particular, the public-types suite retains V5's separately corrected
independent 6,912-record baseline. Source-only operations authenticate
manifest bytes without opening any reference archive.

## Actual guard and reversible activation

An actual worker installs the immutable strict version-2 runtime guard before
importing `candidates.vm_candidate` or the first-party
`candidates._vm_native` bridge. No standard-library regex engine, third-party
regex engine, alternative candidate, `ctypes` loader, or fallback is admitted.
Both separately tagged native roles must identify the very same authenticated
C18 native inode. A single, exactly authenticated historical top-level
`ctypes` import is replaced by a fail-closed proxy in memory; historical and
current producer source files are never edited.

Only an explicit, independently pinned actual operation may open the exact
receipt-bound C18 phase. Its private output has mode `0700` and resides on a
different device from the workspace. The controller first durably journals the
original workspace native, creates an adjacent hard-link backup, publishes
exclusive stage and promotion intentions, streams a new same-device native at
mode `0600`, and atomically promotes only that journal-bound inode. It restores
the exact original inode, bytes, and `0755` mode before publishing results.
An interrupted activation can be recovered only with the exact frozen
controller, full actual authorization, and caller-pinned recovery journal.

Every suite receives a distinct pinned `-I -B -S` worker and a hard **120
second per-suite timeout**. A timeout, crash, malformed result, output limit,
or actual candidate execution failure is published as a failure; the
controller still attempts every remaining original suite. Complete stdout,
stderr, original records, semantic mismatches, and genuine producer failure
details are retained. Neither a durable publication `PASS` nor a build `PASS`
means candidate correctness `PASS`.

The authentic externally prepared original locales are `en_US.iso88591` and
`en_US.utf8`; a candidate worker never starts `localedef`. Original scoped
fork and correctness-clock cases, 11 real guarded subinterpreters and 394
nested execution calls, and shared-thread obligations remain intact. No timing
trial or performance benchmark is authorized.

## Source-only and explicit-operation boundary

The only source-only modes are `--self-test`, `--verify-frozen-context`, and
`--render-contract`. They physically deny candidate imports, installed-native
inspection, private-root access, archive access, subprocesses, clocks,
workspace mutation, and the sealed holdout. Each independently requires the
V6 source and protocol SHA-256; self-test and context verification additionally
require the exact machine contract SHA-256.

`--run`, `--worker`, and `--recover` are distinct actual operations, never
implicit source gates. Every actual operation additionally requires all exact
machine-contract `actual_operation_policy.required_authority` flags, including
the independently frozen C18 owner triplet, both genuine C18 receipts, the V5
producer owner triplet, strict V2 guard owner triplet, passing V4 contract,
original V1 reference manifest, unopened proposal contract, both native-role
digests, family, label, and exact 120-second worker bound. The controller
constructs actual worker flags itself. No caller-supplied guessed private
root, external regex package, alternate engine, benchmark, or holdout path is
accepted.

The evidence preserves the previous complete failing C10 and C15 results and
the signed Rust observation: 13 attempted suites, eight completed suites,
five infrastructure failures, and 12,942 verified passing cases. The Rust
semantic mismatch count and underlying failure cause remain **NOT MEASURED**
and **NOT ESTABLISHED**, respectively. A separately authenticated version-87
overview is explicitly the overview at this source freeze, not a claim that no
newer chart can subsequently be published.

Only zero semantic mismatches, zero infrastructure or execution failures, all
13 complete original suites, all 31,237 original observations, a genuine
guard-first run, and exact original-native restoration may qualify this C
candidate. Three qualified independent families, the frozen performance
oracle, holdout speedup, a winner, and `import rebar as re` remain unproven.
