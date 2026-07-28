# V8 first-party C source-build freeze

Status: source freeze only. No V8 compiler has run, no repaired source has
been written, and no candidate has been imported or tested.

This is a small, explicitly controlled attempt to repair our own C engine.
It does not wrap, invoke, import, or link to Python's regular-expression
engine or an external regular-expression package. It does not change any of
the 25 frozen candidate source files.

## Exactly what is frozen

The baseline remains the complete CPython 3.14.6 oracle: 13 frozen suites,
31,237 counted case executions, and 13 explicitly named private upstream
waivers. The hidden performance holdout remains unopened.

The unchanged candidates/_vm_native.c is 218,185 bytes with SHA-256
bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55.
The unchanged candidates/vm_candidate.py is 60,707 bytes with SHA-256
b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096.

The separately frozen first-party repair changes exactly one anchored block
in the C substitution function. Its private derived result is 218,308 bytes
with SHA-256
f44694759174c1c3975423e07095ae91a853e66242c4e55d11836df03a730c4d.
It prepares a non-callable replacement before acquiring a subject buffer.
Callable replacements, existing PyBUF_SIMPLE behavior, and the single
successful subject-release path remain intact. Failed subject acquisition
releases the prepared template exactly once and never releases an
unacquired subject.

Only the authenticated, frozen apply_private function in
tools/apply_owned_first_party_source_repair_v1.py can write the repair.
Source verification derives and independently audits the bytes in memory;
it never calls apply_private or writes the derived source.

## Future explicit build boundary

An actual build is a separate, explicitly pinned --build. Its fresh root
must match /tmp/rebar-phase2-native-build-v8-c-*. Both reference-a and
reference-b, their source directories, and their candidates directories
must already be distinct, real, owner-only mode-0700 directories before the
first repair application.

Each phase copies the unchanged adapter and calls the frozen source repair
exactly once. Its derived C destination must not already exist. The file is
created with O_CREAT, O_EXCL, and O_NOFOLLOW in mode 0600. The repository
sources are authenticated again after every application. The older
original-source snapshot copier and original-source reproducibility
verifier are forbidden for the repaired source.

Each phase runs the authenticated V7 C compiler with its exact strict flags.
It records exactly seven separate actual processes: the compiler and ELF
inspector version checks, C compilation, and dynamic, exported-symbol,
section, and note inspections. Both phases together run exactly 14
processes. The complete ELF bytes, unchanged adapter snapshots, repaired
source snapshots, and distinct phase identities must agree.

An actual separately authorized pass or failure is a fresh canonical,
deterministically compressed report and an exclusive durable receipt.
Files and their directory are synchronized. Failures remain visible.
A successfully published receipt never turns a failed build or candidate
into a pass.

## Preserved history

The frozen repair authenticates all 76 digest-addressed V19 historical
references. This is different from the 71 actual repository evidence owners.
The inherited V7 history retains 169 actual historical compiler and
inspection processes.

The 13-suite Go campaign remains a failure: 4,518 semantic mismatches and
four infrastructure failures. Its restoration passed. No candidate is
qualified, no performance or memory has been measured, and no winner has
been selected.

## Gates

Run the isolated, effect-blocked, in-memory source self-test:

    /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
      -I -B tools/reproduce_owned_native_source_build_v8.py --self-test

Read-only context verification requires independent exact SHA-256 pins for
the V8 recorder, this document, and the V8 machine contract:

    /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
      -I -B tools/reproduce_owned_native_source_build_v8.py --verify-context \
      --source-sha256 RECORDER_SHA256 \
      --protocol-sha256 PROTOCOL_SHA256 \
      --contract-sha256 CONTRACT_SHA256

Neither operation compiles, applies source, imports a candidate, opens the
hidden holdout, samples a clock, measures performance, or chooses a winner.
